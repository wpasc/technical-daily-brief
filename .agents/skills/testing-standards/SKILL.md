---
name: testing-standards
description: >-
  Codex runtime skill generated from canonical `skills/testing-standards/SKILL.md`. Principles for writing tests that catch bugs and survive refactoring -- behavioral testing, mocking boundaries, test isolation, coverage targets, and realistic-scale fixtures for bulk-I/O and storage code.
---

# testing-standards (Codex Runtime Skill)

Canonical source: `skills/testing-standards/SKILL.md`

This file is self-contained for Codex runtime. Shared behavior belongs
in the canonical source skill; regenerate this file after changing the
source.

## Codex Runtime Notes

- Prefer `AGENTS.md` for root guidance. Treat `CLAUDE.md` only as supplemental fallback when older Claude-specific text in the inlined body requires it.
- Use Codex-native tools and `.agents/skills/`; translate older Claude coordination wording in the body into explicit user requests, current tools, or durable artifacts when the workflow requires them.

## Classification

- Migration category: Generate as Codex runtime skill + reinforce in AGENTS.md
- Rationale: Still valuable as an explicit skill, but the core rule set also belongs in always-on Codex guidance.

## Inlined Skill Body

## Testing Standards

Principles for writing tests that catch bugs and survive refactoring.

---

### Core Principles

#### 1. Test Behavior, Not Implementation

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

#### 2. Mock Only at System Boundaries

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

#### 3. Tests Must Be Independent

Each test should:
- Create its own test data
- Not depend on other tests running first
- Not share mutable state
- Produce the same result regardless of run order

#### 4. Tests Must Be Deterministic

No flaky tests. If a test sometimes passes and sometimes fails, fix it or delete it. Common causes:
- Time-dependent logic
- Random data without seeds
- Race conditions
- External service dependencies

#### 5. Include Integration Tests

Unit tests alone miss integration bugs. Your test suite needs both:

**Unit tests:** Fast, isolated, mock external boundaries. Run on every change.

**Integration tests:** Test components working together. Use real database (with transaction rollback). Slower but catch real bugs.

Structure your tests to support both:
```
tests/
  unit/           # Fast, isolated
  integration/    # Components together
```

#### 6. Realistic-Scale Tests for Bulk-I/O Code

Unit tests on 3-row fixtures miss quadratic-memory bugs. Any code that
writes to a columnar format, manages partitioned files, handles bulk I/O,
or operates on input that may be unbounded in principle must have at least
one test at production-shape scale.

**Minimum fixture sizes:**
- Storage / Parquet / data lake writes: 10,000+ rows per fixture
- Stream processing tests: 100x the buffer/chunk/batch boundary
- Network-backed reads: enough data to fill one full response page

**Memory-bound assertions:** Storage tests must assert that peak memory
during the operation does NOT scale with total row count. The assertion
is: "this function's memory is bounded by batch size, not by dataset size."

Example (pyarrow / Python):
```python
import resource
def peak_rss_kb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

def test_writer_memory_bounded():
    before = peak_rss_kb()
    writer.write_all(generate_rows(25_000))
    after = peak_rss_kb()
    # 50 MB headroom; 25K rows should not cost proportionally more
    assert after - before < 50_000  # KB
```

**Pre-test discovery ritual:** Before writing the first test for bulk-I/O
code, enumerate the size thresholds the code will encounter: row count,
file size, rows-per-flush, partition boundaries. The test suite must
include a fixture at or above each threshold. If you do not know the
thresholds, read the implementation first.

**Partition file count is a correctness property:** Any partition with
more than ~100 files indicates a broken writer or missing compaction.
Tests for partition writers must assert exact output file counts per run.

---

### Guidelines (Not Rules)

#### Test Names Should Be Descriptive

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

#### Arrange-Act-Assert Is Usually Helpful

Most tests read better with clear setup, action, and verification phases. But don't force it if it doesn't fit.

#### Keep Test Setup DRY But Explicit

Repeated setup code makes tests hard to maintain. Fixtures, factories, and helper functions are all valid approaches. Choose based on readability, not dogma.

---

### What to Test

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

### Coverage Targets

- 80%+ test coverage for new modules
- 90%+ test coverage for critical paths
- Coverage is a guide, not a goal -- 100% coverage with bad tests is worse than 80% with good ones

---

### Summary

- **Test behavior** - not implementation details
- **Mock boundaries** - external services only
- **Stay independent** - no test ordering dependencies
- **Stay deterministic** - no flaky tests
- **Include integration tests** - unit tests alone aren't enough
