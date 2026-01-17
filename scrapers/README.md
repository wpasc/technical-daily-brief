# Scrapers

RSS feed scraper module that fetches news from public sources and submits events to the backend API.

## Purpose

Fetches news articles from configured RSS feeds and submits them as "events" to the backend API for later processing by the story writer.

## Architecture

```
scrapers/
  run_scraper.py    # CLI entry point
  base_scraper.py   # Abstract base class defining scraper interface
  rss_scraper.py    # RSS feed implementation
  sources/
    config.yaml     # Feed configuration (URLs, rate limits)
```

## Usage

```bash
# From project root
source .venv/bin/activate

# Normal run (submits to API)
python scrapers/run_scraper.py

# Dry run (prints what would be submitted)
python scrapers/run_scraper.py --dry-run

# Custom API URL
python scrapers/run_scraper.py --api-url http://localhost:8000
```

## Configuration

Edit `sources/config.yaml` to add or modify RSS sources:

```yaml
sources:
  - name: "BBC News"
    rss_url: "https://feeds.bbci.co.uk/news/rss.xml"
    enabled: true
  - name: "NPR"
    rss_url: "https://feeds.npr.org/1001/rss.xml"
    enabled: true

rate_limit_seconds: 2        # Delay between requests
max_articles_per_source: 10  # Limit per feed
```

## How It Works

1. Loads source configuration from `sources/config.yaml`
2. For each enabled source:
   - Fetches RSS feed
   - Parses entries into `ScrapedEvent` objects
   - Submits each event to `POST /api/events`
3. Duplicates are handled by the API (409 Conflict response)

## Extending

To add a new scraper type (e.g., HTML scraper):

1. Create new class inheriting from `BaseScraper` in `base_scraper.py`
2. Implement the `scrape()` method returning `List[ScrapedEvent]`
3. Update `run_scraper.py` to use the new scraper based on config

## Data Flow

```
RSS Feed --> RssScraper --> ScrapedEvent --> POST /api/events --> Events DB
```

Events remain in the database with `processed=false` until the story writer processes them.
