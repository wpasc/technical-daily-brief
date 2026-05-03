---
name: migration-strategy
description: >-
  Codex runtime skill generated from canonical `skills/migration-strategy/SKILL.md`. Patterns for zero-downtime system migrations including database schema evolution, service replacement, and infrastructure transitions.
---

# migration-strategy (Codex Runtime Skill)

Canonical source: `skills/migration-strategy/SKILL.md`

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

## Migration Strategy

Patterns for migrating databases, services, and infrastructure with
minimal downtime.

---

### Purpose

- Provide proven migration patterns with explicit tradeoffs
- Ensure every migration has a tested rollback path
- Minimize business impact through phased execution
- Prevent data loss through validation and reconciliation

---

### Database Migration Patterns

#### Expand-Contract (default for schema changes)

1. **Expand**: add new column/table as nullable with defaults (no locks)
2. **Dual-write**: application writes to both old and new structures
3. **Backfill**: batch migrate existing data (e.g., 5000 rows per batch)
4. **Transition**: application reads from new, stops writing to old
5. **Contract**: drop old structure after validation window

#### Parallel Schema

Run old and new schemas simultaneously. Route traffic with feature flags.
Compare outputs for consistency. Cut over when confidence is high.

#### Change Data Capture

Use CDC (Debezium, etc.) to stream changes from source to target in
real time. Preferred for large datasets where batch backfill would take
too long or require downtime.

---

### Service Migration Patterns

#### Strangler Fig

- Proxy intercepts all requests to legacy service
- Gradually replace individual endpoints with new service
- Monitor each replacement before proceeding to the next
- Retire legacy after all endpoints migrated

#### Parallel Run

- Execute both old and new services on the same traffic (shadow mode)
- Compare outputs for correctness
- Gradually shift real traffic based on comparison results
- Keep old service available for rollback

#### Canary Deployment

- Deploy new version to small percentage of users (e.g., 5%)
- Monitor error rates and latency vs baseline
- Increase traffic incrementally (5% -> 25% -> 50% -> 100%)
- Automated rollback if metrics degrade

---

### Rollback Strategies

| Scope | Method | Preparation |
|-------|--------|-------------|
| Schema | Reverse migration (down script) | Test down migration in staging first |
| Data | Point-in-time recovery from backup | Take logical backup before migration |
| Service | Traffic switch to previous version | Keep previous version running |
| Infrastructure | Revert IaC to previous commit | Version all infrastructure changes |

#### Rules

- Every migration has a tested rollback path before execution
- For irreversible changes (data loss), take backups first
- Keep rollback window short; if contract phase has run, rollback
  requires a new forward migration
- Test rollback in staging, not just the forward path

---

### Risk Assessment

| Category | Examples | Mitigation |
|----------|----------|------------|
| Data loss | Schema drop, failed transform | Backup before, validate after, batch with checkpoints |
| Downtime | Lock contention, failed cutover | Expand-contract, blue-green, feature flags |
| Integration | API contract break, schema mismatch | Parallel run, canary, contract testing |
| Performance | Query regression, missing indexes | Load test before cutover, gradual traffic shift |

---

### Validation and Reconciliation

After every migration phase, validate:

- **Row counts**: source vs target with threshold alerting
- **Checksums**: hash critical data subsets for integrity
- **Business logic**: aggregate queries on both systems must match
- **Delta detection**: query for missing or extra records
- **Correction**: automated idempotent fixes for detected deltas

---

### Feature Flags for Migrations

Use feature flags to control migration rollout:
- Hash-based user segmentation for gradual exposure
- Circuit breaker: automatic fallback to legacy when new system degrades
  (closed -> open -> half-open states)
- Separate flags for read path and write path

---

### Migration Checklist

**Pre-migration:**
- [ ] Plan reviewed and approved
- [ ] Rollback tested in staging
- [ ] Backups taken and verified
- [ ] Monitoring and alerting in place
- [ ] Communication sent to stakeholders
- [ ] Feature flags configured

**During:**
- [ ] Execute phases in order
- [ ] Validate after each phase
- [ ] Monitor error rates and latency
- [ ] Log deviations from plan

**Post-migration:**
- [ ] Full validation pass (counts, checksums, business logic)
- [ ] Health checks passing for 72 hours
- [ ] Old resources cleaned up (contract phase)
- [ ] Documentation updated
- [ ] Retrospective scheduled

---

### Guidelines

**Do:**
- Default to expand-contract for database schema changes
- Test rollback in staging before executing in production
- Validate data at every phase boundary
- Use feature flags for gradual rollout

**Don't:**
- Run migrations without a tested rollback path
- Skip the validation phase to save time
- Drop old structures before the validation window closes
- Attempt big-bang migrations when phased alternatives exist
