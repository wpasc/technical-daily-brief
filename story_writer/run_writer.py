"""CLI entry point for running the story writer."""
import argparse
import logging
import sys
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def fetch_unprocessed_events(api_url: str, limit: int = 10) -> list:
    """
    Fetch unprocessed events from the API.

    Args:
        api_url: Backend API URL
        limit: Maximum events to fetch

    Returns:
        List of event dictionaries
    """
    try:
        response = httpx.get(
            f"{api_url}/api/events",
            params={"processed": "false", "limit": limit},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return []


def submit_article(article_data: dict, api_url: str) -> bool:
    """
    Submit generated article to the API.

    Args:
        article_data: Article data dictionary
        api_url: Backend API URL

    Returns:
        True if successful
    """
    try:
        response = httpx.post(
            f"{api_url}/api/articles",
            json=article_data,
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(f"Submitted article: {article_data['title'][:50]}...")
        return True
    except Exception as e:
        logger.error(f"Error submitting article: {e}")
        return False


def mark_event_processed(event_id: str, api_url: str) -> bool:
    """
    Mark an event as processed.

    Args:
        event_id: Event ID
        api_url: Backend API URL

    Returns:
        True if successful
    """
    try:
        response = httpx.patch(
            f"{api_url}/api/events/{event_id}",
            json={"processed": True},
            timeout=30.0,
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error marking event processed: {e}")
        return False


def run_writer(
    api_url: str = "http://localhost:8000",
    limit: int = 10,
    dry_run: bool = False,
    engine: str = "markov",
):
    """
    Run the story writer.

    Args:
        api_url: Backend API URL
        limit: Maximum events to process
        dry_run: If True, don't submit or mark processed
        engine: Generation engine ("markov" is free, "claude" needs an API key)
    """
    # Fetch unprocessed events
    events = fetch_unprocessed_events(api_url, limit=limit)
    logger.info(f"Found {len(events)} unprocessed events")

    if not events:
        logger.info("No events to process")
        return

    # Initialize writer (imports are lazy so the markov engine
    # works without the anthropic package or an API key)
    if engine == "claude":
        from story_writer.writer import ArticleWriter

        writer = ArticleWriter()
    else:
        from story_writer.markov_writer import MarkovWriter

        writer = MarkovWriter()
        writer.train(events)

    articles_generated = 0
    articles_submitted = 0

    for event in events:
        logger.info(f"Processing: {event['title'][:60]}...")

        # Generate article
        article = writer.generate_article(
            title=event["title"],
            source_name=event["source_name"],
            raw_content=event["raw_content"],
        )

        if article:
            articles_generated += 1

            article_data = {
                "event_id": event["id"],
                "title": article.headline,
                "content": article.content,
                "excerpt": article.excerpt,
                "section": article.section,
                "priority": article.priority,
                "writer_persona": article.writer_persona,
                # Pass the source's editorial image through with credit
                "image_url": event.get("image_url"),
                "image_credit": event["source_name"] if event.get("image_url") else None,
            }

            if dry_run:
                logger.info(f"[DRY RUN] Would submit: {article.headline}")
                logger.info(f"  Section: {article.section}, Priority: {article.priority}")
                logger.info(f"  Excerpt: {article.excerpt[:100]}...")
            else:
                if submit_article(article_data, api_url):
                    articles_submitted += 1
                    mark_event_processed(event["id"], api_url)
        else:
            logger.warning(f"Failed to generate article for: {event['title'][:60]}")

    logger.info(f"Complete. Generated: {articles_generated}, Submitted: {articles_submitted}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate articles from events")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Backend API URL",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum events to process",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't submit articles, just print what would be generated",
    )
    parser.add_argument(
        "--engine",
        choices=["markov", "claude"],
        default="markov",
        help="Generation engine: markov (zero-cost, default) or claude (requires ANTHROPIC_API_KEY)",
    )
    args = parser.parse_args()

    run_writer(api_url=args.api_url, limit=args.limit, dry_run=args.dry_run, engine=args.engine)


if __name__ == "__main__":
    main()
