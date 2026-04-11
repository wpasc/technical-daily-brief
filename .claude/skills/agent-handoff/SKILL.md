---
name: agent-handoff
description: Lightweight protocol for passing context between AI agents - JSON schema for cross-tool, cross-session, and audit-trail handoffs. Not needed for single-tool native coordination.
user-invocable: false
---
<!-- repo-types: api-service, cli-tool, library, frontend-app, full-stack, monorepo -->

# Agent Handoff Standard

Lightweight specification for passing context between AI agents.

> **Status: Optional / Advanced**
>
> This file-based handoff protocol is no longer required for standard workflows.
> Modern AI tools -- Claude Code subagents, Anthropic Agent SDK, Google A2A
> protocol, and similar frameworks -- handle agent coordination natively through
> in-memory message passing.
>
> **When this protocol remains useful:**
> - Cross-tool interoperability (coordinating between different AI platforms)
> - Cross-session persistence (handoffs that must survive beyond a single session)
> - Audit trails (when a human-inspectable record of agent decisions is required)

---

## Minimal Handoff

The simplest valid handoff:

```json
{
  "handoff": {
    "id": "uuid-v4",
    "timestamp": "2025-01-29T14:30:00.000Z",
    "source": { "agentType": "code-writer" },
    "status": { "state": "submitted" },
    "task": {
      "type": "code-review",
      "summary": "Review authentication changes"
    }
  }
}
```

**Required fields:** id, timestamp, source.agentType, status.state, task.type, task.summary

## Task States

```
submitted -> working -> completed
                    \-> failed
                    \-> input_required
```

## Agent Types

| Type | Purpose |
|------|---------|
| `code-writer` | Implements features, fixes bugs |
| `code-reviewer` | Reviews code quality and security |
| `test-writer` | Writes and maintains tests |
| `investigator` | Debugs, researches, analyzes |
| `refactorer` | Restructures without behavior change |
| `documenter` | Writes documentation |
| `auditor` | Validates alignment with declared intent |
| `fixer` | Applies minimal interventions from audit findings |
| `general` | Multi-purpose |

## Task Types

| Type | Use For |
|------|---------|
| `code-review` | Code quality, security review |
| `code-write` | New features, bug fixes |
| `refactor` | Code restructuring |
| `investigate` | Debugging, root cause analysis |
| `test` | Writing tests |
| `document` | Documentation |
| `audit` | Validation against declared intent |
| `fix` | Apply minimal intervention from audit finding |
| `general` | Everything else |

## Optional Fields

Add when they provide value: `task.instructions`, `task.constraints`, `task.acceptance_criteria`, `context.files`, `context.decisions`, `context.assumptions`, `artifacts`, `metadata.priority`, `metadata.tags`.

## Guidelines

**DO:** Generate UUIDs for id, include only context the next agent needs, keep handoffs focused on one task.

**DON'T:** Include secrets or credentials, dump entire conversation history, add fields "just in case."
