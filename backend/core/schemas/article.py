"""Pydantic schemas for Article model."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from core.models.models import ArticlePriority


class ArticleCreate(BaseModel):
    """Schema for creating a new article."""

    event_id: Optional[str] = None
    title: str = Field(..., max_length=500)
    content: str
    excerpt: str = Field(..., max_length=500)
    section: str = Field(..., max_length=100)
    priority: ArticlePriority = ArticlePriority.MEDIUM
    writer_persona: str = Field(..., max_length=200)


class ArticleResponse(BaseModel):
    """Schema for article response."""

    id: str
    event_id: Optional[str]
    title: str
    content: str
    excerpt: str
    section: str
    priority: str
    writer_persona: str
    published_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
