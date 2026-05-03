---
name: test-driven-development
description: >-
  Codex runtime skill generated from canonical `skills/test-driven-development/SKILL.md`. Red-green-refactor cycle for writing tests before implementation code.
---

# test-driven-development (Codex Runtime Skill)

Canonical source: `skills/test-driven-development/SKILL.md`

This file is self-contained for Codex runtime. Shared behavior belongs
in the canonical source skill; regenerate this file after changing the
source.

## Codex Runtime Notes

- Prefer `AGENTS.md` for root guidance. Treat `CLAUDE.md` only as supplemental fallback when older Claude-specific text in the inlined body requires it.
- Use Codex-native tools and `.agents/skills/`; translate older Claude coordination wording in the body into explicit user requests, current tools, or durable artifacts when the workflow requires them.

## Classification

- Migration category: Generate as Codex runtime skill
- Rationale: Workflow or reference guidance is useful in Codex as a self-contained runtime skill.

## Inlined Skill Body

## Test-Driven Development

Write a failing test first, make it pass with minimal code, then refactor.

---

### Iron Law

NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.

Code written before its test must be deleted. Do not keep it as reference
or try to adapt it. Start fresh from the test.

---

### Purpose

- Force thinking about desired behavior before implementation
- Catch edge cases (nulls, types, boundaries) before production
- Prevent over-engineering by writing only what the test requires
- Build a regression safety net as a side effect of development

---

### When to Use

| Scenario | Use TDD |
|----------|---------|
| New feature | Yes |
| Bug fix | Yes -- failing test reproduces the bug |
| Refactoring | Yes -- tests prove behavior is preserved |
| Behavior change | Yes |
| Config-only change | No |
| Generated code | No |
| Throwaway prototype | No (with explicit acknowledgment) |

---

### The Cycle

#### RED: Write one failing test

- Test one behavior only. If the name contains "and", split it.
- Use a clear name that describes the behavior, not the implementation.
- Test real code, not mocks of the code under test.

| Good | Bad |
|------|-----|
| `test_returns_empty_list_when_no_events_match` | `test_filter` |
| `test_raises_on_invalid_date_range` | `test_error` |
| `test_upserts_existing_market_by_id` | `test_database` |

**Verify RED:** Run the test. It MUST fail. Confirm it fails for the
expected reason (missing function, wrong return value), not a typo or
import error.

#### GREEN: Write minimal code to pass

- Write the simplest code that makes the test pass. Nothing more.
- Do not add features, handle edge cases the test does not cover, or
  "improve" the design.

**Verify GREEN:** Run ALL tests. Every test must pass. Not just the new
one -- all of them.

#### REFACTOR: Clean up while green

- Remove duplication, improve names, extract helpers.
- Do NOT add new behavior. Tests must stay green throughout.
- If a refactoring breaks a test, undo it and try a smaller step.

#### Repeat

Move to the next behavior. One cycle per behavior.

---

### Verification Checklist

Before marking work complete:

- [ ] Every new function has at least one test
- [ ] Watched each test fail before implementing (RED)
- [ ] Each test failed for the expected reason
- [ ] Wrote minimal code to pass (GREEN)
- [ ] All tests pass (full suite, not just new tests)
- [ ] Tests use real code, not mocks of the thing under test
- [ ] Edge cases covered (nulls, empty collections, boundaries)

---

### Testing Anti-Patterns

**Never test mock behavior.** If a test validates that a mock returns
what you told it to return, it tests nothing. Test real behavior or
do not mock.

**Never add test-only methods to production code.** If a method exists
only for tests (like `destroy()` or `_reset()`), move it to test
utilities.

**Never mock without understanding dependencies.** Over-mocking removes
side effects the test depends on. Understand what a dependency does
before deciding to mock it.

**Watch for over-complex mocks:** If mock setup is longer than the test
logic, you are probably testing the mock, not the code.

---

### Common Rationalizations

| Excuse | Reality |
|--------|---------|
| Too simple to need a test | Simple code has edge cases; test is fast to write |
| I will write the test after | After never comes; behavior verified by implementation bias |
| I already tested manually | Manual tests do not persist or run in CI |
| Code is already written, just add test | Delete the code, write the test, rewrite the code |
| TDD is too slow | TDD is faster when you account for debugging time saved |
| Mocking is too hard | Difficulty mocking signals a design problem worth addressing |

---

### Red Flags (STOP -- delete code, start with test)

- Writing production code before a test exists
- Test passes immediately on first run (not a real test)
- Cannot explain why the test should fail
- Rationalizing "just this once" for skipping the test
- Keeping pre-TDD code "as reference"

---

### When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test it | Describe the behavior in words; that is the test name |
| Test is too complicated | Split into smaller behaviors; test each one |
| Must mock everything | Design problem -- refactor to reduce coupling |
| Huge setup required | Extract test fixtures; share setup across related tests |

---

### Guidelines

**Do:**
- One behavior per test, one cycle per behavior
- Name tests after behavior, not implementation
- Run the full test suite at every GREEN step
- Delete pre-TDD code and start from the test

**Don't:**
- Write production code without a failing test
- Keep code that was written before its test
- Add behavior during the REFACTOR step
- Mock the thing under test
