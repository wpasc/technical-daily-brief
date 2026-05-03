---
name: database-design
description: >-
  Schema design principles, index optimization, migration patterns, and
  performance tuning for relational databases.
  TRIGGER when: designing database schemas, optimizing queries, planning
  migrations, or selecting database engines.
  DO NOT TRIGGER when: writing application code that does not involve
  schema or query changes.
user-invocable: false
---

# Database Design

Schema architecture, index strategy, and migration patterns.

---

## Purpose

- Guide schema design from requirements to implementation
- Optimize index strategy for actual query patterns
- Enable zero-downtime migrations
- Inform database engine selection

---

## Schema Design

### Normalization

| Form | Rule | Violation Example |
|------|------|-------------------|
| 1NF | Atomic values, no repeating groups | Comma-separated tags in one column |
| 2NF | No partial dependencies on composite keys | Attribute depends on half the key |
| 3NF | No transitive dependencies | Non-key depends on another non-key |
| BCNF | Every determinant is a candidate key | Edge cases in 3NF |

Start at 3NF. Denormalize selectively only after measuring a performance
bottleneck, not speculatively.

### Denormalization Patterns

- **Redundant storage**: pre-computed totals, duplicated foreign key names
- **Materialized aggregates**: summary tables refreshed on schedule
- **Historical snapshots**: point-in-time copies for analytics

Maintain consistency via triggers, materialized views, or application-level
validation. Document every denormalization decision with performance
justification.

### Data Type Optimization

Right-size columns. Avoid VARCHAR(255) when VARCHAR(50) fits. Match types
to actual data ranges. Consider storage efficiency and index performance.

---

## Index Strategy

### Index Types

| Type | Use For | Notes |
|------|---------|-------|
| B-tree (default) | Equality, range, ORDER BY | O(log n) lookup |
| Hash | Exact match only | O(1) but no range support |
| Partial | Subset of rows | Reduces index size (e.g., only active users) |
| Covering | Include extra columns | Enables index-only scans |
| Functional | Transformed values | e.g., LOWER(email) for case-insensitive |
| GIN | Full-text, JSONB, arrays | PostgreSQL |
| GiST | Geometry, ranges | PostgreSQL |

### Composite Index Design

- Place most selective columns first (highest distinct/total ratio)
- Match composite order to query patterns:
  - Equality + Range: `(col_a, col_b)` for `WHERE a = ? AND b BETWEEN ? AND ?`
  - Equality + Sort: `(col_a, col_b DESC)` for `WHERE a = ? ORDER BY b DESC`
- One well-designed composite index often replaces multiple single-column indexes
- Monitor usage statistics; drop indexes with zero scans

---

## Migration Patterns

### Expand-Contract (Zero-Downtime)

1. **Expand**: Add new column/table as nullable with defaults. No locks,
   backward compatible.
2. **Migrate**: Backfill in batches (e.g., 5000 rows) to avoid lock
   contention. Implement dual-write in application.
3. **Transition**: Application reads from new structure; stops writing
   to old.
4. **Contract**: Drop old column/table after validation window.

### Backfill Strategy

Batch updates to avoid long-running locks:
```sql
UPDATE table SET new_col = transform(old_col)
WHERE id IN (
  SELECT id FROM table WHERE new_col IS NULL LIMIT 5000
);
```
Repeat in a loop. Track progress. Set rollback points.

### Rollback Rules

- Every up migration has a corresponding down migration
- Test down migrations in staging before deploying up
- For irreversible changes (data loss), take logical backups first
- Name files with timestamps: `20260101_000001_description.up.sql`

---

## Performance Optimization

### Reading EXPLAIN Plans

| Signal | Meaning | Action |
|--------|---------|--------|
| Seq Scan on large table | Missing index | Add appropriate index |
| Nested Loop with high rows | Inefficient join | Consider hash/merge join or add index |
| Buffers read >> hit | Working set exceeds memory | Partition or add cache layer |
| Index-only scan | Covering index working | No action needed |

### N+1 Query Detection

Symptom: one query per row in a loop (e.g., fetching profile per order).
Fix: JOIN or subquery for batch fetching, ORM eager loading
(`select_related`, `joinedload`), DataLoader pattern for GraphQL.

### Connection Pooling

Rule of thumb: pool size = 2 x CPU cores. For cloud SSDs, start at
2 x vCPUs and tune. Use PgBouncer for PostgreSQL, ProxySQL for MySQL.

### Read Replicas

Route SELECT queries to replicas; writes to primary. Account for
replication lag (<1s async). Check lag before reading critical data.

---

## Database Selection

| Criteria | PostgreSQL | MySQL | SQLite | DuckDB |
|----------|-----------|-------|--------|--------|
| Best for | Complex queries, JSONB | Web apps, read-heavy | Embedded, dev/test | Analytics, columnar |
| JSON | Excellent (JSONB + GIN) | Good | Minimal | Good |
| Max size | Multi-TB | Multi-TB | ~1TB single-writer | In-process analytics |
| License | Open source | Open source / commercial | Public domain | Open source |

**Default:** PostgreSQL for transactional, DuckDB for analytical.
SQLite for embedded/CLI. MySQL for existing ecosystem.

**NoSQL only when:** access patterns clearly demand document flexibility
(MongoDB), key-value speed (Redis), or serverless scale (DynamoDB).

---

## Guidelines

**Do:**
- Start at 3NF, denormalize only with measured justification
- Design indexes for actual query patterns, not speculative ones
- Use expand-contract for all production schema changes
- Batch backfills to avoid lock contention
- Monitor index usage and drop unused indexes

**Don't:**
- Add indexes speculatively (each index costs write performance)
- Run schema migrations without a tested rollback path
- Use VARCHAR(255) as a default for everything
- Skip EXPLAIN analysis for slow queries
