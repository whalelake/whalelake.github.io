#!/usr/bin/env python3
"""Create the daily fixed-topic Jekyll posts."""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import html
import re
from html.parser import HTMLParser
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
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
class ArticleContext:
    title: str
    source: str
    url: str
    summary: str


@dataclass(frozen=True)
class TrendIssue:
    title: str
    approx_traffic: str
    pub_date: str
    news_items: tuple[NewsItem, ...]
    article_contexts: tuple[ArticleContext, ...] = ()

    def with_article_contexts(self, contexts: tuple[ArticleContext, ...]) -> "TrendIssue":
        return replace(self, article_contexts=contexts)


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
    return " ".join(html.unescape(value).split())


def truncate_text(value: str, limit: int = 240) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def clean_article_summary(value: str) -> str:
    summary = clean_text(value)
    stop_patterns = [
        "Copyright",
        "무단 전재",
        "무단전재",
        "재배포 금지",
        "공감언론",
        "◎",
        "저작권자",
    ]
    for pattern in stop_patterns:
        index = summary.find(pattern)
        if index >= 0:
            summary = summary[:index].strip()

    summary = re.sub(r"\S+@\S+", "", summary)
    return clean_text(summary)


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


class ArticleHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.description = ""
        self.paragraphs: list[str] = []
        self._tag_stack: list[str] = []
        self._current_text: list[str] = []
        self._current_tag = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        if tag in {"script", "style", "nav", "header", "footer", "aside"}:
            self._tag_stack.append(tag)
            return

        if tag == "meta":
            key = (attrs_dict.get("property") or attrs_dict.get("name") or "").lower()
            content = clean_text(attrs_dict.get("content"))
            if key in {"og:title", "twitter:title"} and content and not self.title:
                self.title = content
            if key in {"description", "og:description", "twitter:description"} and content and not self.description:
                self.description = content
            return

        if tag in {"title", "p"} and not self._tag_stack:
            self._current_tag = tag
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
            return

        if tag != self._current_tag:
            return

        text = clean_text("".join(self._current_text))
        if tag == "title" and text and not self.title:
            self.title = text
        elif tag == "p" and len(text) >= 35 and not any(
            marker in text for marker in ("Copyright", "무단 전재", "무단전재", "재배포 금지")
        ):
            self.paragraphs.append(text)

        self._current_tag = ""
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_tag and not self._tag_stack:
            self._current_text.append(data)


def extract_article_context(html_text: str, fallback_title: str, source: str, url: str) -> ArticleContext:
    parser = ArticleHTMLParser()
    parser.feed(html_text)

    title = parser.title or fallback_title
    summary_parts = [parser.description, *parser.paragraphs[:2]]
    summary = clean_article_summary(" ".join(part for part in summary_parts if part))
    if not summary:
        summary = fallback_title

    return ArticleContext(
        title=truncate_text(title, 120),
        source=source,
        url=url,
        summary=truncate_text(summary, 360),
    )


def fetch_article_html(url: str, timeout: int = 8) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 whalelake-blog-automation/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        return body.decode(charset, errors="replace")


