---
name: scrape-site
description: Fetch a URL from the user's local IP and return clean markdown text plus title -- use when skills or commands need web content without server-side fetch restrictions
user-invocable: false
---
<!-- repo-types: api-service, cli-tool, library, frontend-app, full-stack, monorepo, documentation -->

# Scrape Site

Local web scraper that fetches URLs from the user's machine (avoiding datacenter
IP blocks that affect server-side tools like WebFetch) and returns cleaned
markdown content.

## When to use

Use this skill whenever you need to fetch and read web content and care about
the actual page text. This runs locally via a Python script, so requests come
from the user's IP -- no 403/429 blocks from sites that reject cloud IPs.

Do NOT use WebFetch for content capture. Use this skill instead.

## How to invoke

Run the script via Bash using the cross_project_ai_resources venv:

```bash
# Plain markdown to stdout
/Users/williampascucci/workspace/cross_project_ai_resources/.venv/bin/python \
  /Users/williampascucci/workspace/cross_project_ai_resources/scripts/scrape_site.py \
  "<url>"

# JSON output (title + markdown as structured data)
/Users/williampascucci/workspace/cross_project_ai_resources/.venv/bin/python \
  /Users/williampascucci/workspace/cross_project_ai_resources/scripts/scrape_site.py \
  --json "<url>"
```

Status/progress messages go to stderr. Only the content goes to stdout.

## What it returns

**Regular URLs:** `{ "title": "...", "url": "...", "markdown": "..." }`

**Hacker News URLs:** `{ "title": "HN: ...", "url": "...", "hn_url": "...",
"comments_markdown": "...", "article_markdown": "...|null",
"article_title": "...|null" }`

For HN links, the script automatically:
1. Fetches the full comment tree via the Algolia API (single request, reliable)
2. Fetches the linked article content (if the post links to an external URL)
3. Returns both as separate markdown fields

This dual-fetch is important -- many HN discussions have high-value commentary
that matters as much as or more than the linked article.

## Limitations

- JS-rendered pages return minimal content (the script does a plain HTTP fetch,
  not a headless browser). Future enhancement: `--render` flag with Playwright.
- No image downloading (unlike the knowledge_store version). Images are
  referenced by their original URLs in the markdown.
- Large pages are not truncated -- the caller should handle context limits.

## Dependencies

Requires: `requests`, `beautifulsoup4`, `markdownify`

These are installed in the cross_project_ai_resources venv. If the venv is
missing, create it:

```bash
cd /Users/williampascucci/workspace/cross_project_ai_resources
python3 -m venv .venv
.venv/bin/pip install requests beautifulsoup4 markdownify
```
