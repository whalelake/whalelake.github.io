#!/usr/bin/env python3
"""Create the daily fixed-topic Jekyll posts."""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import html
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

TRENDS_RSS_URL = "https://trends.google.com/trending/rss?geo=KR"
HT_NS = "{https://trends.google.com/trending/rss}"


@dataclass(frozen=True)
class DailyPost:
    topic: str
    category: str
    slug: str
    title_label: str
    tags: tuple[str, ...]
    hour: int


@dataclass(frozen=True)
class CreateResult:
    created: list[Path]
    skipped: list[Path]


@dataclass(frozen=True)
class NewsItem:
    title: str
    source: str
    url: str


@dataclass(frozen=True)
class TrendIssue:
    title: str
    approx_traffic: str
    pub_date: str
    news_items: tuple[NewsItem, ...]


DAILY_POSTS: tuple[DailyPost, ...] = (
    DailyPost(
        topic="시사",
        category="Current Affairs",
        slug="current-affairs",
        title_label="시사",
        tags=("current-affairs", "society"),
        hour=9,
    ),
    DailyPost(
        topic="AI",
        category="AI",
        slug="ai",
        title_label="AI",
        tags=("ai", "technology"),
        hour=13,
    ),
    DailyPost(
        topic="개발",
        category="Development",
        slug="development",
        title_label="개발",
        tags=("development", "programming"),
        hour=17,
    ),
)


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return html.unescape(value).strip()


