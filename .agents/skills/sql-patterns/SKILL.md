---
name: sql-patterns
description: >-
  Codex runtime skill generated from canonical `skills/sql-patterns/SKILL.md`. Day-to-day SQL query optimization, anti-patterns, ORM integration, and multi-dialect guidance.
---

# sql-patterns (Codex Runtime Skill)

Canonical source: `skills/sql-patterns/SKILL.md`

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

## SQL Patterns

Query optimization, anti-patterns, and ORM guidance for daily database work.

---

### Purpose

- Optimize queries using EXPLAIN analysis, not guesswork
- Prevent common SQL anti-patterns
- Guide ORM usage that produces efficient queries
- Handle dialect differences across database engines

---

### Query Optimization Workflow

1. Identify slow query (logs, APM, or observation)
2. Run EXPLAIN ANALYZE
3. Find the costliest node
4. Check: missing index? Bad join order? Estimation vs actual row mismatch?
5. Apply targeted fix
6. Re-run EXPLAIN to confirm improvement

#### EXPLAIN Signals

| Signal | Meaning | Fix |
|--------|---------|-----|
| Seq Scan on large table | Missing index | Add index on filter/join columns |
| Nested Loop with high rows | Inefficient join | Add index or restructure query |
| Rows estimated >> actual | Stale statistics | Run ANALYZE |
| Rows actual >> estimated | Bad plan choice | Update statistics, consider hints |

---

### Common Query Patterns

#### Top-N Per Group

```sql
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY group_col ORDER BY rank_col DESC
  ) AS rn FROM table
) t WHERE rn <= N;
```

#### Running Totals

```sql
SELECT *, SUM(amount) OVER (
  ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
) AS running_total FROM table;
```

#### UPSERT

- PostgreSQL: `INSERT ... ON CONFLICT (key) DO UPDATE SET ...`
- MySQL: `INSERT ... ON DUPLICATE KEY UPDATE ...`
- SQLite: `INSERT OR REPLACE INTO ...`

#### Gap Detection

```sql
SELECT a.id + 1 AS gap_start
FROM table a LEFT JOIN table b ON a.id + 1 = b.id
WHERE b.id IS NULL;
```

---

### Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `SELECT *` | Reads unnecessary columns, breaks covering indexes | List explicit columns |
| `WHERE YEAR(date) = 2026` | Prevents index use (not sargable) | `WHERE date >= '2026-01-01' AND date < '2027-01-01'` |
| Correlated subquery in SELECT | Runs once per row | Rewrite as JOIN |
| `NOT IN (subquery)` with NULLs | NULL comparison breaks logic | Use `NOT EXISTS` instead |
| N+1 queries | One query per row in a loop | JOIN, eager loading, or batch fetch |
| No connection pooling | Connection overhead per request | Use PgBouncer, ProxySQL, or ORM pool |
| Unbounded queries | Full table scan on large tables | Always paginate (LIMIT + OFFSET or keyset) |
| Money as FLOAT | Rounding errors | Use DECIMAL(19,4) or integer cents |
| String concatenation in queries | SQL injection | Use parameterized queries |
| Missing FK indexes | Slow JOINs and cascade deletes | Add index on every foreign key column |

---

### ORM Integration

#### SQLAlchemy (Python)

- Use `relationship()` with `lazy="selectin"` or `lazy="joined"` to
  prevent N+1
- Use `select_related` patterns: `session.execute(select(Model).options(joinedload(Model.related)))`
- Escape hatch: `session.execute(text("raw SQL"))` for complex queries
- Migrations: Alembic with `--autogenerate` for schema diffs

#### General ORM Rules

- Understand what SQL your ORM generates (enable query logging)
- Use eager loading for known relationships
- Use raw SQL for complex analytics (CTEs, window functions)
- Never let the ORM generate unbounded queries

---

### Dialect Differences

| Feature | PostgreSQL | MySQL | SQLite | DuckDB |
|---------|-----------|-------|--------|--------|
| UPSERT | ON CONFLICT | ON DUPLICATE KEY | INSERT OR REPLACE | INSERT OR REPLACE |
| Boolean | native | TINYINT(1) | INTEGER (0/1) | native |
| Auto-increment | SERIAL / GENERATED | AUTO_INCREMENT | INTEGER PRIMARY KEY | GENERATED |
| JSON | JSONB (indexable) | JSON | text | JSON |
| Arrays | native | not supported | not supported | native |
| Window functions | full | 8.0+ | 3.25+ | full |
| LIMIT syntax | LIMIT N OFFSET M | LIMIT M, N or LIMIT N OFFSET M | LIMIT N OFFSET M | LIMIT N OFFSET M |

---

### Data Integrity

#### Constraint Strategy

- Primary keys on all tables (surrogate preferred)
- Foreign keys with explicit ON DELETE behavior
- UNIQUE constraints for business uniqueness
- CHECK constraints for value ranges and enums
- NOT NULL as default; nullable only when justified

#### Transaction Isolation

| Level | Tradeoff | Use When |
|-------|----------|----------|
| READ COMMITTED | Default, good balance | Most applications |
| REPEATABLE READ | No phantom reads, some overhead | Financial calculations |
| SERIALIZABLE | Strongest, highest overhead | Critical consistency requirements |

#### Deadlock Prevention

- Acquire locks in consistent order across transactions
- Keep transactions short
- Use advisory locks for application-level coordination
- Retry with exponential backoff on deadlock detection

---

### Guidelines

**Do:**
- Start with EXPLAIN ANALYZE for any slow query
- Use parameterized queries everywhere (no string concatenation)
- Add indexes based on measured query patterns
- Enable ORM query logging to catch N+1 issues

**Don't:**
- Use `SELECT *` in application queries
- Store money as floating point
- Write dialect-specific SQL without noting the assumption
- Skip connection pooling in production
