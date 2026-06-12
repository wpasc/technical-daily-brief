"""Generic RSS feed scraper."""
import time
from typing import List, Optional
import logging

import feedparser
import httpx
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, ScrapedEvent

logger = logging.getLogger(__name__)


class RssScraper(BaseScraper):
    """Scraper for RSS feeds."""

    def __init__(
        self,
        source_name: str,
        rss_url: str,
        rate_limit_seconds: float = 2.0,
    ):
        """
        Initialize RSS scraper.

        Args:
            source_name: Name of the news source
            rss_url: URL of the RSS feed
            rate_limit_seconds: Seconds between requests
        """
        super().__init__(source_name, rate_limit_seconds)
        self.rss_url = rss_url
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; NewsScraper/1.0)"
            }
        )

    def scrape(self, max_articles: int = 10) -> List[ScrapedEvent]:
        """
        Scrape articles from RSS feed.

        Args:
            max_articles: Maximum articles to scrape

        Returns:
            List of scraped events
        """
        events = []

        try:
            # Fetch and parse RSS feed
            feed = feedparser.parse(self.rss_url)

            if feed.bozo:
                self.logger.warning(f"Feed parsing issue: {feed.bozo_exception}")

            entries = feed.entries[:max_articles]
            self.logger.info(f"Found {len(entries)} entries in {self.source_name} feed")

            for entry in entries:
                try:
                    event = self._process_entry(entry)
                    if event:
                        events.append(event)
                        time.sleep(self.rate_limit_seconds)
                except Exception as e:
                    self.logger.warning(f"Error processing entry: {e}")
                    continue

            self.log_success(len(events))

        except Exception as e:
            self.log_error(e)

        return events

    def _process_entry(self, entry) -> Optional[ScrapedEvent]:
        """
        Process a single RSS entry.

        Args:
            entry: Feedparser entry object

        Returns:
            ScrapedEvent or None if processing fails
        """
        # Get article URL
        link = entry.get("link")
        if not link:
            return None

        # Get title
        title = entry.get("title", "").strip()
        if not title:
            return None

        # Try to get content from RSS first
        content = self._get_rss_content(entry)

        # If RSS content is too short, fetch full article
        if len(content) < 200:
            fetched_content = self._fetch_article_content(link)
            if fetched_content and len(fetched_content) > len(content):
                content = fetched_content

        if not content or len(content) < 50:
            self.logger.warning(f"Skipping article with insufficient content: {title[:50]}")
            return None

        return ScrapedEvent(
            source_url=link,
            source_name=self.source_name,
            title=title,
            raw_content=content,
            image_url=self._get_entry_image(entry),
        )

    def _get_entry_image(self, entry) -> Optional[str]:
        """
        Extract an image URL from an RSS entry.

        Checks media:thumbnail and media:content (picking the largest
        by declared width), then image enclosure links. Most major feeds
        (BBC, Guardian, NPR) ship editorial images this way, so the photo
        actually belongs to the story.

        Args:
            entry: Feedparser entry

        Returns:
            Image URL or None
        """
        for key in ("media_thumbnail", "media_content"):
            best_url = None
            best_width = -1
            for item in entry.get(key) or []:
                url = item.get("url")
                if not url:
                    continue
                medium = item.get("medium", "image")
                if medium != "image":
                    continue
                try:
                    width = int(item.get("width") or 0)
                except (TypeError, ValueError):
                    width = 0
                if width > best_width:
                    best_url, best_width = url, width
            if best_url:
                return self._upgrade_known_cdn_sizes(best_url)

        for link in entry.get("links") or []:
            if link.get("rel") == "enclosure" and str(link.get("type", "")).startswith("image/"):
                return self._upgrade_known_cdn_sizes(link.get("href"))

        return None

    @staticmethod
    def _upgrade_known_cdn_sizes(url: Optional[str]) -> Optional[str]:
        """
        Swap known size-parameterized CDN URLs to a larger variant.

        BBC feeds ship 240px thumbnails, but their image CDN serves the
        same asset at standard widths via the path segment.
        """
        if url and "ichef.bbci.co.uk" in url and "/standard/240/" in url:
            return url.replace("/standard/240/", "/standard/800/")
        return url

    def _get_rss_content(self, entry) -> str:
        """
        Extract content from RSS entry.

        Args:
            entry: Feedparser entry

        Returns:
            Content string
        """
        # Try content field first
        if entry.get("content"):
            content_list = entry.get("content", [])
            if content_list:
                content_html = content_list[0].get("value", "")
                return self._html_to_text(content_html)

        # Try summary
        if entry.get("summary"):
            return self._html_to_text(entry.get("summary", ""))

        # Try description
        if entry.get("description"):
            return self._html_to_text(entry.get("description", ""))

        return ""

    def _fetch_article_content(self, url: str) -> Optional[str]:
        """
        Fetch full article content from URL.

        Args:
            url: Article URL

        Returns:
            Article text content or None
        """
        try:
            response = self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script, style, and nav elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
                element.decompose()

            # Try common article content selectors
            article = None
            for selector in ["article", "[role='main']", ".article-body", ".story-body", ".post-content"]:
                article = soup.select_one(selector)
                if article:
                    break

            if article:
                return self._extract_text(article)

            # Fallback to body
            body = soup.find("body")
            if body:
                return self._extract_text(body)

            return None

        except Exception as e:
            self.logger.warning(f"Error fetching article content from {url}: {e}")
            return None

    def _extract_text(self, element) -> str:
        """
        Extract clean text from BeautifulSoup element.

        Args:
            element: BeautifulSoup element

        Returns:
            Clean text
        """
        # Get all paragraph text
        paragraphs = element.find_all("p")
        if paragraphs:
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
        else:
            text = element.get_text(separator=" ", strip=True)

        # Clean up whitespace
        text = " ".join(text.split())
        return text

    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text.

        Args:
            html: HTML string

        Returns:
            Plain text
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def close(self):
        """Close HTTP client."""
        self.client.close()