def object_particle(value: str) -> str:
    if not value:
        return "를"
    last = value[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:
        return "을" if (code - 0xAC00) % 28 else "를"
    return "을"


def format_pub_date_kst(value: str) -> str:
    if not value:
        return "확인 필요"
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return value
    kst = parsed.astimezone(dt.timezone(dt.timedelta(hours=9)))
    return f"{kst:%Y-%m-%d %H:%M} KST"


def parse_date(value: str | None) -> dt.date:
    if value:
        return dt.date.fromisoformat(value)
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date()


def post_filename(post: DailyPost, target_date: dt.date) -> str:
    return f"{target_date.isoformat()}-{post.slug}-daily-note.md"


def trend_post_filename(target_date: dt.date, index: int) -> str:
    return f"{target_date.isoformat()}-hot-issue-{index:02d}.md"


def render_post(post: DailyPost, target_date: dt.date) -> str:
    display_date = target_date.strftime("%Y년 %m월 %d일")
    post_time = dt.datetime.combine(target_date, dt.time(post.hour, 0))
    tags = ", ".join((*post.tags, "daily-note"))
    title = f"{display_date} {post.title_label} 노트"

    return f"""---
title: "{title}"
date: {post_time:%Y-%m-%d %H:%M:%S} +0900
categories: [{post.category}]
tags: [{tags}]
excerpt: "{display_date}에 남기는 {post.topic} 분야의 관찰과 질문."
---

## 오늘의 질문

- 오늘 {post.topic}에서 가장 중요하게 볼 변화는 무엇인가?
- 이 변화가 개인, 조직, 혹은 개발자의 일하는 방식에 어떤 영향을 줄 수 있는가?
- 당장 확인해야 할 근거와 후속 질문은 무엇인가?

## 관찰

오늘의 {post.topic} 노트는 하나의 결론보다 판단의 재료를 남기는 데 목적이 있다. 눈에 띄는 변화, 반복해서 등장하는 신호, 아직 확인이 필요한 가정을 분리해 기록한다.

## 해석

현상 자체보다 중요한 것은 그 현상이 어떤 방향으로 이어질 가능성이 있는지다. 단기적인 반응과 장기적인 구조 변화를 구분해서 바라본다.

## 다음 확인할 것

- 관련 자료와 원문 확인
- 이해관계자와 사용자 관점 정리
- 다음 글에서 이어서 볼 질문 선정
"""


def fetch_google_trends_rss(url: str = TRENDS_RSS_URL, timeout: int = 20) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "whalelake-blog-automation/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def parse_trend_issues(rss_xml: str, limit: int = 3) -> list[TrendIssue]:
    root = ET.fromstring(rss_xml)
    issues: list[TrendIssue] = []

    for item in root.findall("./channel/item"):
        news_items: list[NewsItem] = []
        for news in item.findall(f"{HT_NS}news_item"):
            news_items.append(
                NewsItem(
                    title=clean_text(news.findtext(f"{HT_NS}news_item_title")),
                    source=clean_text(news.findtext(f"{HT_NS}news_item_source")),
                    url=clean_text(news.findtext(f"{HT_NS}news_item_url")),
                )
            )

        issues.append(
            TrendIssue(
                title=clean_text(item.findtext("title")),
                approx_traffic=clean_text(item.findtext(f"{HT_NS}approx_traffic")),
                pub_date=clean_text(item.findtext("pubDate")),
                news_items=tuple(news_items),
            )
        )

        if len(issues) >= limit:
            break

    return issues


def render_trend_post(issue: TrendIssue, target_date: dt.date, index: int) -> str:
    display_date = target_date.strftime("%Y년 %m월 %d일")
    post_time = dt.datetime.combine(target_date, dt.time(8 + index, 0))
    safe_title = issue.title.replace('"', "'")
    excerpt = f"{display_date} Google Trends Korea 핫이슈 '{safe_title}'{object_particle(safe_title)} 보고 남기는 관찰과 생각."
    references = "\n".join(
        f"- {item.source}: {item.title}" if item.source else f"- {item.title}"
        for item in issue.news_items[:3]
        if item.title
    )
    if not references:
        references = "- Google Trends RSS에 연결된 관련 기사 없음"

    source_links = "\n".join(
        f"- [{item.source or '관련 기사'}]({item.url})"
        for item in issue.news_items[:3]
        if item.url
    )
    if not source_links:
        source_links = "- 관련 기사 링크 없음"

    return f"""---
title: "{display_date} 핫이슈: {safe_title}"
date: {post_time:%Y-%m-%d %H:%M:%S} +0900
categories: [Current Affairs]
tags: [google-trends, hot-issue, korea, daily-note]
excerpt: "{excerpt}"
---

## 오늘의 신호

- 검색어: **{issue.title}**
- 추정 검색량: {issue.approx_traffic or "확인 필요"}
- Google Trends 반영 시각: {format_pub_date_kst(issue.pub_date)}

## 함께 뜬 기사

{references}

## 내 생각

이 검색어가 올라왔다는 것은 사람들이 단순히 뉴스를 소비하는 수준을 넘어, 사건의 의미나 다음 전개를 직접 확인하려는 단계에 들어섰다는 신호로 볼 수 있다. 검색량은 여론 그 자체는 아니지만, 관심이 어디로 쏠리는지 보여주는 빠른 온도계다.

내가 오늘 주목하는 지점은 세 가지다. 첫째, 이 이슈가 일회성 화제인지 아니면 반복될 구조적 변화의 표면인지 봐야 한다. 둘째, 관련 기사들이 같은 사실을 다르게 해석하고 있는지 확인해야 한다. 셋째, 검색어 자체가 사람들의 궁금증을 얼마나 정확히 드러내는지 살펴야 한다.

## 더 확인할 질문

- 이 검색어가 갑자기 오른 직접 계기는 무엇인가?
- 관련 보도는 사실 확인, 해석, 전망을 구분하고 있는가?
- 내일도 이어질 이슈인지, 오늘의 관심으로 끝날 이슈인지 판단할 근거는 무엇인가?

## 참고 링크

{source_links}
"""


def create_daily_posts(target_date: dt.date, output_dir: Path, force: bool = False) -> CreateResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    skipped: list[Path] = []

    for post in DAILY_POSTS:
        target = output_dir / post_filename(post, target_date)
        if target.exists() and not force:
            skipped.append(target)
            continue

        target.write_text(render_post(post, target_date), encoding="utf-8")
        created.append(target)

    return CreateResult(created=created, skipped=skipped)


def create_trend_posts(
    target_date: dt.date,
    output_dir: Path,
    issues: list[TrendIssue],
    force: bool = False,
) -> CreateResult:
    if len(issues) < 3:
        raise ValueError(f"Expected at least 3 trend issues, got {len(issues)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    skipped: list[Path] = []

    for index, issue in enumerate(issues[:3], start=1):
        target = output_dir / trend_post_filename(target_date, index)
        if target.exists() and not force:
            skipped.append(target)
            continue

        target.write_text(render_trend_post(issue, target_date, index), encoding="utf-8")
        created.append(target)

    return CreateResult(created=created, skipped=skipped)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create three fixed-topic daily Jekyll posts.")
    parser.add_argument("--date", help="Target date in YYYY-MM-DD format. Defaults to today in Asia/Seoul.")
    parser.add_argument("--output-dir", default="_posts", help="Directory where Markdown posts are written.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing posts for the date.")
    parser.add_argument(
        "--source",
        choices=("trends", "fixed"),
        default="trends",
        help="Use Google Trends Korea hot issues or fixed topic placeholders.",
    )
    parser.add_argument("--trends-url", default=TRENDS_RSS_URL, help="Google Trends RSS URL.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target_date = parse_date(args.date)

    if args.source == "trends":
        rss_xml = fetch_google_trends_rss(args.trends_url)
        issues = parse_trend_issues(rss_xml, limit=3)
        result = create_trend_posts(target_date, Path(args.output_dir), issues, force=args.force)
    else:
        result = create_daily_posts(target_date, Path(args.output_dir), force=args.force)

    for path in result.created:
        print(f"created {path}")
    for path in result.skipped:
        print(f"skipped {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
