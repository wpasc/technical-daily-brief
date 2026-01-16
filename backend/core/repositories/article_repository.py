"""Repository for Article model."""
from typing import List, Optional

from sqlalchemy.orm import Session

from core.models import Article
from core.models.models import ArticlePriority
from core.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[Article]):
    """Repository for Article operations."""

    def __init__(self, db: Session):
        """Initialize with Article model."""
        super().__init__(Article, db)

    def get_by_section(self, section: str, limit: int = 100) -> List[Article]:
        """
        Get articles by section.

        Args:
            section: Section name
            limit: Maximum number of articles to return

        Returns:
            List of articles in the section
        """
        return (
            self.db.query(Article)
            .filter(Article.section == section)
            .order_by(Article.published_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_priority(self, priority: ArticlePriority, limit: int = 100) -> List[Article]:
        """
        Get articles by priority level.

        Args:
            priority: Priority level
            limit: Maximum number of articles to return

        Returns:
            List of articles with the priority
        """
        return (
            self.db.query(Article)
            .filter(Article.priority == priority)
            .order_by(Article.published_at.desc())
            .limit(limit)
            .all()
        )

    def get_featured(self) -> Optional[Article]:
        """
        Get the most recent featured article.

        Returns:
            Featured article or None
        """
        return (
            self.db.query(Article)
            .filter(Article.priority == ArticlePriority.FEATURED)
            .order_by(Article.published_at.desc())
            .first()
        )

    def get_latest(self, limit: int = 50) -> List[Article]:
        """
        Get the latest articles.

        Args:
            limit: Maximum number of articles to return

        Returns:
            List of latest articles
        """
        return (
            self.db.query(Article)
            .order_by(Article.published_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_event(self, event_id: str) -> List[Article]:
        """
        Get articles generated from a specific event.

        Args:
            event_id: ID of the source event

        Returns:
            List of articles from the event
        """
        return (
            self.db.query(Article)
            .filter(Article.event_id == event_id)
            .all()
        )
