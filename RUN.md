# RUN: daily brief

Runbook for producing a daily brief. The "Routine prompt" below is what a
Claude cloud routine runs on a schedule (suggested: daily, 07:00
America/New_York). It uses the Claude subscription -- the routine's agent
writes the brief itself; nothing in this pipeline calls a metered LLM API.

The routine's job ends at committed markdown. Rendering and deployment happen
in GitHub Actions on push (see `.github/workflows/pages.yml`), so the site
also rebuilds after hand-edits or backfills.

## Routine prompt

Paste this as the routine's prompt. It is self-contained; a fresh session can
run it cold. Paths are relative to the repository root.

> Produce today's technical daily brief, writing it yourself (Claude
> subscription) -- do not call any external LLM API.
>
> 1. Run `python3 brief/gather.py`. It fetches the no-auth sources and writes
>    `brief/.context.md` (today's items plus any sources that failed to load).
> 2. Read `brief/.context.md` and `brief/writing-guide.md`. Write the brief to
>    `briefs/<YYYY-MM-DD>.md` for today's date (America/New_York), following
>    the guide exactly. Curate hard; do not pad; note coverage gaps honestly.
> 3. Commit only `briefs/<YYYY-MM-DD>.md` with message
>    `brief: <YYYY-MM-DD>` and push to main. Do not commit `.context.md`.
>    Do not edit the sources or the writing guide.

## Network egress (cloud routine)

Cloud routines default to a "Trusted" network policy: GitHub is reachable but
the source feeds are not (`403 host_not_allowed`). One-time setup:

1. Open the routine -> environment settings -> set **Network access** to
   **Custom**, keeping "include default list" checked (preserves GitHub so the
   push works).
2. Paste the domains from [`network-allowlist.txt`](network-allowlist.txt)
   into the custom-domains field.

Keep `network-allowlist.txt` in sync with `brief/sources.json` when adding or
dropping a source.

## Local run

```bash
python3 brief/gather.py        # fetch -> brief/.context.md (no key needed)
# write briefs/<date>.md yourself or via a local Claude session, then:
pip install markdown==3.6      # once
python3 site/build.py          # render -> _site/
python3 -m http.server 8080 -d _site   # preview
```
