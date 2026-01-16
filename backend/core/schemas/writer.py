"""Pydantic schemas for Writer model."""
from pydantic import BaseModel, Field


class WriterCreate(BaseModel):
    """Schema for creating a new writer."""

    name: str = Field(..., max_length=100)
    persona: str = Field(..., max_length=200)
    style_description: str


class WriterResponse(BaseModel):
    """Schema for writer response."""

    id: int
    name: str
    persona: str
    style_description: str

    model_config = {"from_attributes": True}
