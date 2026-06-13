---
name: system-diagrams
description: >-
  Codex runtime skill generated from canonical `skills/system-diagrams/SKILL.md`. Create evidence-backed diagrams for software engineering systems.
---

# system-diagrams (Codex Runtime Skill)

Canonical source: `skills/system-diagrams/SKILL.md`

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

## System Diagrams

Explain engineering systems visually, using diagrams that clarify real code paths or system behavior.

### Workflow

1. Define the scope in one sentence. If the target system, entry point, or question is unclear, ask before diagramming.
2. Gather evidence before drawing:
   - Read local instructions first.
   - Use `rg` and file reads to find entry points, services, models, tasks, and tests.
   - Cite concrete source paths and line numbers for important nodes and edges.
3. Choose the smallest useful diagram, then pick the renderer per Renderer Choice:
   - Request or async lifecycle -> sequence diagram.
   - Component ownership, data flow, or service boundaries -> flowchart or container diagram.
   - State transitions -> state diagram or a state table.
   - Data shape or persistence relationships -> ER diagram, table, or simple text diagram.
   - Fewer than 5 moving pieces -> plain text or a table may beat any diagram.
4. Draw concepts, not every function. Aim for 5-12 nodes and 2-4 groups. Collapse implementation details unless they change the user's understanding.
5. Make fidelity visible. If an edge is inferred, label it as inferred. If a source is missing, put it in Unknowns instead of inventing it.
6. Pair with `worked-example` when one concrete scenario would make the diagram easier to understand; read that skill's `SKILL.md` first.

### Output Shape

Use this shape unless the user requested a specific format:

````markdown
Scope: {one sentence}

```mermaid
{diagram}
```

What to notice:
- {2-4 bullets about the important relationships or handoffs}

Evidence:
| Diagram item | Meaning | Source |
|---|---|---|
| {node/edge} | {plain-language role} | `{file}:{line}` |

Unknowns / inferences:
- {only if any}
````

### Renderer Choice

- Use D2 when `d2` is installed and the deliverable is a rendered file the user will open, such as a learning aid, architecture review, or before/after pair. Prefer `d2 --layout elk in.d2 out.svg` for cleaner layout.
- Use Mermaid when the diagram must render inline where it lives, such as GitHub, Linear, Notion, or chat, or when the diagram is small enough that layout does not matter.
- Keep diagram source next to a rendered SVG only when the user asks to persist the artifact.
- Render local SVGs when useful, then provide the path or attach/show the image through the current environment. Ask before launching GUI apps.
- When rendering D2/SVG, run the renderer, confirm the output file exists and is nonempty, and surface renderer errors instead of pretending the diagram rendered.
- The evidence rules apply identically to both renderers.

### Diagram Rules

- Keep diagram source portable, reviewable, and diffable.
- Keep labels short and readable. Put details in the evidence table, not inside node text.
- Do not make decorative diagrams. Every important node should map to source, runtime evidence, a user-provided fact, or an explicit inference.
- Do not cite files you have not read.
- If rendering matters, offer a follow-up validation pass instead of blocking the first useful answer on visual perfection.

### D2 Crib

Render:

```bash
d2 in.d2 out.svg
d2 --layout elk in.d2 out.svg
d2 --sketch in.d2 out.svg
d2 --watch in.d2
```

Core:

```d2
direction: right

api: API server
api.shape: hexagon

api -> worker: enqueues job
worker -> db: INSERT charge {
  style.stroke-dash: 3
}
db: PostgreSQL { shape: cylinder }
```

Containers:

```d2
billing: Billing service {
  worker: Charge worker
  retry: Retry queue { shape: queue }
  worker -> retry: on failure
}
web -> billing.worker: HTTP POST
```

Classes for before/after diagrams:

```d2
classes: {
  changed: { style: { fill: "#fff3bf"; stroke: "#e67700"; stroke-width: 2 } }
  removed: { style: { fill: "#ffe3e3"; stroke-dash: 3 } }
  inferred: { style.stroke-dash: 5 }
}
worker.class: changed
```

Before/after pairs: use two `.d2` files with identical node keys and order so layout stays comparable. In the after file, mark changed, removed, or added elements with classes.

Sequence diagrams:

```d2
shape: sequence_diagram
patron -> api: POST /memberships
api -> db: insert row, status=pending
api -> queue: ChargeJob{member_id}
queue -> worker: dequeue
worker."retries up to 3x"
```

Misc:

- Use `# comment` for source notes. Keep `file:line` evidence in the markdown table, not node labels.
- Long labels: `key: |md **bold** text |` renders markdown.
- Use `sql_table` shape for schemas with fields as `col: type` lines.
- Do not fight layout by hand; switch to `--layout elk` before adding manual positions.

### Trigger Check

Good triggers:

- "Diagram this request flow."
- "Map the architecture around notifications."
- "Show me the state transitions."
- "I need a visual explanation of how this data moves."

Non-triggers:

- "Explain this function briefly."
- "Walk me through a concrete example."
- "Fix this bug."
- "Write tests."
- "Make a polished presentation diagram."
