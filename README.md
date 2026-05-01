# whalelake

Personal magazine blog for development, current affairs, data analysis, everyday notes, and project records.

## Publish on GitHub Pages

1. Create a GitHub repository named `whalelake.github.io`.
2. Push this folder to that repository.
3. In GitHub, open **Settings > Pages**.
4. Set the source to **GitHub Actions**.
5. Visit `https://whalelake.github.io` after the workflow finishes.

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
category: data
excerpt: "Short summary shown on the home page."
featured: false
---
```

Supported categories are `development`, `affairs`, `data`, `life`, and `projects`.
