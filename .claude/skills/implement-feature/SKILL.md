---
name: implement-feature
description: >-
  Multi-agent workflow for implementing new features through sequential scout,
  dialogue, context-gathering, implementation, and review phases.
  TRIGGER when: user requests a substantial new feature requiring codebase
  understanding, user clarification, and structured implementation with review.
  DO NOT TRIGGER when: quick bug fixes, documentation-only changes, simple
  refactors with known solutions, or single-file changes.
---
<!-- repo-types: api-service, cli-tool, library, frontend-app, full-stack, monorepo -->

# Feature Implementation Workflow

Multi-agent workflow for implementing new features through collaborative agent handoffs.

---

## Purpose

- Systematically implement features from discovery through validated code
- Ensure thorough understanding of codebase before implementation
- Gather complete context before writing code
- Validate implementations through review cycles
- Provide clear exit points when implementation diverges from intent

---

## When to Use

| Scenario | Use This Workflow |
|----------|-------------------|
| Adding new feature to existing codebase | Yes |
| Feature requires understanding existing patterns | Yes |
| Implementation needs user clarification | Yes |
| Quick bug fix with known solution | No - use direct implementation |
| Documentation-only changes | No - use documenter agent |

---

## Workflow Overview

```
[Repository Scout] --> [Feature Dialoguer] --> [Context Gatherer]
                              ^                       |
                              |                       v
                        (if unclear)          [Implementer]
                                                     |
                                                     v
                              +---(revision)--- [Reviewer]
                              |                      |
                              v                      |
                        [Implementer]          (approve/exit)
                                                     |
                                                     v
                                              [User Commits]
```

---

## Agent Definitions

| Agent | Type | Purpose |
|-------|------|---------|
| Repository Scout | `investigator` | Builds initial codebase understanding |
| Feature Dialoguer | `general` | Clarifies requirements with user |
| Context Gatherer | `investigator` | Collects all files relevant to feature |
| Implementer | `code-writer` | Writes code and tests |
| Reviewer | `code-reviewer` | Validates implementation quality |

---

## Prompt

