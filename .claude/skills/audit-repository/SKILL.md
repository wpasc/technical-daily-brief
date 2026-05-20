---
name: audit-repository
description: >-
  Multi-vector repository health audit. Throw at any repo to investigate
  whether docs and code cohere and whether the codebase holds up against
  established standards. Lean orchestrator: parallel workers per vector
  (documentation, code quality), cross-vector synthesis, verdict report.
  Validation over modification -- the auditor reports; humans or separate
  workflows fix.
  TRIGGER when: user asks to audit a repository, check repo health, run
  a convergence audit, verify a repo against standards, or audit a new
  codebase for alignment between documentation and implementation.
  DO NOT TRIGGER when: user wants adversarial code review (use red-team),
  reviewing a specific PR (use code-review), debugging a bug (use
  systematic-debugging), or auditing only documentation (use
  audit-documentation directly).
---

# Audit Repository

Lean orchestrator that fans out documentation and code-quality auditors
against a repository and consolidates their findings. Mirrors the
multi-vector pattern from `red-team`, but with a constructive framing:
the goal is to validate the repo's coherence and standards adherence,
not to attack it.

This skill descends from the retired `repository-convergence-auditor`
prompt and preserves its principles (validation over modification,
no-inferred-intent, change threshold, ambiguity protocol, change
precedence). It drops the file-based agent-handoff machinery and the
interactive-fix phase, both of which were not load-bearing in practice.

---

## Philosophy

**Coherence is the headline.** A repo is well-formed when its docs and
code agree on what the project is, and when the code holds up against
the standards the project (or its source library) declares. The auditor
makes coherence and adherence visible -- it does not modify the repo.

These principles govern every phase:

1. **Validation over modification.** Observe and classify; do not fix.
   Reporting that no changes are required is a first-class outcome.

2. **No inferred intent.** Score only against explicitly stated intent
   (docs, AI guidance, declared standards). If intent is unstated, that
   is a GAP, not a failure of the code.

3. **Authority hierarchy.** Explicit project documentation > AI guidance
   files > inline comments > code structure. Lower authority never
   silently overrides higher.

4. **Fail closed on ambiguity.** When intent is unclear or
   contradictory, halt that scope, record the ambiguity, propose a
   clarification question. Continue with independent scopes.

5. **Change threshold.** A finding only warrants attention if leaving
   it unchanged would materially harm comprehension, maintainability,
   correctness, or architectural coherence. Discard cosmetic and
   speculative items.

6. **Change precedence.** When proposing fixes, prefer: documentation
   updates -> comment additions -> structural changes -> code changes.

7. **Substance over ceremony.** Whole-repo systemic patterns, not
   line-level nits. The auditor is a tool for understanding repo
   health; cosmetic findings dilute the signal.

---

## Vectors

| Code | Vector | What It Audits | Composes With |
|------|--------|----------------|---------------|
| DOC | Documentation | Doc quality vs declared standards + docs/code convergence | audit-documentation, documentation-standards |
| CODE | Code Quality | Whole-repo adherence to declared engineering standards | code-review, anti-patterns, testing-standards |

Default scope is both vectors. If the user explicitly limits
("just docs", "DOC only"), run that vector alone and report
partial coverage.

---

## Workflow

### Phase 0: Target Acquisition

Determine scope and vectors:

**Scope options:**

- Whole repository (default if no scope specified).
- Specific subtree ("audit src/api/").
- A target repo other than the current working directory (caller
  passes a path).

**Vector selection:**

- Default to both DOC and CODE.
- "just docs" / "DOC only" -> DOC alone.
- "just code" / "CODE only" -> CODE alone.

### Phase 1: Reconnaissance

The orchestrator (main agent) performs minimal recon:

1. Read root README, top-level structure, and AI guidance in harness
   priority order (`AGENTS.md` for Codex, `CLAUDE.md` for Claude, then
   referenced guidance files).
2. Identify the tech stack, primary language(s), framework(s), and
   apparent project type.
