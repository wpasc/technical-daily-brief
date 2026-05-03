---
name: engage
description: >-
  Codex runtime skill generated from canonical `skills/engage/SKILL.md`. Adaptive task-context router.
---

# engage (Codex Runtime Skill)

Canonical source: `skills/engage/SKILL.md`

This file is self-contained for Codex runtime. Shared behavior belongs
in the canonical source skill; regenerate this file after changing the
source.

## Codex Runtime Notes

- Prefer `AGENTS.md` for root guidance. Treat `CLAUDE.md` only as supplemental fallback when older Claude-specific text in the inlined body requires it.
- Use Codex-native tools and `.agents/skills/`; translate older Claude coordination wording in the body into explicit user requests, current tools, or durable artifacts when the workflow requires them.

## Classification

- Migration category: Generate as Codex runtime skill
- Rationale: Workflow or reference guidance is useful in Codex as a self-contained runtime skill.

## Skill-Specific Notes

- For project-docs routing, derive paths from `AGENTS.md` external-context entries first; use `CLAUDE.md` only as supplemental fallback when older Claude-only `@` import wording is the only available routing source.

## Inlined Skill Body

## Engage

Pulls up the right prior context at the start of substantive work, or routes
net-new work onto the project's task-filing golden path. The matching
intelligence lives in this skill and runs against ACTIVE.md/TODO.md discovered
from loaded context or root AI guidance.

### Purpose

A real complaint this skill addresses: at session start the model doesn't reliably pull up relevant prior work, so the user has to re-orient the conversation by hand. Engage makes that re-orientation an explicit, instructed behavior. It also gives ad-hoc "let me just start working on X" prompts a path onto the project's task-tracking conventions instead of letting them drift untracked.

### Routing

ACTIVE.md is the lightweight catalog; TODO.md is the long-form companion. They
may already be loaded via the repo's root AI guidance; if not, read guidance in
harness priority order (for example, `AGENTS.md` for Codex, `CLAUDE.md` for
Claude) and follow any external-context references, `@` imports, or explicit
project-docs paths.

Each Active Task entry in ACTIVE.md typically looks like:

```
- **task-name** [in flight] -- `tasks/task-name/plan.md` -- One-line description.
```

Status hints inside `[]` weight matching: `[in flight]` is the strongest match candidate, `[parked]` weaker, `[blocked]` weaker still. Todo handles in ACTIVE.md are one-sentence teasers; full descriptions for matching live in TODO.md.

Match the user's prompt against ACTIVE.md (Active Tasks first, then Todo handles) and TODO.md, then pick one branch:

#### Branch 1: Match in Active Tasks

Prompt names or clearly describes an entry in `## Active Tasks`.

1. Read `{task-path}/plan.md` and the latest entry in `{task-path}/status.md` (the file's first `##` block)
2. Surface a short orient: goal in one line, where things stand in one line, next step in one line
3. Proceed with the user's prompt in that loaded context

Do not dump the full plan into the response -- the model now has it in context, that is enough.

#### Branch 2: Match in Todo

Prompt names or clearly describes an entry in TODO.md (or its handle in ACTIVE.md's `## Todo`).

1. Surface the matched entry's full TODO.md description (not just the ACTIVE.md handle) so the user sees the captured context
2. Ask: "Promote to an Active Task and start working on it now?"
3. If yes: file as new active task (golden path below) and proceed; remove the entry from TODO.md and from ACTIVE.md's Todo handles
4. If no: answer the prompt without filing anything

#### Branch 3: Net-new substantive work

Prompt describes work that doesn't match any ACTIVE.md entry but sounds like it deserves to be tracked (a multi-step implementation, an exploration with deliverables, a bug needing investigation across multiple touchpoints, a design decision with downstream impact).

1. Briefly state: "This looks new -- want to file it as an Active Task before we start?"
2. If yes: golden path below
3. If no: proceed without filing, but offer once at the end of the session to capture what was done

#### Branch 4: One-off prompt

Prompt is a question, a quick fix, a tool/command request, or otherwise doesn't merit task ceremony. Do not engage. Proceed normally.

This is the default when uncertain. Engage adds value when there is real prior context to pull or real new work to file -- it should not be a tax on every session.

### New-Task Golden Path

When filing net-new work or promoting a Todo:

1. Pick a short kebab-case task name
2. Create `{project-docs-folder}/tasks/{task-name}/plan.md` with a Goal section, an initial Approach if known, and a Steps checklist
3. Create `{project-docs-folder}/tasks/{task-name}/status.md` with an initial entry noting the task was just opened
4. Update ACTIVE.md: add an entry under `## Active Tasks` with the `[in flight]` status hint, the `tasks/{task-name}/plan.md` pointer, and a one-line description. If promoting from Todo, also remove the original entry from both TODO.md and ACTIVE.md's `## Todo` handles.
5. Surface the new entry's path so the user can read or edit the plan if they want to refine it before work starts

Derive `{project-docs-folder}` from loaded context or root AI guidance
references -- do not hardcode paths.

### Output Format

Keep the orient short and scannable. The user wants to start working, not read a status report.

```
{Picking up | Filing} {task-name}
Goal: {one line}
Status: {one line from latest status entry, or "fresh" for new tasks}
Next: {one line if known, omit if not}
```

Then move into the user's prompt.

### Status Hint Conventions

Status hints inside `[]` on each Active Tasks entry:

| Hint | Meaning |
|---|---|
| `[in flight]` | Currently being worked on; preferred match for ambiguous prompts |
| `[parked]` | Paused intentionally; context is in the task folder, not in active rotation |
| `[blocked]` | Waiting on external input (someone else, a decision, a dependency) |

Maintain these by hand or via checkpoint when it writes to a task's `status.md`. Treat absence of a hint as `[in flight]` for matching purposes (legacy entries).

### Notes

- Engage is reactive to the user's prompt -- it does not fire blindly at session start. If the user's first message is "how does X work" or a one-off command, do nothing.
- If ACTIVE.md and TODO.md are both empty, and the prompt is net-new substantive work, the golden path is the only useful response.
- Legacy Claude note: this skill replaces the older legacy Claude engage command and the
  legacy Claude engaged-task state file. There is no sticky session-state file
  anymore -- the matching happens fresh against ACTIVE.md each time.
- Pairs with `checkpoint`: where engage loads context for a task, checkpoint writes status back. Together they form the loop that keeps ACTIVE.md and the per-task `plan.md` / `status.md` files in sync without manual ceremony.
