# Content lives in git; the database is a disposable mirror

Learning content stays canonical in git repositories (Stores); a
manifest-driven sync mirrors selected documents and image assets into
Postgres for serving. The database is authoritative only for review state
(an append-only review log plus current scheduling state). Consequence: the
database is rebuildable from the Stores at any time — the only irreplaceable
tables are the review ones, so the backup story is a tiny pg_dump. Rejected
alternative: making the app's database canonical for content, which would
break the no-lock-in, plain-markdown-on-disk convention the Stores follow.
