"""Tests for RSS entry image extraction."""
import sys
from pathlib import Path

import pytest

# scrapers lives at the project root, not under backend/
sys.path.insert(0, str(Path(__file__).parents[3]))

from scrapers.rss_scraper import RssScraper  # noqa: E402


@pytest.fixture
def scraper():
    return RssScraper(source_name="Test Wire", rss_url="https://example.com/rss")


class TestGetEntryImage:
    def test_prefers_media_thumbnail(self, scraper):
        entry = {
            "media_thumbnail": [{"url": "https://cdn.example.com/thumb.jpg"}],
            "media_content": [{"url": "https://cdn.example.com/content.jpg"}],
        }
        assert scraper._get_entry_image(entry) == "https://cdn.example.com/thumb.jpg"

    def test_picks_largest_media_content_by_width(self, scraper):
        entry = {
            "media_content": [
                {"url": "https://cdn.example.com/small.jpg", "width": "140"},
                {"url": "https://cdn.example.com/large.jpg", "width": "1024"},
                {"url": "https://cdn.example.com/medium.jpg", "width": "460"},
            ],
        }
        assert scraper._get_entry_image(entry) == "https://cdn.example.com/large.jpg"

    def test_skips_non_image_media(self, scraper):
        entry = {
            "media_content": [
                {"url": "https://cdn.example.com/clip.mp4", "medium": "video"},
            ],
        }
        assert scraper._get_entry_image(entry) is None

    def test_falls_back_to_image_enclosure_link(self, scraper):
        entry = {
            "links": [
                {"rel": "alternate", "type": "text/html", "href": "https://example.com/story"},
                {"rel": "enclosure", "type": "image/jpeg", "href": "https://cdn.example.com/enc.jpg"},
            ],
        }
        assert scraper._get_entry_image(entry) == "https://cdn.example.com/enc.jpg"

    def test_returns_none_when_no_image(self, scraper):
        assert scraper._get_entry_image({}) is None

    def test_handles_malformed_width_gracefully(self, scraper):
        entry = {
            "media_content": [
                {"url": "https://cdn.example.com/a.jpg", "width": "not-a-number"},
            ],
        }
        assert scraper._get_entry_image(entry) == "https://cdn.example.com/a.jpg"

    def test_upgrades_bbc_thumbnail_to_larger_size(self, scraper):
        entry = {
            "media_thumbnail": [
                {"url": "https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/abcd/live/img.jpg"},
            ],
        }
        assert (
            scraper._get_entry_image(entry)
            == "https://ichef.bbci.co.uk/ace/standard/800/cpsprodpb/abcd/live/img.jpg"
        )

    def test_leaves_other_cdn_urls_unchanged(self, scraper):
        entry = {
            "media_thumbnail": [
                {"url": "https://media.guim.co.uk/abc/460.jpg"},
            ],
        }
        assert scraper._get_entry_image(entry) == "https://media.guim.co.uk/abc/460.jpg"
