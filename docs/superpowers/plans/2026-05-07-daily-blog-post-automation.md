# Daily Blog Post Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate three Jekyll blog posts every day from Korea's Google Trends hot issues, then commit them automatically from GitHub Actions.

**Architecture:** A small Python CLI fetches the Google Trends Korea RSS feed, selects the top three issues, and creates deterministic Markdown posts under `_posts`. A scheduled GitHub Actions workflow runs the CLI daily in Asia/Seoul timing, commits only when files changed, and then the existing Pages workflow publishes the pushed commit.

**Tech Stack:** Python 3 standard library, Jekyll Markdown posts, GitHub Actions.

---

### Task 1: Daily Post Generator

**Files:**
- Create: `scripts/create_daily_posts.py`
- Create: `test/test_create_daily_posts.py`

- [x] Add a Python CLI that accepts `--date`, `--output-dir`, and `--force`.
- [x] Fetch Korea hot issues from Google Trends RSS.
- [x] Generate one post per top trend issue.
- [x] Preserve a fixed-topic fallback mode for local/manual use.
- [x] Skip existing files unless `--force` is passed.
- [x] Test filename generation, front matter, skip behavior, and force overwrite behavior.

### Task 2: GitHub Actions Automation

**Files:**
- Create: `.github/workflows/daily-posts.yml`

- [x] Run daily at 09:00 KST.
- [x] Support manual `workflow_dispatch`.
- [x] Run the generator with the current date in `Asia/Seoul`.
- [x] Commit and push only when `_posts` changed.

### Task 3: Documentation And Verification

**Files:**
- Modify: `README.md`

- [x] Document local generation commands.
- [x] Run Python tests.
- [x] Run Jekyll production build.
- [x] Run HTML-Proofer.
