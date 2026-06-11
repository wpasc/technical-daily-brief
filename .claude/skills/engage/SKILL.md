---
name: engage
description: >-
  Adaptive task-context router backed by Linear that uses a sub-agent to
  evaluate the user's first work-style prompt against Linear Issues while
  preserving the main agent's context window. After matching, either pull up
  the matching Issue's context, propose promoting a Backlog Issue into active
  work, or route net-new work onto the Issue-filing golden path.
  TRIGGER when: a session opens with a vague work prompt ("what's the latest",
  "where did we leave off"), OR a prompt names or describes work that may match
  a Linear Issue, OR a prompt describes substantive new work that should be
  filed rather than handled ad-hoc.
  DO NOT TRIGGER when: the prompt is a one-off question, a slash command, a
  quick fix with obvious scope, or the session is already deep in a task and
  the user is continuing that line of work.
---

# Engage

Pulls up the right prior context at the start of substantive work, or routes
net-new work onto the Issue-filing golden path. The matching intelligence
lives in this skill and runs against the repo's Linear project, preferably in a
sub-agent so the main agent receives only the digest it needs.

## Purpose

A real complaint this skill addresses: at session start the model doesn't
reliably pull up relevant prior work, so the user has to re-orient by hand.
Engage makes that re-orientation an explicit, instructed behavior. It also
gives ad-hoc "let me just start working on X" prompts a path onto the project's
task tracking instead of letting them drift untracked.

## Linear Access

Use whichever Linear access the environment provides. Preference order:

1. A Linear MCP server, if one is configured in the harness.
2. Linear's GraphQL API (`https://api.linear.app/graphql`) with a personal
   API token from the user's environment.

The skill body does not name specific MCP tools or API endpoints -- those are
runtime concerns. Operations described below (list issues by state, read an
issue and its comments, transition state, toggle a label, create an issue) are
first-class in both surfaces.

## Reading Linear

This skill matches against the repo's Linear project. Spawn a sub-agent to
query the project's Issues, inspect likely matches, and return a compact
digest. The main agent should not load every candidate Issue and comment into
its own context unless sub-agents are unavailable.

The sub-agent maps Issues to the task model:

| Linear | Task meaning | Match weight |
|---|---|---|
| "In Progress" Issue | Active work | strongest |
| "Backlog" Issue with `parked` / `blocked` label | Paused active work | weaker |
| "Backlog" Issue without those labels | Queued idea | weaker still |
| "Done" Issue | Recently done (history) | ignore for matching |

The sub-agent matches the user's prompt against Issue titles and descriptions:
In Progress first, then labeled Backlog, then plain Backlog. It returns the
best match, confidence, latest relevant continuity comment, and recommended
branch. The main agent decides whether to proceed or ask the user.

If sub-agents are unavailable, do the same lookup locally and keep the orient
compact.

## Branches

### Branch 1: Match existing tracked work

Prompt names or clearly describes an Issue that already represents tracked
work -- an "In Progress" Issue, or a "Backlog" Issue carrying a `parked` or
`blocked` label.

1. Have the sub-agent read the Issue's description and latest relevant comment
   (newest first is usually the most recent handoff or historical checkpoint).
2. Surface a short orient: goal in one line, where things stand in one line
   (from the latest continuity comment), next step in one line.
3. If the Issue was `parked` / `blocked` and the user is resuming it,
   transition it to "In Progress" and remove the label so the board reflects
   reality.
4. Proceed with the user's prompt in that loaded context.

Do not dump the full description into the response -- the model now has it in
context, that is enough.

### Branch 2: Match a queued Backlog Todo

Prompt names or describes a "Backlog" Issue with no `parked` / `blocked` label
(a queued idea).

1. Surface the matched Issue's full description so the user sees the captured
   context.
2. Ask: "Promote to active (move to In Progress) and start now?"
3. If yes: transition the Issue Backlog -> In Progress, then proceed.
4. If no: answer the prompt without changing the Issue.

### Branch 3: Net-new substantive work

Prompt describes work that doesn't match any Issue but sounds like it deserves
tracking (a multi-step implementation, an exploration with deliverables, a bug
needing investigation across multiple touchpoints, a design decision with
downstream impact).

1. Briefly state: "This looks new -- want to file it as a Linear Issue before
   we start?"
2. If yes: golden path below.
3. If no: proceed without filing, but offer once at the end of the session to
   capture what was done.

### Branch 4: One-off prompt

Prompt is a question, a quick fix, a tool/command request, or otherwise
doesn't merit task ceremony. Do not engage. Proceed normally.

This is the default when uncertain. Engage adds value when there is real prior
context to pull or real new work to file -- it should not be a tax on every
session.

## New-Issue Golden Path

When filing net-new work or promoting a Todo:

1. Create a Linear Issue in this repo's Linear project or team. For net-new
   active work, open it directly in "In Progress"; when promoting a Backlog
   Todo, transition the existing Issue rather than creating a duplicate.
2. Give it a clear title and a description carrying the goal, an initial
   approach if known, and a steps checklist -- the Issue description is the
   Linear planning artifact.
3. Surface the Issue identifier (and URL if available) so the user can open it
   to refine the description before work starts.

## Output Format

Keep the orient short and scannable. The user wants to start working, not read
a status report.

```
{Picking up | Filing} {issue-id}: {title}
Goal: {one line}
Status: {one line from the latest continuity comment, or "fresh" for new issues}
Next: {one line if known, omit if not}
```

Then move into the user's prompt.

## Notes

- Engage is reactive to the user's prompt -- it does not fire blindly at
  session start. If the user's first message is "how does X work" or a one-off
  command, do nothing.
- If the project has no In Progress or Backlog Issues and the prompt is
  net-new substantive work, the golden path is the only useful response.
- Pairs with `handoff`: where this skill loads an Issue's context, handoff
  writes lightweight checkpoints or fuller handoff documents back to Linear
  and transitions the Issue. Together they keep the Linear board in sync with
  the work without manual ceremony.
