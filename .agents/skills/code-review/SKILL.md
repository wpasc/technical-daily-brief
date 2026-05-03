---
name: code-review
description: >-
  Codex runtime skill generated from canonical `skills/code-review/SKILL.md`. Structured code review protocol with severity levels, test coverage requirements, security checklist, and language-specific considerations
---

# code-review (Codex Runtime Skill)

Canonical source: `skills/code-review/SKILL.md`

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

- Keep the source skill's reporting contract. In Codex, present findings first with file references, then assumptions or residual risks.

## Inlined Skill Body

## Code Review

Structured code review protocol for pull requests.

---

### Purpose

Perform structured code reviews that:

- **Enforce project standards** - Apply local AI rules and conventions first
- **Apply industry best practices** - Catch common issues even without project rules
- **Verify test coverage** - Ensure functional changes have corresponding tests
- **Maintain code quality** - Identify maintainability and security concerns

---

### Review Process

#### 1. Context Gathering

First, understand the change:
- Read the PR description/commit messages
- Identify the type of change (feature, bugfix, refactor, docs, tests, config)
- Note the scope (files changed, lines added/removed)

#### 2. Project Standards (Load First)

Check for and apply local project rules:
- Read AI guidance in harness priority order: `AGENTS.md` for Codex,
  `CLAUDE.md` for Claude, and any referenced guidance files
- If multiple guidance files exist, treat the current harness's file as
  primary and use the other as supplemental context when referenced
- Apply any project-specific code style, architecture, or review requirements
- These take precedence over general best practices

#### 3. Review Checklist

##### Functional Correctness
- Does the code do what the PR description claims?
- Are edge cases handled appropriately?
- Are error conditions handled (not silently swallowed)?

##### Test Coverage (REQUIRED for Functional Changes)
- Do functional changes have corresponding test updates or new tests?
- Do tests verify behavior, not implementation details?
- Are edge cases and error paths tested?
- If tests are missing, flag as blocking issue

##### Code Quality
- Is the code readable and self-documenting?
- Are names (variables, functions, classes) descriptive?
- Is complexity appropriate (no over-engineering)?
- Is there unnecessary duplication?

##### Security (Critical)
- No hardcoded secrets, API keys, or credentials
- User input validated and sanitized where applicable
- No SQL injection, XSS, or command injection vulnerabilities
- Sensitive data not logged or exposed in errors

##### Architecture
- Does the change fit the existing patterns in the codebase?
- Are dependencies appropriate (not introducing unnecessary ones)?
- Is the change in the right location/layer?

##### Documentation
- Are public APIs documented?
- Are complex algorithms or non-obvious logic explained?
- Is README/docs updated if behavior changes?

---

### Severity Levels

#### Blocking (Must Fix)
- **Missing tests for functional changes**
- **Security vulnerabilities** - Hardcoded secrets, injection risks, auth bypasses
- **Broken functionality** - Code doesn't do what PR claims
- **Silent failures** - Errors caught and ignored without handling
- **Data loss risks** - Destructive operations without safeguards

#### Non-Blocking (Should Consider)
- Code clarity improvements
- Performance optimizations (unless critical path)
- Additional edge case handling
- Documentation improvements

#### Nitpicks (Informational Only)
- Style preferences not in project style guide
- Alternative approaches that aren't clearly better
- Naming suggestions that are subjective

---

### Output Format

```markdown
### Summary
[1-2 sentences: overall assessment and recommendation]

### Blocking Issues (Must Fix)
[List issues that must be resolved before merge]

### Suggestions (Should Consider)
[List improvements that would strengthen the PR]

### Nitpicks (Optional)
[Minor style or preference items, clearly marked as non-blocking]

### Questions
[Clarifying questions for the author if intent is unclear]

### Recommendation
- [ ] APPROVE - Ready to merge
- [ ] REQUEST CHANGES - Has blocking issues
- [ ] COMMENT - Needs discussion or clarification
```

---

### Security Red Flags

- `password`, `secret`, `api_key` as string literals
- `eval()`, `exec()`, or dynamic code execution
- SQL string concatenation instead of parameterized queries
- User input passed directly to shell commands
- Disabled SSL/TLS verification
- Overly permissive CORS settings

### Reliability Red Flags

- Any read-modify-write on a growing file or unbounded data container
  (re-read + concat + rewrite is O(dataset) memory)
- One-shot serialization APIs (`write_table`, `to_csv`, `json.dumps`) inside
  a loop over the same logical output
- `fetchall()` or `list(query.all())` on an unbounded query
- Health endpoint that queries the dataset it monitors (must be O(1))
- Scheduled job with no exit-code alerting or row-count delta monitoring
- In-memory accumulator that grows without bound before flushing

---

### Test Coverage Requirements

**Functional changes require test changes.**

What counts as functional change: new features, bug fixes, behavioral changes, new error handling paths.

What doesn't require new tests: documentation-only changes, config/environment changes, refactoring with existing coverage, dependency version bumps.

---

### Success Criteria

A good code review:
- **Finds real issues** - Not just style nitpicks
- **Is actionable** - Author knows exactly what to fix
- **Respects author** - Professional tone, questions before accusations
- **Prioritizes correctly** - Blocking vs suggestions vs nitpicks
- **Verifies tests** - Functional changes have test coverage
- **Applies context** - Uses project-specific rules when available

**Valid outcomes include approving with no comments** - not every PR needs feedback.
