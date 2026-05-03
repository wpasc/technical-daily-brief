---
name: dispatch
description: >-
  Codex runtime skill generated from canonical `skills/dispatch/SKILL.md`. Decompose complex prompts into parallel workers or sub-agents with validation.
---

# dispatch (Codex Runtime Skill)

Canonical source: `skills/dispatch/SKILL.md`

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

- Use Codex subagents when available: `explorer` for bounded read-only codebase questions, `worker` for scoped implementation with clear ownership, and `default` for general decomposition or review. If subagents are unavailable, keep the same decomposition local and validate each step before integrating.

## Inlined Skill Body

## Prompt Dispatch Workflow

Generic multi-worker workflow that decomposes any prompt into parallel
sub-tasks, executes them via independent workers or sub-agents, validates all
results, and reports consolidated status -- while keeping the orchestrating
agent's context window lean.

---

### Purpose

- Execute complex prompts by decomposing them into independent sub-tasks
- Run workers in parallel where tasks are independent
- Validate every worker's output before accepting results
- Avoid context compaction by offloading all heavy work to workers where the
  current harness supports it
- Apply generically to any prompt without workflow-specific customization

---

### When to Use

| Scenario | Use This Workflow |
|----------|-------------------|
| Prompt touches multiple files or systems | Yes |
| Prompt has clearly separable concerns | Yes |
| Session is long-running, context at risk | Yes |
| Prompt involves research + implementation | Yes |
| Quick single-file fix with known solution | No - direct execution |
| Highly sequential chain (each step needs prior output) | No - use feature implementation workflow |

---

### Workflow Overview

```
[User Prompt]
      |
      v
[Decomposer Worker]  -- analyzes prompt, produces sub-task plan
      |
      v
[Orchestrator (main agent)]  -- reviews plan, spawns workers
      |
      +---> [Worker 1] ---> [Validator 1] ---+
      +---> [Worker 2] ---> [Validator 2] ---+---> [Orchestrator]
      +---> [Worker N] ---> [Validator N] ---+     consolidates + reports
```

**Context window strategy:** The orchestrator (main agent) does NO heavy
lifting. It routes, spawns, collects, and reports. Where the harness supports
separate workers/sub-agents, file reading, code analysis, research, and writing
happen inside those separate contexts.

**Validation strategy:** Each worker gets its own dedicated validator
(1:1 ratio). This prevents any single validator from being overwhelmed
and keeps each validation context focused on one unit of work.

---

### Plan File Coordination

If a task's `plan.md` is already loaded into the session's context (the
`engage` skill matched the user's prompt against ACTIVE.md and pulled the
plan in, or the orchestrator was working from that plan when dispatch was
invoked), the dispatch workflow uses it as an external coordination artifact:

1. **Before decomposition:** The plan's Goal, Approach, and current step
   status inform sub-task breakdown.
2. **After execution:** Update the plan file with completed steps and any
   new information discovered during dispatch.
3. **Worker prompts:** Include relevant plan context so workers understand
   how their piece fits the larger goal.

This means workers coordinate through a shared, persistent artifact
rather than relying solely on the orchestrator's context window.

If no task plan is loaded, dispatch operates standalone (no plan file).

---

### Prompt

```
You are orchestrating a prompt dispatch workflow. You received a user prompt
and your job is to execute it through decomposition, parallel workers,
and validation. Follow the phases below exactly.

IMPORTANT: You are the orchestrator. Your job is to ROUTE, not to DO. Do
not read files, analyze code, or write code yourself. Offload ALL substantive
work to available worker/sub-agent tools. If the current harness has no worker
mechanism, report that dispatch cannot run as designed rather than pretending
to parallelize.


## Phase 0: Load Plan Context (if a task plan is in scope)

If a task's `plan.md` is already loaded into context (the `engage` skill
matched earlier in this session, or the user explicitly referenced a task
folder), include the plan's Goal, Approach, and current step status as
context for the decomposer in Phase 1.

If no task plan is in scope, skip to Phase 1.


## Phase 1: Decompose

Start a single decomposer worker using the current harness's available
worker/sub-agent mechanism. Pass it the user's original prompt verbatim. If
plan context was loaded in Phase 0, append it to the prompt.

### Decomposer Worker Instructions

```
You are a task decomposition specialist. You receive a user prompt and
repository context. Your job is to break the prompt into independent,
parallelizable sub-tasks that can be executed by separate workers.

