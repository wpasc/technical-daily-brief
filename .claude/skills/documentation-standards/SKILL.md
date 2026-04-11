---
name: documentation-standards
description: Zero-context documentation principles, README structure, encoding preferences, and anti-patterns for writing clear documentation
user-invocable: false
---
<!-- repo-types: api-service, cli-tool, library, frontend-app, full-stack, monorepo, documentation -->

# Documentation Standards

Comprehensive guide to writing clear, complete documentation that any reader - human or AI - can understand with zero prior context.

---

## Core Philosophy

### Zero-Context Principle

Every piece of documentation should be written assuming the reader has:

**The reader HAS:**
- General programming knowledge
- Understanding of common patterns (MVC, REST, etc.)

**The reader DOES NOT have:**
- Knowledge of your project's history
- Knowledge of your team's conventions
- Knowledge of why certain decisions were made

**Why?** This ensures:
- New team members can onboard quickly
- AI agents can contribute effectively
- Future maintainers understand the codebase
- Documentation ages well

---

## README Files - Context Where It Matters

**When to Create a README:**
- Root of the project (always)
- Major modules or packages with distinct functionality
- Directories that would confuse a new developer
- Complex subsystems that need architectural explanation

**When NOT to Create a README:**
- Build artifact directories (`__pycache__`, `node_modules`, etc.)
- Directories with only a few self-explanatory files
- Utility folders where file names are sufficient
- Temporary directories

Use judgment: a README should add value, not just exist to check a box.

**Required README Structure:**
```markdown
# {Directory Name}

{One-sentence description}

## Quick Start / Usage
{How to use/run this code - concrete examples}

## Directory Structure
{Tree view of contents with brief descriptions}

## {Context-Specific Sections}
{Architecture, API, Features, Dependencies - whatever is relevant}

## Testing
{How to test this module}
```

---

## Writing Effective Documentation

### Use Concrete Examples

**Bad:**
```markdown
Configure the database properly before running.
```

**Good:**
```markdown
Configure the database connection in `config.yaml`:

```yaml
database:
  host: localhost
  port: 5432
  name: myapp_dev
  user: postgres
  password: your_password
```

Then run migrations:
```bash
python manage.py migrate
```
```

### Explain the "Why"

**Bad:**
```markdown
Use the repository pattern for all database access.
```

**Good:**
```markdown
Use the repository pattern for all database access.

**Why?**
- **Testability**: Easy to mock repositories in unit tests
- **Maintainability**: Query logic centralized, not scattered
- **Flexibility**: Can swap database without changing business logic
- **Consistency**: Same patterns across entire codebase
```

### Show Good and Bad Examples

Always include both correct and incorrect examples so the reader understands the boundary.

### Link Related Documentation

Include file paths and cross-references to related docs.

### Keep It Current

Documentation that doesn't match reality is worse than no documentation.

**Strategies:**
1. **Update docs when changing code** - Make it part of your workflow
2. **Link to code** - Include file paths and line numbers
3. **Use tests as documentation** - Well-named tests explain behavior
4. **Use git commits** - Good commit messages track changes and rationale

---

## Character Encoding Preference

Prefer plain ASCII in documentation for simplicity and compatibility. This is a soft preference, not a hard rule.

- **Avoid** decorative emoji in documentation -- they add noise, not information
- **Prefer** `+--` notation or Mermaid for directory trees over box-drawing characters
- **Use** standard characters that render well across terminals and editors

---

## Diagrams: Use Mermaid

For visual diagrams, use Mermaid. Mermaid is text-defined and LLM-readable in source form, but renders as rich visuals in GitHub, VS Code, and most markdown viewers.

**Use Mermaid for:** architecture diagrams, flowcharts, sequence diagrams, dependency relationships, and any structure more complex than a simple text tree.

**For simple directory trees**, plain text is fine (`+--` notation). Use Mermaid when showing relationships, not just hierarchy.

---

## Documentation Anti-Patterns

### 1. The Vague Description

**Bad:** "This module handles user stuff."

**Good:** "This module provides user authentication and authorization: JWT token generation and validation, password hashing with bcrypt, role-based access control, session management."

### 2. The Assumed Context

**Bad:** "As discussed in the meeting, we're using the new approach."

**Good:** "We're using JWT tokens instead of sessions for authentication. **Rationale:** Sessions don't scale horizontally."

### 3. The Reference to Ephemeral Knowledge

**Bad:** "Ask Bob about the deployment process."

**Good:** Document the deployment process directly with concrete steps.

### 4. The Over-Technical Explanation

**Bad:** Dumping architectural jargon without explanation.

**Good:** Start simple, link to details. Explain what the system does before how.

---

## Summary

**Key Principles:**
- **Zero-context** - Assume nothing about the reader
- **"Why" matters** - Explain rationale, not just "what"
- **Show don't tell** - Concrete examples throughout
- **Keep it current** - Update docs when code changes
- **No redundancy** - Say things once, in the right place
- **Plain text** - Prefer ASCII, avoid decorative emoji

Good documentation serves all readers - humans and AI alike. Write it clearly once, and everyone benefits.
