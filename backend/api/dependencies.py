"""FastAPI dependencies for dependency injection."""
from sqlalchemy.orm import Session

from core.database.session import get_db
from core.repositories import EventRepository, ArticleRepository, WriterRepository


def get_event_repository(db: Session) -> EventRepository:
    """
    Get EventRepository instance.

    Args:
        db: Database session

    Returns:
        EventRepository instance
    """
    return EventRepository(db)


def get_article_repository(db: Session) -> ArticleRepository:
    """
    Get ArticleRepository instance.

    Args:
        db: Database session

    Returns:
        ArticleRepository instance
    """
    return ArticleRepository(db)


def get_writer_repository(db: Session) -> WriterRepository:
    """
    Get WriterRepository instance.

    Args:
        db: Database session

    Returns:
        WriterRepository instance
    """
    return WriterRepository(db)
