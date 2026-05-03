---
name: verification-before-completion
description: >-
  Require fresh verification evidence before claiming any task is
  complete, fixed, or passing.
  TRIGGER when: about to claim a task is done, tests pass, a build
  succeeds, or a bug is fixed -- before making the claim.
  DO NOT TRIGGER when: actively investigating or mid-implementation
  (not yet at the completion claim stage).
user-invocable: false
---

# Verification Before Completion

No completion claims without fresh verification evidence.

---

## Iron Law

NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.

If the verification command has not been run in the current context,
the claim is invalid.

---

## Purpose

- Prevent false completion claims that waste downstream time
- Ensure every "done" is backed by actual evidence
- Catch regressions before they propagate

---

## The Gate Function

Before ANY completion claim, execute these steps in order:

1. **Identify** -- what command proves the claim?
2. **Run** -- execute the complete command freshly (not from cache or memory)
3. **Read** -- examine full output, exit code, failure counts
4. **Verify** -- does the output actually confirm the claim?
5. **State** -- make the claim WITH the evidence

Skipping any step is not a shortcut -- it is a false claim.

---

## Common Failures

| Claim | Required Evidence | NOT Sufficient |
|-------|-------------------|----------------|
| "Tests pass" | Test command output showing 0 failures | Previous run, "should pass", partial suite |
| "Build succeeds" | Build command output with exit 0 | "Linter passed", "compiled without errors" |
| "Bug is fixed" | Failing test now passes + no regressions | "Code looks correct", manual spot check |
| "Linter is clean" | Linter output with 0 warnings/errors | "I fixed the issues" |
| "Requirements met" | Checklist verified against plan, item by item | "Tests pass" (tests may not cover all requirements) |
| "Agent completed task" | Verified changes in VCS diff | Trusting agent's self-report |
| "Ready for production / ready to ship / ready to deploy" | The production-readiness checklist (`checklists/production-readiness-checklist.md`) executed end-to-end, with a recorded answer for every item AND concrete evidence (file paths, command outputs, metric names, test fixture sizes) for memory-bound storage code, healthcheck shape, alerting wiring, scheduled-job exit-code monitoring, and data-health checks | "Tests pass", "code looks correct", "I added a healthcheck", "the deploy worked once", "looks production ready" |
| "Memory leak fixed" | Anon RSS measured over time via cgroup `memory.stat` showing flat baseline; NOT `docker stats memory.current` (which includes reclaimable page cache) | "Memory looks lower in `docker stats`", "the cache was the problem" |
| "Performance regression fixed" | Profiler output (`py-spy`, `perf`, EXPLAIN ANALYZE) before and after | "Feels faster", "the obvious thing was slow" |

---

## Red Flags (STOP -- verify before continuing)

- Modal language: "should work", "probably passes", "seems correct"
- Satisfaction before verification: "Great!", "Done!", "Perfect"
- About to commit or push without running tests
- Trusting a subagent's self-reported success
- Relying on partial verification ("linter passed" for "build succeeds")
- Thinking "just this once"
- Fatigue or time pressure tempting shortcuts

---

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "Should work now" | "Should" is not evidence |
| "I'm confident" | Confidence is not verification |
| "Just this once" | One exception creates a pattern |
| "Linter passed" | Linter is not tests is not build |
| "Agent said it succeeded" | Verify the actual changes |
| "Partial check is enough" | Partial verification is not verification |

---

## Guidelines

**Do:**
- Run the full verification command, not a subset
- Include evidence (output, counts, exit code) with every claim
- Re-verify after any change, even "trivial" ones
- Verify subagent work independently

**Don't:**
- Claim completion based on code inspection alone
- Trust cached or remembered test results
- Use different words to avoid the rule ("looks good" = "done")
- Skip verification under time pressure
