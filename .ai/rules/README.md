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

## Standards

Standards for documentation, testing, code review, and anti-patterns are
provisioned as skills in `.claude/skills/`. These are loaded automatically
when relevant -- no external references needed.

## Directory Structure

```
.ai/
  rules/           # Conditional guidance (checked into git)
    README.md      # This file - indexes rules
  checkpoints/     # Session state persistence (gitignored)
  a2a/             # Agent-to-agent communication (gitignored)
```
