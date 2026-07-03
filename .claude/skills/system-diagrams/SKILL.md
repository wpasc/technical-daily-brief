---
name: system-diagrams
description: >-
  Create evidence-backed SVG diagrams for software engineering systems -- architecture, request lifecycles, data flow, state transitions, decision logic, code paths, and system maps. Hand-authored SVG against a fixed design system; every box carries a copy-pasteable code anchor and traces to real source. Covers both quick evidence maps and richer teaching diagrams. Do not use for ordinary prose explanations where a diagram would not clarify the system.
user-invocable: true
argument-hint: "system, flow, request, state machine, or code path to diagram"
---

# System Diagrams

Explain engineering systems visually with hand-authored SVG that clarifies real code paths or
system behavior. A good diagram is two separate things, and this skill owns both:

- **True** - every node and edge traces to source, runtime evidence, a user fact, or a labeled inference.
- **Clear** - a deliberate visual you placed yourself, not whatever an auto-layout engine produced.

The medium is SVG only - no auto-layout engines. Auto-layout decides spacing, routing, and density
for you, which is the root cause of generic, sprawling, or overlapping diagrams. Hand-placed SVG
means every coordinate, color, and gap is a decision.

One skill, two dials. The same rules cover a quick evidence map (a few boxes to orient someone) and a
richer teaching diagram (numbered, phased, code-anchored). Default to the teaching treatment in
"Authoring For Clarity"; dial it down for small or throwaway maps.

## Workflow

1. Define scope in one sentence. If the target system, entry point, or question is unclear, ask before drawing.
2. Gather evidence before drawing:
   - Read local instructions first.
   - Use `rg` / file reads to find entry points, services, models, tasks, and tests.
   - Cite concrete `file:line` for every important node and edge. Do not cite files you have not read.
3. Choose the smallest useful shape:
   - Request or async lifecycle -> vertical numbered sequence flow.
   - Component ownership, data flow, or boundaries -> grouped flow / container map.
   - State transitions -> state diagram or a state table.
   - Data shape or persistence -> ER-style boxes or a table.
   - Fewer than ~5 moving pieces -> a table or plain text may beat any diagram.
4. Draw concepts, not every function. 5-12 nodes, 2-4 groups. Collapse detail unless it changes the
   user's understanding. Two focused diagrams beat one dense wall, e.g. an architecture view plus a
   "where the issue is" view.
5. Make fidelity visible. Inferred edge -> label it inferred. Missing source -> Unknowns, not invented.
6. Hand-author the SVG using the Design System and Authoring For Clarity below, then run the
   Pre-finalize Checklist before returning it.
7. Pair with `worked-example` when one concrete scenario would make the diagram easier to understand.

## Why SVG Only

- Vector text: a boxes-and-arrows diagram is ~1-3 KB and a few hundred tokens; a PNG of the same is
  tens of KB and ~1000+ vision tokens, read lossily. SVG re-reads losslessly - exact labels and values.
- Deliberate layout: you place every box. No engine to fight.
- Auditable: plain text, so it is greppable, diffable, and re-checkable against source.
- Portable: a self-contained SVG renders in a browser, in Quick Look, and inline in Linear.

## Diagram Design System

A standalone SVG has no host CSS. The file must be fully self-contained: explicit hex colors, an
explicit font stack, and its own background. Do not rely on a host's CSS classes or `var(--...)` -
undefined in a standalone file, they render black or invisible. An SVG's own in-file `<style>` block
is fine, and good for DRY (define `.scan`, `.acl`, `.route`, `.mono` once); keep geometry like
`x` / `width` as attributes.

### Canvas and self-containment

- `<svg xmlns="http://www.w3.org/2000/svg" width="W" height="H" viewBox="0 0 W H" role="img"><title>...</title><desc>...</desc>...`
- Canvas width ~680-720 for a lean map; up to ~1280 (two-column / two-phase) for a dense teaching
  diagram meant to be opened full size. Linear scales inline images to ~600px wide - for wide diagrams
  tell the reader to click to full size. Keep text >= 12px at full size.
- First element is a full-bleed background `<rect>` filled white `#FFFFFF` or off-white `#FAFAF7`.
  Never rely on the host background or transparency - a transparent diagram with dark text vanishes in
  dark-mode. Self-paint so it looks identical in any theme.
