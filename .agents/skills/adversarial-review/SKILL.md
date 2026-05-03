---
name: adversarial-review
description: >-
  Codex runtime skill generated from canonical `skills/adversarial-review/SKILL.md`. Adversarial code review that breaks the self-review monoculture through hostile reviewer personas with mandatory findings.
---

# adversarial-review (Codex Runtime Skill)

Canonical source: `skills/adversarial-review/SKILL.md`

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

## Adversarial Code Review

Forces genuine perspective shifts through hostile reviewer personas that catch
blind spots the author's mental model shares with the reviewer. Each persona
MUST find at least one issue. "Looks good" is not an output.

---

### The Self-Review Problem

When an agent reviews code it wrote (or just read), it shares the same mental
model that produced the code. It will naturally think the code looks correct
because it matches its expectations. This produces rubber-stamp reviews on
code that a fresh perspective would flag immediately.

**To break this pattern:**
1. Read code bottom-up (start from the last function, work backward)
2. For each function, state its contract BEFORE reading the body -- does the body match?
3. Assume every variable could be null/undefined until proven otherwise
4. Assume every external call will fail
5. Ask: "If I deleted this entirely, what would break?" -- if nothing, it may be unnecessary

---

### The Three Personas

#### Persona 1: The Saboteur

**Mindset:** "I am trying to break this code in production."

Look for:
- Input that was never validated
- State that can become inconsistent
- Concurrent access without synchronization
- Error paths that swallow exceptions or return misleading results
- Assumptions about data format, size, or availability that could be violated
- Off-by-one errors, integer overflow, null/undefined dereferences
- Resource leaks (file handles, connections, subscriptions, listeners)

**Process:**
1. For each function: "What is the worst input I could send this?"
2. For each external call: "What if this fails, times out, or returns garbage?"
3. For each state mutation: "What if this runs twice? Concurrently? Never?"
4. For each conditional: "What if neither branch is correct?"

You MUST find at least one issue. If the code is genuinely bulletproof, note
the most fragile assumption it relies on.

---

#### Persona 2: The Newcomer

**Mindset:** "I just joined this team. I need to understand and modify this
code in 6 months with zero context from the original author."

Look for:
- Names that don't communicate intent
- Logic requiring 3+ files to understand
- Magic numbers, magic strings, unexplained constants
- Functions doing more than one thing
- Missing type information forcing call-chain tracing
- Inconsistency with surrounding code style
- Tests that test implementation details instead of behavior
- Comments that describe "what" (redundant) instead of "why" (useful)

**Process:**
1. Read each function as if you've never seen the codebase -- can you understand
   it from name, parameters, and body alone?
2. Trace one code path end-to-end -- how many files do you need to open?
3. Would a new contributor know where to add a similar feature?
4. Look for implicit knowledge baked into the code

You MUST find at least one issue. If the code is crystal clear, note the most
likely point of confusion for a newcomer.

---

#### Persona 3: The Security Auditor

**Mindset:** "This code will be attacked. My job is to find the vulnerability
before an attacker does."

| Category | What to Look For |
|----------|-----------------|
| Injection | User input reaching queries or commands without parameterization |
| Broken Auth | Hardcoded credentials, missing auth on endpoints, session tokens in URLs/logs |
| Data Exposure | Sensitive data in error messages, logs, or API responses |
| Insecure Defaults | Debug mode, permissive CORS, wildcard permissions, default passwords |
| Missing Access Control | IDOR, missing role checks, privilege escalation paths |
| Dependency Risk | Known CVEs, pinned to vulnerable versions, unnecessary transitive deps |
| Secrets | API keys, tokens, passwords in code, config, or comments |

**Process:**
1. Identify every trust boundary (user input, API calls, database, filesystem, env vars)
2. For each boundary: is input validated? Output sanitized? Least privilege followed?
3. Could an authenticated user escalate privileges?
4. Does this expose new attack surface?

You MUST find at least one issue. If the code has no security surface, note the
closest security-relevant assumption.

---

### Severity Classification

| Severity | Definition | Action |
|----------|-----------|--------|
| CRITICAL | Data loss, security breach, or production outage. | Block merge. |
| WARNING | Edge-case bugs, performance degradation, or maintainability risk. | Fix or explicitly accept risk. |
| NOTE | Minor improvement opportunity or documentation gap. | Author's discretion. |

**Promotion rule:** A finding flagged by 2+ personas is promoted one level
(NOTE -> WARNING, WARNING -> CRITICAL).

---

### Output Format

```
## Adversarial Review: [what was reviewed]

**Scope:** [files, lines changed, change type]
**Verdict:** BLOCK / CONCERNS / CLEAN

### Critical Findings
[Block the merge]

### Warnings
[Should-fix items]

### Notes
[Nice-to-fix items]

### Summary
[2-3 sentences: risk profile, single most important thing to fix]
```

**Verdicts:**
- **BLOCK** -- 1+ CRITICAL findings. Do not merge.
- **CONCERNS** -- No criticals, 2+ warnings. Merge at your own risk.
- **CLEAN** -- Only notes. Safe to merge. (This should be rare.)

---

### Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|-------------|---------------|
| "LGTM, no issues found" | You didn't look hard enough. Every change has risk. |
| Cosmetic-only findings | Reporting whitespace while missing a null dereference is worse than no review. |
| Pulling punches | "This might possibly be a minor concern" -- no. State defects as facts. |
| Restating the diff | "This function handles auth" is not a finding. What's WRONG with it? |
| Ignoring test gaps | New code without tests is always a finding. |
| Reviewing only changed lines | Bugs live in the interaction between new and existing code. |
