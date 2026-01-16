"""Base repository with common database operations."""
from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from core.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize the repository.

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    def get_by_id(self, id_value: any) -> Optional[ModelType]:
        """
        Get a single record by primary key.

        Args:
            id_value: Primary key value

        Returns:
            Model instance or None
        """
        return self.db.query(self.model).filter_by(**self._get_pk_filter(id_value)).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def count(self) -> int:
        """
        Count total records.

        Returns:
            Total count
        """
        return self.db.query(self.model).count()

    def create(self, **data) -> ModelType:
        """
        Create a new record.

        Args:
            **data: Field values

        Returns:
            Created model instance
        """
        instance = self.model(**data)
        self.db.add(instance)
        self.db.flush()
        return instance

    def update(self, id_value: any, **data) -> Optional[ModelType]:
        """
        Update a record by primary key.

        Args:
            id_value: Primary key value
            **data: Fields to update

        Returns:
            Updated model instance or None
        """
        instance = self.get_by_id(id_value)
        if instance:
            for key, value in data.items():
                if value is not None:
                    setattr(instance, key, value)
            self.db.flush()
        return instance

    def delete(self, id_value: any) -> bool:
        """
        Delete a record by primary key.

        Args:
            id_value: Primary key value

        Returns:
            True if deleted, False if not found
        """
        instance = self.get_by_id(id_value)
        if instance:
            self.db.delete(instance)
            self.db.flush()
            return True
        return False

    def _get_pk_filter(self, id_value: any) -> dict:
        """
        Get primary key filter dict.

        Args:
            id_value: Primary key value

        Returns:
            Filter dictionary
        """
        pk_columns = [col.name for col in self.model.__table__.primary_key.columns]
        if len(pk_columns) == 1:
            return {pk_columns[0]: id_value}
        else:
            raise NotImplementedError("Composite primary keys not yet supported")