- Put `<title>` + one-sentence `<desc>` first, for accessibility.

### Typography

- Font on every `<text>`: `font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"`.
- Code anchors use a mono family: `font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"`.
- Two text sizes: 14px node/group labels, 12px subtitles, anchors, and edge labels. Never below 12px.
- Two weights: 400 normal, 600 (or 700) for titles. Sentence case everywhere - never Title Case, never ALL CAPS.
- Every `<text>` carries an explicit `fill` (a palette text stop). Never omit fill.

### Color encodes meaning, not sequence

- 2-3 ramps per diagram. Gray = neutral/structural. Do not rainbow the steps.
- Group nodes by category; same category shares one ramp. Reserve red/amber/green for
  error/warning/success and blue for informational; use purple/teal/coral/pink for general categories.
- Light-node recipe: fill = 50 stop, stroke = 600 stop (1.5px), text = 900 stop.
- Emphasis-node recipe: fill = 600 stop, text = 50 stop (light text on a strong fill).
- Text on a colored fill always comes from the same ramp - never black or gray.

| ramp | 50 fill | 600 stroke | 900 text |
|---|---|---|---|
| gray | `#F1F5F8` | `#5F5E5A` | `#2C2C2A` |
| blue | `#E6F1FB` | `#185FA5` | `#042C53` |
| teal | `#E1F5EE` | `#0F6E56` | `#04342C` |
| purple | `#EEE0FE` | `#534AB7` | `#26215C` |
| coral | `#FAECE7` | `#993C10` | `#4A1B0C` |
| amber | `#FAEEDA` | `#854F0B` | `#412402` |
| green | `#EAF5DE` | `#3B6D11` | `#173404` |
| red | `#FCEBEB` | `#A32020` | `#501313` |
| pink | `#FBEAF0` | `#993556` | `#4B1528` |

### Complexity budget

- Each box: a title plus one subtitle of <=5 words, plus its code anchor (see Authoring). A
  `file:line` is a fine subtitle.
- Keep one obvious reading order and don't crowd a row - roughly <=4 full-width boxes across.
- No hard node cap. Add nodes as long as each earns its place and the diagram stays decipherable.
  When one diagram starts carrying two stories - or a box wants a paragraph - split into two rather
  than packing tighter.

### Fit math (check before placing text)

- `width_px ~= chars x 8.4` (14px bold) or `chars x 6.5` (12px normal/mono).
- Require `text_width + 2x16px padding <= box width`. Otherwise shorten the label or widen the box.
- SVG `<text>` never wraps. Multi-line needs explicit `<tspan x="..." dy="1.2em">`.

### Building blocks

- Arrow marker, defined once in `<defs>`, neutral by default:
  ```svg
  <defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1 L8 5 L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
  ```
- Neutral arrows: `<line ... stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#arrow)" />`. For a
  colored/emphasis edge, set the line stroke to a 600 hex and give it its own same-color marker.
- Box: `<rect rx="4">` with a centered label `<text>` and the code anchor `<text>` beneath.
- Numbered badge: a filled `<circle>` with a white centered number, beside the box it indexes.

### Pre-finalize Checklist (run on the finished SVG; fix before returning)

- [ ] `viewBox` height = bottom-most element + ~20px; no dead space.
- [ ] Every box: `x >= 0` and `x + width <= canvas width`.
- [ ] Same row: each left box (`x + width`) is `< next box x by >= 20px`.
- [ ] No two unrelated bounding boxes intersect. Allowed: a label inside its own box, an arrowhead touching its target.
- [ ] Every text label fits its box per the fit math.
- [ ] One obvious reading order (top-down or left-to-right).
- [ ] Background rect present; every `<text>` has an explicit fill.

### Anti-patterns

- No gradients, shadows, blur, or glow.
- No icons or illustrations inside boxes; text only.
- No paragraphs, titles, or orphan labels inside the SVG beyond the single synthesis callout - explanation lives in your response prose.
- No reliance on host CSS classes, `var(--...)`, or host theme. An in-file `<style>` block is fine.

## Authoring For Clarity

These practices make a diagram teachable. They are the default; scale them down for a quick map.

Every box pairs a teaching label with a copy-pasteable code anchor.