### Steps

1. **Scan the environment:**
   - Use available search and file-listing tools to understand the directory structure
   - Read README.md and AI guidance in harness priority order (`AGENTS.md` for
     Codex, `CLAUDE.md` for Claude, then referenced guidance)
   - Identify the project type, language, and conventions
   - Do NOT do deep exploration -- just enough to inform decomposition

2. **Analyze the prompt:**
   - What distinct concerns does the prompt contain?
   - What types of work are needed? (research, code changes, tests, docs,
     commands, configuration)
   - What files or systems are likely involved?

3. **Identify sub-tasks:**
   - Each sub-task should be independently executable
   - Each sub-task prompt must be SELF-CONTAINED: include all file paths,
     function names, search terms, and context the worker will need
   - Workers may not see the main conversation -- their prompt is all they get
   - If two tasks depend on each other, merge them into one worker

4. **Select worker kind:**

   | Work Type | Worker Kind | When |
   |-----------|-------------|------|
   | Find files, map structure, search code | explore | Discovery and search |
   | Read + write + edit files, multi-step work | general | Code changes, research, analysis |
   | Run builds, tests, shell commands | shell | Execution and verification |
   | Design approach before implementation | planning | Architectural decisions |

5. **Define validation criteria:**
   - What should the validator check to confirm the original prompt was met?
   - Map criteria back to the user's stated intent

### Output

Return ONLY this JSON (no other text):

{
  "original_prompt": "the user's prompt, verbatim",
  "prompt_summary": "1-sentence summary of intent",
  "sub_tasks": [
    {
      "id": "task-1",
      "title": "short title (5 words max)",
      "worker_kind": "explore | general | shell | planning",
      "parallel_group": 1,
      "depends_on": [],
      "prompt": "complete, self-contained instructions for this worker -- include all file paths, context, and expected output format",
      "expected_output": "what this worker should return"
    }
  ],
  "validation_criteria": [
    "specific, testable criterion the validator should check"
  ]
}

### Rules

- Maximum 5 sub-tasks. Merge related work to stay under this limit.
- If the prompt is simple enough for 1 agent, return 1 sub-task.
- Every sub-task prompt must end with: "Return a structured summary of what
  you did, what you found or produced, any issues encountered, and your
  confidence level (high/medium/low)."
- parallel_group numbers indicate execution order: group 1 runs first,
  group 2 runs after group 1 completes, etc. Tasks in the same group
  run simultaneously.
- Keep depends_on empty for parallel tasks. Only populate it if a task
  must wait for a specific other task's output (and put them in a later
  parallel_group).
