---
name: red-team
description: >-
  Codex runtime skill generated from canonical `skills/red-team/SKILL.md`. Multi-vector adversarial code review that strips sympathetic context and attacks from security, engineering, architecture, dependency, and testing angles simultaneously.
---

# red-team (Codex Runtime Skill)

Canonical source: `skills/red-team/SKILL.md`

This file is self-contained for Codex runtime. Shared behavior belongs
in the canonical source skill; regenerate this file after changing the
source.

## Codex Runtime Notes

- Prefer `AGENTS.md` for root guidance. Treat `CLAUDE.md` only as supplemental fallback when older Claude-specific text in the inlined body requires it.
- Use Codex-native tools and `.agents/skills/`; translate older Claude coordination wording in the body into explicit user requests, current tools, or durable artifacts when the workflow requires them.

## Classification

- Migration category: Generate as Codex runtime skill
- Rationale: Workflow or reference guidance is useful in Codex as a self-contained runtime skill.

## Skill-Specific Notes

- Keep the source skill's reporting contract. In Codex, present findings first with file references, then assumptions or residual risks.

## Inlined Skill Body

## Red Team

Multi-vector adversarial review that hits a codebase from every angle at once.
Dispatch-style parallel workers or sub-agents, each attacking from a different
perspective, with cross-vector synthesis that promotes findings flagged by
multiple vectors.

This is the "rager." Default mode is full assault.

---

### Philosophy

**Good code is self-evidently defensible.** If it needs backstory to justify
its existence, it is not good code.

These principles govern every worker in every vector:

1. **Zero sympathetic context.** We do not care about requirements, deadlines,
   constraints, or "how it got this way." We evaluate the code on its merits
   as it exists right now. Path-dependent decisions that produced bad code are
   not excuses -- they are findings.

2. **Mandatory findings.** Every worker MUST produce at least one finding
   per reviewed scope. "Looks good" is not an output. If you cannot find a
   defect, you have not looked hard enough. Report the most fragile assumption
   the code relies on.

3. **Everything is a vulnerability.** Frame every defect in terms of what it
   enables an adversary (attacker, scale, entropy, time) to exploit:
   - Unbounded memory -> DoS surface
   - Silent failure -> hiding attack success
   - Missing validation -> injection surface
   - Vague naming -> social engineering vector against future maintainers
   - Dead code -> attack surface that nobody monitors
   - Over-abstraction -> complexity that hides bugs

4. **Not destructive.** The goal is to find every flaw, not to say "burn it
   down." Findings must be specific, evidenced, and include what defensible
   code would look like. "This is bad" without "here's what good looks like"
   is not a finding.

5. **Substance over ceremony.** Report structural problems, not style
   preferences. A null dereference is a finding. A missing trailing comma
   is not.

---

### Attack Vectors

| Code | Vector | Targets | Composes With |
|------|--------|---------|---------------|
| SEC | Security Assault | OWASP Top 10, injection, auth bypass, secrets, trust boundaries | security-audit, code-review (Security Red Flags) |
| ENG | Engineering Demolition | Bloat, dead code, over-abstraction, silent failures, god objects | adversarial-review, anti-patterns |
| DEP | Dependency Rot | CVEs, unused deps, bloat, transitive risk, supply chain | dependency-audit |
| ARCH | Architecture Stress Test | Unbounded memory, DoS surfaces, concurrency, scaling assumptions | anti-patterns (Unbounded Memory), code-review (Reliability Red Flags) |
| TEST | Test Gauntlet | Coverage gaps, mock abuse, implementation-coupled tests, unrealistic fixtures | testing-standards |
| ALL | Full Assault | Everything above, simultaneously | All of the above |

**Default is ALL.** If the user specifies vectors (e.g., "red team SEC DEP"),
run only those. If they say "red team this" with no qualifier, run everything.

---

### Workflow

#### Phase 0: Target Acquisition

Determine scope and vectors:

**Scope options:**
- Whole repository (default if no scope specified)
- Specific files or directories ("red team src/auth/")
- Recent changes ("red team the last PR" -> use git diff)
- Staged changes ("red team what I'm about to commit")

