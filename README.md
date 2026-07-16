# Technical Daily Brief

A personal daily technical news site. Every morning a scheduled agent reads a
fixed set of public feeds, curates the handful of items a working engineer
would actually care about, and writes a short digest. The digests accumulate
in [`briefs/`](briefs/) and render as a static site on GitHub Pages.

This is the website spin on the "personal daily brief" idea: instead of a
brief delivered *to* you, it is a small newspaper that publishes itself.

## How it works

```
brief/sources.json --> brief/gather.py --> brief/.context.md
                                                |
                              scheduled Claude agent (RUN.md)
                                                |
                                    briefs/YYYY-MM-DD.md  (committed)
                                                |
                       GitHub Action: site/build.py --> GitHub Pages
```

- **Gather** ([brief/gather.py](brief/gather.py)): stdlib-only fetch of
  no-auth RSS/Atom feeds into a single context file. No API keys anywhere.
- **Write** ([RUN.md](RUN.md)): a Claude cloud routine reads the context and
  [brief/writing-guide.md](brief/writing-guide.md), writes the day's brief,
  and commits it. The agent's judgment is the curation; the guide is the
  contract (3-8 items per section, every claim linked, no padding).
- **Render** ([site/build.py](site/build.py)): a GitHub Action turns the
  markdown archive into plain HTML/CSS and deploys to Pages on every push,
  so hand-edits and backfills rebuild the site too.

Sections in v0: **AI/LLM developments** and **Engineering & systems**.

## Running locally

```bash
python3 brief/gather.py                 # fetch feeds -> brief/.context.md
# write briefs/<YYYY-MM-DD>.md (see brief/writing-guide.md), then:
pip install markdown==3.6
python3 site/build.py                   # render -> _site/
python3 -m http.server 8080 -d _site    # http://localhost:8080
```

## Repository layout

| Path | Role |
|---|---|
| `brief/sources.json` | Feed list with curation notes. Long-term source preferences. |
| `brief/gather.py` | Stdlib-only feed fetcher. |
| `brief/writing-guide.md` | Format and voice contract for every brief. |
| `briefs/<date>.md` | Committed output. The archive is the site content. |
| `RUN.md` | Runbook and the exact routine prompt. |
| `site/build.py`, `site/style.css` | Static site renderer. |
| `network-allowlist.txt` | Feed domains for the routine's egress allowlist. |

## One-time setup

1. Create a Claude cloud routine with the prompt in [RUN.md](RUN.md),
   scheduled daily; configure its network egress per the same file.
2. In the repository settings, enable GitHub Pages with **GitHub Actions** as
   the source. (Pages requires the repository to be public on a free plan.)
