"""Writer API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_writer_repository
from core.database.session import get_db
from core.schemas import WriterCreate, WriterResponse

router = APIRouter(prefix="/api/writers", tags=["writers"])


@router.get("", response_model=List[WriterResponse])
def list_writers(
    db: Session = Depends(get_db),
):
    """
    List all writers.

    Args:
        db: Database session

    Returns:
        List of writers
    """
    repo = get_writer_repository(db)
    return repo.get_all()


@router.get("/{writer_id}", response_model=WriterResponse)
def get_writer(
    writer_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific writer by ID.

    Args:
        writer_id: Writer ID
        db: Database session

    Returns:
        Writer data

    Raises:
        HTTPException: If writer not found
    """
    repo = get_writer_repository(db)
    writer = repo.get_by_id(writer_id)
    if not writer:
        raise HTTPException(status_code=404, detail="Writer not found")
    return writer


@router.post("", response_model=WriterResponse, status_code=201)
def create_writer(
    writer_data: WriterCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new writer.

    Args:
        writer_data: Writer creation data
        db: Database session

    Returns:
        Created writer
    """
    repo = get_writer_repository(db)
    writer = repo.create(**writer_data.model_dump())
    db.commit()
    return writer