**Vector selection:**
- Parse user input for vector codes (SEC, ENG, DEP, ARCH, TEST)
- Default to ALL if no vectors specified
- "Just security" -> SEC only
- "Everything" or no qualifier -> ALL

#### Phase 1: Reconnaissance

The orchestrator (main agent) performs minimal recon:

1. Read README, top-level structure, and AI guidance in harness priority order
   (`AGENTS.md` for Codex, `CLAUDE.md` for Claude, then referenced guidance)
2. Identify the tech stack, language(s), and framework(s)
3. List the target files within scope
4. Note what the codebase *claims* to be and do -- this becomes ammunition,
   not sympathy. Claims that don't match reality are findings.

**Do NOT do deep analysis here.** The orchestrator stays lean. All heavy
analysis happens in workers.

#### Phase 2: Parallel Attack

Start one worker or sub-agent per selected vector. Run them in parallel using
the current harness's available orchestration mechanism. Each worker receives:

1. The shared adversarial philosophy preamble (below)
2. Vector-specific attack checklist
3. Instructions to read relevant existing skills for detailed checklists,
   resolving skill names from the current harness runtime surface first and
   from canonical `skills/` if working in the source library
4. The target file paths
5. Output format requirements

**Launch pattern:**
- 1-2 vectors: foreground execution is fine
- 3+ vectors: use parallel/background execution when the current harness
  supports it; otherwise keep worker prompts independent and collect results
- ALL (5 vectors): prefer all 5 simultaneously

##### Shared Preamble (include in every worker prompt)

```
You are an adversarial code reviewer. Your job is to find what is wrong,
not what is right. You have zero sympathetic context -- you do not care
why decisions were made, only whether they are defensible on their merits.

CORE PRINCIPLE: Good code is self-evidently defensible.

MANDATORY FINDINGS: You MUST produce at least one finding per file or
module reviewed. "Looks good" is not an output. If you cannot find a
defect, report the most fragile assumption the code relies on.

FRAMING: Every finding is a vulnerability. Unbounded memory is a DoS
surface. A silent failure is hiding attack success. Missing validation
is an injection surface. Dead code is unmonitored attack surface.
Frame accordingly.

DO NOT: soften with "might" or "could potentially", acknowledge good
intentions, suggest code is "mostly fine", report cosmetic issues while
missing structural problems.

DO: state defects as facts with evidence, cite file paths and line
numbers, provide the attack scenario (who exploits this, how, impact),
rank by exploitability not by ease of fix.

OUTPUT FORMAT per finding:
- ID: [VECTOR]-[number] (e.g., SEC-1, ENG-3)
- Severity: CRITICAL / WARNING / NOTE
- File: path:line
- Finding: one-sentence summary
- Attack scenario: who exploits this, how, what is the impact
- Evidence: the specific code or pattern
- Defensible alternative: what good code would look like here
```

##### Worker: SEC (Security Assault)

Include in prompt:
```
Read the security-audit skill from the current harness runtime surface, or
from canonical `skills/security-audit/SKILL.md` if working in the source
library. Apply the OWASP Top 10 checklist and attack pattern taxonomy.

Also read the code-review skill's Security Red Flags section for additional
patterns.

Your attack checklist:
- Map every trust boundary (user input, API calls, DB, filesystem, env vars)
- For each boundary: is input validated? Output sanitized? Least privilege?
- Injection surfaces: SQL, NoSQL, command, template, XSS
- Auth/authz: hardcoded creds, missing auth on endpoints, IDOR, privilege escalation
- Secrets: API keys, tokens, passwords in code/config/logs/git history
- Session management: fixation, cookie flags, invalidation
- Data exposure: sensitive data in errors, logs, API responses
- Cryptographic issues: weak hashing, hardcoded keys, weak PRNG
```

##### Worker: ENG (Engineering Demolition)

