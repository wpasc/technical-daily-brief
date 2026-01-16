"""Unit tests for SQLAlchemy models.

Tests Event, Article, and Writer models for proper field handling,
defaults, constraints, and relationships.
"""
import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from core.models import Base, Event, Article, Writer
from core.models.models import ArticlePriority


# -----------------------------------------------------------------------------
# Event Model Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.db
class TestEventModel:
    """Tests for the Event model."""

    def test_create_event_minimal_fields(self, db_session):
        """Test creating an Event with only required fields.

        Arrange: Prepare minimal event data
        Act: Create and persist the event
        Assert: Event is created with auto-generated ID and defaults
        """
        # Arrange
        source_url = f"https://example.com/{uuid.uuid4()}"

        # Act
        event = Event(
            source_url=source_url,
            source_name="Test Source",
            title="Test Title",
            raw_content="Test content",
        )
        db_session.add(event)
        db_session.flush()

        # Assert
        assert event.id is not None
        assert len(event.id) == 36  # UUID format
        assert event.source_url == source_url
        assert event.processed is False  # default
        assert event.scraped_at is not None

    def test_create_event_all_fields(self, db_session):
        """Test creating an Event with all fields specified.

        Arrange: Prepare full event data including processed flag
        Act: Create and persist the event
        Assert: All fields are stored correctly
        """
        # Arrange
        event_id = str(uuid.uuid4())
        source_url = f"https://news.example.com/{uuid.uuid4()}"

        # Act
        event = Event(
            id=event_id,
            source_url=source_url,
            source_name="News Site",
            title="Breaking News",
            raw_content="Full article content here",
            processed=True,
        )
        db_session.add(event)
        db_session.flush()

        # Assert
        assert event.id == event_id
        assert event.source_url == source_url
        assert event.source_name == "News Site"
        assert event.title == "Breaking News"
        assert event.raw_content == "Full article content here"
        assert event.processed is True

    def test_event_unique_source_url_constraint(self, db_session):
        """Test that source_url must be unique across events.

        Arrange: Create an event with a specific URL
        Act: Attempt to create another event with the same URL
        Assert: IntegrityError is raised
        """
        # Arrange
        source_url = f"https://unique.example.com/{uuid.uuid4()}"
        event1 = Event(
            source_url=source_url,
            source_name="Source 1",
            title="Title 1",
            raw_content="Content 1",
        )
        db_session.add(event1)
        db_session.flush()

        # Act & Assert
        event2 = Event(
            source_url=source_url,  # duplicate URL
            source_name="Source 2",
            title="Title 2",
            raw_content="Content 2",
        )
        db_session.add(event2)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_event_repr(self, sample_event):
        """Test the string representation of an Event.

        Arrange: Use sample_event fixture
        Act: Get the repr string
        Assert: Repr includes id and truncated title
        """
        # Act
        repr_str = repr(sample_event)

        # Assert
        assert sample_event.id in repr_str
        assert "Event" in repr_str

    def test_event_articles_relationship(self, db_session, sample_event, sample_article_data):
        """Test that Event has a working articles relationship.

        Arrange: Create an event and an article linked to it
        Act: Access the articles relationship
        Assert: The article is in the event's articles list
        """
        # Arrange
        article_data = sample_article_data.copy()
        article_data["event_id"] = sample_event.id
        article = Article(**article_data)
        db_session.add(article)
        db_session.flush()

        # Act
        db_session.refresh(sample_event)
        articles = sample_event.articles

        # Assert
        assert len(articles) == 1
        assert articles[0].id == article.id