```

### Orchestrator Action After Decomposition

1. Parse the decomposer's JSON output
2. Sanity-check: does the decomposition cover the user's prompt?
3. If the decomposition has obvious gaps, note them and proceed (the
   validator will catch them)
4. Move to Phase 2


## Phase 2: Execute Workers

For each parallel_group (starting with group 1):

1. Start ALL tasks in the group simultaneously using the current harness's
   available parallel worker/sub-agent mechanism
2. Map `worker_kind` to the closest available capability:
   - `explore` -> discovery/search worker or read-only explorer
   - `general` -> general editing/research worker
   - `shell` -> command execution worker
   - `planning` -> design/planning worker
3. Use background execution only when the current tool supports it and the
   group size makes monitoring useful; otherwise run parallel calls in one
   tool message or collect foreground worker results
4. Collect all results before moving to the next parallel_group
5. If a worker in an earlier group produces output that a later group
   depends on, include that output in the later worker's prompt

### Worker Result Tracking

For each worker, record:
- task_id from the decomposition plan
- status: succeeded / failed / partial
- result summary (keep this concise -- key findings and actions only)
- any files changed or created

After all workers complete, move to Phase 3.


## Phase 3: Validate

Start one validator worker PER worker
from Phase 2 -- a strict 1:1 ratio. This prevents any single validator
from being overwhelmed and keeps each validation context tightly scoped.

For each worker, spawn a validator with the following context:

- The original user prompt (for overall intent)
- The specific sub-task from the decomposition plan that this worker executed
- The result summary from THIS worker only
- The validation criteria from the decomposition plan that apply to this
  worker's sub-task

Start all validators in parallel using the same harness mechanism and
background/foreground rules used for workers.

### Validator Worker Instructions

```
You are a validation specialist. You receive the original user prompt,
a single sub-task definition, and results from one worker. Your
job is to verify that this worker's output correctly and completely
addresses its assigned sub-task.

### Validation Steps

1. **Completeness Check:**
   - Did this worker fully address its assigned sub-task?
   - Are there gaps -- aspects of the sub-task the worker missed?
   - Were the validation criteria relevant to this sub-task met?

2. **Correctness Check:**
   - Are the worker's outputs accurate and well-formed?
   - If the worker edited files, do changes follow existing codebase patterns?
   - Did the worker introduce any regressions or errors?

3. **Artifact Verification:**
   - If the worker claims it created or modified files, use available file
     reading/search tools to verify those files exist and contain the expected
     changes
   - If the worker claims test results, verify by inspecting actual output

4. **Criteria Evaluation:**
   - For each validation criterion relevant to this sub-task, state whether
     it was met and cite evidence

### Output

Return ONLY this JSON (no other text):

{
  "task_id": "the task-id this validator checked",
  "status": "pass | fail | needs_revision",
  "summary": "1-2 sentence assessment of this worker's output",
  "completeness": {
    "covered": ["aspects of the sub-task that were addressed"],
    "gaps": ["aspects that were missed or incomplete"]
  },
  "issues": ["specific issues found, empty array if none"],
  "criteria_results": [
    {
      "criterion": "from decomposition plan",
      "met": true,
      "evidence": "how verified"
    }
  ],
  "recommendations": ["actionable fixes for any issues, empty if none"]
}
```

### Orchestrator Action After Validation

After all validators return, consolidate their results:

1. Collect all validator JSON outputs into a single results array
2. Derive the overall status:
   - **pass** -- all validators returned "pass"
   - **partial** -- at least one "needs_revision" but no "fail"
   - **fail** -- any validator returned "fail"
3. Check for cross-worker conflicts: compare file paths changed across
   workers. If multiple workers modified the same file, flag this as an
   integration concern in the report.
4. Move to Phase 4


## Phase 4: Update Plan (if a task plan was loaded in Phase 0)

If a task's `plan.md` was loaded in Phase 0:
1. Update `{task-path}/plan.md` -- mark completed steps, add new steps
   discovered during dispatch, note any decisions made
2. Write a status entry to `{task-path}/status.md` summarizing what
   dispatch accomplished

This ensures the plan file stays current as the coordination artifact
for future sessions and dispatch runs.


## Phase 5: Report

Based on the validator's output, report to the user with the following
structure. Adapt the detail level to the result.

### If PASS:

```
### Dispatch Complete -- PASS

**Request:** [prompt summary]

#### Work Completed
- [Task 1 title]: [1-line summary]
- [Task 2 title]: [1-line summary]

#### Validation
All criteria met. [any notable observations]

#### Files Changed
- path/to/file1 (created | modified)
- path/to/file2 (created | modified)
```

### If PARTIAL:

```
### Dispatch Complete -- PARTIAL

