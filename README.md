# AI News Site

An experiment in how far a fully agent-run news website can go at minimal cost.
Articles are generated from open-source RSS feeds at zero marginal cost.

## Overview

This project scrapes news from public RSS feeds, generates articles from the
scraped text, and displays them on a newspaper-style React frontend. The
default generation engine is a Markov chain trained on each run's scraped
content: free to run, no API key, and the word salad it produces remixes the
day's real news vocabulary. A Claude-powered engine remains available behind
`--engine claude` for when the budget allows.

## Architecture

```
RSS Feeds --> Scraper --> Events DB --> Story Writer --> Articles DB --> Frontend
                                              |
                                   markov chains (default, free)
                                   or Claude API (--engine claude)
```

- **Scraper**: Fetches RSS feeds from major news outlets (BBC, NPR, Guardian, etc.),
  including each story's editorial image when the feed provides one (most do).
  Images are hotlinked from the source CDN and credited on the page; no image
  API or storage costs.
- **Story Writer**: Transforms raw events into articles with different writer personas
- **Backend**: FastAPI REST API with SQLite database
- **Frontend**: React app with newspaper-style layout

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- uv (Python package manager)
- Anthropic API key (optional, only for `--engine claude`)

### Setup

1. Clone and navigate to the project:
   ```bash
   cd projects/news_site
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   # Optional: add ANTHROPIC_API_KEY if using --engine claude
   ```

3. Install dependencies:
   ```bash
   make setup
   ```

4. Initialize the database:
   ```bash
   source .venv/bin/activate
   cd backend && PYTHONPATH=. python -c "from core.database.session import init_db; init_db()"
   ```

### Running

**Option 1: Docker (recommended)**
```bash
make dev
```

**Option 2: Manual**

Terminal 1 - Backend:
```bash
source .venv/bin/activate
cd backend && PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend && npm start
```

### Generating Content

Publish a fresh edition (scrape + write) in one step:
```bash
source .venv/bin/activate
make edition
```

Or run the steps individually:

1. Scrape news from RSS feeds:
   ```bash
   python scrapers/run_scraper.py
   ```

2. Generate articles (markov engine by default, zero cost):
   ```bash
   python story_writer/run_writer.py
   # or, with an API key: python story_writer/run_writer.py --engine claude
   ```

3. View at http://localhost:3000

## Project Structure

```
news_site/
  backend/
    api/              # FastAPI routes
    core/
      models/         # SQLAlchemy models
      repositories/   # Data access layer
      schemas/        # Pydantic schemas
      database/       # DB session management
    lib/config/       # Configuration
  scrapers/           # RSS scrapers
  story_writer/       # LLM article generation
  frontend/           # React app
  data/               # SQLite database
```

## Writer Personas

Articles are bylined by one of five writer personas (matched to section):

- **Alex Chen** - Analytical Reporter: Data-driven, factual analysis
- **Sarah Mitchell** - Investigative Correspondent: Deep-dive investigations
- **Marcus Webb** - Tech Analyst: Technology and science coverage
- **Elena Rodriguez** - Human Interest Reporter: People-focused stories
- **David Park** - Commentary Writer: Opinion and analysis

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/health | GET | Health check |
| /api/events | GET | List events (?processed=false for unprocessed) |
| /api/events | POST | Create event (from scraper) |
| /api/events/{id} | PATCH | Update event (mark processed) |
| /api/articles | GET | List articles (?section=X for filtering) |
| /api/articles | POST | Create article (from writer) |
| /api/writers | GET | List writer personas |

## Configuration

Copy `config.example.yaml` to `config.yaml` to customize:
- RSS feed sources
- Rate limiting
- LLM model and parameters
- API settings

## Development

See `CLAUDE.md` for development guidelines and conventions.
