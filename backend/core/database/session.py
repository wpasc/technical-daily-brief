"""Database session management."""
import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from core.models import Base


def get_database_url() -> str:
    """Get database URL from environment or use default SQLite."""
    url = os.getenv("DATABASE_URL", "sqlite:///./data/news.db")

    # Ensure data directory exists for SQLite
    if url.startswith("sqlite:///"):
        db_path = url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    return url


# Create engine
database_url = get_database_url()
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, echo=False, connect_args=connect_args)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    # Ensure data directory exists
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db_session() -> Session:
    """
    Context manager for database sessions.

    Usage:
        with get_db_session() as db:
            db.query(Event).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db():
    """
    Dependency for FastAPI routes.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
