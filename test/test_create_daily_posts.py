import datetime as dt
import tempfile
import unittest
from pathlib import Path

from scripts.create_daily_posts import (
    DailyPost,
    create_daily_posts,
    create_trend_posts,
    parse_trend_issues,
    render_post,
    render_trend_post,
)


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:ht="https://trends.google.com/trending/rss" version="2.0">
  <channel>
    <item>
      <title>민지</title>
      <ht:approx_traffic>500+</ht:approx_traffic>
      <pubDate>Wed, 6 May 2026 19:10:00 -0700</pubDate>
      <ht:news_item>
        <ht:news_item_title>민지, 뉴진스 복귀하나…어도어 &quot;긍정 방향 협의&quot;</ht:news_item_title>
        <ht:news_item_url>https://example.com/minji</ht:news_item_url>
        <ht:news_item_source>뉴시스</ht:news_item_source>
      </ht:news_item>
    </item>
    <item>
      <title>롯데면세점</title>
      <ht:approx_traffic>100+</ht:approx_traffic>
      <pubDate>Wed, 6 May 2026 18:40:00 -0700</pubDate>
      <ht:news_item>
        <ht:news_item_title>롯데면세점, 장애인 선수 직접 고용</ht:news_item_title>
        <ht:news_item_url>https://example.com/lotte</ht:news_item_url>
        <ht:news_item_source>연합뉴스</ht:news_item_source>
      </ht:news_item>
    </item>
    <item>
      <title>한덕수</title>
      <ht:approx_traffic>2000+</ht:approx_traffic>
      <pubDate>Wed, 6 May 2026 18:10:00 -0700</pubDate>
      <ht:news_item>
        <ht:news_item_title>한덕수 2심 선고</ht:news_item_title>
        <ht:news_item_url>https://example.com/han</ht:news_item_url>
        <ht:news_item_source>한겨레</ht:news_item_source>
      </ht:news_item>
    </item>
  </channel>
</rss>
"""


class CreateDailyPostsTest(unittest.TestCase):
    def test_render_post_includes_jekyll_front_matter(self):
        post = DailyPost(
            topic="AI",
            category="AI",
            slug="ai",
            title_label="AI",
            tags=("ai", "technology"),
            hour=13,
        )

        content = render_post(post, dt.date(2026, 5, 7))

        self.assertIn('title: "2026년 05월 07일 AI 노트"', content)
        self.assertIn("date: 2026-05-07 13:00:00 +0900", content)
        self.assertIn("categories: [AI]", content)
        self.assertIn("tags: [ai, technology, daily-note]", content)
        self.assertIn("## 오늘의 질문", content)

    def test_create_daily_posts_writes_three_expected_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = create_daily_posts(dt.date(2026, 5, 7), Path(tmpdir))

            self.assertEqual(3, len(result.created))
            self.assertEqual([], result.skipped)
            self.assertTrue((Path(tmpdir) / "2026-05-07-current-affairs-daily-note.md").exists())
            self.assertTrue((Path(tmpdir) / "2026-05-07-ai-daily-note.md").exists())
            self.assertTrue((Path(tmpdir) / "2026-05-07-development-daily-note.md").exists())

    def test_create_daily_posts_skips_existing_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            create_daily_posts(dt.date(2026, 5, 7), output_dir)

            result = create_daily_posts(dt.date(2026, 5, 7), output_dir)

            self.assertEqual([], result.created)
            self.assertEqual(3, len(result.skipped))

    def test_create_daily_posts_force_overwrites_existing_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            target = output_dir / "2026-05-07-ai-daily-note.md"
            create_daily_posts(dt.date(2026, 5, 7), output_dir)
            target.write_text("old content", encoding="utf-8")

            result = create_daily_posts(dt.date(2026, 5, 7), output_dir, force=True)

            self.assertEqual(3, len(result.created))
            self.assertEqual([], result.skipped)
            self.assertIn("2026년 05월 07일 AI 노트", target.read_text(encoding="utf-8"))

    def test_parse_trend_issues_reads_google_trends_rss(self):
        issues = parse_trend_issues(SAMPLE_RSS, limit=3)

        self.assertEqual(["민지", "롯데면세점", "한덕수"], [issue.title for issue in issues])
        self.assertEqual("500+", issues[0].approx_traffic)
        self.assertEqual("민지, 뉴진스 복귀하나…어도어 \"긍정 방향 협의\"", issues[0].news_items[0].title)
        self.assertEqual("뉴시스", issues[0].news_items[0].source)

    def test_render_trend_post_includes_issue_context_and_opinion_sections(self):
        issue = parse_trend_issues(SAMPLE_RSS, limit=1)[0]

        content = render_trend_post(issue, dt.date(2026, 5, 7), 1)

        self.assertIn('title: "2026년 05월 07일 핫이슈: 민지"', content)
        self.assertIn("date: 2026-05-07 09:00:00 +0900", content)
        self.assertIn("categories: [Current Affairs]", content)
        self.assertIn("추정 검색량: 500+", content)
        self.assertIn("Google Trends 반영 시각: 2026-05-07 11:10 KST", content)
        self.assertIn("## 내 생각", content)
        self.assertIn("- 뉴시스: 민지, 뉴진스 복귀하나", content)

    def test_create_trend_posts_writes_three_ranked_hot_issue_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            issues = parse_trend_issues(SAMPLE_RSS, limit=3)

            result = create_trend_posts(dt.date(2026, 5, 7), output_dir, issues)

            self.assertEqual(3, len(result.created))
            self.assertTrue((output_dir / "2026-05-07-hot-issue-01.md").exists())
            self.assertTrue((output_dir / "2026-05-07-hot-issue-02.md").exists())
            self.assertTrue((output_dir / "2026-05-07-hot-issue-03.md").exists())


if __name__ == "__main__":
    unittest.main()