3. Note declared standards: any `standards/` directory imported,
   `documentation-standards`-style references, project-specific
   conventions called out in AI guidance.
4. Note what the repo *claims to be*. This is the canonical intent
   that workers compare reality against. Do NOT yet evaluate
   correctness.

**Do NOT do deep analysis here.** The orchestrator stays lean.

### Phase 2: Parallel Vectors

Start one worker per selected vector. Run in parallel using the
current harness's subagent or parallel-execution mechanism. Each
worker receives:

1. The shared constructive-audit preamble (below).
2. Vector-specific instructions.
3. The recon summary from Phase 1.
4. The target scope.

#### Shared Preamble (include in every worker prompt)

```
You are a constructive auditor. Your job is to surface whether this
repository holds up against declared standards and whether its parts
cohere. Findings should be specific, evidenced, and actionable -- but
the goal is to inform, not to attack.

GUIDING PRINCIPLES:

- Validation over modification. Observe and classify; do not fix.
- No inferred intent. Score only against explicitly stated standards
  and declared intent. Unstated expectations produce GAPs, not
  failures.
- Authority hierarchy: explicit project docs > AI guidance > inline
  comments > code structure.
- Change threshold: only surface findings whose presence materially
  harms comprehension, maintainability, correctness, or architectural
  coherence. Discard cosmetic and speculative items.
- Substance over ceremony: report whole-repo systemic patterns, not
  line-level nits. Aim for <15 substantive findings per vector on a
  repo of normal size. If you have more, you are probably reporting
  nits.

DO NOT:
- Propose silent reconciliation when docs and code disagree -- flag
  the drift and apply change precedence (docs first).
- Soften findings with "might" or "could potentially"; state observed
  conditions as facts with evidence.
- Pad the report with style preferences (emoji, whitespace,
  formatting).

DO:
- Cite file paths (and line numbers where helpful).
- Trace each finding to a declared standard, principle, or stated
  intent. If you cannot trace it, discard it.
- Apply change precedence when proposing fixes: documentation -> comments
  -> structure -> code.

OUTPUT FORMAT per finding:
- ID: [VECTOR]-[number] (e.g., DOC-1, CODE-3)
- Severity: CRITICAL / WARNING / NOTE
- File: path:line (when applicable)
- Finding: one-sentence summary
- Evidence: the specific observation
- Standard: which declared standard or principle this traces to
- Precedence fix: recommended fix following docs > comments > structure > code
```

#### Worker: DOC (Documentation Vector)

Include in prompt:

```
Apply the audit-documentation skill from the current harness runtime
surface, or from canonical `skills/audit-documentation/SKILL.md` if
working in the source library. Follow its full Phase 0 (inventory),
Phase 1 (quality audit), Phase 2 (convergence audit), and Phase 3
(report) workflow.

Return the structured findings list (DOC-* and DRIFT-*) plus the
verdict, formatted per the audit-documentation report template.

Do not invoke audit-documentation as a separate sub-agent -- read its
body as your methodology and execute the workflow yourself.
```

#### Worker: CODE (Code Quality Vector)

This is the lighter-built vector and needs the most framing
discipline. Without a strong preamble, repurposing PR-scope skills at
whole-repo scope will produce a cosmetic-finding deluge.

Include in prompt:

