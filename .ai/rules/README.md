# AI Rules Index

Project-specific conditional guidance for AI agents. Load rules based on task type.

## Rule Files

| File | Load When |
|------|-----------|
| (none yet) | - |

## Adding Rules

Create rule files in this directory for project-specific guidance that should only apply conditionally. Examples:

- `api_conventions.md` - Load when modifying API endpoints
- `testing_rules.md` - Load when writing tests
- `llm_integration.md` - Load when modifying story_writer or prompts

## External Standards

This project references standards from `cross_project_ai_resources`:

```
~/workspace/cross_project_ai_resources/agent_context/core/
  - documentation_standards.md (ASCII-only, zero-context)
  - testing_standards.md (80%+ coverage, AAA pattern)

~/workspace/cross_project_ai_resources/agent_context/conditional/
  - anti_patterns.md (load during code review)
  - agent_handoff_standard.md (load for multi-agent workflows)
```

## Directory Structure

```
.ai/
  rules/           # Conditional guidance (checked into git)
    README.md      # This file - indexes rules
  checkpoints/     # Session state persistence (gitignored)
  a2a/             # Agent-to-agent communication (gitignored)
```
