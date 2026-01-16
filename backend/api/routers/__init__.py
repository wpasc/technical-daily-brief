"""API routers."""
from .events import router as events_router
from .articles import router as articles_router
from .health import router as health_router
from .writers import router as writers_router

__all__ = ["events_router", "articles_router", "health_router", "writers_router"]
