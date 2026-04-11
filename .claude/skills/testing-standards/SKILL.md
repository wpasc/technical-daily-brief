---
name: testing-standards
description: Principles for writing tests that catch bugs and survive refactoring - behavioral testing, mocking boundaries, test isolation, and coverage guidelines
user-invocable: false
---
<!-- repo-types: api-service, cli-tool, library, frontend-app, full-stack, monorepo -->

# Testing Standards

Principles for writing tests that catch bugs and survive refactoring.

---

## Core Principles

### 1. Test Behavior, Not Implementation

Tests should verify *what* code does, not *how* it does it. If you refactor internals without changing behavior, tests should still pass.

**Good - tests behavior:**
```python
def test_user_repository_returns_user_when_found(db_session):
    db_session.add(User(id="123", name="Alice"))

    result = user_repo.get_by_id("123")

    assert result.name == "Alice"
```

**Bad - tests implementation:**
```python
def test_user_repository_calls_sqlalchemy_query():
    mock_db = Mock()
    repo = UserRepository(mock_db)
    repo.get_by_id("123")

    mock_db.query.assert_called_once()  # Breaks on any refactor
```

### 2. Mock Only at System Boundaries

Mock external dependencies. Use real code for everything else.

**Mock these:**
- External APIs and third-party services
- Network calls, filesystem, time/dates
- Email/SMS/payment gateways

**Don't mock these:**
- Your own classes and functions
- Your own database (use a test database with rollback)
- Simple utilities and data structures

Over-mocking is a smell. If you're mocking your own code, you're probably testing implementation.

### 3. Tests Must Be Independent

Each test should:
- Create its own test data
- Not depend on other tests running first
- Not share mutable state
- Produce the same result regardless of run order

### 4. Tests Must Be Deterministic

No flaky tests. If a test sometimes passes and sometimes fails, fix it or delete it. Common causes:
- Time-dependent logic
- Random data without seeds
- Race conditions
- External service dependencies

### 5. Include Integration Tests

Unit tests alone miss integration bugs. Your test suite needs both:

**Unit tests:** Fast, isolated, mock external boundaries. Run on every change.

**Integration tests:** Test components working together. Use real database (with transaction rollback). Slower but catch real bugs.

Structure your tests to support both:
```
tests/
  unit/           # Fast, isolated
  integration/    # Components together
```

---

## Guidelines (Not Rules)

### Test Names Should Be Descriptive

A reader should understand what's being tested without reading the implementation.

**Clear:**
```python
def test_create_user_raises_error_for_duplicate_email()
def test_expired_token_returns_unauthorized()
```

**Unclear:**
```python
def test_user()
def test_error_case()
```

### Arrange-Act-Assert Is Usually Helpful

Most tests read better with clear setup, action, and verification phases. But don't force it if it doesn't fit.

### Keep Test Setup DRY But Explicit

Repeated setup code makes tests hard to maintain. Fixtures, factories, and helper functions are all valid approaches. Choose based on readability, not dogma.

---

## What to Test

**Focus on:**
- Business logic and domain rules
- Error handling and edge cases
- Integration points (where components meet)
- Anything that has broken before

**Skip:**
- Trivial getters/setters
- Framework internals
- Third-party library behavior
- Auto-generated code

---

## Coverage Targets

- 80%+ test coverage for new modules
- 90%+ test coverage for critical paths
- Coverage is a guide, not a goal -- 100% coverage with bad tests is worse than 80% with good ones

---

## Summary

- **Test behavior** - not implementation details
- **Mock boundaries** - external services only
- **Stay independent** - no test ordering dependencies
- **Stay deterministic** - no flaky tests
- **Include integration tests** - unit tests alone aren't enough
