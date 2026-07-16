"""Fetch the no-auth feeds in sources.json and write .context.md.

Stdlib only. No API keys, no LLM calls. The output file is the raw
material a writing agent (or a human) turns into briefs/<date>.md.

Usage: python3 brief/gather.py
"""

from __future__ import annotations

import html
import json
import logging
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

BRIEF_DIR = Path(__file__).resolve().parent
CONTEXT_PATH = BRIEF_DIR / ".context.md"
USER_AGENT = "technical-daily-brief gather.py (github.com/wpasc/technical-daily-brief)"
FETCH_TIMEOUT_SECONDS = 20
SUMMARY_MAX_CHARS = 400

ATOM_NS = "{http://www.w3.org/2005/Atom}"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("gather")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
        return response.read()


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_date(raw: str) -> datetime | None:
    raw = raw.strip()
    try:
        return parsedate_to_datetime(raw)  # RFC 822, used by RSS
    except (TypeError, ValueError):
        pass
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))  # Atom
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def parse_feed(content: bytes) -> list[dict]:
    """Parse RSS 2.0 or Atom into [{title, link, published, summary}]."""
    root = ET.fromstring(content)
    items = []
    if root.tag == f"{ATOM_NS}feed":
        for entry in root.iter(f"{ATOM_NS}entry"):
            link = ""
            for candidate in entry.iter(f"{ATOM_NS}link"):
                if candidate.get("rel", "alternate") == "alternate":
                    link = candidate.get("href", "")
                    break
            items.append(
                {
                    "title": (entry.findtext(f"{ATOM_NS}title") or "").strip(),
                    "link": link,
                    "published": entry.findtext(f"{ATOM_NS}published")
                    or entry.findtext(f"{ATOM_NS}updated")
                    or "",
                    "summary": entry.findtext(f"{ATOM_NS}summary")
                    or entry.findtext(f"{ATOM_NS}content")
                    or "",
                }
            )
    else:  # RSS
        for item in root.iter("item"):
            items.append(
                {
                    "title": (item.findtext("title") or "").strip(),
                    "link": (item.findtext("link") or "").strip(),
                    "published": item.findtext("pubDate") or "",
                    "summary": item.findtext("description") or "",
                }
            )
    return items


def gather_source(source: dict, max_items: int, max_age_hours: int) -> list[dict]:
    items = parse_feed(fetch(source["url"]))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    fresh = []
    for item in items:
        published = parse_date(item["published"]) if item["published"] else None
        if published is not None and published < cutoff:
            continue
        fresh.append(
            {
                "title": item["title"],
                "link": item["link"],
                "published": published.isoformat() if published else "unknown",
                "summary": strip_html(item["summary"])[:SUMMARY_MAX_CHARS],
            }
        )
        if len(fresh) >= max_items:
            break
    return fresh


def main() -> None:
    config = json.loads((BRIEF_DIR / "sources.json").read_text())
    now = datetime.now().astimezone()
    failures = []
    lines = [
        "# Gathered context",
        "",
        f"Generated: {now.isoformat()}",
        f"Window: last {config['max_age_hours']} hours "
        "(items without a parseable date are included).",
        "",
    ]

    for section in config["sections"]:
        lines += [f"## Section: {section}", ""]
        for source in config["sources"]:
            if source["section"] != section:
                continue
            try:
                items = gather_source(
                    source, config["max_items_per_source"], config["max_age_hours"]
                )
            except Exception as error:  # noqa: BLE001 - report, don't crash the run
                log.warning("failed %s: %s", source["name"], error)
                failures.append(f"{source['name']} ({source['url']}): {error}")
                continue
            log.info("%s: %d items", source["name"], len(items))
            lines += [f"### {source['name']}", "", f"Curation notes: {source['notes']}", ""]
            if not items:
                lines += ["(no items in window)", ""]
            for item in items:
                lines += [
                    f"- **{item['title']}**",
                    f"  - link: {item['link']}",
                    f"  - published: {item['published']}",
                    f"  - summary: {item['summary'] or '(none)'}",
                ]
            lines.append("")

    lines += ["## Coverage gaps", ""]
    if failures:
        lines += [f"- FAILED to load: {failure}" for failure in failures]
    else:
        lines.append("- none; all sources loaded")
    lines.append("")

    CONTEXT_PATH.write_text("\n".join(lines))
    log.info("wrote %s (%d sources failed)", CONTEXT_PATH, len(failures))


if __name__ == "__main__":
    main()
