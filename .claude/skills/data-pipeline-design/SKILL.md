---
name: data-pipeline-design
description: >-
  Architecture decision frameworks and patterns for data pipelines, modeling,
  orchestration, and data quality.
  TRIGGER when: designing data pipelines, choosing between batch and streaming,
  selecting data modeling approaches, or implementing data quality checks.
  DO NOT TRIGGER when: writing application code that does not involve data
  pipeline architecture.
user-invocable: false
---

# Data Pipeline Design

Decision frameworks for building scalable, reliable data systems.

---

## Purpose

- Provide architecture decision frameworks with explicit tradeoffs
- Guide data modeling choices (star schema, SCD types, Data Vault)
- Establish orchestration and data quality patterns
- Prevent over-engineering by matching architecture to actual requirements

---

## Architecture Decision Frameworks

### Batch vs Streaming

| Criteria | Batch | Streaming |
|----------|-------|-----------|
| Latency | Hours to days | Seconds to minutes |
| Data volume | Large historical | Continuous events |
| Processing | Complex transforms, ML | Aggregations, filtering |
| Cost | Lower | Higher infrastructure |
| Error handling | Easy reprocessing | Requires careful design |

**Decision:** Need real-time insight? Streaming. Otherwise batch.
Batch + volume >1TB daily? Spark. Otherwise dbt + warehouse.

### Lambda vs Kappa

- **Lambda**: Dual codebases (batch + stream). Higher maintenance but
  supports complex batch transforms and ML training. Use when existing
  batch infrastructure or mixed workloads.
- **Kappa**: Single stream codebase. Lower maintenance, event-sourced.
  All processing via replay from immutable log (Kafka/Kinesis). Use for
  pure event-driven systems starting fresh.

### Warehouse vs Lakehouse

- **Warehouse** (Snowflake, BigQuery): BI/SQL analytics, schema-on-write,
  mature BI ecosystem, higher cost
- **Lakehouse** (Delta Lake, Iceberg): ML + unstructured data,
  schema-on-read, lower cost, growing tooling

---

## Medallion Architecture

| Layer | Purpose | Pattern |
|-------|---------|---------|
| Bronze | Raw ingestion | Append-only, schema evolution, no transforms |
| Silver | Validated data | Deduplicated, standardized, type-corrected |
| Gold | Business-ready | Aggregated, star schema, optimized for queries |

---

## Data Modeling Patterns

### Star vs Snowflake vs One Big Table

| Pattern | Pros | Cons | Use When |
|---------|------|------|----------|
| Star schema | Fast queries, simple JOINs | Higher storage | Standard BI analytics |
| Snowflake schema | Less storage, less ETL | More JOINs | Storage-constrained, many dimensions |
| One Big Table | Simplest queries | Stale risk, update anomalies | Columnar storage, read-heavy |

### Slowly Changing Dimensions

| Type | Behavior | Use When |
|------|----------|----------|
| 0 | Never update | Reference data (country codes) |
| 1 | Overwrite | No history needed |
| 2 | New row with effective dates | Full history required (most common) |
| 3 | Previous value column | Only one level of history |

Type 2 implementation: hash-based change detection, `is_current` flag,
`effective_from` / `effective_to` date columns.

### Data Vault

- **Hubs**: business keys only (immutable identifiers)
- **Satellites**: descriptive attributes with full history + hash_diff
- **Links**: relationships between hubs

Use for: audit-heavy environments, parallel loading, frequently changing
business rules.

---

## Pipeline Orchestration

### Batch Patterns

- **Idempotent tasks**: same execution date always produces same output.
  Use MERGE/UPSERT for loads.
- **Backfill support**: date-specific partitioning, catchup enabled,
  max active runs limited.
- **Dependency management**: sensor tasks for cross-DAG dependencies,
  task groups for parallel extract stages.

### Stream Patterns

- **Watermarks for late data**: define acceptable lateness window;
  append mode only for complete windows.
- **Exactly-once semantics**: idempotent producer + transactional
  consumer + MERGE on write.
- **Partition design**: 24-48 partitions for 10K-100K msg/s,
  3x replication, 7-day retention.

### Change Data Capture

Use CDC (Debezium for PostgreSQL) to stream database changes as events.
Processes insert/update/delete operations with schema tracking.
Preferred over polling for real-time pipelines.

---

## Data Quality

### Testing Layers

| Layer | What to Test | Example |
|-------|-------------|---------|
| Schema | Column presence and types | columns_to_match_set |
| Completeness | Null rates | not_null on required fields |
| Uniqueness | Primary key integrity | unique on ID columns |
| Range | Value boundaries | accepted_range for amounts |
| Freshness | Data recency | max timestamp within 24h of now |
| Cross-table | Referential integrity | relationships between tables |

### Error Handling

- **Dead Letter Queue**: capture failed records with error metadata and
  retry count. Process DLQ separately.
- **Circuit Breaker**: fail fast when downstream is unhealthy. States:
  Closed (normal) -> Open (failing, reject requests) -> Half-Open (testing recovery).
- **Idempotent writes**: deduplicate by batch_id for streaming-to-database.

### Data Contracts

Define schemas as versioned YAML with type, required, and breaking_change
flags. Track deprecation timelines. Ensure backward compatibility.

---

## Guidelines

**Do:**
- Start with batch; add streaming only when latency requirements demand it
- Make every pipeline task idempotent
- Test data quality at each medallion layer boundary
- Use hash-based change detection for SCD Type 2
- Document first-run vs steady-state behavior for new pipelines

**Don't:**
- Choose streaming because it sounds modern
- Skip the Bronze layer (raw data is your recovery mechanism)
- Assume data quality from upstream sources
- Build without backfill support
- Use a one-shot serialization API (`write_table`, `to_csv`, `dumps`) in a
  loop over the same logical output -- use the streaming primitive instead
  (see `anti-patterns` skill, "Unbounded Memory Anti-Patterns" section)
- Re-read a growing file to "append" to it -- this is the same bug whether
  the format is Parquet, JSON, or CSV
