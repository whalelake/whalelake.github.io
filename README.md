# whalelake

Personal blog for development, current affairs, data analysis, everyday notes, and project records.

The site uses Jekyll, GitHub Pages Actions, and the Chirpy theme.

## Local Preview

Install dependencies:

```bash
bundle install
```

Ruby 3.x is recommended for local builds. The macOS system Ruby 2.6 can fail on current GitHub Pages dependencies.

Run the site locally:

```bash
bundle exec jekyll serve
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

## Theme

Chirpy is configured with `theme: jekyll-theme-chirpy` in `_config.yml`.
Top-level navigation pages live in `_tabs`.
