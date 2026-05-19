# news_site

<!-- AGENTS.md is an open, AAIF-stewarded standard (https://agents.md/) -- not a Codex-only convention. -->

This file is the source-library-owned AI runtime baseline. It is clobbered by
`cross_project_ai_resources/scripts/sync.py` on every sync. Project-specific
content lives in `README.md` and `guidance.local.md`, both `@`-imported below.
Codex harnesses that do not natively follow `@`-imports should treat the
listed files as required reading before substantive work.

## Project Documentation

@README.md
@guidance.local.md
@../project-docs/news_site/ACTIVE.md
@../project-docs/news_site/TODO.md

## Available Workflows

Codex invokes skills by mention (e.g. `$dispatch`) or by description-based
auto-activation. The bundle installed for this repo:

| Workflow | Purpose |
|----------|---------|
| dispatch | Decompose complex prompts into parallel sub-agents with validation |
| implement-feature | Sequential scout/dialogue/gather/implement/review for new features |
| code-review | Structured code review with severity levels |
| checkpoint | Preserve session context, route to project-docs |
| compound | Capture session feedback into `guidance.local.md` |
| engage | Adaptive task-context router for prompt-to-task matching |
| systematic-debugging | Root-cause-first debugging methodology |
| test-driven-development | Red-green-refactor cycle for new behavior |
| verification-before-completion | Require fresh evidence before claiming done |
| red-team | Multi-vector adversarial code review |
| xray | Trace execution flow with targeted logging to understand unfamiliar code |
| xray-clean | Remove xray instrumentation and restore the repo to its original state |

Reference and helper skills auto-detect via TRIGGER conditions in their
`SKILL.md` files: `documentation-standards`, `testing-standards`,
`anti-patterns`, `data-pipeline-design`, `database-design`, `sql-patterns`,
`docker-development`, `devops-practices`, `observability-design`,
`migration-strategy`, `agent-handoff`, `adversarial-review`, `security-audit`,
`dependency-audit`.

## Key Rules

### Honest Assessment Over Agreement
State your genuine evaluation before executing. State assumptions explicitly;
if uncertain, ask. If multiple interpretations of the request exist, present
them rather than picking silently. If you see a problem -- a simpler approach,
a flaw in the plan -- flag it. The user can override; silent agreement when
you see an issue is the actual failure mode.

### Simplicity First
Write the minimum code that solves the problem. No features beyond what was
asked, no abstractions for single-use code, no error handling for impossible
scenarios. If a 200-line solution could be 50, rewrite it.

### Surgical Changes
Touch only what the request requires. Do not "improve" adjacent code,
comments, or formatting. Match existing style even when you would write it
differently. If your changes create orphaned imports or unused symbols,
remove them; do not delete pre-existing dead code unless asked. Every changed
line should trace to the request.

### Harness Neutrality For Skill Authoring
If you create or modify a skill body locally (`.claude/skills/<x>/SKILL.md` or
`.agents/skills/<x>/SKILL.md`), keep the prose harness-neutral wherever
practical. Claude- or Codex-specific behavior belongs in runtime packaging,
not in the canonical body.

### Plain ASCII Documentation
Prefer plain ASCII in markdown. Avoid decorative emoji. Use Mermaid for
diagrams when one adds value.

### Plan Before Executing
For non-trivial work, sketch the approach before editing. Define what "done"
looks like as a check, not a feeling -- "tests pass for invalid inputs" beats
"make it work". If a task plan already exists in
`~/workspace/project-docs/news_site/tasks/`, keep it aligned with what
was actually learned and add a sibling plan file rather than overwriting prior
planning.

### Single-Line Shell Commands
Keep Bash commands on a single line; chain Python statements with semicolons,
shell commands with `&&`. Multi-line commands trigger an unbypassable approval
prompt in some harnesses.

### Prefer Dedicated Tools Over Bash
Use the harness's read/search/edit tools instead of shelling out to `cat`,
`grep`, `find`, or `sed`. Reserve Bash for git, build tools, test runners, and
package managers.

### Cross-Project Routing
If the user flags an idea or concern as out-of-scope for this project, append
it to `~/workspace/nexus/routing.md` with a one-line summary and the source
project name. Do not proactively search for cross-project relevance.

## AI Collaboration

Compact runtime baseline. Canonical long-form source lives in
`standards/ai-collaboration-principles.md` in `cross_project_ai_resources`.

- Measure before attribution. Treat root-cause claims as hypotheses until a
  concrete measurement, test, trace, or source supports them.
- Agent confidence is not evidence. Confident AI output still needs
  verification before it drives a fix, commit, or decision.
- Repeated failures require guardrails. If the same failure class appears
  twice, stop adding prose reminders and add a test, validation check, alert,
  or workflow gate.
- Standards must block something. Promote broad principles into checklists,
  tests, validators, alerts, or review gates when they need to shape behavior.

## Task Tracking

Four files in `~/workspace/project-docs/news_site/` form the task
system. ACTIVE.md and TODO.md are auto-loaded above; per-task plans and
status are loaded on demand.

| File | Role |
|---|---|
| `ACTIVE.md` | Lightweight catalog with `[in flight]` / `[parked]` / `[blocked]` status hints. |
| `TODO.md` | Full descriptions of queued ideas. |
| `tasks/{name}/plan.md` | Per-task goal, approach, steps. |
| `tasks/{name}/status.md` | Per-task status entries (latest first). |

The `engage` skill matches your first work-style prompt against ACTIVE.md and
TODO.md and either loads the matching `plan.md` or files a new task. The
`checkpoint` skill writes status back at session end.

Status hint vocabulary: `[in flight]` (currently being worked on; preferred
match for ambiguous prompts), `[parked]` (paused intentionally), `[blocked]`
(waiting on external input). New tasks default to `[in flight]`.