- Line 1, the label: bold, plain-language "what this does," sentence case.
- Line 2, the anchor: the exact symbol in monospace - `Class.method.post_id()`, `module.function`,
  a table name, or the real route/query string. It must be something the reader can paste into `rg` or
  an editor and land in the code. Pair the name with a label so it still teaches; never prose-only
  nodes, never bare names without a label.

Make it learnable.

- Numbered step badges and an explicit top-to-bottom reading order; lifecycle/trace diagrams lean vertical.
- Group the flow into 2-3 named phases (titled panels) so the shape is legible before any small text is read.
- Exactly one synthesis callout box stating the non-obvious takeaway in prose - the "what to notice," inside the visual.
- A short legend mapping each color to its category, e.g. scan / ACL / route / insight.
- A source footer citing the artifact path + claim IDs (or `file:line`) - the audit anchor.

Mechanism first. Default to the real request lifecycle / call path / numbered time-sequence. Reach
for a decision/branch diagram (gates, yes/no, parity grid) only when the user asks a "should we / when
do we" question.

Rich is not dense. Richer labels, not more text. Per box: label + anchor + at most one clarifier of
<=8 words. Arrows stay mostly unlabeled; annotate only the one or two non-obvious edges. If a box
needs a paragraph, the detail goes in your prose or the Evidence table.

## Output Shape

Use this shape unless the user requested a specific format:

````markdown
Scope: {one sentence}

{the SVG - write it to a file, then embed or link per Delivering The Diagram}

What to notice:
- {2-4 bullets about the important relationships or handoffs}

Evidence:
| Diagram item | Meaning | Source |
|---|---|---|
| {node/edge} | {plain-language role} | `{file}:{line}` |

Unknowns / inferences:
- {only if any}
````

## Auditability

The SVG is the rendering; the Evidence table is its audit index. Because the SVG is plain text:

- Every node and edge label is greppable and the whole file diffs cleanly across edits.
- Re-audit: re-open each `file:line` in the Evidence table and confirm the node still matches - the
  same check an adversarial verifier runs against an `explain` artifact. Update the SVG and the table together.
- Keep the `.svg` beside its artifact (eng-notes, or attached to the issue) so a stale diagram is caught
  by re-running the artifact's verification against the cited sources.

Plain-text source you can relate back to code, with layout you placed yourself.

## Delivering The Diagram

The `.svg` file is the source of truth - write it to disk first, then deliver based on why you drew it.
Don't paste `<svg>` inline and assume it renders: over SSH, in a plain terminal, or outside the desktop
app it shows up as a raw blob. Pick the destination from context; ask only when it is genuinely unclear.

- Task work -> Linear. Upload the `.svg` as a file attachment through whatever Linear access the
  session has (MCP attachment upload, or the GraphQL file-upload mutation), then embed the returned
  URL as a markdown image in the issue body or comment. Raw `<svg>` pasted into a Linear body
  renders as literal text.
- Learning / research -> eng-notes. Save the `.svg` somewhere sensible in eng-notes and link it from
  the note, beside the prose it illustrates.
- Inline -> only when you know the surface renders SVG. When unsure, write the file and use one of the above.

## Diagram Rules

- Keep the SVG source portable, reviewable, and diffable.
- Labels short; details in the Evidence table, not inside node text.
- Every node maps to source, runtime evidence, a user-provided fact, or an explicit inference. No decorative nodes.
- Do not cite files you have not read. Every code anchor must be real and current - if you have not
  opened the symbol, do not print it as an anchor.
- Before/after comparisons reuse the same layout and mark only the changed elements.

## Trigger Check

Good triggers:

- "Diagram this request flow."
- "Map the architecture around notifications."
- "Show me the state transitions."
- "I need a visual explanation of how this data moves."
- "Make a polished, teachable diagram of X."

Non-triggers:

- "Explain this function briefly."
- "Walk me through a concrete example." (use `worked-example`)
- "Fix this bug."
- "Write tests."

## Examples

Bundled reference diagrams, if present - read one before drawing if you want a concrete pattern to imitate:

- `examples/domain-events-delete-post.svg` - vertical numbered lifecycle / trace.
- `examples/mediation-lakehouse.svg` - grouped container / architecture map.
- `examples/arm-before-after.svg` - before/after on one shared layout, only deltas marked.
- `examples/events-taxonomy-decision.svg` - decision / "when do we" branch.
