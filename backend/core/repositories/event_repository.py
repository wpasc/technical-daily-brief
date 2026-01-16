"""Repository for Event model."""
from typing import List, Optional

from sqlalchemy.orm import Session

from core.models import Event
from core.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """Repository for Event operations."""

    def __init__(self, db: Session):
        """Initialize with Event model."""
        super().__init__(Event, db)

    def get_by_url(self, source_url: str) -> Optional[Event]:
        """
        Get event by source URL.

        Args:
            source_url: The source URL to look up

        Returns:
            Event or None
        """
        return self.db.query(Event).filter(Event.source_url == source_url).first()

    def get_unprocessed(self, limit: int = 100) -> List[Event]:
        """
        Get events that haven't been processed yet.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of unprocessed events
        """
        return (
            self.db.query(Event)
            .filter(Event.processed == False)
            .order_by(Event.scraped_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_source(self, source_name: str, limit: int = 100) -> List[Event]:
        """
        Get events from a specific source.

        Args:
            source_name: Name of the news source
            limit: Maximum number of events to return

        Returns:
            List of events from the source
        """
        return (
            self.db.query(Event)
            .filter(Event.source_name == source_name)
            .order_by(Event.scraped_at.desc())
            .limit(limit)
            .all()
        )

    def mark_processed(self, event_id: str) -> Optional[Event]:
        """
        Mark an event as processed.

        Args:
            event_id: ID of the event

        Returns:
            Updated event or None
        """
        return self.update(event_id, processed=True)

    def url_exists(self, source_url: str) -> bool:
        """
        Check if a URL already exists in the database.

        Args:
            source_url: URL to check

        Returns:
            True if exists, False otherwise
        """
        return self.db.query(Event).filter(Event.source_url == source_url).count() > 0
