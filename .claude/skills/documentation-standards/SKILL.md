---
name: documentation-standards
description: Documentation principles -- zero-context writing, declared intent, README placement stack, self-evident navigation, currency maintenance, and anti-patterns
user-invocable: false
---

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

### Documentation as Declared Intent

Documentation is not decoration or commentary. It is the **authoritative statement of what the project is supposed to be**. Code is observable reality. When code and docs diverge, that gap is a drift signal that needs resolving -- not a sign that "docs are out of date and the code is what really matters."

**Authority hierarchy** (when sources conflict, higher wins on intent):

1. Explicit project documentation (README, ADRs, `/docs`)
2. Explicit AI guidance files (`AGENTS.md`, `CLAUDE.md`, or another
   harness-specific guidance file) if designated authoritative
3. Inline comments explicitly stating intent
4. Code structure (lowest authority -- never overrides documentation)

Code structure is evidence of what *is*, not what *ought to be*. Inference from code never overrides a higher-authority source. If the code does X but the README says it does Y, the ambiguity must be resolved -- either the code has drifted or the docs have drifted, and that requires a human call. Neither silently wins.

This is what makes documentation enforceable rather than aspirational. The
`audit-documentation` skill exists to surface exactly these drift signals
(and `audit-repository` runs it alongside a code-quality vector for a
full repo health pass).

### Self-evident Navigation

A reader dropped anywhere in the repo should never feel lost. The hierarchy itself should make the next step obvious -- what this folder is, and where to go for the bigger picture or the next level of detail.

This is a layout principle, not a linking mandate. A tightly-scoped folder README does not need to link back to its enclosing README; the folder structure itself provides the upward path. The goal is a repo whose shape a reader can hold in their head after a brief scan.

Cross-references between READMEs are fine when they add navigation value. Do not turn that into ceremony -- if a link exists only to satisfy a rule, omit it.

---

## README Files -- The Placement Stack

READMEs form a layered navigation stack. Not every folder gets one; placement is tiered.

**The stack (outermost to innermost):**

1. **Global README (repo root)** -- always exists. Describes what the project is, its rough outline, and points to where the major pieces live.
2. **Major-folder READMEs** -- for modules or packages with distinct functionality, or folders that would confuse a new reader without orientation. Describe scope and point onward.
3. **Minor-folder READMEs** -- only when they add value. A folder with five well-named, self-explanatory files does not need one.
4. **Source-file comments** -- the innermost layer, for the "why" of specific code. Use sparingly; well-named identifiers should carry most of the meaning.

**When NOT to create a README:**

- Build artifact directories (`__pycache__/`, `node_modules/`, `.venv/`)
- Directories with only a few self-explanatory files
- Utility folders where file names are sufficient
- Temporary directories

Use judgment: a README should add value, not exist to check a box.

### The README-as-Index Pattern

A good README does two things: it **describes its own scope**, and it **points to where the next level of detail lives**. At the root, that means pointing to major subsystems. Inside a module, it means pointing to the files or subfolders that carry the real implementation.

This makes READMEs a navigation surface, not a wall of prose. A reader should land on any README and know two things within ten seconds: *what is this?* and *where do I go next?*

### README Structure

```markdown
# {Directory Name}

{One-sentence description}

## Quick Start / Usage
{How to use/run this code -- concrete examples}

## Directory Structure
{Tree view of contents with brief descriptions, pointing to sub-READMEs where they exist}

## {Context-Specific Sections}
{Architecture, API, Features, Dependencies -- whatever is relevant}

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

Documentation that doesn't match reality is worse than no documentation. Stale docs corrupt the "declared intent" role they are supposed to play -- a reader can no longer tell which sources to trust.

**Strategies:**
1. **Update docs when changing code** -- make it part of the workflow
2. **Link to code** -- include file paths and line numbers
3. **Use tests as documentation** -- well-named tests explain behavior
4. **Use git commits** -- good commit messages track changes and rationale
5. **Run the `audit-documentation` skill periodically** -- surfaces drift
   between declared intent and observable code before it accumulates. Use
   `audit-repository` when you want it bundled with a code-quality audit.

### Change Precedence when Docs and Code Disagree

When docs and code diverge, prefer fixes in this order:

1. **Documentation updates** -- clarify the intent
2. **Comment additions** -- explain the existing code's intent inline
3. **Structural changes** -- move or rename to match intent
4. **Code changes** -- last resort

This is not "always change the docs first." It is a **precedence** for when either fix would be valid: reach for the higher-level fix because doc fixes are cheaper, preserve the history of why the gap existed, and carry the least risk. Code changes are the last resort because they carry the most.

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
- **Zero-context** -- Assume nothing about the reader
- **Declared intent** -- Docs are authoritative; code is observable reality. Divergence is drift, not "code wins"
- **Self-evident navigation** -- The hierarchy itself should make the next step obvious
- **Placement stack** -- Global README -> major-folder READMEs -> minor only when valuable -> source comments
- **README-as-index** -- Describe scope, then point to where detail lives
- **"Why" matters** -- Explain rationale, not just "what"
- **Show don't tell** -- Concrete examples throughout
- **Keep it current** -- Stale docs corrupt the intent signal
- **Change precedence** -- When docs and code disagree and either fix is valid, fix docs before code
- **No redundancy** -- Say things once, in the right place
- **Plain text** -- Prefer ASCII, avoid decorative emoji

Good documentation serves all readers - humans and AI alike. Write it clearly once, and everyone benefits.
