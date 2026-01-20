"""Health check endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "news-site-api",
        "version": "1.0.0",
    }


# Lightweight healthz endpoint for infrastructure health checks (no /api prefix)
healthz_router = APIRouter(tags=["health"])


@healthz_router.get("/healthz")
def healthz() -> dict:
    """
    Lightweight health check endpoint for infrastructure monitoring.
    Required by Hetzner VPS infrastructure (project_infra app contract).

    Returns:
        Simple health status
    """
    return {"status": "healthy"}
