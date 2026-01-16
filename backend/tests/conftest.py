"""Shared test fixtures for news_site backend tests.

This module provides database fixtures following the patterns from
prediction_market_analysis with transaction rollback isolation.
"""
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.models import Base, Event, Article, Writer
from core.models.models import ArticlePriority


# -----------------------------------------------------------------------------
# Database Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def test_db_url():
    """Session-scoped database URL for testing."""
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine(test_db_url):
    """Session-scoped database engine.

    Creates a SQLite in-memory database engine for fast testing.
    """
    eng = create_engine(
        test_db_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    return eng


@pytest.fixture(scope="session")
def tables(engine):
    """Session-scoped table creation/teardown.

    Creates all tables at the start of the test session and drops them
    at the end. This is more efficient than creating tables per test.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine, tables):
    """Function-scoped database session with transaction rollback.

    Each test gets a fresh transaction that is rolled back after the test,
    ensuring test isolation without the overhead of recreating tables.
    """
    connection = engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    # Only rollback if transaction is still active (not already rolled back
    # due to IntegrityError or similar)
    if transaction.is_active:
        transaction.rollback()
    connection.close()


# -----------------------------------------------------------------------------
# Model Data Fixtures (dictionaries)
# -----------------------------------------------------------------------------


@pytest.fixture
def sample_event_data():
    """Sample event data dictionary for testing."""
    return {
        "source_url": f"https://example.com/news/{uuid.uuid4()}",
        "source_name": "Example News",
        "title": "Test Event Title",
        "raw_content": "This is the raw content of the test event.",
        "processed": False,
    }


@pytest.fixture
def sample_article_data():
    """Sample article data dictionary for testing."""
    return {
        "title": "Test Article Title",
        "content": "This is the full content of the test article.",
        "excerpt": "This is the article excerpt for preview.",
        "section": "technology",
        "priority": ArticlePriority.MEDIUM,
        "writer_persona": "Tech Reporter",
    }


@pytest.fixture
def sample_writer_data():
    """Sample writer data dictionary for testing."""
    return {
        "name": f"Test Writer {uuid.uuid4().hex[:6]}",
        "persona": "A seasoned technology journalist",
        "style_description": "Writes with clarity and depth, focusing on impact.",
    }


# -----------------------------------------------------------------------------
# Model Instance Fixtures (committed to database)
# -----------------------------------------------------------------------------


@pytest.fixture
def sample_event(db_session, sample_event_data):
    """Create and commit a sample Event to the database."""
    event = Event(**sample_event_data)
    db_session.add(event)
    db_session.flush()
    return event


@pytest.fixture
def sample_processed_event(db_session):
    """Create and commit a processed Event to the database."""
    event = Event(
        source_url=f"https://example.com/processed/{uuid.uuid4()}",
        source_name="Example News",
        title="Processed Event",
        raw_content="Content of processed event.",
        processed=True,
    )
    db_session.add(event)
    db_session.flush()
    return event


@pytest.fixture
def sample_article(db_session, sample_event, sample_article_data):
    """Create and commit a sample Article linked to an event."""
    article_data = sample_article_data.copy()
    article_data["event_id"] = sample_event.id
    article = Article(**article_data)
    db_session.add(article)
    db_session.flush()
    return article


@pytest.fixture
def sample_featured_article(db_session):
    """Create and commit a featured Article."""
    article = Article(
        title="Featured Article",
        content="This is a featured article with priority.",
        excerpt="Featured article excerpt.",
        section="politics",
        priority=ArticlePriority.FEATURED,
        writer_persona="Senior Correspondent",
    )
    db_session.add(article)
    db_session.flush()
    return article


@pytest.fixture
def sample_writer(db_session, sample_writer_data):
    """Create and commit a sample Writer to the database."""
    writer = Writer(**sample_writer_data)
    db_session.add(writer)
    db_session.flush()
    return writer


# -----------------------------------------------------------------------------
# Pytest Configuration
# -----------------------------------------------------------------------------


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: marks test as a unit test")
    config.addinivalue_line("markers", "db: marks test as requiring database")
    config.addinivalue_line("markers", "integration: marks test as integration test")
