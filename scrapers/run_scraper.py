"""CLI entry point for running the news scraper."""
import argparse
import logging
import sys
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

import httpx
import yaml

from scrapers.rss_scraper import RssScraper
from scrapers.base_scraper import ScrapedEvent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_sources_config() -> dict:
    """Load sources configuration from YAML."""
    config_path = Path(__file__).parent / "sources" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def submit_event(event: ScrapedEvent, api_url: str) -> bool:
    """
    Submit event to backend API.

    Args:
        event: Scraped event to submit
        api_url: Backend API URL

    Returns:
        True if successful, False otherwise
    """
    try:
        response = httpx.post(
            f"{api_url}/api/events",
            json={
                "source_url": event.source_url,
                "source_name": event.source_name,
                "title": event.title,
                "raw_content": event.raw_content,
                "image_url": event.image_url,
            },
            timeout=30.0,
        )

        if response.status_code == 201:
            logger.info(f"Submitted: {event.title[:50]}...")
            return True
        elif response.status_code == 409:
            logger.debug(f"Duplicate URL, skipping: {event.source_url}")
            return False
        else:
            logger.warning(f"Failed to submit event: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error submitting event: {e}")
        return False


def run_scraper(api_url: str = "http://localhost:8000", dry_run: bool = False):
    """
    Run the news scraper.

    Args:
        api_url: Backend API URL
        dry_run: If True, don't submit to API
    """
    config = load_sources_config()
    sources = config.get("sources", [])
    rate_limit = config.get("rate_limit_seconds", 2)
    max_articles = config.get("max_articles_per_source", 10)

    total_scraped = 0
    total_submitted = 0

    for source in sources:
        if not source.get("enabled", True):
            logger.info(f"Skipping disabled source: {source['name']}")
            continue

        logger.info(f"Scraping {source['name']}...")

        scraper = RssScraper(
            source_name=source["name"],
            rss_url=source["rss_url"],
            rate_limit_seconds=rate_limit,
        )

        try:
            events = scraper.scrape(max_articles=max_articles)
            total_scraped += len(events)

            if not dry_run:
                for event in events:
                    if submit_event(event, api_url):
                        total_submitted += 1
            else:
                for event in events:
                    logger.info(f"[DRY RUN] Would submit: {event.title[:60]}...")

        finally:
            scraper.close()

    logger.info(f"Scraping complete. Scraped: {total_scraped}, Submitted: {total_submitted}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scrape news from RSS feeds")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Backend API URL",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't submit to API, just print what would be submitted",
    )
    args = parser.parse_args()

    run_scraper(api_url=args.api_url, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
