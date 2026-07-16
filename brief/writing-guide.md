# Writing guide

How to turn `.context.md` into `briefs/<YYYY-MM-DD>.md`. Follow this exactly;
the site renders whatever you write, and the archive is permanent.

## File format

```markdown
---
date: YYYY-MM-DD
generated: <ISO-8601 timestamp with offset>
---

# Daily Technical Brief -- YYYY-MM-DD

## AI/LLM developments

### [Item title](https://source-link)
Two to four sentences on what happened and why it matters.

## Engineering & systems

### [Item title](https://source-link)
...
```

- Frontmatter keys `date` and `generated` are required; the site build parses
  them.
- Section headings must match the section names in `sources.json`, in the same
  order.
- Every item heading is a markdown link to the primary source. No unlinked
  claims.
- ASCII only. Use `--` for a dash.

## Curation

- 3 to 8 items per section. Fewer beats padding.
- An item earns a spot if a working engineer would act on it or think about it:
  a real capability change, a substantive technical write-up, a meaningful
  release, a well-argued analysis. Business gossip, funding news, product
  marketing, and outrage do not qualify.
- Deduplicate: if several sources carry the same story, one item, best link.
- If a section has nothing above the bar, keep the heading and write one line:
  `Nothing above the bar today.` Never invent significance.
- If `.context.md` lists coverage gaps (failed sources), add a final line to
  the brief: `Note: <source> failed to load today.`

## Voice

- Lead each item with the concrete fact, not throat-clearing. "Postgres 18
  adds X" beats "In an exciting development for databases".
- Say why it matters in terms of consequences: what it changes, what it
  replaces, what to watch for. Plain declarative sentences.
- No hype adjectives (game-changing, powerful, seamless). No exclamation
  points. Understatement is the house style.
- It is fine to state a measured judgment ("the benchmark methodology is
  thin") when the source supports it.
