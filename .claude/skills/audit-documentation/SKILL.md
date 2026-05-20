---
name: audit-documentation
description: >-
  Audit a repository's documentation against documentation-standards principles
  and check that docs and code cohere. Walks the placement stack (root README,
  major-folder READMEs, AI guidance, docs/, ADRs), scores quality against
  declared standards, then extracts claims from docs and verifies them against
  the code, flagging drift signals without silently picking a winner.
  TRIGGER when: user asks to audit documentation, check doc quality, verify
  docs match code, find documentation gaps, or evaluate documentation
  freshness in a repo. Also TRIGGER when the audit-repository orchestrator
  invokes the DOC vector.
  DO NOT TRIGGER when: writing or editing documentation (use
  documentation-standards as the reference instead), debugging a specific
  bug (use systematic-debugging), or running a full repo health audit (use
  audit-repository which composes this skill).
---

# Audit Documentation

Walks a repository's documentation surface, scores it against the standards
declared in `documentation-standards`, and checks whether the documentation
and the code cohere. Produces a structured report with findings classified
by type (ALIGNED / GAP / DRIFT / STALE) and a precedence-ordered fix list.

Standalone-invocable when only the documentation audit is wanted. The
`audit-repository` orchestrator also calls this skill as its DOC vector.

---

## Principles Source

This skill audits against `documentation-standards`. Read that skill from
the harness runtime surface (or from canonical `skills/documentation-
standards/SKILL.md` if working in the source library) before scoring. Do
not restate or paraphrase its principles here -- this skill is the auditor,
not the standard.

Key principles this audit applies (full text in documentation-standards):

- Zero-context: docs assume general programming knowledge but no project
  history.
- Declared intent: docs are authoritative on intent; code is observable
  reality.
- Authority hierarchy: explicit project docs > AI guidance > inline
  comments > code structure.
- Self-evident navigation: hierarchy itself should make the next step
  obvious.
- README placement stack: global -> major-folder -> minor-when-valuable ->
  source comments.
- README-as-index: describe scope, then point to where detail lives.
- Change precedence when docs and code disagree: docs > comments >
  structure > code.

---

## Governing Rules

- **No inferred intent.** Score only against explicit statements in docs.
  If a guideline is generic or unstated, flag it as a GAP, not a violation.
- **Drift requires a human call.** When docs and code disagree, do not
  silently pick a winner -- flag the drift and propose the precedence-
  ordered fix path (docs first, code last).
- **Fail closed on ambiguity.** When intent is unclear or contradictory,
  halt that scope, record the ambiguity, and propose a clarification
  question. Continue with independent scopes.
- **Substance over style.** Decorative emoji, ASCII preference, etc. are
  notes, not findings. Missing zero-context guarantees, broken
  README-as-index navigation, and drift between declared behavior and
  code are findings.

---

## Workflow

### Phase 0: Documentation Inventory

Walk the documentation placement stack and inventory what exists:

1. **Root README** (`README.md`) -- presence, length, structure.
2. **AI guidance files** -- `AGENTS.md` for Codex and `CLAUDE.md` for Claude
   as harness-specific roots; `guidance.local.md`, `.cursor/rules/`, or other
   harness-specific guidance files as supplemental in-repo guidance.
3. **Major-folder READMEs** -- READMEs at the first level of significant
   subdirectories (e.g. `src/`, `scripts/`, `services/<name>/`,
   `packages/<name>/`).
4. **Minor-folder READMEs** -- READMEs anywhere deeper in the tree.
5. **`/docs` directory** -- presence, structure, and any obvious
   organization (ADRs, runbooks, design docs).
6. **ADRs** -- whether and where Architecture Decision Records live.
7. **Inline doc comments** -- spot-check a handful of source files for
   module-level docstrings or comment intent.

Output: a flat inventory mapping each artifact to its path. Do NOT yet
score quality.

### Phase 1: Documentation Quality Audit

For each artifact in the inventory, score against the principles above.
Findings types:

- **GAP** -- expected artifact missing (no root README, major folder
  with no README and confusing structure, missing harness-specific AI
  guidance roots -- `AGENTS.md` for Codex, `CLAUDE.md` for Claude -- in
  a repo with AI-assisted workflows, etc.).
- **STALE** -- documentation references files, commands, or behaviors
  that no longer exist (paths that grep returns no hits for, retired
  commands, removed flags).
- **GAP-QUALITY** -- documentation exists but violates a principle
  (vague descriptions, assumed context, ephemeral references, missing
  rationale on non-obvious decisions, README that is not an index).

For each finding, record:

| Field | Content |
|-------|---------|
| `id` | DOC-<n> |
| `severity` | CRITICAL / WARNING / NOTE |
| `type` | GAP / STALE / GAP-QUALITY |
| `path` | File path (and line if applicable) |
| `principle` | Which documentation-standards principle is violated |
| `evidence` | Direct quote or specific observation |
| `precedence_fix` | Recommended fix following docs > comments > structure > code |

**Severity guidance:**

