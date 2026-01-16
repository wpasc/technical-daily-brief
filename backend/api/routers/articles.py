"""Article API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_article_repository
from core.database.session import get_db
from core.schemas import ArticleCreate, ArticleResponse

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=List[ArticleResponse])
def list_articles(
    section: Optional[str] = Query(None, description="Filter by section"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    List articles with optional filters.

    Args:
        section: Filter by section name
        priority: Filter by priority level
        skip: Number of records to skip
        limit: Maximum records to return
        db: Database session

    Returns:
        List of articles
    """
    repo = get_article_repository(db)

    if section:
        return repo.get_by_section(section, limit=limit)
    else:
        return repo.get_latest(limit=limit)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific article by ID.

    Args:
        article_id: Article ID
        db: Database session

    Returns:
        Article data

    Raises:
        HTTPException: If article not found
    """
    repo = get_article_repository(db)
    article = repo.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("", response_model=ArticleResponse, status_code=201)
def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new article.

    Args:
        article_data: Article creation data
        db: Database session

    Returns:
        Created article
    """
    repo = get_article_repository(db)
    article = repo.create(**article_data.model_dump())
    db.commit()
    return article