```
You are auditing this REPO AS A WHOLE against declared engineering
standards. This is NOT a PR review and NOT an adversarial red team.
Your output should help a maintainer understand systemic code-quality
state, not nit individual lines.

REFRAMING -- read carefully:

PR-scope skills (code-review, anti-patterns, testing-standards) you
will draw from were written to review CHANGES. You are applying them
to a STATE. Translate accordingly:
- code-review's severity tiers (Blocking/Suggestion/Nitpick) become
  CRITICAL/WARNING/NOTE applied to systemic patterns, not individual
  diffs.
- anti-patterns checklists become "is this pattern present anywhere
  load-bearing in this repo?", not "did this PR introduce it?".
- testing-standards' coverage and fixture rules become "does the
  repo's test posture satisfy them overall?", not "did this test
  diff?".

MANDATORY REFRAMING RULES:
- Report systemic findings only. "5 of 12 modules silently swallow
  exceptions" is a finding. "Line 47 of foo.py uses bare except" is
  a nit unless it is illustrative of the systemic pattern.
- Target <15 substantive findings. If you have 30, you are reporting
  nits.
- Findings must trace to a declared standard or principle from the
  repo's AI guidance, `standards/` directory, or one of the named
  source skills.

READ THESE SKILLS for the underlying checklists, resolving from the
current harness runtime surface first and from canonical `skills/`
if working in the source library:
- code-review -- Security Red Flags and Reliability Red Flags
  sections especially; treat their patterns as systemic checks
  rather than per-diff items
- anti-patterns -- the full anti-pattern checklist; ask "is this
  load-bearing here?" for each
- testing-standards -- test posture, mock boundaries, realistic
  fixture sizing

YOUR AUDIT AREAS:

1. Test posture: Does the repo have meaningful test coverage of
   load-bearing code paths? Are fixtures realistic? Are mock
   boundaries at system edges (DB, HTTP, filesystem) rather than
   internal code?

2. Reliability patterns: Are there systemic anti-patterns in error
   handling, unbounded memory, silent failures, or scaling
   assumptions?

3. Security posture: Are secrets, credentials, and trust boundaries
   handled systematically (config, env vars, secret management) or
   sprinkled ad-hoc through the code?

4. Code organization: Does the code follow the structure the docs
   claim? Are there obvious god-objects, copy-pasted modules, or
   dead code at the repo level?

5. Declared-standards adherence: If the repo imports or references
   particular standards (`standards/software-project-principles.md`,
   `anti-patterns`, etc.), spot-check whether the code observes
   them.

ANTI-DELUGE TEST: Before reporting, re-read your findings. If more
than half are about individual lines rather than patterns spanning
multiple files, restart with tighter focus. Pattern-level findings
are what this vector exists for.
```

### Phase 3: Cross-Vector Synthesis

After all workers return, the orchestrator consolidates:

1. **Collect** all findings into a single list, preserving vector
   labels.

2. **Cross-promote** findings flagged by both vectors:
   - Same concern surfaced by DOC and CODE -> promote one severity
     level (NOTE -> WARNING, WARNING -> CRITICAL).
   - Example: docs claim a feature works that the code has not
     implemented (DOC drift) AND the tests do not cover that feature
     (CODE testing gap) -> promote both findings, treat as a single
     compound issue.

3. **Identify choke points** -- systemic patterns that multiple
   findings trace back to. Example: "8 of 14 findings stem from
   missing harness-root guidance sections (`AGENTS.md` for Codex,
   `CLAUDE.md` for Claude) that downstream skills expected." Choke
   points are the highest-leverage fixes.

4. **Apply change threshold** -- discard findings that fail the
   "would unchanged materially harm comprehension, maintainability,
   correctness, or coherence?" test. Be willing to drop NOTE-level
   findings here.

5. **Derive verdict** -- see Verdict Calibration below.

### Phase 4: Consolidated Report

