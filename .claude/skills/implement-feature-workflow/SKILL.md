---
name: implement-feature-workflow
description: >-
  Use when building a substantial multi-file feature with unclear requirements,
  integration points, or enough risk to need a scout, plan, test, and review
  loop; do not use for quick fixes, docs-only changes, explanations, reviews,
  simple refactors, single-file edits, or tasks covered by narrower skills.
  Principles and exit criteria only; mechanics delegate to native subagents
  and sibling skills.
---

# Implement Feature Workflow

Sequence a substantial feature through five phases. Each phase has an exit
criterion; do not advance past a phase you cannot exit honestly.

## Phases

1. **Scout** -- map the territory with read-only subagents: project type,
   conventions, integration points, prior art for similar features.
   Exit: you can name the files you will touch and the patterns to follow.

2. **Clarify** -- state assumptions, ask at most 3 focused questions
   (prefer options over open-ended), and confirm scope back to the user.
   Exit: testable acceptance criteria the user has confirmed, plus explicit
   out-of-scope items. If the user says "just do it", record the defaults
   you chose as assumptions.

3. **Plan** -- ordered steps, each paired with its own verification check.
   Decompose parallelizable work per the dispatch skill; keep sequential
   work in the main context.
   Exit: every acceptance criterion maps to at least one step.

4. **Implement** -- test-first per test-driven-development. Follow existing
   patterns exactly; no refactoring of unrelated code; nothing beyond the
   spec. Run the affected tests before calling the phase done.
   Exit: new tests pass and existing tests still pass.

5. **Review** -- review the diff against the spec per code-review. Fix and
   re-review; if convergence fails after about 3 cycles or the
   implementation has diverged from the spec, stop and report rather than
   force it through.
   Exit: review passes with fresh verification evidence
   (verification-before-completion).

## Rules

- Never auto-commit; present the verified diff and let the user commit.
- Surface tradeoffs and simpler alternatives during Clarify, not after
  Review.
- If a later phase invalidates an earlier phase's output (wrong assumption,
  missing integration point), return to that phase explicitly -- do not
  patch around it.
