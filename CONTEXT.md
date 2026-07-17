# Learning Center

The owner's private, single-user web app for interacting with all of his
technical learning material — the daily brief, flashcards, long-form knowledge
docs, and captured external content. Everything sits behind auth; the repo is
open-source. "Learning Center" is a working name.

## Language

**Store**:
A git repository that canonically holds learning material (the flashcard and
knowledge-doc repos, and this repo's brief archive). Content always lives in a
Store; the app is never the system of record for content, only for Review
state.
_Avoid_: source (collides with news-feed sources), silo

**Document**:
The unit of content and of Review: one card, one knowledge doc, one brief, one
future Capture. All content is a Document; kinds differ only in their Prompt
and frontend interaction, not in the model.
_Avoid_: item, note, page

**Prompt**:
The part of a Document shown before reveal in a prompt-first Review — a card's
front, or an authored self-test question. When absent, the title stands in.
_Avoid_: front, question

**Review**:
A scheduled, self-graded retention check on a Document. One mechanism for all
Documents — there is no separate ungraded "resurfacing" mode. Adding a
Document to the schedule is always a deliberate act, never a bulk auto-import
of a whole Store.
_Avoid_: resurface, revisit

**Grade**:
The self-assessed retention rating ending a Review — one of again, hard, good,
easy. Determines the Document's next due date.
_Avoid_: score, rating

**Skip**:
Declining a due Document without engaging it: no Grade, no effect on its
schedule. A first-class action, not a failure mode.
_Avoid_: suspend (Anki semantics), pass

**Queue**:
The set of scheduled Documents currently due, served in randomized order so
that no subset starves.
_Avoid_: feed (collides with news feeds)

**Capture**:
Saving an external resource (blog post, video link) into a Store as committed
markdown, via the app. A Capture becomes a Document. Deferred — not in v1.
_Avoid_: bookmark, clip

**Brief**:
The daily generated digest of curated technical news. Unchanged from v0; one
Document kind among several. Its individual stories — not the whole Brief —
are the likely future review units (deferred).