```
## REPOSITORY AUDIT: [target description]

**Scope:** [repo path / subtree, vectors run]
**Verdict:** ALIGNED / DRIFT / MISALIGNED / INCOMPLETE

---

### Summary

[2-3 sentences: overall coherence and standards-adherence posture,
most significant systemic issue, whether the repo's declared intent
matches reality. Be direct.]

### Critical Findings (BLOCK)

| # | Vector | Finding | Path | Standard | Severity |
|---|--------|---------|------|----------|----------|
| 1 | DOC-1 | ... | ... | ... | CRITICAL |
| 2 | CODE-2 | ... | ... | ... | CRITICAL |

[Per finding: evidence, standard violated, precedence-ordered fix]

### Drift Findings

[DOC<->code disagreement specifically. Each carries a precedence_fix
that honors the docs > comments > structure > code order.]

### Standards-Adherence Findings

[Where the code or docs don't match declared standards from
`standards/`, AI guidance, or imported principles.]

### Cross-Vector Promotions

[Findings independently flagged by both DOC and CODE, with promoted
severity and explanation of why convergence from multiple angles
matters.]

### Choke Points

[Systemic issues that multiple findings trace back to. Highest
leverage fixes -- address the choke point and multiple findings
resolve simultaneously.]

### Notes

[NOTE-severity findings worth recording but not actioning urgently.]

### Ambiguities Requiring Clarification

[Where the audit halted on contradictory or unstated intent. One
clarification question per ambiguity.]

### Precedence-Ordered Fix Recommendations

[Findings grouped by recommended fix layer, in order:]

1. **Doc fixes** (preferred -- cheapest, least risky)
2. **Comment additions**
3. **Structural changes**
4. **Code changes** (last resort)
```

---

## Verdict Calibration

- **ALIGNED** -- repo's docs and code cohere, declared standards are
  observed, no findings above NOTE severity. Rare. If you give this,
  double-check the CODE vector did not silently narrow scope.

- **DRIFT** -- most common verdict on active repos. Docs and code
  generally agree, declared standards mostly observed, but specific
  drift or gaps exist. Repo is usable; declared intent is largely
  trustworthy with the called-out exceptions.

- **MISALIGNED** -- 1+ CRITICAL findings, or systemic divergence
  between declared intent and observable code. Repo's docs cannot be
  trusted as declared intent without doing the listed work first.

- **INCOMPLETE** -- audit halted on irreducible ambiguity. Verdict
  pending human clarification on the recorded questions.

When in doubt between DRIFT and MISALIGNED, count CRITICAL findings.
0 -> DRIFT. 1+ -> MISALIGNED.

---

## When to Use

- Onboarding a new repo: what state is it actually in?
- Periodically (quarterly) on long-lived repos to detect slow drift.
- Before a major release or refactor, to surface accumulated drift.
- After ingesting an external repo, to baseline its coherence and
  standards posture.

---

## Anti-Patterns for the Auditor

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Cosmetic-finding deluge from the CODE vector | The reframing rules exist for a reason; if the CODE worker reports 30+ line-level findings, the preamble was ignored. Re-run with tighter focus. |
| Proposing code fixes when docs are the cheaper reconciliation | Change precedence is non-negotiable: prefer doc updates when intent can be clarified, code changes last. |
| Giving ALIGNED when only one vector ran | Partial coverage cannot produce a full verdict. Note the partial scope explicitly. |
| Inferring intent the docs do not state | No-inferred-intent rule. Unstated expectations are GAPs to surface, not failures to grade. |
| Silently resolving DOC<->CODE drift | Drift requires a human call; flag it with the precedence_fix path, do not pick a winner. |
| Skipping Phase 3 cross-promotion | Findings flagged by both vectors are systemic; missing the promotion underweights real issues. |
| Reporting findings without a `Standard:` trace | If no declared standard or principle backs a finding, it should have been discarded at the change-threshold step. |

---

## Composition Notes

- This skill is the entry point. It invokes `audit-documentation` as
  its DOC worker (as methodology, not as a separate sub-agent
  invocation -- workers read the skill body and execute the workflow
  themselves).
- The CODE worker composes `code-review`, `anti-patterns`, and
  `testing-standards` by reference with mandatory whole-repo
  reframing. No dedicated `audit-code-quality` skill exists yet; if
  the CODE vector grows or needs symmetry, factor it out then.
- `red-team` is a sibling, not a dependency. Red-team is adversarial
  and finding-mandatory; this auditor is constructive and
  change-threshold-gated. Run red-team when you want to know what an
  attacker could exploit; run audit-repository when you want to know
  whether the repo holds up against its own declared standards.
