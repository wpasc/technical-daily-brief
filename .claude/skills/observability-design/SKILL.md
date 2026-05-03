---
name: observability-design
description: >-
  SLI/SLO frameworks, golden signals monitoring, alerting design, and
  dashboard principles for production systems.
  TRIGGER when: designing monitoring, defining SLOs, creating alerts or
  dashboards, designing health checks or freshness probes, implementing
  metrics endpoints, or investigating observability gaps.
  DO NOT TRIGGER when: debugging a specific issue (use systematic-debugging)
  or writing application code without observability concerns.
user-invocable: false
---

# Observability Design

Frameworks for monitoring, alerting, and dashboards.

---

## Purpose

- Define measurable reliability targets (SLIs/SLOs)
- Monitor the four golden signals consistently
- Design alerts that are actionable, not noisy
- Build dashboards that answer questions at a glance

---

## SLI/SLO Framework

| Concept | Definition | Example |
|---------|-----------|---------|
| SLI | Measurable health signal | P99 latency, error rate |
| SLO | Reliability target | 99.9% of requests < 500ms |
| SLA | Customer-facing commitment | Contractual uptime guarantee |
| Error budget | Allowed unreliability | 0.1% = 43 min/month downtime |

### Burn Rate Alerting

Alert when error budget is consumed faster than sustainable:
- **Fast burn** (14.4x): fires in 1 hour, pages immediately
- **Slow burn** (1x over 30 days): warns before budget exhaustion
- Multi-window alerts reduce false positives (short window for speed,
  long window for confirmation)

---

## Golden Signals

| Signal | What to Measure | Alert When |
|--------|----------------|------------|
| Latency | P50, P95, P99 response time | P99 exceeds SLO threshold |
| Traffic | Requests/sec, active sessions | Sudden drop (may indicate upstream failure) |
| Errors | 4xx/5xx rate, error budget burn | Error rate exceeds baseline or budget burning fast |
| Saturation | CPU, memory, disk, connection pools | Approaching capacity (80%+ sustained) |

### Complementary Frameworks

- **RED** (Rate, Errors, Duration): request-driven services
- **USE** (Utilization, Saturation, Errors): infrastructure resources
- Use golden signals as the primary framework; RED/USE for drill-down

---

## Three Pillars

### Metrics

- Golden signals + RED/USE + business metrics
- Use histograms for latency (not averages)
- Manage cardinality: avoid unbounded label values
- Tiered retention: high-resolution recent, downsampled historical

### Logs

- Structured JSON with consistent field naming
- Correlation IDs across services for distributed tracing
- Log levels: DEBUG (dev only), INFO (state changes), WARN (degraded),
  ERROR (failures), FATAL (unrecoverable)
- Sample high-volume logs to control cost

### Traces

- Distributed tracing for end-to-end request flow
- Sampling strategy: head-based (simple, predictable cost), tail-based
  (captures errors and slow requests), adaptive (adjusts to traffic)
- Add meaningful span metadata: service, operation, status, duration

---

## Dashboard Design

### Hierarchy

1. **Overview**: system health at a glance (all golden signals)
2. **Service**: per-service metrics with SLO status
3. **Component**: database, cache, queue, dependency health
4. **Instance**: individual host/container for investigation

### Principles

- Max 7 panels per view (cognitive load limit)
- 80% operational metrics, 20% exploratory
- Reference lines for SLO targets and capacity thresholds
- Default time ranges: 4h for incidents, 7d for trends
- Color: red (critical), amber (warning), green (healthy)
- Drill-down links from overview to service to component

---

## Alert Design

### Severity

| Level | Criteria | Response |
|-------|----------|----------|
| Critical | Service down, SLO burn rate high | Page on-call immediately |
| Warning | Approaching thresholds, degraded | Notify team, investigate soon |
| Info | Deployment complete, capacity alert | No immediate action needed |

### Quality Rules

- Every alert must have a clear, documented response action
- Prefer precision (few false positives) over recall
- Use hysteresis: different thresholds for firing vs resolution
- Suppress dependent alerts during known outages
- Group related alerts into single notifications
- Test alerts against historical data before enabling

### Runbook Structure

For each alert, document:
1. What the alert means and why it fires
2. Impact assessment (user-facing vs internal)
3. Investigation steps (ordered, with time estimates)
4. Resolution actions (common fixes, escalation paths)
5. Post-incident follow-up

---

## Health Endpoint Shape

A health endpoint that can OOM the container it monitors is worse than no
health endpoint -- it manufactures the outage it would have detected.
Health endpoints in any project must be O(1) in wall time and memory,
regardless of dataset size.

### Three Probe Types (Do Not Conflate)

