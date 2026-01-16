"""Repository for Writer model."""
from typing import Optional

from sqlalchemy.orm import Session

from core.models import Writer
from core.repositories.base import BaseRepository


class WriterRepository(BaseRepository[Writer]):
    """Repository for Writer operations."""

    def __init__(self, db: Session):
        """Initialize with Writer model."""
        super().__init__(Writer, db)

    def get_by_name(self, name: str) -> Optional[Writer]:
        """
        Get writer by name.

        Args:
            name: Writer name

        Returns:
            Writer or None
        """
        return self.db.query(Writer).filter(Writer.name == name).first()
