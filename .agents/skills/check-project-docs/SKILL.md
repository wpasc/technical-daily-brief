---
name: check-project-docs
description: >-
  Codex runtime skill generated from canonical `skills/check-project-docs/SKILL.md`. Route any "project docs" interaction to the sibling project-docs repository via a sub-agent: look up long-form documentation for the current repo, add or update entries, and commit the result so the docs repo stays clean.
---

# check-project-docs (Codex Runtime Skill)

Canonical source: `skills/check-project-docs/SKILL.md`

This file is self-contained for Codex runtime. Shared behavior belongs
in the canonical source skill; regenerate this file after changing the
source.

## Codex Runtime Notes

- Prefer `AGENTS.md` for root guidance. Treat `CLAUDE.md` only as supplemental fallback when older Claude-specific text in the inlined body requires it.
- Use Codex-native tools and `.agents/skills/`; translate older Claude coordination wording in the body into explicit user requests, current tools, or durable artifacts when the workflow requires them.

## Classification

- Migration category: Generate as Codex runtime skill
- Rationale: Workflow or reference guidance is useful in Codex as a self-contained runtime skill.

## Inlined Skill Body

## Check Project Docs

The `project-docs` repository is the long-form documentation home for every
repo in the workspace -- retros, historical narrative, decision logs, and
anything that would pollute a code repo. The user often dictates, so
negotiating "where should I look?" burns tokens and patience. This skill
makes the routing automatic: resolve the location, delegate the work to a
sub-agent, and leave the docs repo committed.

### Locating the Docs

1. `project-docs` is a sibling of the current repo: from the repo root,
   `../project-docs` (both live directly under the workspace folder).
2. Docs for the current repo live in a subfolder named exactly after the
   repo's directory name: work in `world_events_analysis` maps to
   `project-docs/world_events_analysis/`. Resolve the name from the repo
   root directory, not from branding or README titles.
3. Shared, cross-repo material lives at the top level (for example
   `learnings/`, `templates/`, and the root README). Consult it when the
   request is not specific to the current repo.

If the expected subfolder does not exist: for a read, say so and list the
top-level folders so an obvious near-match can be confirmed rather than
guessed; for a write, create the subfolder -- that is the convention, not a
deviation.

### Delegate to a Sub-Agent

Keep the main agent's context lean: the whole point is that the main session
should not page through documentation. Whenever the harness provides
sub-agents, hand the interaction to one. Only fall back to doing the work
inline when sub-agents are unavailable, and say so briefly.

Give the sub-agent:

- The resolved paths: the project-docs root and the current repo's subfolder
- The operation (read lookup, new entry, or update) and the user's request
  verbatim -- dictated phrasing often carries the real intent
- For writes: the session context needed to draft the content (decisions,
  outcomes, file paths, dates), plus a reminder to redact secrets and
  personally identifiable information

#### Read operations

The sub-agent searches the repo's subfolder first, then shared top-level
material if the answer is not there. It returns a distilled answer plus the
file paths it drew from -- paths matter so the user can jump to the source.
It does not dump whole documents back into the main session.

#### Write operations

The sub-agent matches the conventions already present in the subfolder
(existing file names such as `guidance.md`, heading styles, date formats)
rather than inventing new structure. Project docs are largely append-only:
prefer adding a dated entry or section over rewriting existing narrative.
New files get names that state their subject plainly.

### Commit Bias

project-docs is a git repository, and a dirty tree there helps no one --
these are docs, mostly append-only, so the default after any write is an
immediate commit:

1. Stage only the files this operation touched. Pre-existing dirty files
   from other sessions stay out of the commit -- surface them to the user
   instead of sweeping them in.
2. Commit with a message naming the repo context and the change, e.g.
   `docs(world_events_analysis): add 2026-07 ingest retro`.
3. Do not push; syncing with the remote stays the user's call.
4. Never run destructive git operations (`reset --hard`, `clean`,
   `checkout --`) in project-docs. If something looks wrong, stop and report
   instead of fixing history.

Read operations change nothing and therefore commit nothing.

### Report Back

Reads: give the answer, then the source paths. Writes: state what was
written where, and quote the commit subject line. Either way, one compact
summary -- the documentation itself stays in project-docs.
