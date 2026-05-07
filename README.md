# whalelake

Personal blog for development, current affairs, data analysis, everyday notes, and project records.

The site uses Jekyll, GitHub Pages Actions, and the Chirpy theme.

## Local Preview

Use Ruby 3.4.9, matching `.ruby-version` and the GitHub Actions workflow. On macOS with Homebrew Ruby, run commands with Ruby 3.4 on your `PATH`:

```bash
export PATH="/opt/homebrew/opt/ruby@3.4/bin:$PATH"
```

Install dependencies:

```bash
bundle install
```

The macOS system Ruby 2.6 will not work with this project.

Run the site locally:

```bash
bundle exec jekyll serve
```

Validate a production-like build:

```bash
bundle exec jekyll build
bundle exec htmlproofer _site --disable-external --ignore-urls '/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/'
```

## Publish on GitHub Pages

1. Create a GitHub repository named `whalelake.github.io`.
2. Push this folder to that repository.
3. In GitHub, open **Settings > Pages**.
4. Set the source to **GitHub Actions**.
5. Visit `https://whalelake.github.io` after the `Build and Deploy` workflow finishes.

## Write a Post

Create a Markdown file in `_posts` using this filename format:

```text
YYYY-MM-DD-post-title.md
```

Use front matter like this:

```yaml
---
title: "Post title"
date: 2026-05-01 09:00:00 +0900
categories: [Data Analysis]
tags: [data, notes]
excerpt: "Short summary shown on the home page."
---
```

Suggested categories are `Development`, `Current Affairs`, `Data Analysis`, `Life`, and `Projects`.

## Daily Trend Post Automation

The repository generates three Korea hot-issue posts per day from Google Trends RSS:

- Source: `https://trends.google.com/trending/rss?geo=KR`
- Count: top 3 trend issues
- Category: `Current Affairs`
- Format: introduction, four analysis points, `whalelake Note`, reference links
- Enrichment: fetches up to 3 linked article pages per trend and extracts title, description, and body paragraphs when available

Generate today's trend posts locally:

```bash
python3 scripts/create_daily_posts.py
```

Skip linked article fetching and use only Google Trends RSS titles:

```bash
python3 scripts/create_daily_posts.py --no-enrich-articles
```

Generate a specific date:

```bash
python3 scripts/create_daily_posts.py --date 2026-05-08
```

Existing posts are skipped by default. To overwrite the three posts for a date:

```bash
python3 scripts/create_daily_posts.py --date 2026-05-08 --force
```

For the old fixed-topic placeholders, use:

```bash
python3 scripts/create_daily_posts.py --source fixed --date 2026-05-08
```

GitHub Actions runs `.github/workflows/daily-posts.yml` every day at 09:00 KST. If new hot-issue posts are created, the workflow commits them back to the repository, which triggers the Pages deployment workflow.

## Theme

Chirpy is configured with `theme: jekyll-theme-chirpy` in `_config.yml`.
Top-level navigation pages live in `_tabs`.
