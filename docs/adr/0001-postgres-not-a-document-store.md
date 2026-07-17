# Postgres, not a document database

The app mostly stores prose documents (markdown), which suggested a
document-oriented database. But "document database" means schemaless nested
JSON, not prose — a markdown body is a text column in any engine, so nothing
about prose favors a document store. The actual query workload is relational:
due-queue scans, review-state joins, tag filters, review-log aggregation.
Chose Postgres (hosted on Neon), which also leaves headroom we may want later
(full-text search, JSONB, pgvector) without adding a second system.
