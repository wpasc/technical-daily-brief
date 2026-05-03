---
name: anti-patterns
description: >-
  Codex runtime skill generated from canonical `skills/anti-patterns/SKILL.md`. Common code anti-patterns to avoid -- configuration, data access, over-engineering, error handling, testing, performance, and unbounded-memory operations on storage and bulk I/O.
---

# anti-patterns (Codex Runtime Skill)

Canonical source: `skills/anti-patterns/SKILL.md`

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

## Anti-Patterns to Avoid

Common mistakes that lead to technical debt, complexity, and maintenance headaches. Load this skill during code review, architectural decisions, or significant refactoring.

---

### Philosophy

#### Simplicity Over Cleverness

The best code is:

**GOOD:** Simple, Boring, Obvious
**BAD:** Clever, Novel, Terse

Code is read 10x more than it's written. Optimize for reading.

---

### Configuration Anti-Patterns

#### Scattered Configuration
Centralize configuration into a single source of truth. Do not scatter across environment variables, config files, and hardcoded values.

#### Hardcoded or Committed Secrets
Use environment variables (12-Factor App standard). Never commit secrets to version control. For production, use secret management services (AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets).

#### Unvalidated Configuration
Validate configuration at startup with clear errors. Use tools like Pydantic BaseSettings to fail fast when required config is missing.

---

### Data Access Anti-Patterns

#### Direct Database Queries Everywhere
Use the repository pattern to centralize data access. This improves testability, reduces duplication, and allows database swaps.

#### Fat Models (Active Record Anti-Pattern)
Keep models as data structures. Separate query logic (repositories) from business logic (services).

#### N+1 Query Problem
Use eager loading (joinedload, prefetch) instead of querying in loops.

---

### Over-Engineering Anti-Patterns

#### Premature Abstraction
Wait until you have 3+ use cases before abstracting. Start simple, add structure when patterns emerge.

#### Unused Configurability
Add configuration options when you need them, not "just in case."

#### Abstraction for One Implementation
Do not create interfaces with only one implementation. Wait for the second implementation to justify the abstraction.

---

### Error Handling Anti-Patterns

#### Silent Failures
Never catch exceptions without handling them. Log and re-raise, or handle explicitly with specific recovery logic.

#### Catch-All Exception Handling
Catch specific exceptions, not `Exception`. Let unexpected exceptions propagate so bugs are visible.

---

### Testing Anti-Patterns

#### Testing Implementation Instead of Behavior
Test outcomes and behavior, not internal method calls. Tests that verify mock interactions break on every refactor.

#### Low-Value Tests
Test logic, not syntax. Skip tests for trivial getters/setters, framework internals, and third-party library behavior.

---

### Code Organization Anti-Patterns

#### God Objects
Split classes with too many responsibilities into focused components (repositories, services, handlers).

#### Circular Dependencies
Use dependency injection or events to break circular module dependencies.

---

### API Design Anti-Patterns

#### Unvalidated Input
Use Pydantic or validation schemas for all API input. Never accept raw dictionaries.

#### Exposing Internal Models
Use response schemas to control what is returned. Never expose database models directly.

---

### Unbounded Memory Anti-Patterns

These patterns have the same root cause: memory usage that grows with dataset
size instead of being bounded by batch or chunk size. They apply symmetrically
to reads AND writes. Match on shape, not on specific APIs.

#### Read-Modify-Write on Growing Data

**Wrong:** Re-read the entire file to "append" to it.
```python
# Memory: O(file_size), grows every run
existing = pq.read_table(path)
combined = pa.concat_tables([existing, new_rows])
pq.write_table(combined, path)
```
**Right:** Use a streaming writer.
```python
# Memory: O(batch_size), fixed regardless of file size
writer = pq.ParquetWriter(path, schema=schema)
writer.write(new_batch)  # one row group at a time
writer.close()
```

#### One-Shot API in a Loop Over Unbounded Input

**Wrong:** Calling a whole-dataset API inside a loop.
```python
# Each call rewrites the entire file
for batch in stream:
    pq.write_table(pa.Table.from_pylist(batch), path)  # creates a new file per batch
```
**Right:** Long-lived streaming handle, one close at the end.
```python
writer = pq.ParquetWriter(path, schema=schema)
for batch in stream:
    writer.write(pa.Table.from_pylist(batch))
writer.close()
```

#### Loading Entire Result Sets Into Memory

**Wrong:** `cursor.fetchall()`, `list(query.all())`, `pd.read_sql(query)` on unbounded queries.

**Right:** `cursor.fetchmany(batch_size)`, `LIMIT/OFFSET` or keyset pagination, `iter_batches()`.

#### In-Memory Accumulators That Grow Without Bound

**Wrong:** Appending to a list or dict for the full run, then flushing once.

**Right:** Flush when the accumulator reaches a threshold; discard after flush.

#### The Smell Test

Before writing any code that touches storage, ask: "as the dataset grows
100x, does this function's memory usage grow at all?" If yes, it is wrong.
The correct answer is always: "memory bounded by batch size or row-group
size, not by total dataset size."

---

### Performance Anti-Patterns

#### Premature Optimization
Measure first, optimize later. Do not add caching, pooling, or complexity before profiling shows a bottleneck.

#### Synchronous I/O in Loops
Use concurrent/async patterns for parallel I/O instead of sequential loops.

---

### Documentation Anti-Patterns

For comprehensive documentation anti-patterns, see the documentation-standards skill.

Key documentation anti-patterns: vague descriptions, assumed context, references to ephemeral knowledge, outdated documentation, over-technical explanations without context.

---

### Summary

**Key Principles:**
- **Simplicity > Cleverness**
- **Abstraction when needed, not before**
- **Centralize configuration**
- **Repository pattern for data access**
- **Test behavior, not implementation**
- **Validate input explicitly**
- **Keep documentation current**
- **Measure before optimizing**

The best code is boring, obvious, and easy to delete.
