---
name: explain
description: Explain a system, architecture, code path, or proposed change by building a verified understanding first, then rendering it example-first and visual. TRIGGER when the user says "explain it to me", "help me understand", "how does X work", "what would this change do architecturally", or wants to learn a system across one or more sources. DO NOT TRIGGER for quick single-fact lookups, implementation work, or code review.
user-invocable: true
---

# Explain It To Me

Build a verified understanding, then render it. Pipeline: scope -> research fan-out -> one
auditable artifact -> adversarial verification -> channels. The artifact is the single source of
truth; every channel is a rendering of it. Never render before verification passes: a beautiful
diagram of a wrong understanding is the failure mode this skill exists to prevent.

The learner is example-first and visual: concrete scenarios, before/after, state tables, diagrams.
Prose clarifies an example; it never replaces one.

## 0. Scope

Classify the question shape. It drives both research and rendering:

| Shape | Sounds like | Channels (primary first) |
|---|---|---|
| Mechanism | "how does X work", "what happens when" | worked example + flow/sequence diagram |
| Structure | "how is X organized", "what talks to what" | diagram + worked example of one path |
| Lifecycle | "what states can X be in" | state table + state diagram |
| Decision | "what would this change do", "should we" | before/after diagram pair + comparison table; worked example of the delta when behavior changes |
| Comparison | "X vs Y" | comparison table + paired diagrams |

Use one channel when the shape is clean and one rendering obviously carries it. Default pair when
ambiguous: worked example + diagram. Hard cap: 3 channels.

Then size the job. A domain is one corpus with its own search surface, such as a repo, wiki, Slack
history, PR, or diff. One repo is one domain; do not over-spawn.

| Tier | When | Research | Verification |
|---|---|---|---|
| S | <= ~3 files, one tight question | inline, no subagents | re-read every cited line yourself |
| M | one domain, real surface area | 1-2 research subagents | 1 adversarial verifier subagent |
| L | multiple domains | 1 subagent per domain, max 4 | 2 adversarial verifier subagents |

Decision questions must research both sides: current behavior from the code and proposed behavior
from the diff/proposal text. Each side is its own claim source.

## Artifact Format

Write one markdown file per question at `/tmp/explain/<slug>/artifact.md`. Two jobs: (1) every
load-bearing statement is independently checkable by a skeptic, (2) the structured sections feed
the output channels mechanically. Sections in order; omit a section only when the question shape
doesn't need it.

### Header

Question (verbatim), shape, tier, domains researched, explicitly out of scope.

### Claims

| ID | Claim | Evidence | Status |
|---|---|---|---|

One row per atomic, falsifiable statement. Evidence is `path:line` or URL; multiple pointers are
allowed. Status is `unverified`, `verified`, or `imprecise (note)`. Write claims a hostile reviewer
can check in under two minutes each. If a statement needs no evidence, it is probably not
load-bearing - cut it.

### Entities & Relations <- feeds the visual diagram channel

Renderer-neutral graph lines, one per node or edge, each tagged with claim IDs:

```text
api_server: Flask app behind nginx (C1)
api_server -> charge_worker: enqueues ChargeJob via Redis (C3, C4)
billing: { charge_worker; retry_queue }  # container when ownership matters
```

This section must be mechanically translatable to visual renderers such as D2, Mermaid, or
FigJam/Figma. The renderer adds layout and styling, not facts, nodes, or edges.

### Trace <- feeds the worked-example channel (mechanism / lifecycle shapes)

ONE concrete scenario with pinned, realistic values. Numbered steps; each step names actor, action,
the important value or state change, and claim refs:

```text
Scenario: patron 8841 joins creator 312's $5 tier
1. Browser -> POST /api/memberships {tier_id: 977} (C2) - row inserted, status=pending
2. ...
```

If values are illustrative rather than sourced, say so once at the top of the section.

### Decision Delta (decision shape only)

| Aspect | Before (claim refs) | After (claim refs) |
|---|---|---|

Both columns cite claims. "After" claims cite the proposal/diff itself as evidence.

### Open Questions

Everything believed but unproven, plus claims demoted by verification. Never silently dropped.

### Verification Log

| Round | Verdicts (counts: V / W / U / I) | Fixes made |
|---|---|---|

## 1. Research

For Tier S, research inline and collect claims directly in the artifact. For Tier M/L, spawn one
general-purpose subagent per domain, in parallel. Each researcher prompt contains:

- The question.
- The domain root and entry-point hints.
- The Claims, Entities & Relations, and Trace specs from the Artifact Format section.
- This instruction: "Return claims with `file:line` or URL evidence, entities and relations, and trace fragments. Structured findings only: no prose essay, no unsourced claims."

## 2. Synthesize One Auditable Artifact

Write `/tmp/explain/<slug>/artifact.md` per the Artifact Format section. Merge researcher
output: dedupe claims, assign IDs, connect cross-domain relations, and pin one concrete scenario
with realistic values for the Trace. Anything you believe but cannot cite goes in Open Questions,
not Claims. The artifact is for auditing: lean, falsifiable, no filler.

## 3. Adversarial Verification

Spawn verifier subagent(s) with the artifact path and corpus access only. Never include the
researchers' notes.

Prompt:

```text
Try to FALSIFY each claim. Open every evidence pointer. Verdict per claim:
VERIFIED / WRONG (evidence contradicts -- show counter-evidence) / UNSUPPORTED
(pointer does not back the claim) / IMPRECISE (true but misleading -- say why).
```

Loop: fix WRONG and UNSUPPORTED claims, re-researching if needed, then re-verify only changed
claims. Exit at zero WRONG/UNSUPPORTED, max 2 rounds. Demote anything still standing to Open
Questions visibly, never silently. Record each round in the Verification Log.

Tier S: you are the verifier. Re-open every cited line before marking claims verified. Still write
the Verification Log.

## 4. Render Channels

Renderers add presentation, never new claims. Each channel reads the artifact plus relevant local
guidance:

- Worked example: render from the Trace section. Prefer concrete values, before/after states, and
  short explanatory prose.
- Diagram: render from Entities & Relations. Read `system-diagrams` first when available. Treat the
  artifact as renderer-neutral facts; the diagram renderer adds layout and styling, not facts,
  nodes, or edges. Prefer hand-authored SVG for durable visuals; use inline Mermaid only when the
  user or destination explicitly requires that format.
- Comparison table: use Decision Delta or comparison dimensions as rows. Every cell must trace to
  a claim ID.
- State table: derive states x events from Trace and Relations. Include claim refs in cells.

One channel: render inline. Two or more: spawn one renderer subagent per channel in parallel. Give
each renderer the artifact path, the channel instructions, and an output path in the same
`/tmp/explain/<slug>/` directory.

If dedicated local skills such as `worked-example` or `system-diagrams` exist, read their
`SKILL.md` before using them for the matching channel. If they do not exist, use the channel
guidance above.

## 5. Deliver

Lead with the primary channel inline in the response. Render a local diagram file only when useful
for the user. List the artifact and output file paths. If the understanding is worth keeping, offer
to persist the directory to notes; never write generated explanation artifacts into work repos
unless the user asks.

## Rules

- No rendering before the verification gate passes.
- Never fabricate a pointer; never cite a file no agent read. Unknowns are stated, not papered over.
- Channel renderings must trace back to the artifact. Do not add new claims while rendering.
- Tier S exists so small questions stay cheap. Do not ceremony a one-file question into a fan-out.
