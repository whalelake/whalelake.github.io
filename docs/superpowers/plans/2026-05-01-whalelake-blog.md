# whalelake Blog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first version of the `whalelake.github.io` GitHub Pages magazine blog.

**Architecture:** A Jekyll static site using the Chirpy theme, Markdown posts, theme-provided layouts, and GitHub Pages Actions. GitHub Pages builds the site from the repository root.

**Tech Stack:** GitHub Pages, Jekyll, Chirpy, Liquid, HTML, CSS, Markdown.

---

### Task 1: Site Scaffold

**Files:**
- Create: `_config.yml`
- Create: `README.md`
- Create: `.gitignore`

- [x] Define site metadata, permalink style, category labels, and GitHub Pages compatible settings.
- [x] Add publishing instructions for GitHub repository setup.
- [x] Ignore local Jekyll build outputs.

### Task 2: Theme System

**Files:**
- Configure: `_config.yml`
- Use: `jekyll-theme-chirpy`
- Use: `_tabs/*.md`

- [x] Configure Chirpy as the site theme.
- [x] Use theme-provided layouts for home, posts, archives, categories, and tags.
- [x] Keep local overrides minimal until a concrete design need appears.

### Task 3: Core Pages

**Files:**
- Create: `index.html`
- Create: `_tabs/archives.md`
- Create: `_tabs/about.md`
- Create: `_tabs/categories.md`
- Create: `_tabs/tags.md`

- [x] Build home page through Chirpy's `home` layout.
- [x] Build archive, categories, and tags pages through Chirpy tab layouts.
- [x] Build about page as a tab.

### Task 4: First Content

**Files:**
- Create: `_posts/2026-05-01-welcome-to-whalelake.md`
- Create: `_posts/2026-05-01-data-notes-as-workbench.md`
- Create: `_posts/2026-05-01-project-logs-and-public-memory.md`

- [x] Add first editorial note.
- [x] Add data analysis note.
- [x] Add project record note.

### Task 5: Deployment Readiness

**Files:**
- Create: `.github/workflows/pages-deploy.yml`
- Create: `docs/custom-domain.md`
- Create: `Gemfile.lock`

- [x] Add GitHub Pages workflow for Jekyll.
- [x] Document future custom domain setup.
- [x] Lock gem dependencies for reproducible CI builds.
- [x] Verify the generated files are present and structurally complete.
