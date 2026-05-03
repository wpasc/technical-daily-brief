---
name: systematic-debugging
description: >-
  Codex runtime skill generated from canonical `skills/systematic-debugging/SKILL.md`. Root-cause-first debugging methodology for any bug, test failure, or unexpected behavior.
---

# systematic-debugging (Codex Runtime Skill)

Canonical source: `skills/systematic-debugging/SKILL.md`

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

## Systematic Debugging

Four-phase methodology that finds root causes before attempting fixes.

---

### Iron Law

NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

If Phase 1 investigation is incomplete, no fixes may be proposed.

---

### Purpose

- Prevent guess-and-check thrashing that wastes hours
- Find the actual root cause, not just the symptom
- Achieve 95% first-time fix rate with near-zero regressions
- Enforce discipline under time pressure (when it matters most)

---

### When to Use

| Scenario | Use This |
|----------|----------|
| Test failure | Yes -- always |
| Bug report | Yes -- always |
| Deployment issue | Yes -- especially multi-component |
| Performance problem | Yes |
| "Quick fix" seems obvious | Yes -- especially then |
| Root cause already confirmed with evidence | No |

---

### Phase 1: Root Cause Investigation

1. **Read error messages carefully.** Full stack traces, line numbers,
   error codes. Do not skip warnings.
2. **Reproduce consistently.** Know the exact steps. If not reproducible,
   gather more data before proceeding.
3. **Check recent changes.** git diff, recent commits, new dependencies,
   config changes, environment differences.
4. **Trace data flow backward.** For errors deep in the stack, trace
   backward through the call chain to find where the bad value originated.
   The symptom is rarely at the source.
5. **Measure before attributing.** Do not name a subsystem as the cause
   until you have measured it changing behavior. Plausible stories are not
   diagnoses. Pick the right measurement for the failure class (see the
   table below). This rule applies throughout the rest of the phase: every
   claim about *what* is failing must come with the measurement that proves
   it. Special case: if you are about to blame a subsystem you have not
   touched, the bar is even higher -- prove it changed behavior, do not
   assume it did.
6. **Multi-component systems.** At each component boundary, log what data
   enters and exits. Verify environment and config propagation at each
   layer. Run diagnostics once to find WHERE it breaks, then investigate
   that specific component.

---

### What to Measure for Common Failure Classes

Vague measurement is worse than no rule. For each common failure class, the
right measurement is concrete and tool-specific:

| Failure class | What to measure | Tool |
|---|---|---|
| Memory leak | anon RSS over time, separated from file-backed cache | cgroup `memory.stat` (anon vs file vs kernel); NOT `docker stats memory.current`, which sums all three and includes reclaimable page cache |
| Slow query | actual rows scanned, plan, index usage | `EXPLAIN ANALYZE`; not `time` alone |
| Slow request | per-call wall time on the suspect path | `time.perf_counter` deltas, sampling profilers (`py-spy top --pid`, `perf top -p`) |
| Process death | exit code, stderr, kernel oom-kill record | `journalctl -u <service>`, `dmesg \| grep -i "killed process"`, `systemctl status` |
| Container restart | resource limits vs actual usage; oom-kill records | `docker inspect` for limits; cgroup `memory.stat` for actual; `dmesg` for kills |
| High CPU | which function, which thread | sampling profiler attached to the live process |

A measurement that does not distinguish between competing hypotheses is not
a measurement. If you cannot say what reading would falsify your hypothesis,
you have not designed the measurement yet.

---

### Phase 2: Pattern Analysis

1. Find working examples in the codebase similar to what is broken.
2. Read reference implementations completely (every line, not skimming).
3. List every difference between working and broken code.
4. Identify all dependencies: components, config, environment, assumptions.

---

### Phase 3: Hypothesis Testing

1. Form a single, specific hypothesis: "X is the root cause because Y."
2. Test with the smallest possible change. One variable at a time.
3. **If the first fix does not work:** before the second workaround attempt,
   search the tool's official docs and GitHub issues. If you are hitting
   repeated failures with a third-party tool, the problem is likely a known
   limitation, not a tuning issue. Spending 30 seconds on research beats
   spending an hour guessing at parameters.
4. If it worked, move to Phase 4. If not, form a new hypothesis.
5. When uncertain, say "I don't understand X" -- do not guess.

---

### Phase 4: Implementation

1. Create a failing test case (simplest possible reproduction).
2. Implement a single fix addressing the root cause from Phase 1.
3. Make ONE change at a time. No bundled improvements.
4. Verify: test passes, no other tests broken, issue resolved.

**If 2+ fixes to the same code path:** STOP. Before patching another
symptom, explicitly ask: "is the premise of this code correct?" Repeated
bugs in the same place almost always mean the approach is wrong, not that
the implementation needs another patch. Escalate to a design change, not
another fix. A useful test: can you state the premise of the code in one
sentence, and does the premise still make sense given everything you know?

**If 3+ fix attempts fail:** This signals an architectural problem, not a
bug. Question fundamentals before attempting fix #4:
- Is the pattern sound or maintained through inertia?
- Should the architecture be refactored instead of patched?

---

### Root Cause Tracing

When the error appears deep in the stack:

1. Observe the symptom (where the error surfaces).
2. Find the immediate cause (what code directly produces it).
3. Ask "what called this?" and trace upward with the values passed.
4. Keep tracing until you find the original trigger.
5. Fix at the source, not at the symptom.

After fixing, add validation at multiple layers (defense-in-depth):
- **Entry point:** reject invalid input at API boundary
- **Business logic:** validate data makes sense for the operation
- **Environment guards:** prevent dangerous operations in wrong context
- **Debug instrumentation:** capture context for future forensics

---

### Red Flags (STOP -- return to Phase 1)

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- "One more fix attempt" after 2+ failures
- Attributing a failure to a subsystem you have not changed without
  measuring it first
- A "plausible story" presented as a diagnosis without supporting
  measurement
- Citing this skill ("per systematic-debugging") while skipping the
  measurement step

---

### Common Rationalizations

| Excuse | Reality |
|--------|---------|
| Issue is simple, skip the process | Simple issues have root causes too; process is fast for simple bugs |
| Emergency, no time | Systematic debugging is FASTER than thrashing |
| Just try this first | First fix sets the pattern; start right |
| Multiple fixes at once saves time | Cannot isolate what worked; causes new bugs |
| I see the problem | Seeing symptoms is not understanding root cause |
| Reference is too long, I will adapt | Partial understanding guarantees bugs |

---

### Guidelines

**Do:**
- Complete Phase 1 before proposing any fix
- Trace backward through the call chain, not forward from a guess
- Add defense-in-depth validation after fixing
- Count fix attempts -- 3+ means architectural problem

**Don't:**
- Skip to Phase 4 because the fix seems obvious
- Bundle unrelated improvements with a bug fix
- Guess at root causes without evidence
- Ignore "I don't understand" signals
