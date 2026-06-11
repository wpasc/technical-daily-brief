---
name: compound
description: >-
  Codex runtime skill generated from canonical `skills/compound/SKILL.md`. Capture session feedback as actionable guidance that prevents the same mistake in future sessions.
---

# compound (Codex Runtime Skill)

Canonical source: `skills/compound/SKILL.md`

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

## Compound Guidance

Capture feedback from the current session as actionable guidance. Low friction, immediately active, local-first.

The bar for capture is intentionally low -- guidance does not need to be perfectly validated to be worth staging. It is easier to discard later than to reconstruct the lesson.

### When to Use

**User-initiated:** The user says "compound" and describes something that went wrong, a mistake that was made, or an approach that should be different.

**Agent-initiated:** The agent detects a mistake worth capturing and proposes compounding it. Triggers:
- A wrong assumption was corrected by the user or by evidence (test failure, runtime error, code review)
- The same class of mistake was made twice in one session
- A pattern failure that existing guidance *would have* prevented, if the guidance existed
- The agent took an approach the user rejected, and the rejection reveals a reusable rule

When self-triggering: state what you observed, what the guidance would be, and ask the user to confirm before writing. Do not write guidance without confirmation -- the user may disagree that it generalizes.

This is not a bug report or a git commit message. It is a standing instruction for future sessions.

### Flow

1. **Listen** -- Understand what happened: what went wrong, what the impact was, what should have been different
2. **Synthesize** -- Generate a concrete, actionable guidance statement. Not a record of the complaint -- the rule or instruction that, if present in context, would have prevented the issue
3. **Write** -- Append the entry to `guidance.local.md` at the working repo root

### Routing

**Write to:** `guidance.local.md` at the working repo root.

If the file does not exist, create it with this header:

```markdown
# Guidance

In-repo guidance for this project. The `compound` skill writes feedback captures here; standing instructions for working in this repo also live here. The root guidance file (`AGENTS.md` for Codex, `CLAUDE.md` for Claude) is an intentionally minimal behavioral baseline; read this file on demand when working in this repo.

Review periodically -- promote useful patterns to cross-project standards or shared skills, discard what does not hold up.
```

The target is unconditional: always the in-repo `guidance.local.md`. Do not write to `~/workspace/project-docs/{repo}/guidance.md` -- that location was retired with the dotfiles-style sync simplification.

### Entry Format

Append new entries below the header, latest first:

```markdown
## YYYY-MM-DD: {short descriptive title}

**Context:** {what happened -- enough to understand why this guidance exists}
**Guidance:** {the actual rule or instruction, written as a directive}
**Scope:** local | promote-candidate
```

#### Writing Good Guidance

The guidance line is the thing that will be read in every future session. Write it as a direct instruction:

- Good: "When modifying the auth middleware, always run the integration test suite before committing -- unit tests alone do not catch token storage regressions."
- Bad: "We had an issue with auth tests."
- Good: "Never mock the database connection in tests under `tests/integration/`. Use the test database fixture instead."
- Bad: "Be careful with database mocks."

#### Scope

- **local** -- Applies to this project specifically. Default.
- **promote-candidate** -- Could apply across projects. The marker is for the guidance-harvest workflow (parked as the `guidance-harvest-prompt` Linear Issue) to pick up later; harvest is intentionally separate from the sync path.

Use judgment: if the guidance is about a project-specific pattern (a particular API, a local convention), it is local. If it is about a general development practice, it is a promote-candidate.

When unsure, ask the user.

### Root Guidance Is Minimal By Design

Do not modify the root guidance file (`AGENTS.md` for Codex, `CLAUDE.md` for Claude) after writing an entry. Provisioned root baselines are source-owned, intentionally minimal, and clobbered on every sync -- do not add an `@guidance.local.md` import where one is absent. Where a repo's root guidance already imports `guidance.local.md` (some repo types do), leave that in place. `guidance.local.md` is on-demand standing context: read it when starting substantive work in a repo.

### Guidelines

**Do:**
- Write guidance as directives, not observations
- Keep entries concise and scannable
- Bias toward capturing -- it is easier to discard than to reconstruct
- Check for duplicates before writing (do not repeat existing guidance)

**Don't:**
- Record debugging steps or fix details (those belong in git history)
- Write vague guidance ("be careful with X")
- Duplicate what is already in root AI guidance or provisioned skills
- Editorialize about whether the feedback is correct -- capture it and let review sort it out
