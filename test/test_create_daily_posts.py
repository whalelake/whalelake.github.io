import datetime as dt
import tempfile
import unittest
from pathlib import Path

from scripts.create_daily_posts import (
    ArticleContext,
    DailyPost,
    clean_article_summary,
    create_daily_posts,
    create_trend_posts,
    extract_article_context,
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
        issue = issue.with_article_contexts(
            (
                ArticleContext(
                    title="민지 복귀 협의가 주목받는 이유",
                    source="뉴시스",
                    url="https://example.com/minji",
                    summary="소속사와 아티스트 측이 복귀 가능성을 두고 긍정적인 방향에서 협의하고 있다는 점이 팬들의 관심을 끌었다.",
                ),
            )
        )

        content = render_trend_post(issue, dt.date(2026, 5, 7), 1)

        self.assertIn('title: "민지, 사람들이 갑자기 검색한 이유를 네 가지로 읽어보기"', content)
        self.assertIn("date: 2026-05-07 09:00:00 +0900", content)
        self.assertIn("categories: [Current Affairs]", content)
        self.assertIn("추정 검색량은 500+", content)
        self.assertIn("Google Trends에는 2026-05-07 11:10 KST 기준으로 반영됐습니다", content)
        self.assertIn("## 1. 먼저, 사람들이 확인하고 싶었던 것은 무엇일까", content)
        self.assertIn("기사 본문에서 확인한 단서", content)
        self.assertIn("복귀 가능성을 두고 긍정적인 방향에서 협의", content)
        self.assertIn("## whalelake Note", content)
        self.assertIn("- 뉴시스: 민지, 뉴진스 복귀하나", content)

    def test_extract_article_context_reads_meta_and_paragraphs(self):
        article_html = """
        <html>
          <head>
            <meta property="og:title" content="제2금융권 예금 금리 경쟁">
            <meta name="description" content="증시 강세 속 저축은행들이 예금 금리를 올리며 자금 이탈 방어에 나섰다.">
          </head>
          <body>
            <p>코스피가 강하게 오르면서 예금에서 투자시장으로 돈이 이동할 가능성이 커졌다.</p>
            <p>저축은행들은 예금 고객을 붙잡기 위해 일부 상품 금리를 높이고 있다.</p>
          </body>
        </html>
        """

        context = extract_article_context(
            article_html,
            fallback_title="RSS 제목",
            source="테스트신문",
            url="https://example.com/article",
        )

        self.assertEqual("제2금융권 예금 금리 경쟁", context.title)
        self.assertEqual("테스트신문", context.source)
        self.assertIn("저축은행들이 예금 금리를 올리며", context.summary)

    def test_clean_article_summary_removes_copyright_noise(self):
        summary = clean_article_summary(
            "LG유플러스는 1분기 영업이익이 늘었다. ◎공감언론 뉴시스 test@example.com Copyright NEWSIS 무단 전재 및 재배포 금지"
        )

        self.assertEqual("LG유플러스는 1분기 영업이익이 늘었다.", summary)

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
