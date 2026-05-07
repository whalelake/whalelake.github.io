import datetime as dt
import tempfile
import unittest
from pathlib import Path

from scripts.create_daily_posts import DailyPost, create_daily_posts, render_post


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


if __name__ == "__main__":
    unittest.main()
