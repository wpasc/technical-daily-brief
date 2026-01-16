"""Unit tests for API routers.

Tests events, articles, and writers endpoints using FastAPI TestClient
with mocked database sessions.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.events import router as events_router
from api.routers.articles import router as articles_router
from api.routers.writers import router as writers_router
from core.models import Event, Article, Writer
from core.models.models import ArticlePriority


# -----------------------------------------------------------------------------
# Test App Setup
# -----------------------------------------------------------------------------


def create_test_app():
    """Create a FastAPI app with routers for testing."""
    app = FastAPI()
    app.include_router(events_router)
    app.include_router(articles_router)
    app.include_router(writers_router)
    return app


# -----------------------------------------------------------------------------
# Mock Helpers
# -----------------------------------------------------------------------------


def create_mock_event(
    id=None,
    source_url=None,
    source_name="Test Source",
    title="Test Event",
    raw_content="Test content",
    processed=False,
):
    """Create a mock Event object."""
    mock = Mock(spec=Event)
    mock.id = id or str(uuid.uuid4())
    mock.source_url = source_url or f"https://example.com/{uuid.uuid4()}"
    mock.source_name = source_name
    mock.title = title
    mock.raw_content = raw_content
    mock.processed = processed
    mock.scraped_at = datetime.now(timezone.utc)
    return mock


def create_mock_article(
    id=None,
    event_id=None,
    title="Test Article",
    content="Test content",
    excerpt="Test excerpt",
    section="test",
    priority=ArticlePriority.MEDIUM,
    writer_persona="Test Writer",
):
    """Create a mock Article object."""
    mock = Mock(spec=Article)
    mock.id = id or str(uuid.uuid4())
    mock.event_id = event_id
    mock.title = title
    mock.content = content
    mock.excerpt = excerpt
    mock.section = section
    mock.priority = priority.value if isinstance(priority, ArticlePriority) else priority
    mock.writer_persona = writer_persona
    mock.published_at = datetime.now(timezone.utc)
    mock.created_at = datetime.now(timezone.utc)
    return mock


def create_mock_writer(
    id=None,
    name="Test Writer",
    persona="Test persona",
    style_description="Test style",
):
    """Create a mock Writer object."""
    mock = Mock(spec=Writer)
    mock.id = id or 1
    mock.name = name
    mock.persona = persona
    mock.style_description = style_description
    return mock


# -----------------------------------------------------------------------------
# Events Router Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestEventsRouter:
    """Tests for the events router endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_test_app()
        return TestClient(app)

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()

    def test_list_events_success(self, client, mock_db):
        """Test listing events returns 200 with event list.

        Arrange: Mock repository to return events
        Act: GET /api/events
        Assert: 200 status with event list
        """
        # Arrange
        mock_events = [create_mock_event(), create_mock_event()]
        mock_repo = Mock()
        mock_repo.get_all.return_value = mock_events

        with patch("api.routers.events.get_db") as mock_get_db:
            with patch("api.routers.events.get_event_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get("/api/events")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_events_with_processed_filter(self, client, mock_db):
        """Test listing events with processed=false filter.

        Arrange: Mock repository to return unprocessed events
        Act: GET /api/events?processed=false
        Assert: Repository's get_unprocessed is called
        """
        # Arrange
        mock_events = [create_mock_event(processed=False)]
        mock_repo = Mock()
        mock_repo.get_unprocessed.return_value = mock_events

        with patch("api.routers.events.get_db") as mock_get_db:
            with patch("api.routers.events.get_event_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get("/api/events?processed=false")

        # Assert
        assert response.status_code == 200
        mock_repo.get_unprocessed.assert_called_once()

    def test_list_events_with_source_filter(self, client, mock_db):
        """Test listing events with source filter.

        Arrange: Mock repository to return events from source
        Act: GET /api/events?source=TestSource
        Assert: Repository's get_by_source is called with source name
        """
        # Arrange
        mock_events = [create_mock_event(source_name="TestSource")]
        mock_repo = Mock()
        mock_repo.get_by_source.return_value = mock_events

        with patch("api.routers.events.get_db") as mock_get_db:
            with patch("api.routers.events.get_event_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get("/api/events?source=TestSource")

        # Assert
        assert response.status_code == 200
        mock_repo.get_by_source.assert_called_once_with("TestSource", limit=100)

    def test_get_event_success(self, client, mock_db):
        """Test getting a single event by ID returns 200.

        Arrange: Mock repository to return an event
        Act: GET /api/events/{id}
        Assert: 200 status with event data
        """
        # Arrange
        event_id = str(uuid.uuid4())
        mock_event = create_mock_event(id=event_id)
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = mock_event

        with patch("api.routers.events.get_db") as mock_get_db:
            with patch("api.routers.events.get_event_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get(f"/api/events/{event_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event_id

    def test_get_event_not_found(self, client, mock_db):
        """Test getting non-existent event returns 404.

        Arrange: Mock repository to return None
        Act: GET /api/events/{id}
        Assert: 404 status with error detail
        """
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None

        with patch("api.routers.events.get_db") as mock_get_db:
            with patch("api.routers.events.get_event_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get("/api/events/non-existent-id")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_event_success(self, client, mock_db):
        """Test creating an event returns 201.

        Arrange: Mock repository to create event
        Act: POST /api/events with event data
        Assert: 201 status with created event
        """
        # Arrange
        event_data = {
            "source_url": f"https://example.com/{uuid.uuid4()}",
            "source_name": "Test Source",
            "title": "Test Event",
            "raw_content": "Test content",
        }
        mock_event = create_mock_event(**event_data)
        mock_repo = Mock()
        mock_repo.url_exists.return_value = False
        mock_repo.create.return_value = mock_event

        with patch("api.routers.events.get_db") as mock_get_db:
            with patch("api.routers.events.get_event_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.post("/api/events", json=event_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == event_data["title"]

    def test_create_event_duplicate_url(self, client, mock_db):
        """Test creating event with duplicate URL returns 409.

        Arrange: Mock repository to indicate URL exists
        Act: POST /api/events with duplicate URL
        Assert: 409 status with conflict error
        """
        # Arrange
        event_data = {
            "source_url": "https://example.com/duplicate",
            "source_name": "Test Source",
            "title": "Test Event",
            "raw_content": "Test content",
        }
        mock_repo = Mock()
        mock_repo.url_exists.return_value = True

        with patch("api.routers.events.get_db") as mock_get_db:
            with patch("api.routers.events.get_event_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.post("/api/events", json=event_data)

        # Assert
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_update_event_success(self, client, mock_db):
        """Test updating an event returns 200.

        Arrange: Mock repository to update event
        Act: PATCH /api/events/{id} with update data
        Assert: 200 status with updated event
        """
        # Arrange
        event_id = str(uuid.uuid4())
        mock_event = create_mock_event(id=event_id, processed=True)
        mock_repo = Mock()
        mock_repo.update.return_value = mock_event

        with patch("api.routers.events.get_db") as mock_get_db:
            with patch("api.routers.events.get_event_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.patch(
                    f"/api/events/{event_id}",
                    json={"processed": True},
                )

        # Assert
        assert response.status_code == 200

    def test_update_event_not_found(self, client, mock_db):
        """Test updating non-existent event returns 404.

        Arrange: Mock repository to return None on update
        Act: PATCH /api/events/{id}
        Assert: 404 status
        """
        # Arrange
        mock_repo = Mock()
        mock_repo.update.return_value = None

        with patch("api.routers.events.get_db") as mock_get_db:
            with patch("api.routers.events.get_event_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.patch(
                    "/api/events/non-existent-id",
                    json={"processed": True},
                )

        # Assert
        assert response.status_code == 404


# -----------------------------------------------------------------------------
# Articles Router Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestArticlesRouter:
    """Tests for the articles router endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_test_app()
        return TestClient(app)

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()

    def test_list_articles_success(self, client, mock_db):
        """Test listing articles returns 200 with article list.

        Arrange: Mock repository to return articles
        Act: GET /api/articles
        Assert: 200 status with article list
        """
        # Arrange
        mock_articles = [create_mock_article(), create_mock_article()]
        mock_repo = Mock()
        mock_repo.get_latest.return_value = mock_articles

        with patch("api.routers.articles.get_db") as mock_get_db:
            with patch("api.routers.articles.get_article_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get("/api/articles")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_articles_with_section_filter(self, client, mock_db):
        """Test listing articles with section filter.

        Arrange: Mock repository to return articles from section
        Act: GET /api/articles?section=technology
        Assert: Repository's get_by_section is called
        """
        # Arrange
        mock_articles = [create_mock_article(section="technology")]
        mock_repo = Mock()
        mock_repo.get_by_section.return_value = mock_articles

        with patch("api.routers.articles.get_db") as mock_get_db:
            with patch("api.routers.articles.get_article_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get("/api/articles?section=technology")

        # Assert
        assert response.status_code == 200
        mock_repo.get_by_section.assert_called_once_with("technology", limit=100)

    def test_get_article_success(self, client, mock_db):
        """Test getting a single article by ID returns 200.

        Arrange: Mock repository to return an article
        Act: GET /api/articles/{id}
        Assert: 200 status with article data
        """
        # Arrange
        article_id = str(uuid.uuid4())
        mock_article = create_mock_article(id=article_id)
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = mock_article

        with patch("api.routers.articles.get_db") as mock_get_db:
            with patch("api.routers.articles.get_article_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get(f"/api/articles/{article_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article_id

    def test_get_article_not_found(self, client, mock_db):
        """Test getting non-existent article returns 404.

        Arrange: Mock repository to return None
        Act: GET /api/articles/{id}
        Assert: 404 status with error detail
        """
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None

        with patch("api.routers.articles.get_db") as mock_get_db:
            with patch("api.routers.articles.get_article_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get("/api/articles/non-existent-id")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_article_success(self, client, mock_db):
        """Test creating an article returns 201.

        Arrange: Mock repository to create article
        Act: POST /api/articles with article data
        Assert: 201 status with created article
        """
        # Arrange
        article_data = {
            "title": "Test Article",
            "content": "Test content",
            "excerpt": "Test excerpt",
            "section": "technology",
            "writer_persona": "Test Writer",
        }
        mock_article = create_mock_article(**article_data)
        mock_repo = Mock()
        mock_repo.create.return_value = mock_article

        with patch("api.routers.articles.get_db") as mock_get_db:
            with patch("api.routers.articles.get_article_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.post("/api/articles", json=article_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == article_data["title"]

    def test_create_article_with_event_id(self, client, mock_db):
        """Test creating an article with event_id.

        Arrange: Mock repository to create article with event reference
        Act: POST /api/articles with event_id
        Assert: 201 status with article having event_id
        """
        # Arrange
        event_id = str(uuid.uuid4())
        article_data = {
            "event_id": event_id,
            "title": "Test Article",
            "content": "Test content",
            "excerpt": "Test excerpt",
            "section": "technology",
            "writer_persona": "Test Writer",
        }
        mock_article = create_mock_article(**article_data)
        mock_repo = Mock()
        mock_repo.create.return_value = mock_article

        with patch("api.routers.articles.get_db") as mock_get_db:
            with patch("api.routers.articles.get_article_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.post("/api/articles", json=article_data)

        # Assert
        assert response.status_code == 201


# -----------------------------------------------------------------------------
# Writers Router Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestWritersRouter:
    """Tests for the writers router endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_test_app()
        return TestClient(app)

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()

    def test_list_writers_success(self, client, mock_db):
        """Test listing writers returns 200 with writer list.

        Arrange: Mock repository to return writers
        Act: GET /api/writers
        Assert: 200 status with writer list
        """
        # Arrange
        mock_writers = [
            create_mock_writer(id=1, name="Writer One"),
            create_mock_writer(id=2, name="Writer Two"),
        ]
        mock_repo = Mock()
        mock_repo.get_all.return_value = mock_writers

        with patch("api.routers.writers.get_db") as mock_get_db:
            with patch("api.routers.writers.get_writer_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get("/api/writers")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_writer_success(self, client, mock_db):
        """Test getting a single writer by ID returns 200.

        Arrange: Mock repository to return a writer
        Act: GET /api/writers/{id}
        Assert: 200 status with writer data
        """
        # Arrange
        writer_id = 1
        mock_writer = create_mock_writer(id=writer_id)
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = mock_writer

        with patch("api.routers.writers.get_db") as mock_get_db:
            with patch("api.routers.writers.get_writer_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get(f"/api/writers/{writer_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == writer_id

    def test_get_writer_not_found(self, client, mock_db):
        """Test getting non-existent writer returns 404.

        Arrange: Mock repository to return None
        Act: GET /api/writers/{id}
        Assert: 404 status with error detail
        """
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None

        with patch("api.routers.writers.get_db") as mock_get_db:
            with patch("api.routers.writers.get_writer_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.get("/api/writers/99999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_writer_success(self, client, mock_db):
        """Test creating a writer returns 201.

        Arrange: Mock repository to create writer
        Act: POST /api/writers with writer data
        Assert: 201 status with created writer
        """
        # Arrange
        writer_data = {
            "name": "New Writer",
            "persona": "A skilled journalist",
            "style_description": "Clear and concise writing style",
        }
        mock_writer = create_mock_writer(**writer_data)
        mock_repo = Mock()
        mock_repo.create.return_value = mock_writer

        with patch("api.routers.writers.get_db") as mock_get_db:
            with patch("api.routers.writers.get_writer_repository") as mock_get_repo:
                mock_get_db.return_value = iter([mock_db])
                mock_get_repo.return_value = mock_repo

                # Act
                response = client.post("/api/writers", json=writer_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == writer_data["name"]
