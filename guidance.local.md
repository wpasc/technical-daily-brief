# Guidance

In-repo guidance for `technical-daily-brief`. The `compound` skill writes
feedback captures here; standing instructions for working in this repo also
live here.

## Standing Rules

### Direction

This repo is public. Direction and decision history live in the project-docs
repo (`project-docs/technical-daily-brief/`) and the Linear project
"Technical Daily Brief" -- not in a NORTH_STAR.md here. Keep personal profile
data (study topics, learning gaps) out of this repo.

### Pipeline invariants

- No metered LLM calls anywhere in the pipeline. The brief is written by an
  agent session on the owner's Claude subscription (see RUN.md); gather and
  build are plain Python.
- `brief/gather.py` stays stdlib-only. The single allowed dependency is
  `markdown` (pinned) in `site/build.py` and the Pages workflow.
- The routine's job ends at committed markdown in `briefs/`; rendering
  belongs to the GitHub Action.
- Keep `network-allowlist.txt` in sync with `brief/sources.json`.

### Conventions

- All markdown files use ASCII only (no emojis, no Unicode symbols).
- Python logging module for output in scripts (no print statements).
- Committed briefs follow `brief/writing-guide.md` exactly; the guide is the
  contract between the writer and the site build.
