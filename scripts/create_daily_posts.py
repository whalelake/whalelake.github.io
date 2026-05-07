#!/usr/bin/env python3
"""Create the daily fixed-topic Jekyll posts."""

from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path


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


def parse_date(value: str | None) -> dt.date:
    if value:
        return dt.date.fromisoformat(value)
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date()


def post_filename(post: DailyPost, target_date: dt.date) -> str:
    return f"{target_date.isoformat()}-{post.slug}-daily-note.md"


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create three fixed-topic daily Jekyll posts.")
    parser.add_argument("--date", help="Target date in YYYY-MM-DD format. Defaults to today in Asia/Seoul.")
    parser.add_argument("--output-dir", default="_posts", help="Directory where Markdown posts are written.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing posts for the date.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target_date = parse_date(args.date)
    result = create_daily_posts(target_date, Path(args.output_dir), force=args.force)

    for path in result.created:
        print(f"created {path}")
    for path in result.skipped:
        print(f"skipped {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