- CRITICAL -- missing root README, AI guidance that's actively
  misleading, doc claims about authentication or data handling that
  conflict with the code.
- WARNING -- README-as-index broken, major folder undocumented in a
  way that confuses navigation, stale references to retired tooling.
- NOTE -- documentation could be clearer; principle adherence
  imperfect but not actively misleading.

### Phase 2: Convergence Audit (docs <-> code)

Extract testable claims from the documentation, then verify each against
the code. This is the original "convergence" check -- does what the
documentation says match what the code does?

**Claim categories to extract:**

- Entry points (commands, main scripts, slash commands).
- Module purposes (what does `src/X/` claim to do?).
- Architectural claims (this service uses pattern Y; data flows through
  Z).
- Configuration claims (this env var controls X; this file is at Y).
- Behavior claims (running command X produces output Y; flag --foo
  does Z).

**Verification:**

- For path claims: does the path exist?
- For command claims: do the commands resolve (script exists, binary
  installed referenced, flag actually accepted)?
- For module-purpose claims: does the actual code in the module match
  the stated purpose?
- For architectural claims: is the claimed pattern visible in the code?

**Drift findings:**

| Field | Content |
|-------|---------|
| `id` | DRIFT-<n> |
| `severity` | CRITICAL / WARNING / NOTE |
| `path_docs` | Where the claim is documented |
| `path_code` | Where the code diverges |
| `claim` | What the docs say |
| `reality` | What the code does |
| `precedence_fix` | Per change-precedence: which side should be reconciled, with rationale |

**Critical rule:** Drift findings must NOT propose silently editing code
to match docs (or vice versa). Apply the documentation-standards change
precedence: prefer doc updates when intent should change; prefer code
changes only when the documented intent is clearly authoritative and the
code has drifted. When unclear, flag for human resolution.

### Phase 3: Report

Produce a consolidated report.

```
## DOCUMENTATION AUDIT: [target]

**Scope:** [repo / subtree audited]
**Inventory size:** [N artifacts]
**Verdict:** ALIGNED / DRIFT / MISALIGNED / INCOMPLETE

### Summary

[2-3 sentences: overall state of documentation, most significant
drift or gap, whether the repo's documentation can be relied on as
declared intent.]

### Inventory

| Artifact | Path | Status |
|----------|------|--------|
| Root README | README.md | present, 180 lines |
| AGENTS.md | AGENTS.md | present |
| ...

### Findings

#### Critical (BLOCK)
[DOC-* and DRIFT-* findings at CRITICAL severity]

#### Warnings
[Findings at WARNING severity]

#### Notes
[Findings at NOTE severity]

### Precedence-Ordered Fix List

[Findings grouped by recommended fix type, in change-precedence order:]

1. **Doc fixes** (preferred -- cheapest, least risky)
   - [list]
2. **Comment additions**
   - [list]
3. **Structural changes** (renames, moves)
   - [list]
4. **Code changes** (last resort)
   - [list]

### Ambiguities Requiring Clarification

[Where the audit halted due to unresolvable conflict; one
clarification question per ambiguity.]
```

---

## Verdict Calibration

- **ALIGNED** -- documentation exists, follows standards, and
  cohere with code. No findings above NOTE severity. Rare in older
  or evolving repos.
- **DRIFT** -- documentation generally aligned with code, but
  specific claims have drifted. Most common verdict for active
  repos.
- **MISALIGNED** -- documentation significantly disagrees with
  code, or large GAPs in coverage. Repo's declared intent cannot
  be trusted without doc work.
- **INCOMPLETE** -- audit halted on ambiguity; verdict pending
  human clarification.

When in doubt between DRIFT and MISALIGNED, count CRITICAL
findings: 0 -> DRIFT; 1+ -> MISALIGNED.

---

## Anti-Patterns for the Auditor

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Proposing code fixes to make code match docs without flagging intent | Drift requires a human call; silent reconciliation hides the divergence |
| Flagging cosmetic issues (emoji, line length) as findings | Notes, not findings; substance over style |
| Inferring intent the docs don't actually state | No inferred intent rule -- score against explicit statements only |
| Padding the inventory by counting every leaf folder's missing README | Placement stack is tiered; minor folders need a README only when it adds value |
| Verdict drift toward MISALIGNED for sparse docs without GAP framing | Missing docs are GAPs; only score MISALIGNED when existing docs contradict reality |
| Skipping the precedence_fix field | Findings without a fix path are not actionable |

---

## When to Run

- New to a repo, want to know whether the documentation reflects what's
  actually there.
- Before a release or large refactor, to surface drift accumulated
  since the last audit.
- After a significant change to architecture, to verify the docs caught
  up.
- Periodically (quarterly) on long-lived repos to detect slow drift.

---

## Composition

The `audit-repository` orchestrator invokes this skill as its DOC vector.
When called standalone, the report stands alone. When called from
`audit-repository`, the orchestrator consolidates the report with the
CODE vector's findings and applies cross-vector promotion.