```
You are orchestrating a multi-agent feature implementation workflow.

## Workflow Phases

### Phase 1: Repository Scout

**Agent Type:** investigator
**Goal:** Build foundational understanding of the codebase

**Tasks:**
1. Identify the project type (language, framework, build system)
2. Map the directory structure and key entry points
3. Locate existing patterns for:
   - How features are organized (by type vs by domain)
   - Testing conventions (framework, file locations, naming)
   - Configuration management
   - Error handling patterns
4. Identify any AI guidance files (CLAUDE.md, .ai/rules/, etc.)
5. Note architectural constraints or conventions

**Output Artifact:** `repository-overview`

```json
{
  "repository_overview": {
    "project_type": "string",
    "language": "string",
    "framework": "string (if applicable)",
    "build_system": "string",
    "structure": {
      "source_root": "path",
      "test_root": "path",
      "config_location": "path",
      "feature_organization": "by-type | by-domain | hybrid"
    },
    "conventions": {
      "naming": "description of naming patterns",
      "testing": "test framework and patterns",
      "error_handling": "patterns observed"
    },
    "ai_guidance_files": ["list of paths"],
    "key_observations": ["notable patterns or constraints"]
  }
}
```

**Handoff:** Submit to Feature Dialoguer with state `submitted`

---

### Phase 2: Feature Dialoguer

**Agent Type:** general
**Goal:** Clarify feature requirements through user dialogue

**Inputs:**
- Repository overview from Scout
- User's initial feature request

**Tasks:**
1. Review the repository overview to understand what's possible
2. Engage user to clarify:
   - Core functionality required
   - Expected inputs and outputs
   - Integration points with existing code
   - Edge cases and error handling expectations
   - Testing requirements
3. If requirements are ambiguous, ask focused questions
4. Produce a clear feature specification

**User Interaction Rules:**
- Ask at most 3 questions per interaction
- Provide options when possible rather than open-ended questions
- Summarize understanding back to user for confirmation
- If user says "just do it" or similar, proceed with reasonable defaults

**Output Artifact:** `feature-specification`

```json
{
  "feature_specification": {
    "title": "short feature name",
    "summary": "1-2 sentence description",
    "user_story": "As a [user], I want [goal] so that [benefit]",
    "requirements": {
      "functional": ["list of functional requirements"],
      "non_functional": ["performance, security, etc."]
    },
    "integration_points": [
      {
        "location": "path or module",
        "interaction": "how the feature connects"
      }
    ],
    "acceptance_criteria": ["testable criteria for completion"],
    "out_of_scope": ["explicitly excluded items"],
    "assumptions": ["assumptions made during clarification"],
    "user_confirmed": true
  }
}
```

**Handoff:** Submit to Context Gatherer with state `submitted`

**Exit Condition:** If user explicitly cancels or requirements cannot be clarified
after 3 rounds of questions, exit with state `failed` and summary.

---

### Phase 3: Context Gatherer

**Agent Type:** investigator
**Goal:** Collect all files and context needed for implementation

**Inputs:**
- Repository overview from Scout
- Feature specification from Dialoguer

**Tasks:**
1. Identify all files that will need modification
2. Identify all files that provide patterns to follow
3. Identify all files that the new code will interact with
4. Gather relevant test files as examples
5. Extract relevant type definitions, interfaces, or schemas
6. Note any external documentation needed

**Search Strategy:**
1. Start from integration points in the specification
2. Trace dependencies inward (what does this code depend on?)
3. Trace dependents outward (what depends on code we'll change?)
4. Find similar features to use as templates
5. Locate configuration that may need updates

**Output Artifact:** `implementation-context`

```json
{
  "implementation_context": {
    "feature_specification_id": "reference to spec",
    "files_to_modify": [
      {
        "path": "file path",
        "reason": "why modification needed",
        "key_sections": "functions/classes to focus on"
      }
    ],
    "files_to_create": [
      {
        "path": "proposed path",
        "purpose": "what this file will contain",
        "template_source": "existing file to use as pattern (if any)"
      }
    ],
    "reference_files": [
      {
        "path": "file path",
        "relevance": "why this is useful context"
      }
    ],
    "test_files": {
      "existing": ["tests that cover related code"],
      "new_locations": ["where new tests should go"]
    },
    "types_and_interfaces": [
      {
        "path": "file path",
        "items": ["specific types/interfaces needed"]
      }
    ],
    "configuration_files": ["config files that may need updates"],
    "external_docs": ["links or references if needed"]
  }
}
```

**Handoff:** Submit to Implementer with state `submitted`

---

### Phase 4: Implementer

**Agent Type:** code-writer
**Goal:** Implement the feature and write tests

**Inputs:**
- Feature specification from Dialoguer
- Implementation context from Context Gatherer
- (On revision) Change requests from Reviewer

**Tasks:**
1. Read all files in implementation context
2. Implement the feature following existing patterns
3. Write tests that verify acceptance criteria
4. Run existing tests to ensure no regressions
5. Update configuration if needed
6. Self-review against the specification before handoff

**Implementation Rules:**
- Follow existing code patterns exactly
- Do not refactor unrelated code
- Do not add features beyond specification
- Ensure all acceptance criteria are testable
- Keep changes minimal and focused

**On Revision (from Reviewer):**
1. Address all change requests
2. Re-run tests
3. Document what was changed in response
4. Resubmit to Reviewer

**Output Artifact:** `implementation-result`

```json
{
  "implementation_result": {
    "feature_specification_id": "reference",
    "status": "completed | partial",
    "changes": [
      {
        "file": "path",
        "action": "created | modified",
        "summary": "what was done"
      }
    ],
    "tests": {
      "written": ["list of test files/functions"],
      "passed": true,
      "coverage_notes": "optional coverage info"
    },
    "acceptance_criteria_met": [
      {
        "criterion": "from specification",
        "how_verified": "test name or manual check"
      }
    ],
    "revision_responses": [
      {
        "request_id": "from reviewer",
        "response": "how it was addressed"
      }
    ],
    "notes": "any implementation notes for reviewer"
  }
}
```

**Handoff:** Submit to Reviewer with state `submitted`

---

### Phase 5: Reviewer

**Agent Type:** code-reviewer
**Goal:** Validate implementation quality and alignment with specification

**Inputs:**
- Feature specification from Dialoguer
- Implementation result from Implementer
- All changed/created files

**Tasks:**
1. Verify all acceptance criteria are met
2. Review code quality:
   - Follows existing patterns
   - No unnecessary complexity
   - Proper error handling
   - No security issues
3. Review test quality:
   - Tests cover requirements
   - Tests are meaningful (not just coverage)
   - Edge cases addressed
4. Check for scope creep (changes beyond specification)
5. Make a decision

**Decision Options:**

**APPROVE:**
- All criteria met
- Code quality acceptable
- Tests adequate
- Output: Approval with optional minor suggestions for user

**REQUEST_CHANGES:**
- Issues are fixable
- Implementation is on track but needs adjustments
- Maximum 3 revision cycles before escalating
- Output: Specific, actionable change requests

**EXIT:**
- Implementation has diverged significantly from specification
- Fundamental approach is wrong
- More than 3 revision cycles without convergence
- Output: Explanation of why workflow is stopping

**Output Artifact:** `review-decision`

```json
{
  "review_decision": {
    "implementation_result_id": "reference",
    "decision": "approve | request_changes | exit",
    "revision_cycle": 1,
    "summary": "brief decision rationale",
    "approval": {
      "final_status": "ready_for_commit",
      "suggestions": ["optional minor improvements for user"],
      "files_to_commit": ["list of files"]
    },
    "change_requests": [
      {
        "id": "CR-001",
        "file": "path",
        "issue": "what's wrong",
        "suggestion": "how to fix",
        "severity": "required | recommended"
      }
    ],
    "exit_reason": {
      "primary_issue": "why we're stopping",
      "attempted_fixes": ["what was tried"],
      "recommendation": "what user should do next"
    }
  }
}
```

**Handoff:**
- APPROVE: Return to orchestrator with state `completed`
- REQUEST_CHANGES: Submit to Implementer with state `submitted`
- EXIT: Return to orchestrator with state `failed`

---

## Orchestration Rules

1. **Sequential Flow:** Phases must execute in order (1 -> 2 -> 3 -> 4 -> 5)
2. **Revision Loop:** Phase 5 may loop back to Phase 4 (max 3 times)
3. **User Commits:** After approval, present changes to user for commit
4. **No Auto-Commit:** The workflow does not commit changes
5. **Exit Points:**
   - Phase 2: User cancels or requirements unclear
   - Phase 5: Reviewer decides to exit
6. **Handoff Persistence:** For workflows spanning multiple sessions or tools,
   use `.ai/a2a/` for disk-based persistence. For single-session workflows,
   native tool coordination (e.g., Claude Code subagents) handles this in-memory.

## State Management

Track workflow state:

```json
{
  "workflow_state": {
    "id": "uuid",
    "started": "ISO8601",
    "current_phase": "1-5",
    "revision_count": 0,
    "phase_artifacts": {
      "repository_overview": "artifact-id or null",
      "feature_specification": "artifact-id or null",
      "implementation_context": "artifact-id or null",
      "implementation_result": "artifact-id or null",
      "review_decision": "artifact-id or null"
    },
    "status": "in_progress | completed | failed | cancelled"
  }
}
```

## Error Handling

| Error | Action |
|-------|--------|
| Agent fails to produce output | Retry once, then exit with failure |
| User stops responding | Pause workflow, resume on user return |
| Tests fail repeatedly | Exit after 3 attempts, report to user |
| Circular dependency in changes | Exit, recommend architectural review |

## Success Criteria

Workflow is successful when:
1. Reviewer approves implementation
2. All acceptance criteria verified
3. Tests pass
4. Changes are presented to user for commit
```