| Probe | Question | Cost | DB access |
|---|---|---|---|
| **Liveness** (`/healthz`) | Is the process alive and the event loop responding? | Trivial | None |
| **Readiness** | Is this instance safe to send traffic to? | Lightweight | Optional, lightweight |
| **Freshness** (`/healthz/ingestion`-style) | Is the data behind this service current? | O(1) | Bookkeeping/meta table only, NEVER the dataset itself |

A liveness probe that touches the database is wrong: a slow query will mark
a healthy process as down and trigger a needless restart. A freshness probe
that scans the dataset is wrong: it grows in cost as the dataset grows, and
under concurrent calls it can OOM-kill the container it monitors.

### Rules

- Liveness must take no DB dependency. In FastAPI/Flask/etc., the route
  function takes no `Depends(...)` arguments that touch storage. Just
  `return {"status": "ok"}`.
- Freshness must query a small bookkeeping table (e.g., `ingestion_runs`,
  one row per run). The right shape is
  `SELECT MAX(completed_at) FROM ingestion_runs WHERE error IS NULL`.
  Cost is O(rows-in-meta), which is hundreds of KB even after years.
- The freshness probe MUST use a separate dependency injection path from
  the analytical endpoints. If both go through the same `get_connection()`
  factory, the probe inherits all that factory's setup cost (view
  registration, ATTACH statements, glob walks). Add a dedicated
  `get_meta_connection()` that opens only what the probe needs.

### Pre-Write Trigger Question

Before adding or modifying any health endpoint, ask: "what does this
endpoint cost as the dataset grows 100x? what does it cost when 3 of these
run at once?" If either answer is anything other than "the same as it costs
at 1x and 1-way concurrency", redesign before merging.

---

## Active Failure Detection

The strongest alerting framework in the world is undermined by a service
that fails silently. Silent failure is the default for unmonitored code.
Active failure detection is observability applied to data correctness, and
it has two layers.

### Layer 1: Process Layer

Every scheduled job (systemd unit, cron, k8s job, Airflow task) emits an
exit code. That exit code must be monitored independently of the job's
log output. A job that fails in the systemd journal but nowhere else is
equivalent to a job that does not run.

Concrete patterns:
- **Prometheus + node_exporter**: alert on
  `node_systemd_unit_state{name="<service>",state="failed"} == 1`.
  Best fit when a Prometheus stack already exists.
- **systemd `OnFailure=`**: directive in the unit pointing at a
  notification service.
- **Wrapper script**: bash wrapper that pipes the exit status to a
  webhook (Slack, Pushover, ntfy, equivalent).

### Layer 2: Data Layer

Process-level monitoring catches "the job died." It does not catch "the
job ran successfully and produced wrong data." Every ingestion or
transform must emit data-shape metrics that fire on regression:

- **Row-count delta per run**: alert if rows ingested drops by >20%
  run-over-run, or below an expected floor for the data source. Catches
  truncated runs, rate-limited runs, upstream API degradation.
- **Null-rate per key column**: alert if null rate increases sharply on
  a column that should be populated. Catches silent schema changes (e.g.,
  upstream renames a field and the transform starts returning None).
- **Distribution sanity**: mean and stddev on numeric columns; alert if
  they move dramatically run-over-run. Catches pricing-format changes,
  unit changes, and type drift.
- **Cardinality checks** on key fields: alert on unexpected drops or
  spikes in distinct counts.

### The "Discovered by Accident" Anti-Pattern

If a failure is discovered by EDA, by grepping logs, by user report, or
by a developer happening to look at metrics for an unrelated reason --
the alert that should have caught it does not exist. **EDA is not a
corruption-detection mechanism.** EDA is the thing that discovers
corruption you already had.

When a "discovered by accident" failure occurs, the response is not just
"fix the bug." It is also "add the alert that would have caught it." Two
work items, not one.

### Example: Prometheus Alert Rule for Row-Count Delta

```yaml
- alert: IngestionRowCountDropped
  expr: |
    rate(ingestion_rows_processed_total[1h])
      < 0.8 * rate(ingestion_rows_processed_total[1h] offset 1h)
  for: 10m
  labels:
    severity: critical
  annotations:
    summary: "Ingestion run produced <80% of last run's row count"
    runbook: "ops/runbooks/ingestion-row-count-drop.md"
```

---

## Cost Optimization

- Tiered metric retention by importance
- Intelligent log sampling for high-volume services
- Tail-based trace sampling (captures interesting traces, skips routine)
- Monitor and cap high-cardinality metrics

---

## Guidelines

**Do:**
- Define SLOs before building dashboards or alerts
- Alert on symptoms (latency, errors), not causes (CPU)
- Include runbooks for every alert
- Review alert quality quarterly (noise ratio, false positive rate)

**Don't:**
- Alert on every metric (leads to alert fatigue)
- Use averages for latency (use percentiles)
- Build dashboards without a clear audience and question they answer
- Skip cost planning for observability infrastructure
