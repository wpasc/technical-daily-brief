"""Writer persona management."""
from dataclasses import dataclass
from typing import Optional

from story_writer.prompts.system_prompts import PERSONA_PROMPTS, get_persona_for_section


@dataclass
class WriterPersona:
    """Represents a writer persona for article generation."""

    name: str
    persona: str
    style_description: str

    @classmethod
    def from_dict(cls, data: dict) -> "WriterPersona":
        """Create persona from dictionary."""
        return cls(
            name=data["name"],
            persona=data["persona"],
            style_description=data["style_description"],
        )

    @classmethod
    def for_section(cls, section: str) -> "WriterPersona":
        """Get appropriate persona for a section."""
        data = get_persona_for_section(section)
        return cls.from_dict(data)

    @classmethod
    def default(cls) -> "WriterPersona":
        """Get the default analytical reporter persona."""
        return cls.from_dict(PERSONA_PROMPTS["analytical_reporter"])


def get_all_personas() -> list[WriterPersona]:
    """Get all available personas."""
    return [WriterPersona.from_dict(p) for p in PERSONA_PROMPTS.values()]
