---
name: compound
description: Capture session feedback as actionable guidance that prevents the same mistake in future sessions. TRIGGER when user says "compound" followed by feedback about what went wrong or could be improved. Also TRIGGER proactively when the agent detects a repeated mistake, a corrected assumption, or a pattern failure that existing guidance would have prevented.
---

# Compound Guidance

Capture feedback from the current session as actionable guidance. Low friction, immediately active, local-first.

The bar for capture is intentionally low -- guidance does not need to be perfectly validated to be worth staging. It is easier to discard later than to reconstruct the lesson.

## When to Use

**User-initiated:** The user says "compound" and describes something that went wrong, a mistake that was made, or an approach that should be different.

**Agent-initiated:** The agent detects a mistake worth capturing and proposes compounding it. Triggers:
- A wrong assumption was corrected by the user or by evidence (test failure, runtime error, code review)
- The same class of mistake was made twice in one session
- A pattern failure that existing guidance *would have* prevented, if the guidance existed
- The agent took an approach the user rejected, and the rejection reveals a reusable rule

When self-triggering: state what you observed, what the guidance would be, and ask the user to confirm before writing. Do not write guidance without confirmation -- the user may disagree that it generalizes.

This is not a bug report or a git commit message. It is a standing instruction for future sessions.

## Flow

1. **Listen** -- Understand what happened: what went wrong, what the impact was, what should have been different
2. **Synthesize** -- Generate a concrete, actionable guidance statement. Not a record of the complaint -- the rule or instruction that, if present in context, would have prevented the issue
3. **Write** -- Append the entry to `guidance.local.md` at the working repo root
4. **Ensure loading** -- Belt-and-suspenders check that the root AI guidance file `@`-imports `guidance.local.md`

## Routing

**Write to:** `guidance.local.md` at the working repo root.

If the file does not exist, create it with this header:

```markdown
# Guidance

In-repo guidance for this project. The `compound` skill writes feedback captures here; standing instructions for working in this repo also live here. This file is auto-loaded into every session via the `@`-imports in the root guidance file (`AGENTS.md` for Codex, `CLAUDE.md` for Claude).

Review periodically -- promote useful patterns to cross-project standards or shared skills, discard what does not hold up.
```

The target is unconditional: always the in-repo `guidance.local.md`. Do not write to `~/workspace/project-docs/{repo}/guidance.md` -- that location was retired with the dotfiles-style sync simplification.

## Entry Format

Append new entries below the header, latest first:

```markdown
## YYYY-MM-DD: {short descriptive title}

**Context:** {what happened -- enough to understand why this guidance exists}
**Guidance:** {the actual rule or instruction, written as a directive}
**Scope:** local | promote-candidate
```

### Writing Good Guidance

The guidance line is the thing that will be read in every future session. Write it as a direct instruction:

- Good: "When modifying the auth middleware, always run the integration test suite before committing -- unit tests alone do not catch token storage regressions."
- Bad: "We had an issue with auth tests."
- Good: "Never mock the database connection in tests under `tests/integration/`. Use the test database fixture instead."
- Bad: "Be careful with database mocks."

### Scope

- **local** -- Applies to this project specifically. Default.
- **promote-candidate** -- Could apply across projects. The marker is for the guidance-harvest workflow to pick up later; harvest is intentionally separate from the sync path.

Use judgment: if the guidance is about a project-specific pattern (a particular API, a local convention), it is local. If it is about a general development practice, it is a promote-candidate.

When unsure, ask the user.

## Ensuring Guidance Loading

After writing the entry, confirm that the root guidance file (`AGENTS.md` for Codex, `CLAUDE.md` for Claude) `@`-imports `guidance.local.md`. The provisioned templates already include this import; this is a belt-and-suspenders check for repos that have drifted or have not yet been re-synced.

If the import is missing, add it alongside the other top-level imports near the start of the file, e.g.:

```
@README.md
@guidance.local.md
@../project-docs/{repo}/ACTIVE.md
@../project-docs/{repo}/TODO.md
```

If the harness in use does not natively follow `@`-imports, document the file path in whatever external-context prose the root guidance uses instead. Do not force `@`-imports into harnesses that do not use them.

## Guidelines

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
