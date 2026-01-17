# Backend

FastAPI REST API for the AI News Site.

## Purpose

Provides HTTP endpoints for:
- Storing scraped news events from RSS feeds
- Storing LLM-generated articles
- Serving articles to the React frontend
- Managing writer personas

## Architecture

```
backend/
  api/
    main.py           # FastAPI app setup, CORS, router registration
    dependencies.py   # Dependency injection (DB sessions)
    routers/          # HTTP endpoint handlers
      health.py       # Health check endpoint
      events.py       # Event CRUD operations
      articles.py     # Article CRUD operations
      writers.py      # Writer persona operations
  core/
    models/           # SQLAlchemy ORM models
    repositories/     # Data access layer (repository pattern)
    schemas/          # Pydantic request/response validation
    database/         # Database session management
    exceptions.py     # Custom exception hierarchy
    logging_config.py # Logging setup
  lib/
    config/           # YAML configuration loading
  tests/
    unit/             # Unit tests
    conftest.py       # Pytest fixtures
```

## Key Patterns

### Repository Pattern
All database access goes through repositories in `core/repositories/`:
- `BaseRepository[T]` provides generic CRUD operations
- Specific repositories (ArticleRepository, EventRepository) extend with custom queries
- Repositories receive a DB session via dependency injection

### Pydantic Validation
Request/response validation happens at the API boundary via `core/schemas/`:
- Input schemas validate incoming data
- Output schemas control response shape
- Schemas are separate from SQLAlchemy models

### Thin Models
SQLAlchemy models in `core/models/` contain only:
- Column definitions
- Relationship mappings
- No business logic

## Running Locally

```bash
# From project root
source .venv/bin/activate
cd backend
PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```

## Running Tests

```bash
# From project root
source .venv/bin/activate
pytest backend/tests -v
```

## Adding a New Endpoint

1. Create or update schema in `core/schemas/`
2. Create or update repository in `core/repositories/` if new data access needed
3. Add route handler in appropriate router under `api/routers/`
4. Register router in `api/main.py` if new router file

## API Documentation

When running locally, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