Include in prompt:
```
Read the adversarial-review skill from the current harness runtime surface, or
from canonical `skills/adversarial-review/SKILL.md` if working in the source
library. Apply ALL THREE PERSONAS (Saboteur, Newcomer, Security Auditor) using
its methodology.

Also read the anti-patterns skill for the full anti-pattern checklist.

Your attack checklist:
- Dead code: functions/modules/files that are never called or imported
- Bloat: over-abstraction, unnecessary indirection, premature generalization
- God objects: classes/modules doing too many things
- Silent failures: caught exceptions that are swallowed or logged-and-ignored
- Error handling: catch-all exceptions, misleading error messages
- Magic values: hardcoded numbers/strings without explanation
- Naming: names that don't communicate intent or actively mislead
- Duplication: copy-pasted logic that should be unified (or shouldn't exist at all)
- Unnecessary complexity: could this be simpler without losing functionality?
- "Why does this exist?": for each abstraction, can you justify its existence
  without referencing the requirements that created it?
```

##### Worker: DEP (Dependency Rot)

Include in prompt:
```
Read the dependency-audit skill from the current harness runtime surface, or
from canonical `skills/dependency-audit/SKILL.md` if working in the source
library, for the full audit methodology.

Your attack checklist:
- Locate all manifest files (package.json, requirements.txt, pyproject.toml,
  go.mod, Cargo.toml, Gemfile, pom.xml, composer.json)
- Unused dependencies: compare imports in source against manifest declarations
- Bloat: oversized packages for simple use cases (lodash for _.get, etc.)
- Redundant deps: multiple packages providing the same functionality
- Version hygiene: floating specifiers, unpinned versions, stale lockfiles
- Known patterns: check for packages with well-known CVE histories
- Supply chain: single-maintainer critical deps, recently transferred packages
- Dev deps in production: development-only packages in production bundles
- Transitive depth: how deep is the dependency tree?
- Lockfile health: exists, committed, in sync with manifest, has integrity hashes
```

##### Worker: ARCH (Architecture Stress Test)

Include in prompt:
```
Read the anti-patterns skill from the current harness runtime surface, or from
canonical `skills/anti-patterns/SKILL.md` if working in the source library,
specifically the Unbounded Memory Anti-Patterns section.

Also read the code-review skill's Reliability Red Flags section.

Your attack checklist:
- Unbounded memory: read-modify-write on full datasets, fetchall() on
  unbounded queries, in-memory accumulators that grow with data, O(dataset)
  memory patterns
- DoS surfaces: unthrottled endpoints, unbounded queries, resource leaks,
  operations that scale with untrusted input size
- Concurrency hazards: shared mutable state, race conditions, missing locks,
  non-atomic read-modify-write
- State consistency: what if this operation runs twice? Concurrently? Never?
  Is it idempotent? Does it need to be?
- Scaling assumptions: what breaks at 100x current load? 1000x? What are
  the implicit assumptions about data volume?
- Single points of failure: what happens if this service/database/API is down?
  Is there graceful degradation or total failure?
- Resource management: file handles, DB connections, HTTP clients -- are they
  properly closed/pooled/limited?
- Health endpoints: do they query the dataset? (O(1) shape required)
```

##### Worker: TEST (Test Gauntlet)

Include in prompt:
```
Read the testing-standards skill from the current harness runtime surface, or
from canonical `skills/testing-standards/SKILL.md` if working in the source
library, for the full testing criteria including production-scale fixtures and
mock boundary rules.

Your attack checklist:
- Coverage gaps: code paths with no test coverage, especially error paths
  and edge cases
- Mock abuse: mocking own code instead of system boundaries (DB, HTTP, filesystem)
- Implementation coupling: tests that break on refactor because they test
  HOW not WHAT
- Unrealistic fixtures: 3-row test data for code that will handle millions
  of rows in production
- Missing integration tests: unit tests pass but components don't work together
- Determinism issues: tests dependent on time, random values without seed,
  execution order, or external state
- Test naming: can you understand what's being tested from the name alone?
- Negative tests: does the test suite verify what SHOULDN'T happen, or only
  happy paths?
- Security tests: are there tests for auth bypass, injection, and access control?
- Assertion quality: tests that assert too little (assertTrue(true)) or
  test implementation details (exact SQL strings, specific log messages)
```

#### Phase 3: Cross-Vector Synthesis

