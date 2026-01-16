"""SQLAlchemy models for the AI news site."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class ArticlePriority(str, PyEnum):
    """Priority levels for articles."""
    FEATURED = "featured"
    HIGH = "high"
    MEDIUM = "medium"


class Event(Base):
    """Raw scraped news event."""

    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_url = Column(String(2000), nullable=False, unique=True)
    source_name = Column(String(200), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    raw_content = Column(Text, nullable=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False, index=True)

    # Relationship to article
    articles: Mapped[list["Article"]] = relationship(back_populates="event")

    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title[:50]}...)>"


class Article(Base):
    """LLM-generated news article."""

    __tablename__ = "articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(String(500), nullable=False)
    section = Column(String(100), nullable=False, index=True)
    priority = Column(Enum(ArticlePriority), default=ArticlePriority.MEDIUM, index=True)
    writer_persona = Column(String(200), nullable=False)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to event
    event: Mapped["Event"] = relationship(back_populates="articles")

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title[:50]}...)>"


class Writer(Base):
    """Writer persona definitions for LLM article generation."""

    __tablename__ = "writers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    persona = Column(String(200), nullable=False)
    style_description = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Writer(id={self.id}, name={self.name})>"
