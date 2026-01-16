"""Unit tests for repository classes.

Tests EventRepository, ArticleRepository, and WriterRepository
for CRUD operations and custom query methods.
"""
import uuid

import pytest

from core.models import Event, Article, Writer
from core.models.models import ArticlePriority
from core.repositories import EventRepository, ArticleRepository, WriterRepository


# -----------------------------------------------------------------------------
# EventRepository Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.db
class TestEventRepository:
    """Tests for the EventRepository class."""

    def test_create_event(self, db_session, sample_event_data):
        """Test creating an event through the repository.

        Arrange: Initialize repository and prepare event data
        Act: Create event using repository
        Assert: Event is created with correct data
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act
        event = repo.create(**sample_event_data)

        # Assert
        assert event.id is not None
        assert event.source_url == sample_event_data["source_url"]
        assert event.title == sample_event_data["title"]
        assert event.processed is False

    def test_get_by_id(self, db_session, sample_event):
        """Test retrieving an event by ID.

        Arrange: Use sample_event fixture, initialize repository
        Act: Get event by ID
        Assert: Correct event is returned
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act
        event = repo.get_by_id(sample_event.id)

        # Assert
        assert event is not None
        assert event.id == sample_event.id

    def test_get_by_id_not_found(self, db_session):
        """Test getting a non-existent event returns None.

        Arrange: Initialize repository
        Act: Get event with non-existent ID
        Assert: None is returned
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act
        event = repo.get_by_id("non-existent-id")

        # Assert
        assert event is None

    def test_get_by_url(self, db_session, sample_event):
        """Test retrieving an event by source URL.

        Arrange: Use sample_event fixture, initialize repository
        Act: Get event by URL
        Assert: Correct event is returned
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act
        event = repo.get_by_url(sample_event.source_url)

        # Assert
        assert event is not None
        assert event.id == sample_event.id

    def test_get_by_url_not_found(self, db_session):
        """Test getting event by non-existent URL returns None.

        Arrange: Initialize repository
        Act: Get event with non-existent URL
        Assert: None is returned
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act
        event = repo.get_by_url("https://non-existent-url.com")

        # Assert
        assert event is None

    def test_get_all_pagination(self, db_session):
        """Test getting all events with pagination.

        Arrange: Create multiple events
        Act: Get events with skip and limit
        Assert: Correct subset is returned
        """
        # Arrange
        repo = EventRepository(db_session)
        for i in range(5):
            repo.create(
                source_url=f"https://example.com/{uuid.uuid4()}",
                source_name="Test Source",
                title=f"Event {i}",
                raw_content="Content",
            )
        db_session.flush()

        # Act
        all_events = repo.get_all(skip=0, limit=100)
        limited_events = repo.get_all(skip=0, limit=2)
        skipped_events = repo.get_all(skip=2, limit=2)

        # Assert
        assert len(all_events) == 5
        assert len(limited_events) == 2
        assert len(skipped_events) == 2

    def test_get_unprocessed(self, db_session, sample_event, sample_processed_event):
        """Test getting only unprocessed events.

        Arrange: Use fixtures for processed and unprocessed events
        Act: Get unprocessed events
        Assert: Only unprocessed events are returned
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act
        unprocessed = repo.get_unprocessed()

        # Assert
        unprocessed_ids = {e.id for e in unprocessed}
        assert sample_event.id in unprocessed_ids
        assert sample_processed_event.id not in unprocessed_ids

    def test_get_by_source(self, db_session):
        """Test getting events by source name.

        Arrange: Create events from different sources
        Act: Get events by source name
        Assert: Only events from specified source are returned
        """
        # Arrange
        repo = EventRepository(db_session)
        repo.create(
            source_url=f"https://source-a.com/{uuid.uuid4()}",
            source_name="Source A",
            title="Event A",
            raw_content="Content",
        )
        repo.create(
            source_url=f"https://source-b.com/{uuid.uuid4()}",
            source_name="Source B",
            title="Event B",
            raw_content="Content",
        )
        db_session.flush()

        # Act
        source_a_events = repo.get_by_source("Source A")
        source_b_events = repo.get_by_source("Source B")

        # Assert
        assert len(source_a_events) == 1
        assert source_a_events[0].source_name == "Source A"
        assert len(source_b_events) == 1
        assert source_b_events[0].source_name == "Source B"

    def test_mark_processed(self, db_session, sample_event):
        """Test marking an event as processed.

        Arrange: Use unprocessed sample_event
        Act: Mark event as processed
        Assert: Event is now processed
        """
        # Arrange
        repo = EventRepository(db_session)
        assert sample_event.processed is False

        # Act
        updated = repo.mark_processed(sample_event.id)

        # Assert
        assert updated is not None
        assert updated.processed is True

    def test_mark_processed_not_found(self, db_session):
        """Test marking non-existent event returns None.

        Arrange: Initialize repository
        Act: Try to mark non-existent event
        Assert: None is returned
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act
        result = repo.mark_processed("non-existent-id")

        # Assert
        assert result is None

    def test_url_exists(self, db_session, sample_event):
        """Test checking if a URL exists.

        Arrange: Use sample_event with known URL
        Act: Check if URL exists
        Assert: Existing URL returns True, non-existent returns False
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act & Assert
        assert repo.url_exists(sample_event.source_url) is True
        assert repo.url_exists("https://non-existent.com") is False

    def test_update_event(self, db_session, sample_event):
        """Test updating an event.

        Arrange: Use sample_event fixture
        Act: Update event through repository
        Assert: Event is updated correctly
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act
        updated = repo.update(sample_event.id, processed=True)

        # Assert
        assert updated is not None
        assert updated.processed is True

    def test_delete_event(self, db_session, sample_event):
        """Test deleting an event.

        Arrange: Use sample_event fixture
        Act: Delete event through repository
        Assert: Event is deleted
        """
        # Arrange
        repo = EventRepository(db_session)
        event_id = sample_event.id

        # Act
        result = repo.delete(event_id)

        # Assert
        assert result is True
        assert repo.get_by_id(event_id) is None

    def test_delete_not_found(self, db_session):
        """Test deleting non-existent event returns False.

        Arrange: Initialize repository
        Act: Try to delete non-existent event
        Assert: False is returned
        """
        # Arrange
        repo = EventRepository(db_session)

        # Act
        result = repo.delete("non-existent-id")

        # Assert
        assert result is False

    def test_count(self, db_session):
        """Test counting events.

        Arrange: Create known number of events
        Act: Count events
        Assert: Correct count is returned
        """
        # Arrange
        repo = EventRepository(db_session)
        for i in range(3):
            repo.create(
                source_url=f"https://count-test.com/{uuid.uuid4()}",
                source_name="Test",
                title=f"Event {i}",
                raw_content="Content",
            )
        db_session.flush()

        # Act
        count = repo.count()

        # Assert
        assert count == 3


# -----------------------------------------------------------------------------
# ArticleRepository Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.db
class TestArticleRepository:
    """Tests for the ArticleRepository class."""

    def test_create_article(self, db_session, sample_article_data):
        """Test creating an article through the repository.

        Arrange: Initialize repository and prepare article data
        Act: Create article using repository
        Assert: Article is created with correct data
        """
        # Arrange
        repo = ArticleRepository(db_session)

        # Act
        article = repo.create(**sample_article_data)

        # Assert
        assert article.id is not None
        assert article.title == sample_article_data["title"]
        assert article.section == sample_article_data["section"]

    def test_get_by_id(self, db_session, sample_article):
        """Test retrieving an article by ID.

        Arrange: Use sample_article fixture, initialize repository
        Act: Get article by ID
        Assert: Correct article is returned
        """
        # Arrange
        repo = ArticleRepository(db_session)

        # Act
        article = repo.get_by_id(sample_article.id)

        # Assert
        assert article is not None
        assert article.id == sample_article.id

    def test_get_by_id_not_found(self, db_session):
        """Test getting a non-existent article returns None.

        Arrange: Initialize repository
        Act: Get article with non-existent ID
        Assert: None is returned
        """
        # Arrange
        repo = ArticleRepository(db_session)

        # Act
        article = repo.get_by_id("non-existent-id")

        # Assert
        assert article is None

    def test_get_by_section(self, db_session):
        """Test getting articles by section.

        Arrange: Create articles in different sections
        Act: Get articles by section
        Assert: Only articles from specified section are returned
        """
        # Arrange
        repo = ArticleRepository(db_session)
        repo.create(
            title="Tech Article",
            content="Content",
            excerpt="Excerpt",
            section="technology",
            writer_persona="Tech Reporter",
        )
        repo.create(
            title="Politics Article",
            content="Content",
            excerpt="Excerpt",
            section="politics",
            writer_persona="Political Reporter",
        )
        db_session.flush()

        # Act
        tech_articles = repo.get_by_section("technology")
        politics_articles = repo.get_by_section("politics")

        # Assert
        assert len(tech_articles) == 1
        assert tech_articles[0].section == "technology"
        assert len(politics_articles) == 1
        assert politics_articles[0].section == "politics"

    def test_get_by_priority(self, db_session):
        """Test getting articles by priority.

        Arrange: Create articles with different priorities
        Act: Get articles by priority
        Assert: Only articles with specified priority are returned
        """
        # Arrange
        repo = ArticleRepository(db_session)
        repo.create(
            title="Featured",
            content="Content",
            excerpt="Excerpt",
            section="test",
            priority=ArticlePriority.FEATURED,
            writer_persona="Reporter",
        )
        repo.create(
            title="High Priority",
            content="Content",
            excerpt="Excerpt",
            section="test",
            priority=ArticlePriority.HIGH,
            writer_persona="Reporter",
        )
        db_session.flush()

        # Act
        featured = repo.get_by_priority(ArticlePriority.FEATURED)
        high = repo.get_by_priority(ArticlePriority.HIGH)

        # Assert
        assert len(featured) == 1
        assert featured[0].priority == ArticlePriority.FEATURED
        assert len(high) == 1
        assert high[0].priority == ArticlePriority.HIGH

    def test_get_featured(self, db_session, sample_featured_article):
        """Test getting the featured article.

        Arrange: Use sample_featured_article fixture
        Act: Get featured article
        Assert: Featured article is returned
        """
        # Arrange
        repo = ArticleRepository(db_session)

        # Act
        featured = repo.get_featured()

        # Assert
        assert featured is not None
        assert featured.priority == ArticlePriority.FEATURED

    def test_get_featured_none(self, db_session):
        """Test getting featured when none exists returns None.

        Arrange: Create only non-featured articles
        Act: Get featured article
        Assert: None is returned
        """
        # Arrange
        repo = ArticleRepository(db_session)
        repo.create(
            title="Not Featured",
            content="Content",
            excerpt="Excerpt",
            section="test",
            priority=ArticlePriority.MEDIUM,
            writer_persona="Reporter",
        )
        db_session.flush()

        # Act
        featured = repo.get_featured()

        # Assert
        assert featured is None

    def test_get_latest(self, db_session):
        """Test getting latest articles.

        Arrange: Create multiple articles
        Act: Get latest articles with limit
        Assert: Correct number of articles returned
        """
        # Arrange
        repo = ArticleRepository(db_session)
        for i in range(5):
            repo.create(
                title=f"Article {i}",
                content="Content",
                excerpt="Excerpt",
                section="test",
                writer_persona="Reporter",
            )
        db_session.flush()

        # Act
        latest_all = repo.get_latest(limit=10)
        latest_limited = repo.get_latest(limit=3)

        # Assert
        assert len(latest_all) == 5
        assert len(latest_limited) == 3

    def test_get_by_event(self, db_session, sample_event, sample_article_data):
        """Test getting articles by event ID.

        Arrange: Create articles linked to an event
        Act: Get articles by event ID
        Assert: Linked articles are returned
        """
        # Arrange
        repo = ArticleRepository(db_session)
        article_data = sample_article_data.copy()
        article_data["event_id"] = sample_event.id
        repo.create(**article_data)
        db_session.flush()

        # Act
        articles = repo.get_by_event(sample_event.id)

        # Assert
        assert len(articles) == 1
        assert articles[0].event_id == sample_event.id

    def test_get_by_event_none(self, db_session):
        """Test getting articles for non-existent event.

        Arrange: Initialize repository
        Act: Get articles for non-existent event
        Assert: Empty list is returned
        """
        # Arrange
        repo = ArticleRepository(db_session)

        # Act
        articles = repo.get_by_event("non-existent-event-id")

        # Assert
        assert articles == []

    def test_update_article(self, db_session, sample_article):
        """Test updating an article.

        Arrange: Use sample_article fixture
        Act: Update article through repository
        Assert: Article is updated correctly
        """
        # Arrange
        repo = ArticleRepository(db_session)

        # Act
        updated = repo.update(sample_article.id, title="Updated Title")

        # Assert
        assert updated is not None
        assert updated.title == "Updated Title"

    def test_delete_article(self, db_session, sample_article):
        """Test deleting an article.

        Arrange: Use sample_article fixture
        Act: Delete article through repository
        Assert: Article is deleted
        """
        # Arrange
        repo = ArticleRepository(db_session)
        article_id = sample_article.id

        # Act
        result = repo.delete(article_id)

        # Assert
        assert result is True
        assert repo.get_by_id(article_id) is None

    def test_count(self, db_session, sample_article_data):
        """Test counting articles.

        Arrange: Create known number of articles
        Act: Count articles
        Assert: Correct count is returned
        """
        # Arrange
        repo = ArticleRepository(db_session)
        for i in range(2):
            data = sample_article_data.copy()
            data["title"] = f"Article {i}"
            repo.create(**data)
        db_session.flush()

        # Act
        count = repo.count()

        # Assert
        assert count == 2


# -----------------------------------------------------------------------------
# WriterRepository Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.db
class TestWriterRepository:
    """Tests for the WriterRepository class."""

    def test_create_writer(self, db_session, sample_writer_data):
        """Test creating a writer through the repository.

        Arrange: Initialize repository and prepare writer data
        Act: Create writer using repository
        Assert: Writer is created with correct data
        """
        # Arrange
        repo = WriterRepository(db_session)

        # Act
        writer = repo.create(**sample_writer_data)

        # Assert
        assert writer.id is not None
        assert writer.name == sample_writer_data["name"]
        assert writer.persona == sample_writer_data["persona"]

    def test_get_by_id(self, db_session, sample_writer):
        """Test retrieving a writer by ID.

        Arrange: Use sample_writer fixture, initialize repository
        Act: Get writer by ID
        Assert: Correct writer is returned
        """
        # Arrange
        repo = WriterRepository(db_session)

        # Act
        writer = repo.get_by_id(sample_writer.id)

        # Assert
        assert writer is not None
        assert writer.id == sample_writer.id

    def test_get_by_id_not_found(self, db_session):
        """Test getting a non-existent writer returns None.

        Arrange: Initialize repository
        Act: Get writer with non-existent ID
        Assert: None is returned
        """
        # Arrange
        repo = WriterRepository(db_session)

        # Act
        writer = repo.get_by_id(99999)

        # Assert
        assert writer is None

    def test_get_by_name(self, db_session, sample_writer):
        """Test retrieving a writer by name.

        Arrange: Use sample_writer fixture, initialize repository
        Act: Get writer by name
        Assert: Correct writer is returned
        """
        # Arrange
        repo = WriterRepository(db_session)

        # Act
        writer = repo.get_by_name(sample_writer.name)

        # Assert
        assert writer is not None
        assert writer.id == sample_writer.id

    def test_get_by_name_not_found(self, db_session):
        """Test getting writer by non-existent name returns None.

        Arrange: Initialize repository
        Act: Get writer with non-existent name
        Assert: None is returned
        """
        # Arrange
        repo = WriterRepository(db_session)

        # Act
        writer = repo.get_by_name("Non Existent Writer")

        # Assert
        assert writer is None

    def test_get_all(self, db_session):
        """Test getting all writers.

        Arrange: Create multiple writers
        Act: Get all writers
        Assert: All writers are returned
        """
        # Arrange
        repo = WriterRepository(db_session)
        for i in range(3):
            repo.create(
                name=f"Writer {uuid.uuid4().hex[:6]}",
                persona=f"Persona {i}",
                style_description=f"Style {i}",
            )
        db_session.flush()

        # Act
        writers = repo.get_all()

        # Assert
        assert len(writers) == 3

    def test_update_writer(self, db_session, sample_writer):
        """Test updating a writer.

        Arrange: Use sample_writer fixture
        Act: Update writer through repository
        Assert: Writer is updated correctly
        """
        # Arrange
        repo = WriterRepository(db_session)

        # Act
        updated = repo.update(sample_writer.id, persona="Updated Persona")

        # Assert
        assert updated is not None
        assert updated.persona == "Updated Persona"

    def test_delete_writer(self, db_session, sample_writer):
        """Test deleting a writer.

        Arrange: Use sample_writer fixture
        Act: Delete writer through repository
        Assert: Writer is deleted
        """
        # Arrange
        repo = WriterRepository(db_session)
        writer_id = sample_writer.id

        # Act
        result = repo.delete(writer_id)

        # Assert
        assert result is True
        assert repo.get_by_id(writer_id) is None

    def test_count(self, db_session):
        """Test counting writers.

        Arrange: Create known number of writers
        Act: Count writers
        Assert: Correct count is returned
        """
        # Arrange
        repo = WriterRepository(db_session)
        for i in range(2):
            repo.create(
                name=f"Count Writer {uuid.uuid4().hex[:6]}",
                persona=f"Persona {i}",
                style_description=f"Style {i}",
            )
        db_session.flush()

        # Act
        count = repo.count()

        # Assert
        assert count == 2
