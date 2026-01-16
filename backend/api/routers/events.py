"""Event API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_event_repository
from core.database.session import get_db
from core.repositories import EventRepository
from core.schemas import EventCreate, EventResponse, EventUpdate

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=List[EventResponse])
def list_events(
    processed: Optional[bool] = Query(None, description="Filter by processed status"),
    source: Optional[str] = Query(None, description="Filter by source name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    List events with optional filters.

    Args:
        processed: Filter by processed status
        source: Filter by source name
        skip: Number of records to skip
        limit: Maximum records to return
        db: Database session

    Returns:
        List of events
    """
    repo = get_event_repository(db)

    if processed is False:
        return repo.get_unprocessed(limit=limit)
    elif source:
        return repo.get_by_source(source, limit=limit)
    else:
        return repo.get_all(skip=skip, limit=limit)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific event by ID.

    Args:
        event_id: Event ID
        db: Database session

    Returns:
        Event data

    Raises:
        HTTPException: If event not found
    """
    repo = get_event_repository(db)
    event = repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("", response_model=EventResponse, status_code=201)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new event.

    Args:
        event_data: Event creation data
        db: Database session

    Returns:
        Created event

    Raises:
        HTTPException: If URL already exists
    """
    repo = get_event_repository(db)

    # Check for duplicate URL
    if repo.url_exists(event_data.source_url):
        raise HTTPException(status_code=409, detail="Event with this URL already exists")

    event = repo.create(**event_data.model_dump())
    db.commit()
    return event


@router.patch("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: str,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an event.

    Args:
        event_id: Event ID
        event_data: Update data
        db: Database session

    Returns:
        Updated event

    Raises:
        HTTPException: If event not found
    """
    repo = get_event_repository(db)
    event = repo.update(event_id, **event_data.model_dump(exclude_unset=True))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.commit()
    return event