# -----------------------------------------------------------------------------
# Article Model Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.db
class TestArticleModel:
    """Tests for the Article model."""

    def test_create_article_minimal_fields(self, db_session):
        """Test creating an Article with only required fields.

        Arrange: Prepare minimal article data
        Act: Create and persist the article
        Assert: Article is created with auto-generated ID and defaults
        """
        # Arrange & Act
        article = Article(
            title="Article Title",
            content="Full article content",
            excerpt="Article excerpt",
            section="tech",
            writer_persona="Tech Reporter",
        )
        db_session.add(article)
        db_session.flush()

        # Assert
        assert article.id is not None
        assert len(article.id) == 36  # UUID format
        assert article.priority == ArticlePriority.MEDIUM  # default
        assert article.event_id is None  # nullable
        assert article.published_at is not None
        assert article.created_at is not None

    def test_create_article_all_fields(self, db_session, sample_event):
        """Test creating an Article with all fields specified.

        Arrange: Prepare full article data with event reference
        Act: Create and persist the article
        Assert: All fields are stored correctly
        """
        # Arrange
        article_id = str(uuid.uuid4())

        # Act
        article = Article(
            id=article_id,
            event_id=sample_event.id,
            title="Featured Story",
            content="Full story content here",
            excerpt="Story excerpt for preview",
            section="politics",
            priority=ArticlePriority.FEATURED,
            writer_persona="Senior Reporter",
        )
        db_session.add(article)
        db_session.flush()

        # Assert
        assert article.id == article_id
        assert article.event_id == sample_event.id
        assert article.title == "Featured Story"
        assert article.priority == ArticlePriority.FEATURED
        assert article.section == "politics"

    def test_article_priority_enum_values(self, db_session):
        """Test that ArticlePriority enum values work correctly.

        Arrange: Prepare article data for each priority level
        Act: Create articles with each priority
        Assert: Priorities are stored and retrieved correctly
        """
        # Arrange & Act
        priorities = [
            ArticlePriority.FEATURED,
            ArticlePriority.HIGH,
            ArticlePriority.MEDIUM,
        ]

        for priority in priorities:
            article = Article(
                title=f"Article {priority.value}",
                content="Content",
                excerpt="Excerpt",
                section="test",
                priority=priority,
                writer_persona="Reporter",
            )
            db_session.add(article)

        db_session.flush()

        # Assert
        articles = db_session.query(Article).filter(
            Article.section == "test"
        ).all()
        stored_priorities = {a.priority for a in articles}
        assert stored_priorities == set(priorities)

    def test_article_repr(self, sample_article):
        """Test the string representation of an Article.

        Arrange: Use sample_article fixture
        Act: Get the repr string
        Assert: Repr includes id and Article class name
        """
        # Act
        repr_str = repr(sample_article)

        # Assert
        assert sample_article.id in repr_str
        assert "Article" in repr_str

    def test_article_event_relationship(self, db_session, sample_event, sample_article_data):
        """Test that Article has a working event relationship.

        Arrange: Create an article linked to an event
        Act: Access the event relationship
        Assert: The event is accessible through the relationship
        """
        # Arrange
        article_data = sample_article_data.copy()
        article_data["event_id"] = sample_event.id
        article = Article(**article_data)
        db_session.add(article)
        db_session.flush()

        # Act
        db_session.refresh(article)
        event = article.event

        # Assert
        assert event is not None
        assert event.id == sample_event.id

    def test_article_without_event(self, db_session, sample_article_data):
        """Test that Article can be created without an event.

        Arrange: Prepare article data without event_id
        Act: Create and persist the article
        Assert: Article is created with null event_id
        """
        # Arrange
        article_data = sample_article_data.copy()
        article_data.pop("event_id", None)

        # Act
        article = Article(**article_data)
        db_session.add(article)
        db_session.flush()

        # Assert
        assert article.event_id is None
        assert article.event is None


# -----------------------------------------------------------------------------
# Writer Model Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.db
class TestWriterModel:
    """Tests for the Writer model."""

    def test_create_writer_minimal_fields(self, db_session):
        """Test creating a Writer with only required fields.

        Arrange: Prepare writer data
        Act: Create and persist the writer
        Assert: Writer is created with auto-increment ID
        """
        # Arrange & Act
        writer = Writer(
            name=f"Writer {uuid.uuid4().hex[:6]}",
            persona="Test persona",
            style_description="Test style",
        )
        db_session.add(writer)
        db_session.flush()

        # Assert
        assert writer.id is not None
        assert isinstance(writer.id, int)

    def test_writer_unique_name_constraint(self, db_session):
        """Test that writer name must be unique.

        Arrange: Create a writer with a specific name
        Act: Attempt to create another writer with the same name
        Assert: IntegrityError is raised
        """
        # Arrange
        unique_name = f"Unique Writer {uuid.uuid4().hex[:6]}"
        writer1 = Writer(
            name=unique_name,
            persona="Persona 1",
            style_description="Style 1",
        )
        db_session.add(writer1)
        db_session.flush()

        # Act & Assert
        writer2 = Writer(
            name=unique_name,  # duplicate name
            persona="Persona 2",
            style_description="Style 2",
        )
        db_session.add(writer2)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_writer_repr(self, sample_writer):
        """Test the string representation of a Writer.

        Arrange: Use sample_writer fixture
        Act: Get the repr string
        Assert: Repr includes id and name
        """
        # Act
        repr_str = repr(sample_writer)

        # Assert
        assert str(sample_writer.id) in repr_str
        assert "Writer" in repr_str

    def test_writer_autoincrement_id(self, db_session):
        """Test that Writer IDs auto-increment correctly.

        Arrange: Create multiple writers
        Act: Check their IDs
        Assert: IDs are sequential integers
        """
        # Arrange & Act
        writers = []
        for i in range(3):
            writer = Writer(
                name=f"Auto Writer {uuid.uuid4().hex[:6]}",
                persona=f"Persona {i}",
                style_description=f"Style {i}",
            )
            db_session.add(writer)
            db_session.flush()
            writers.append(writer)

        # Assert
        ids = [w.id for w in writers]
        assert all(isinstance(id_, int) for id_ in ids)
        # IDs should be increasing (not necessarily by 1 in all DBs)
        assert ids == sorted(ids)