---

## Usage Example

**Initial Prompt to Start Workflow:**

```
I want to add a feature to [describe feature]. Please use the feature
implementation workflow to guide this process.
```

**The orchestrator will:**
1. Spawn Repository Scout to understand the codebase
2. Present findings and engage user via Feature Dialoguer
3. Gather context with Context Gatherer
4. Implement with Implementer
5. Validate with Reviewer
6. Present approved changes for user commit

---

## Comparison with Prompt Dispatch Workflow

| Aspect | Feature Implementation | Prompt Dispatch |
|--------|----------------------|-----------------|
| Scope | New features only | Any prompt |
| Flow | Sequential (5 phases) | Fan-out / fan-in |
| User interaction | Dialogue phase for requirements | No mid-workflow dialogue |
| Revision loop | Reviewer can loop back to implementer | 1:1 parallel validation (no revision loop) |
| Context strategy | Each phase in main context | All work in sub-agents |
| Best for | Complex features needing clarification | Parallel, well-defined work |

---

## Integration Notes

**Claude Code (Task tool):**
- Scout/Gatherer: `Task(subagent_type="Explore", prompt=...)`
- Dialoguer: Direct interaction in main context (needs user input)
- Implementer: `Task(subagent_type="general-purpose", prompt=...)`
- Reviewer: `Task(subagent_type="general-purpose", prompt=...)`

**Other LLM tools:**
- The phase instructions are self-contained prompts
- Adapt the spawning mechanism to your tool's multi-agent capabilities
- The JSON artifact schemas are the integration points between phases
