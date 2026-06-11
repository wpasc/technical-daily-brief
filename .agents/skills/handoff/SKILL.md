---
name: handoff
description: >-
  Codex runtime skill generated from canonical `skills/handoff/SKILL.md`. Preserve session continuity in Linear with sub-agent drafting and one handoff scale: either a lightweight checkpoint comment or a fuller handoff document for another agent/session to resume from.
---

# handoff (Codex Runtime Skill)

Canonical source: `skills/handoff/SKILL.md`

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

- For task routing, use Linear Issues directly; treat legacy markdown task files as historical context unless a repo explicitly documents otherwise.

## Inlined Skill Body

## Handoff

Preserve session continuity in Linear. This is one skill with two modes:

- **Checkpoint mode** -- compact Linear comment for ordinary pause/resume.
- **Handoff mode** -- fuller markdown handoff document for another agent or a
  fresh session.

The skill decides the mode from user intent and current task complexity. Do
not expose checkpoint as a separate workflow.

### Linear Access

Use whichever Linear access the environment provides. Preference order:

1. A Linear MCP server, if one is configured in the harness.
2. Linear's GraphQL API (`https://api.linear.app/graphql`) with a personal
   API token from the user's environment.

The skill body intentionally does not name specific MCP tools or API
endpoints -- those are runtime concerns. Operations described below (post a
comment, attach a file, transition state, toggle a label, look up an issue by
ID) are first-class in both surfaces.

### Issue Lookup

This skill needs to know which Issue the handoff is about. Lookup order:

1. **Loaded Linear context** -- if `engage` matched an Issue earlier in this
   conversation, or the current work is already clearly tied to a loaded
   Issue, use that Issue.
2. **Explicit user signal** -- if the user names an Issue in the invocation
   ("handoff to WPA-12"), prefer that.
3. **Git branch convention** -- if the current branch matches `task/<slug>`
   or `<team>-<num>-...`, look up the matching Issue and confirm with the user
   before writing.
4. **Ask** -- if none of the above resolve, prompt the user for the Issue ID.
   Do not guess.

### Sub-Agent Drafting

Use a sub-agent for the continuity summary whenever the harness provides one.
The main agent should stay lean: resolve the Linear Issue, collect only the
minimal inputs, then delegate synthesis.

Give the sub-agent:

- Target mode (`checkpoint` or `handoff`)
- The current Issue ID/title/URL and current state
- The user's argument, if provided, as the next-session focus
- Relevant git status and changed file paths
- Artifact references already created in the session (PRDs, plans, ADRs,
  issues, commits, diffs)
- A reminder to redact secrets and personally identifiable information

The sub-agent returns markdown only. The main agent reviews for accuracy,
redaction, and duplication before writing to Linear.

If sub-agents are unavailable, say so briefly and proceed locally only when
the continuity write is still useful.

### Mode Selection

Choose **checkpoint mode** when:

- The user says "checkpoint" or "save state"
- The task is likely to resume in the same project/context
- The useful state fits in a short comment
- No explicit next-session focus was provided

Choose **handoff mode** when:

- The user says "handoff" or asks for another agent/session to continue
- The user provides an argument describing next-session focus
- The session has enough decisions, artifacts, or open threads that a compact
  comment would force the next agent to reconstruct context
- The current agent is about to stop and a fresh agent needs a runnable
  restart packet

When uncertain, use checkpoint mode. It is easier to add a fuller handoff than
to bury the Issue under unnecessary ceremony.

### Linear Routing

The current-Issue lookup decides the target Issue. The table below decides
state changes.

| Situation | Action |
|-----------|--------|
| Resolved Issue is in "Backlog" or "Todo" and substantive work just happened on it | Transition to "In Progress" before posting. If it still carries a `parked`/`blocked` label that no longer applies, remove the label. |
| Resolved Issue is "In Progress" and the user is pausing without parking | Keep the state; post the continuity artifact. |
| User is parking the task ("parking this", "shelving for now") | Transition to "Backlog", apply the `parked` label, then post. |
| User signals the task is blocked on external input | Transition to "Backlog", apply the `blocked` label, then post. |
| Task is complete | See Task Completion below. |
| No Issue resolves and the work is a project-scoped todo | Create a Backlog Issue in the same Linear team or project as the current work; ask for the target only if the project home is unclear. |

