# news_site - Claude Rules

## Project Overview

AI-generated news site with scraper, LLM writer, and React frontend.

Tech Stack: Python 3.12, FastAPI, SQLAlchemy, SQLite, React, Claude API

## Project Documentation

@../project-docs/news_site/ACTIVE.md
@../project-docs/news_site/TODO.md
@../project-docs/news_site/guidance.md

## Task Tracking

Four files in `~/workspace/project-docs/news_site/` form the task system. The first three are auto-loaded into every session via the `@` imports above; the fourth is loaded on demand by the engage skill when it matches a user prompt against a task.

| File | Role |
|---|---|
| `ACTIVE.md` | Lightweight catalog. Active Tasks (with `[in flight]` / `[parked]` / `[blocked]` status hints) and one-sentence Todo handles. |
| `TODO.md` | Full descriptions of queued ideas. Auto-loaded so the engage skill can match prompts against rich descriptions. |
| `tasks/{name}/plan.md` | Per-task goal, approach, steps. Loaded on demand by the engage skill when a prompt matches that task. |
| `tasks/{name}/status.md` | Per-task status entries (latest first). Written by the checkpoint skill. |

**Loop:** the `engage` skill matches a session's first work-style prompt against ACTIVE.md and TODO.md, loads the relevant `plan.md` (or files a new task), then work proceeds; the `checkpoint` skill writes status back at session end. There is no `.claude/engaged-task` file or SessionStart hook -- the matching intelligence lives in the engage skill description.

**Status hint vocabulary**: `[in flight]` (currently being worked on; preferred match for ambiguous prompts), `[parked]` (paused intentionally), `[blocked]` (waiting on external input). New tasks default to `[in flight]`.


## Core Principles

### Honest Assessment Over Agreement
State your genuine evaluation of the user's approach before executing. If you see a problem, flag it -- do not comply silently to avoid friction. When you disagree, say so plainly with reasoning. The user can still override, but silent agreement when you see an issue is the actual failure mode.

### Zero-Context Documentation
All documentation assumes no prior project knowledge. Explain the "why" for every non-obvious choice.

### Plain Documentation
Prefer plain ASCII in documentation. Avoid decorative emoji.

### Test Behavior, Not Implementation
Test what code does, not how it does it. No mocking internals.

### Simplicity Over Cleverness
Boring, obvious code over clever abstractions. Wait for real needs.

### Single-Line Shell Commands
When using Bash, keep commands on a single line -- use semicolons to chain Python statements, `&&` for shell commands. Multi-line commands trigger an unbypassable approval prompt.

### Prefer Dedicated Tools Over Bash
Use Glob instead of `find`, Grep (ripgrep) instead of `grep`/`rg`, and Read instead of `cat`/`head`/`tail`. Dedicated tools need no permission approval and produce better-structured output. When Bash is genuinely needed for file operations, prefer `fd` over `find` and `rg` over `grep`. Reserve Bash for commands that have no dedicated equivalent (git, build tools, test runners, package managers).

### Plan Before Executing
For non-trivial work, prefer plan mode. Enter plan mode to align on approach before writing code. When exiting plan mode:
- If a task's `plan.md` is in context (the engage skill matched earlier this session), save the plan as a new file in that task's folder (e.g., `plan-{description}.md` alongside the main `plan.md`).
- If no task is in scope, just exit normally.
This creates durable plan artifacts that sub-agents can reference and that persist across sessions.

### Cross-Project Routing
If the user flags an idea or concern as out-of-scope for this project, or mentions it belongs elsewhere, append it as a bullet to `~/workspace/nexus/routing.md` with a one-line summary and the source project name. Do not proactively search for cross-project relevance.

## Testing

```bash
make test
# or: cd backend && pytest tests/ -v
```

- Coverage targets: 80%+ for new modules, 90%+ for critical paths
- Test paths: `backend/tests/`

## Key Patterns

- Repository pattern for data access (core/repositories/)
- Pydantic validation at API boundary (core/schemas/)
- Thin SQLAlchemy models without business logic (core/models/)
- Presentational React components (no state in children)
- Priority-based article layout (featured, high, medium)

## Directory Structure

```
news_site/
  backend/
    api/              # FastAPI application and routers
    core/
      models/         # SQLAlchemy models
      repositories/   # Data access layer
      schemas/        # Pydantic validation schemas
      database/       # Session management
    lib/config/       # Configuration loading
  scrapers/           # RSS feed scrapers
  story_writer/       # LLM article generation
  frontend/           # React application
  data/               # SQLite database
```

## Common Workflows

1. Scrape news: `source .venv/bin/activate && python scrapers/run_scraper.py`
2. Generate articles: `source .venv/bin/activate && python story_writer/run_writer.py`
3. Run backend: `source .venv/bin/activate && cd backend && PYTHONPATH=. uvicorn api.main:app --reload`
4. Run frontend: `cd frontend && npm start`
5. Run with Docker: `make dev`

## API Endpoints

- GET /api/health - Health check
- GET /api/events - List events (?processed=false for unprocessed)
- POST /api/events - Create event (from scraper)
- PATCH /api/events/{id} - Update event (mark processed)
- GET /api/articles - List articles (?section=X for filtering)
- POST /api/articles - Create article (from writer)
- GET /api/writers - List writer personas

## Models

Event: Raw scraped news data
- source_url, source_name, title, raw_content, scraped_at, processed

Article: LLM-generated article
- title, content, excerpt, section, priority, writer_persona, event_id

Writer: Persona definitions for LLM
- name, persona, style_description

## Environment Variables

- ANTHROPIC_API_KEY: Claude API key (required for story writer)
- DATABASE_URL: Database connection string (defaults to SQLite)

## Conventions

- All markdown files use ASCII only (no emojis, no Unicode symbols)
- Logging via Python logging module (no print statements)
- Error handling via custom exception hierarchy (core/exceptions.py)
