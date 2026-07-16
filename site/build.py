"""Render briefs/*.md into a static site at _site/.

The only dependency is the `markdown` package (pinned in the Pages workflow):
    pip install markdown==3.6
    python3 site/build.py

Layout produced:
    _site/index.html            latest brief + archive list
    _site/briefs/<date>.html    one page per brief
    _site/style.css
All links are relative so the site works at any base path (GitHub Pages
project sites are served under /<repo-name>/).
"""

import logging
import re
import shutil
from pathlib import Path

import markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
BRIEFS_DIR = REPO_ROOT / "briefs"
SITE_DIR = REPO_ROOT / "_site"
STYLE_SRC = Path(__file__).resolve().parent / "style.css"

BRIEF_FILENAME = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{root}style.css">
</head>
<body>
<header>
  <p class="masthead"><a href="{root}index.html">Technical Daily Brief</a></p>
  <p class="tagline">A curated daily digest of technical news. Written by an agent, read by a human.</p>
</header>
<main>
{main}
</main>
<footer>
  <p>Briefs are written by a scheduled Claude agent from public feeds and
  committed to <a href="https://github.com/wpasc/technical-daily-brief">the repository</a>;
  every item links its source.</p>
</footer>
</body>
</html>
"""

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("build")


def parse_brief(path: Path) -> dict:
    text = path.read_text()
    frontmatter = {}
    body = text
    if text.startswith("---"):
        _, raw, body = text.split("---", 2)
        for line in raw.strip().splitlines():
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()
    return {
        "date": frontmatter.get("date", path.stem),
        "generated": frontmatter.get("generated", ""),
        "html": markdown.markdown(body.strip()),
    }


def render_page(title: str, main: str, root: str) -> str:
    return PAGE_TEMPLATE.format(title=title, main=main, root=root)


def archive_list(briefs: list[dict], root: str) -> str:
    entries = "\n".join(
        f'<li><a href="{root}briefs/{brief["date"]}.html">{brief["date"]}</a></li>'
        for brief in briefs
    )
    return f'<section class="archive"><h2>Archive</h2>\n<ul>\n{entries}\n</ul></section>'


def main() -> None:
    paths = sorted(
        (p for p in BRIEFS_DIR.glob("*.md") if BRIEF_FILENAME.match(p.name)),
        reverse=True,
    )
    briefs = [parse_brief(path) for path in paths]

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    (SITE_DIR / "briefs").mkdir(parents=True)
    shutil.copy(STYLE_SRC, SITE_DIR / "style.css")

    for brief in briefs:
        page = render_page(
            title=f"Technical Daily Brief -- {brief['date']}",
            main=f'<article>\n{brief["html"]}\n</article>',
            root="../",
        )
        (SITE_DIR / "briefs" / f"{brief['date']}.html").write_text(page)

    if briefs:
        latest = briefs[0]
        index_main = (
            f'<article>\n{latest["html"]}\n</article>\n{archive_list(briefs, "")}'
        )
    else:
        index_main = "<article><p>No briefs published yet.</p></article>"
    (SITE_DIR / "index.html").write_text(
        render_page(title="Technical Daily Brief", main=index_main, root="")
    )

    log.info("rendered %d brief(s) to %s", len(briefs), SITE_DIR)


if __name__ == "__main__":
    main()
