---
name: worked-example
description: >-
  Codex runtime skill generated from canonical `skills/worked-example/SKILL.md`. Explain software systems through concrete worked examples.
---

# worked-example (Codex Runtime Skill)

Canonical source: `skills/worked-example/SKILL.md`

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

## Worked Example

Teach a system by walking one realistic case end-to-end before generalizing.

### Workflow

1. Pick the scenario:
   - Use the user's concrete case when provided.
   - If no case is provided, choose a small realistic example and say the values are illustrative.
   - Ask only when the missing value would make the example misleading or risky.
2. Gather source evidence:
   - Read local instructions first.
   - Trace the entry point through the key code path with `rg` and file reads.
   - Prefer tests, fixtures, logs, docs, or API examples that already contain realistic values.
   - Cite concrete source paths and line numbers for claims about code behavior.
3. Build the example setup:
   - Actors / records / IDs.
   - Starting state.
   - Input request or event.
   - Expected output or observable symptom.
4. Walk the journey step by step:
   - Name the code or system boundary for each step.
   - Show the important intermediate state.
   - Explain why the next step happens.
   - Mark unknown or inferred steps explicitly.
5. End with the learning:
   - What to notice.
   - Edge cases or mismatch patterns.
   - How to swap in the user's own values.
6. Pair with `system-diagrams` when a small visual trace would clarify the journey.

### Output Shape

Use this shape unless the user requested another format:

```markdown
Scenario: {one concrete case in one sentence}

Setup:
| Value | Example | Meaning |
|---|---|---|
| {field} | `{value}` | {why it matters} |

Journey:
| Step | What happens | State / value | Source |
|---|---|---|---|
| 1 | {action or handoff} | `{important value}` | `{file}:{line}` |

Result:
- {what the system returns, stores, sends, hides, denies, or displays}

What to notice:
- {2-4 bullets that generalize from the example}

Swap in your case:
- Replace `{field}` with your value.

Unknowns / inferences:
- {only if any}
```

### Quality Rules

- Example first, abstraction second.
- Use real-ish values, but never pretend illustrative values came from source data.
- Do not fabricate file paths, logs, database rows, or API responses.
- Keep the path tight. A worked example should make the system easier to hold in memory, not become a full tutorial.
- Prefer a table for state changes; prefer a short Mermaid sequence only when the handoffs are otherwise hard to follow.

### Trigger Check

Good triggers:

- "Walk me through an example."
- "What happens if this user clicks send?"
- "Show the lifecycle with real values."
- "I learn better from a concrete scenario."
- "Trace this request end to end."

Non-triggers:

- "Give me the high-level architecture."
- "Diagram this flow."
- "Write the implementation."
- "Review this PR."
- "Generate a diagram only."

### Useful Local Examples

Load these only when useful and only if the paths exist in this environment or are supplied by the user:

- Feature-doc worked examples for a full example-first debugging journey.
- API lifecycle notes for request lifecycle examples.
- Investigation playbooks for concrete trace and proof shape.
