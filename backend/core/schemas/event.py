"""Pydantic schemas for Event model."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Schema for creating a new event."""

    source_url: str = Field(..., max_length=2000)
    source_name: str = Field(..., max_length=200)
    title: str = Field(..., max_length=500)
    raw_content: str


class EventUpdate(BaseModel):
    """Schema for updating an event."""

    processed: Optional[bool] = None


class EventResponse(BaseModel):
    """Schema for event response."""

    id: str
    source_url: str
    source_name: str
    title: str
    raw_content: str
    scraped_at: datetime
    processed: bool

    model_config = {"from_attributes": True}
