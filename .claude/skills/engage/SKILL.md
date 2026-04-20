---
name: engage
description: >-
  Adaptive task-context router. After CLAUDE.md and ACTIVE.md load, evaluate
  the user's first work-style prompt and either pull up relevant prior context
  for a matched task, propose promoting a Todo into active work, or route
  net-new work onto the golden-path filing flow.
  TRIGGER when: a session opens with a vague work prompt ("what's the latest",
  "where did we leave off"), OR a prompt names or describes work that may match
  an entry in ACTIVE.md, OR a prompt describes substantive new work that should
  be filed rather than handled ad-hoc.
  DO NOT TRIGGER when: the prompt is a one-off question, a slash command, a
  quick fix with obvious scope, or the session is already deep in a task and
  the user is continuing that line of work.
---

# Engage

Pulls up the right prior context at the start of substantive work, or routes net-new work onto the project's task-filing golden path. Replaces the older `/engage` command + `.claude/engaged-task` file: the matching intelligence now lives in this skill, evaluated against ACTIVE.md (already in context via CLAUDE.md `@` reference).

## Purpose

A real complaint this skill addresses: at session start the model doesn't reliably pull up relevant prior work, so the user has to re-orient the conversation by hand. Engage makes that re-orientation an explicit, instructed behavior. It also gives ad-hoc "let me just start working on X" prompts a path onto the project's task-tracking conventions instead of letting them drift untracked.

## Routing

ACTIVE.md is the lightweight catalog; TODO.md is the long-form companion. Both auto-load via CLAUDE.md `@` imports. Each Active Task entry in ACTIVE.md typically looks like:

```
- **task-name** [in flight] -- `tasks/task-name/plan.md` -- One-line description.
```

Status hints inside `[]` weight matching: `[in flight]` is the strongest match candidate, `[parked]` weaker, `[blocked]` weaker still. Todo handles in ACTIVE.md are one-sentence teasers; full descriptions for matching live in TODO.md.

Match the user's prompt against ACTIVE.md (Active Tasks first, then Todo handles) and TODO.md, then pick one branch:

### Branch 1: Match in Active Tasks

Prompt names or clearly describes an entry in `## Active Tasks`.

1. Read `{task-path}/plan.md` and the latest entry in `{task-path}/status.md` (the file's first `##` block)
2. Surface a short orient: goal in one line, where things stand in one line, next step in one line
3. Proceed with the user's prompt in that loaded context

Do not dump the full plan into the response -- the model now has it in context, that is enough.

### Branch 2: Match in Todo

Prompt names or clearly describes an entry in TODO.md (or its handle in ACTIVE.md's `## Todo`).

1. Surface the matched entry's full TODO.md description (not just the ACTIVE.md handle) so the user sees the captured context
2. Ask: "Promote to an Active Task and start working on it now?"
3. If yes: file as new active task (golden path below) and proceed; remove the entry from TODO.md and from ACTIVE.md's Todo handles
4. If no: answer the prompt without filing anything

### Branch 3: Net-new substantive work

Prompt describes work that doesn't match any ACTIVE.md entry but sounds like it deserves to be tracked (a multi-step implementation, an exploration with deliverables, a bug needing investigation across multiple touchpoints, a design decision with downstream impact).

1. Briefly state: "This looks new -- want to file it as an Active Task before we start?"
2. If yes: golden path below
3. If no: proceed without filing, but offer once at the end of the session to capture what was done

### Branch 4: One-off prompt

Prompt is a question, a quick fix, a tool/command request, or otherwise doesn't merit task ceremony. Do not engage. Proceed normally.

This is the default when uncertain. Engage adds value when there is real prior context to pull or real new work to file -- it should not be a tax on every session.

## New-Task Golden Path

When filing net-new work or promoting a Todo:

1. Pick a short kebab-case task name
2. Create `{project-docs-folder}/tasks/{task-name}/plan.md` with a Goal section, an initial Approach if known, and a Steps checklist
3. Create `{project-docs-folder}/tasks/{task-name}/status.md` with an initial entry noting the task was just opened
4. Update ACTIVE.md: add an entry under `## Active Tasks` with the `[in flight]` status hint, the `tasks/{task-name}/plan.md` pointer, and a one-line description. If promoting from Todo, also remove the original entry from both TODO.md and ACTIVE.md's `## Todo` handles.
5. Surface the new entry's path so the user can read or edit the plan if they want to refine it before work starts

Derive `{project-docs-folder}` from the `@` reference in CLAUDE.md's Project Documentation section -- do not hardcode paths.

## Output Format

Keep the orient short and scannable. The user wants to start working, not read a status report.

```
{Picking up | Filing} {task-name}
Goal: {one line}
Status: {one line from latest status entry, or "fresh" for new tasks}
Next: {one line if known, omit if not}
```

Then move into the user's prompt.

## Status Hint Conventions

Status hints inside `[]` on each Active Tasks entry:

| Hint | Meaning |
|---|---|
| `[in flight]` | Currently being worked on; preferred match for ambiguous prompts |
| `[parked]` | Paused intentionally; context is in the task folder, not in active rotation |
| `[blocked]` | Waiting on external input (someone else, a decision, a dependency) |

Maintain these by hand or via checkpoint when it writes to a task's `status.md`. Treat absence of a hint as `[in flight]` for matching purposes (legacy entries).

## Notes

- Engage is reactive to the user's prompt -- it does not fire blindly at session start. If the user's first message is "how does X work" or a one-off command, do nothing.
- If ACTIVE.md and TODO.md are both empty, and the prompt is net-new substantive work, the golden path is the only useful response.
- This skill replaces the older `/engage` command and the `.claude/engaged-task` state file. There is no sticky session-state file anymore -- the matching happens fresh against ACTIVE.md each time.
- Pairs with `checkpoint`: where engage loads context for a task, checkpoint writes status back. Together they form the loop that keeps ACTIVE.md and the per-task `plan.md` / `status.md` files in sync without manual ceremony.
