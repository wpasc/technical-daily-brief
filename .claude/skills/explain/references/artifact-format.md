# Auditable Artifact Format

One markdown file per question: `/tmp/explain/<slug>/artifact.md`. It has two jobs:

1. Every load-bearing statement is independently checkable by a skeptic.
2. Structured sections feed the output channels mechanically.

Use sections in this order. Omit a section only when the question shape does not need it.

## Header

Question (verbatim), shape, tier, domains researched, explicitly out of scope.

## Claims

| ID | Claim | Evidence | Status |
|---|---|---|---|

One row per atomic, falsifiable statement. Evidence is `path:line` or URL; multiple pointers are
allowed. Status is `unverified`, `verified`, or `imprecise (note)`. Write claims a hostile reviewer
can check in under two minutes each. If a statement needs no evidence, it is probably not
load-bearing; cut it.

## Entities & Relations

Feeds the diagram channel. Near-D2 lines, one per node or edge, each tagged with claim IDs:

```text
api_server: Flask app behind nginx (C1)
api_server -> charge_worker: enqueues ChargeJob via Redis (C3, C4)
billing: { charge_worker; retry_queue }  # container when ownership matters
```

This section must be mechanically translatable to D2 or Mermaid. The renderer adds layout and
styling, not edges.

## Trace

Feeds the worked-example channel for mechanism and lifecycle shapes.

Use one concrete scenario with pinned, realistic values. Numbered steps; each step names actor,
action, important value or state change, and claim refs:

```text
Scenario: patron 8841 joins creator 312's $5 tier
1. Browser -> POST /api/memberships {tier_id: 977} (C2) -- row inserted, status=pending
2. ...
```

If values are illustrative rather than sourced, say so once at the top of the section.

## Decision Delta

Decision shape only.

| Aspect | Before (claim refs) | After (claim refs) |
|---|---|---|

Both columns cite claims. After claims cite the proposal or diff itself as evidence.

## Open Questions

Everything believed but unproven, plus claims demoted by verification. Never silently drop these.

## Verification Log

| Round | Verdicts (counts: V / W / U / I) | Fixes made |
|---|---|---|
