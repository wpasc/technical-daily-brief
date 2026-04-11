# news_site - Claude Rules

## Project Overview

AI-generated news site with scraper, LLM writer, and React frontend.

Tech Stack: Python 3.12, FastAPI, SQLAlchemy, SQLite, React, Claude API

## Project Documentation

@../project-docs/news-site/ACTIVE.md

## Core Principles

### Zero-Context Documentation
All documentation assumes no prior project knowledge. Explain the "why" for every non-obvious choice.

### Plain Documentation
Prefer plain ASCII in documentation. Avoid decorative emoji.

### Test Behavior, Not Implementation
Test what code does, not how it does it. No mocking internals.

### Simplicity Over Cleverness
Boring, obvious code over clever abstractions. Wait for real needs.

### Plan Before Executing
For non-trivial work, prefer plan mode. Enter plan mode to align on approach before writing code. When exiting plan mode:
- If there is an engaged task (`.claude/engaged-task` exists), save the plan as a new file in the task's folder (e.g., `plan-{description}.md` alongside the main `plan.md`).
- If there is no engaged task, just exit normally.
This creates durable plan artifacts that sub-agents can reference and that persist across sessions.

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
