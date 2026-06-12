"""Shared article dataclass for generation engines."""
from dataclasses import dataclass


@dataclass
class GeneratedArticle:
    """Represents a generated article."""

    headline: str
    excerpt: str
    content: str
    section: str
    priority: str
    writer_persona: str