`parked` and `blocked` are labels on a Backlog Issue, not custom workflow
states.

### Checkpoint Mode

Checkpoint mode writes a single compact Linear comment.

Use this body:

```markdown
**Checkpoint -- YYYY-MM-DD**

### Summary
{One-paragraph summary.}

### Current State
- {What is working}
- {Partially complete / open threads}
- {Blockers, if any}

### Next Steps (optional)
- {Concrete follow-up}
```

Omit `Next Steps` when there are no concrete follow-ups. Keep links and paths
as references instead of copying large content already captured elsewhere.

### Handoff Mode

Handoff mode produces a markdown document staged in the user's OS temporary
directory, then persists it to Linear.

1. Ask the sub-agent to draft the document.
2. Save the markdown file under the OS temp directory, not the workspace.
   Use a stable filename such as `handoff-{issue-id}-{YYYYMMDD-HHMM}.md`.
3. Attach the file to the Linear Issue if attachment support is available.
4. If attachments are unavailable, paste the document into a Linear comment.
5. Post or include a short Linear comment headed `Handoff -- YYYY-MM-DD` so
   the Issue timeline clearly shows the latest continuity artifact.

The temp file is only a staging copy. Linear is the durable home.

#### Document Sections

```markdown
# Handoff -- {issue-id}: {title}

## Next Session Focus
{Use the user's argument if provided; otherwise infer the likely next focus.}

## Current State
{Concise state of the work.}

## Artifacts To Read
- {Path or URL only; do not duplicate the artifact content.}

## Decisions And Constraints
- {Decision, constraint, or assumption the next agent must preserve.}

## Open Questions And Blockers
- {Question, blocker, or dependency.}

## Suggested Skills
- {Skill name}: {why it should be invoked next.}

## Resume Steps
1. {First concrete next action.}
2. {Second concrete next action.}

## Redactions
{State that secrets/credentials/PII were excluded, or note "None found."}
```

Do not duplicate content already captured in PRDs, plans, ADRs, issues,
commits, or diffs. Reference those artifacts by path or URL.

Redact sensitive information, including API keys, passwords, tokens,
credentials, private customer/user data, and personally identifiable
information.

### Working-Repo Git State

Before posting to Linear, check the working repo for uncommitted state:

1. Run `git status --short` in the repo root.
2. If the output is empty, proceed -- no prompt needed.
3. If there are uncommitted or untracked files, surface them to the user
   before continuing:
   - List the files with one-line characterizations of what they relate to.
   - Offer three dispositions:
     - **Stage** -- run `git add` on the listed files. Default offer; fully
       reversible via `git reset`.
     - **Stage and commit** -- stage the files and commit with a descriptive
       message drafted from session context. Requires explicit user
       confirmation. Never auto-commit.
     - **Leave as-is** -- user wants to review or discard manually.
4. Never run destructive operations (`git reset --hard`, `git clean`,
   `git checkout --`, branch deletion) from this skill. If the user wants to
   discard work, ask them to do it themselves.

### Todo Routing

Todos live in Linear. When the user says "add to todo" or similar:

- **Project-scoped todo** -- create a new Linear Issue in the same team or
  project as the current work, in "Backlog" state (no `parked`/`blocked`
  label). Title from the user's phrasing; description left for them to flesh
  out.
- **Cross-project, general, or unclear-home todo** -- create a Backlog Issue
  in the Nexus Linear project or team. Include the source project and why no
  better owning project was obvious. Use `~/workspace/nexus/routing.md` only
  as a project-discovery index when deciding whether a better owner exists;
  do not append todos there.

### Task Completion

When the user signals a task is done:

1. Post a final checkpoint-mode comment unless the next session needs a full
   handoff document.
2. Transition the Issue to "Done".

The Issue itself stays as history in Linear; nothing is deleted.
