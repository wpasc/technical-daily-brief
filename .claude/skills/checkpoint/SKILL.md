---
name: checkpoint
description: Create checkpoints and capture todos, routing to the project's documentation in project-docs
---

# Session Checkpoint

Capture session context and todos, routing them to the project's documentation folder in project-docs. ACTIVE.md (loaded via CLAUDE.md `@` reference) tells you where to write.

## Routing

Every repo's CLAUDE.md references an ACTIVE.md in project-docs. That file tells you:
- What project-docs folder to write to
- Whether there's an active task
- The todo list for this project

**Derive the project-docs path from the `@` reference in CLAUDE.md.** Do not hardcode paths.

### Checkpoint Routing

The session itself tells you where to write. The `engage` skill, if it fired earlier, already loaded a task's `plan.md` into context -- that's the strongest signal. Otherwise fall back to ACTIVE.md status hints, then ask.

| Situation | Write to |
|-----------|----------|
| A task's `plan.md` is already in context this session (engage loaded it, or you opened the file directly while working) | That task's `status.md` (prepend, latest first) |
| No task in context, but ACTIVE.md has exactly one `[in flight]` entry | That task's `status.md` (prepend, latest first) |
| No task in context, multiple `[in flight]` entries in ACTIVE.md | Ask the user which task to checkpoint |
| No active task at all | `{project-docs-folder}/tasks/status.md` (general project status) |

If you write to a task's `status.md` and the corresponding ACTIVE.md entry's status hint no longer reflects reality (e.g., task was `[parked]` and you just resumed it), update the hint inline -- this keeps the catalog honest.

### Todo Routing

When the user says "add to todo", "put this on my list", or similar:

| Todo is about | Write to |
|---------------|----------|
| The current project | `TODO.md` in this project's project-docs folder (full description), then add a one-sentence handle under `## Todo` in ACTIVE.md |
| Cross-project, general, or unclear | `~/workspace/nexus/todo.md` under `## General` |

Use judgment: if the todo names a specific project or relates to the work at hand, it's project-specific. If it's about the workspace, tooling across repos, a general idea, or you're not sure, route to nexus.

If a project does not yet have a `TODO.md` (the split is currently scoped to `cross_project_ai_resources`; other repos still keep todos inline in ACTIVE.md's `## Todo` section), write to whichever shape that project uses -- check ACTIVE.md and the presence of `TODO.md` to decide.

### Task Creation

When the user says "start a task" or picks up a todo item to work on:
1. Create `{project-docs-folder}/tasks/{task-name}/plan.md` with goal and steps
2. Create `{project-docs-folder}/tasks/{task-name}/status.md` with initial entry
3. Update ACTIVE.md: add an Active Tasks entry with link to plan.md and the `[in flight]` status hint (where supported); remove the original Todo handle. If TODO.md exists, also remove the corresponding full-description entry there.

This overlaps with the engage skill's golden path -- they should produce the same end state.

## Checkpoint Structure

### Required Sections

**1. Summary** - Brief description of work completed. Focus on what was accomplished, key changes, and important context. Keep concise but complete.

**2. Current State** - Snapshot of where things stand:
- What is working
- What is partially complete
- Any blockers or issues discovered
- Relevant file paths

### Conditional Section

**3. Next Steps** - Include ONLY when there are specific follow-up actions. Actionable items, not vague suggestions. Omit if work is complete.

## Status File Format

New entries go at the top of status.md:

```markdown
## YYYY-MM-DD

{Summary of what was done, where things stand, what's next.}
```

## When to Checkpoint

| Scenario | Checkpoint |
|----------|-----------|
| Stopping mid-task with planned continuation | Yes |
| Complex work requiring context preservation | Yes |
| Important decisions made that need documentation | Yes |
| Simple completed task with no follow-up | No |

## Guidelines

**Do:**
- Keep summaries focused on essential context
- Include specific file paths when relevant
- Write in a way that is scannable and clear
- Only include next steps when genuinely needed

**Don't:**
- Include verbose explanations of obvious code
- Duplicate information available in git history
- Create checkpoints for trivial changes
- Include implementation details clear from the code

## Task Completion

When a task is done:
1. Add a final status entry to `tasks/{task}/status.md`
2. Remove the task from ACTIVE.md's Active Tasks section
3. The task folder stays as history -- do not delete it