**Request:** [prompt summary]

#### Work Completed
- [Task 1 title]: PASS - [summary]
- [Task 2 title]: NEEDS REVISION - [summary + issue]

#### Issues
- [issue 1 with recommendation]

#### Validation
[overall assessment, gaps identified]

#### Files Changed
- path/to/file1 (created | modified)

#### Recommended Next Steps
- [what user should do to address gaps]
```

### If FAIL:

```
### Dispatch Complete -- FAIL

**Request:** [prompt summary]

#### Issues
- [issue 1]
- [issue 2]

#### What Was Attempted
- [Task 1 title]: [what happened]

#### Recommendations
- [what to try next]
```


## Orchestration Rules

1. **Decomposition is mandatory.** Even simple prompts go through the
   decomposer. It may return a single sub-task -- that is fine.

2. **Worker prompts must be self-contained.** Workers cannot see the main
   conversation. Everything they need must be in their prompt.

3. **Validation is mandatory and 1:1.** Every worker gets its own
   dedicated validator. Even a single-worker workflow spawns one validator.
   Validators run in parallel when the harness supports it.

4. **Maximum 5 workers.** The decomposer enforces this. If it returns
   more, ask it to merge.

5. **No auto-commit.** Present results to user. Do not commit, push,
   or deploy.

6. **Fail fast.** If the decomposer fails to return valid JSON, report
   the error to the user immediately rather than guessing.

7. **Orchestrator stays lean.** Do NOT read files, write code, or do
   analysis yourself. Use only the current harness's worker/sub-agent
   orchestration tools and text output to report to the user.

8. **Preserve worker attributions.** In the final report, attribute
   findings and changes to specific sub-tasks so the user can trace
   what each agent did.
```

---

### Usage Example

**Starting the workflow:**

```
/dispatch Refactor the authentication module to use JWT tokens instead of
session cookies. Update all tests and ensure backwards compatibility with
the existing API contract.
```

**What happens:**

1. Decomposer analyzes the prompt, finds 3 concerns:
   - Research current auth implementation (Explore)
   - Implement JWT refactor (general-purpose)
   - Update and verify tests (general-purpose)

2. Group 1 (parallel): Research runs via Explore agent
3. Group 2 (after research): Implementation + test updates run in parallel,
   informed by research findings
4. Validators (one per worker) check their respective outputs in parallel
5. Orchestrator consolidates validator results, reports PASS/PARTIAL/FAIL

---

### Comparison with Feature Implementation Workflow

| Aspect | Feature Implementation | Prompt Dispatch |
|--------|----------------------|-----------------|
| Scope | New features only | Any prompt |
| Flow | Sequential (5 phases) | Fan-out / fan-in |
| User interaction | Dialogue phase for requirements | No mid-workflow dialogue |
| Revision loop | Reviewer can loop back to implementer | 1:1 parallel validation (no revision loop) |
| Context strategy | Each phase in main context | All work in workers/sub-agents |
| Best for | Complex features needing clarification | Parallel, well-defined work |

---

### Integration Notes

**Codex subagent guidance:**
- Decomposer: use the main Codex agent unless decomposition can run in parallel with other useful work; the default subagent role is usually sufficient.
- Workers: map `worker_kind` to the closest available Codex role. Use `explorer` for bounded read-only codebase questions, `worker` for scoped implementation with clear file ownership, and `default` for general work.
- Validators: use independent Codex subagents for parallel validation when useful, then inspect their reported evidence before integrating results.
- For parallel groups of 3+, start independent subagents only when their work is self-contained and does not block the immediate local step. If subagents are unavailable, execute the same decomposition locally with explicit checkpoints between workers.

**Other LLM tools and harnesses:**
- The decomposer/validator instructions are self-contained prompts
- Adapt the spawning mechanism to the available multi-agent, parallel tool, or
  worker capability
- The JSON contracts between phases are the integration points