def enrich_issue_articles(issue: TrendIssue, max_articles: int = 3, timeout: int = 8) -> TrendIssue:
    contexts: list[ArticleContext] = []
    for news in issue.news_items[:max_articles]:
        if not news.url:
            continue
        try:
            article_html = fetch_article_html(news.url, timeout=timeout)
            contexts.append(
                extract_article_context(
                    article_html,
                    fallback_title=news.title,
                    source=news.source,
                    url=news.url,
                )
            )
        except Exception:
            continue

    return issue.with_article_contexts(tuple(contexts))


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
    particle = object_particle(safe_title)
    subject_particle = "은" if particle == "을" else "는"
    excerpt = f"{display_date}, 사람들이 '{safe_title}'{particle} 검색한 이유를 네 가지 포인트로 풀어본다."
    references = "\n".join(
        f"- {item.source}: {item.title}" if item.source else f"- {item.title}"
        for item in issue.news_items[:3]
        if item.title
    )
    if not references:
        references = "- Google Trends RSS에 연결된 관련 기사 없음"

    article_notes = "\n".join(
        f"- {context.source}: {context.title}\n  - 기사 본문에서 확인한 단서: {context.summary}"
        for context in issue.article_contexts[:3]
        if context.summary
    )
    if not article_notes:
        article_notes = "- 기사 본문을 추가로 확인하지 못했습니다. RSS에 연결된 기사 제목을 기준으로 맥락을 정리합니다."

    source_links = "\n".join(
        f"- [{item.source or '관련 기사'}]({item.url})"
        for item in issue.news_items[:3]
        if item.url
    )
    if not source_links:
        source_links = "- 관련 기사 링크 없음"

    return f"""---
title: "{safe_title}, 사람들이 갑자기 검색한 이유를 네 가지로 읽어보기"
date: {post_time:%Y-%m-%d %H:%M:%S} +0900
categories: [Current Affairs]
tags: [google-trends, hot-issue, korea, daily-note]
excerpt: "{excerpt}"
---

안녕하세요. 오늘 Google Trends Korea에서 눈에 들어온 검색어는 **{issue.title}**였습니다.

추정 검색량은 {issue.approx_traffic or "확인 필요"}이고, Google Trends에는 {format_pub_date_kst(issue.pub_date)} 기준으로 반영됐습니다. 검색어 하나가 세상을 전부 설명해주지는 않습니다. 하지만 사람들이 같은 단어를 같은 시간대에 검색하기 시작했다는 것은 분명 하나의 신호입니다.

뉴스는 사건을 보여주고, 검색어는 사람들이 그 사건 앞에서 무엇을 궁금해하는지 보여줍니다. 오늘은 검색어 **{issue.title}**가 어떤 장면을 가리키는지 네 가지 포인트로 정리해보겠습니다.

## 1. 먼저, 사람들이 확인하고 싶었던 것은 무엇일까

검색어가 오른다는 것은 단순히 어떤 사건이 발생했다는 뜻만은 아닙니다. 사람들은 이미 본 기사나 들은 이야기를 다시 확인하고 싶을 때 검색합니다. 사실관계를 알고 싶을 수도 있고, 배경을 이해하고 싶을 수도 있고, 내 생활이나 돈, 일, 관계에 어떤 영향을 줄지 따져보고 싶을 수도 있습니다.

**{issue.title}**도 그런 종류의 검색어로 보입니다. 검색어 자체보다 중요한 것은 사람들이 이 단어를 통해 무엇을 확인하려 했는가입니다.

## 2. 함께 뜬 기사들이 보여주는 흐름

Google Trends에 함께 묶인 기사들은 이 이슈가 어디서 출발했는지 대략의 방향을 보여줍니다.

{references}

기사 제목만으로 모든 맥락을 단정할 수는 없습니다. 그래서 연결된 기사 본문과 메타 설명에서 확인 가능한 단서도 함께 살펴봤습니다.

{article_notes}

여러 기사들이 비슷한 방향을 가리킬 때는 그 안에 반복되는 질문이 있습니다. 어떤 이슈는 제도 변화의 신호이고, 어떤 이슈는 시장의 긴장이고, 어떤 이슈는 대중의 감정이 한꺼번에 모인 결과입니다.

## 3. 검색량보다 중요한 것은 관심의 방향

추정 검색량은 숫자입니다. 하지만 블로그에서 더 중요하게 볼 것은 숫자 자체보다 관심의 방향입니다. 왜 하필 오늘 이 단어였는지, 이 단어를 검색한 사람들은 무엇을 알고 싶었는지, 그리고 이 관심이 내일도 이어질지 봐야 합니다.

**{issue.title}**{subject_particle} 그래서 하루짜리 화제로만 넘기기에는 아깝습니다. 검색어는 작지만, 그 뒤에는 정보의 빈틈과 감정의 움직임이 함께 있습니다.

## 4. 오늘 남겨둘 질문

저는 이 이슈를 보며 세 가지 질문을 남겨두고 싶습니다.

- 이 검색어가 갑자기 오른 직접 계기는 무엇인가?
- 관련 보도들은 같은 사실을 두고 어떤 해석 차이를 보이는가?
- 이 관심은 내일도 이어질 구조적 이슈인가, 오늘의 검색량으로 끝날 일회성 이슈인가?

## whalelake Note

오늘의 검색어를 따라가며 다시 느낀 것은, 사람들의 관심은 늘 사건보다 조금 더 넓게 움직인다는 점입니다. 뉴스는 하나의 장면을 보여주지만, 검색은 그 장면을 본 사람들이 어디에서 멈칫했는지를 보여줍니다.

**{issue.title}**도 그런 멈칫함의 기록으로 볼 수 있습니다. 이 단어가 내일도 이어질지, 아니면 오늘의 검색량으로 지나갈지는 조금 더 봐야 합니다. 다만 오늘 사람들이 이 단어를 검색했다는 사실만큼은, 지금 한국 사회가 어디에 신경을 쓰고 있는지 보여주는 작은 단서가 됩니다.

## 참고 링크

{source_links}

_알림: 이 글은 Google Trends Korea RSS에 노출된 검색어와 관련 기사 제목을 바탕으로 작성한 자동 초안입니다. 사실관계 판단이나 투자·정책 판단을 대신하지 않습니다._
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
    enrich_articles: bool = False,
    max_articles: int = 3,
    article_timeout: int = 8,
) -> CreateResult:
    if len(issues) < 3:
        raise ValueError(f"Expected at least 3 trend issues, got {len(issues)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    skipped: list[Path] = []

    for index, issue in enumerate(issues[:3], start=1):
        if enrich_articles:
            issue = enrich_issue_articles(issue, max_articles=max_articles, timeout=article_timeout)
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
    parser.add_argument(
        "--no-enrich-articles",
        action="store_true",
        help="Skip fetching linked article pages. RSS titles are still used.",
    )
    parser.add_argument("--max-articles", type=int, default=3, help="Number of linked articles to fetch per trend.")
    parser.add_argument("--article-timeout", type=int, default=8, help="Timeout in seconds per linked article fetch.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target_date = parse_date(args.date)

    if args.source == "trends":
        rss_xml = fetch_google_trends_rss(args.trends_url)
        issues = parse_trend_issues(rss_xml, limit=3)
        result = create_trend_posts(
            target_date,
            Path(args.output_dir),
            issues,
            force=args.force,
            enrich_articles=not args.no_enrich_articles,
            max_articles=args.max_articles,
            article_timeout=args.article_timeout,
        )
    else:
        result = create_daily_posts(target_date, Path(args.output_dir), force=args.force)

    for path in result.created:
        print(f"created {path}")
    for path in result.skipped:
        print(f"skipped {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