After all workers return, the orchestrator consolidates:

1. **Collect** all findings into a single list

2. **Cross-promote** findings flagged by 2+ vectors:
   - Same file + same concern from different vectors -> promote one severity level
   - NOTE -> WARNING, WARNING -> CRITICAL
   - Document which vectors independently flagged the issue

3. **Identify choke points** -- systemic patterns behind multiple findings:
   - "5 of 12 findings trace back to missing input validation at the API layer"
   - "3 findings stem from the same god object handling too many concerns"
   - Choke points are the highest-leverage fixes

4. **Derive verdict:**
   - **HOSTILE** -- 1+ CRITICAL findings. Code is actively dangerous.
   - **CONTESTED** -- No criticals, 3+ structural findings. Works but fragile.
   - **DEFENSIBLE** -- Minor findings only. Rare. Double-check if you give this.

5. **Identify compound candidates** -- patterns worth capturing via the compound
   skill for cross-session/cross-project persistence

#### Phase 4: Report

Present the consolidated report:

```
## RED TEAM REPORT: [target description]

**Scope:** [files reviewed, total lines, change type]
**Vectors:** [which vectors were run]
**Verdict:** HOSTILE / CONTESTED / DEFENSIBLE

---

### Assault Summary

[2-3 sentences: overall risk posture, most critical systemic issue,
whether the code could survive adversarial scrutiny. Be blunt.]

### Critical Findings (BLOCK)

| # | Vector | Finding | File:Line | Attack Scenario | Severity |
|---|--------|---------|-----------|-----------------|----------|
| 1 | SEC-1 | ... | ... | ... | CRITICAL |

[Detail each critical finding with evidence and defensible alternative]

### Structural Findings (CONTEST)

| # | Vector | Finding | File:Line | Attack Scenario | Severity |
|---|--------|---------|-----------|-----------------|----------|

[Detail each structural finding]

### Cross-Vector Promotions

[Findings independently flagged by 2+ vectors, with promoted severity
and explanation of why convergence from multiple angles matters]

### Choke Points

[Systemic issues that multiple findings trace back to. These are the
highest-leverage fixes -- address the choke point and multiple findings
resolve simultaneously.]

### Minor Findings

[NOTE-level findings, briefly listed]

### Compound Candidates

[Patterns worth capturing via the compound skill for future sessions:
- Pattern description
- Suggested guidance entry
- Scope: local or promote-candidate]
```

---

### Verdict Calibration

- **HOSTILE** should be given when the code has real, exploitable problems.
  Not theoretical -- actual code paths that an adversary (human attacker,
  scale, entropy, time) can use to cause damage.

- **CONTESTED** is the most common verdict for real-world code. Most code
  works but has fragility that will eventually bite.

- **DEFENSIBLE** should be genuinely rare. If you give this verdict, go back
  and re-examine. Code that survives five parallel adversarial reviews with
  only minor findings is exceptional. When it happens, acknowledge it -- but
  verify first.

---

### Running a Targeted Review

Examples of targeted invocations:

- `red team` -- full assault on the whole repo
- `red team src/auth/` -- full assault on auth module only
- `red team SEC` -- security assault only, whole repo
- `red team SEC DEP` -- security + dependency vectors only
- `red team the last PR` -- full assault on recent changes
- `red team ENG ARCH src/core/` -- engineering + architecture on core module

---

### Anti-Patterns for the Red Team Itself

| Anti-Pattern | Why It's Wrong |
|-------------|---------------|
| Giving DEFENSIBLE too easily | If you found nothing critical, you probably missed something. Verify. |
| Cosmetic findings padding the count | Mandatory findings means substantive findings, not "missing semicolons." |
| Pulling punches on well-written code | Even good code has assumptions. Find the fragile ones. |
| Ignoring the test suite | Untested code is automatically CONTESTED at minimum. |
| Reporting without defensible alternatives | "This is bad" without "here's what good looks like" is useless. |
| Sympathizing with the author | "They probably had a reason for this" -- we don't care. Evaluate the code. |
| Running only one vector | Unless explicitly requested, default to ALL. Partial review = partial picture. |
