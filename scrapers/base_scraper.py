"""Abstract base class for news scrapers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScrapedEvent:
    """Represents a scraped news event."""

    source_url: str
    source_name: str
    title: str
    raw_content: str


class BaseScraper(ABC):
    """Abstract base class for news scrapers."""

    def __init__(self, source_name: str, rate_limit_seconds: float = 2.0):
        """
        Initialize the scraper.

        Args:
            source_name: Name of the news source
            rate_limit_seconds: Seconds to wait between requests
        """
        self.source_name = source_name
        self.rate_limit_seconds = rate_limit_seconds
        self.logger = logging.getLogger(f"{__name__}.{source_name}")

    @abstractmethod
    def scrape(self, max_articles: int = 10) -> List[ScrapedEvent]:
        """
        Scrape articles from the source.

        Args:
            max_articles: Maximum number of articles to scrape

        Returns:
            List of scraped events
        """
        pass

    def log_success(self, count: int):
        """Log successful scrape."""
        self.logger.info(f"Successfully scraped {count} articles from {self.source_name}")

    def log_error(self, error: Exception):
        """Log scraping error."""
        self.logger.error(f"Error scraping {self.source_name}: {error}")
