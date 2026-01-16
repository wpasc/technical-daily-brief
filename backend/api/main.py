"""FastAPI application for the AI News Site."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import events_router, articles_router, health_router, writers_router
from core.database.session import init_db
from core.logging_config import setup_logging

# Setup logging
setup_logging()

# Initialize database on startup
init_db()

app = FastAPI(
    title="AI News Site API",
    description="API for AI-generated news articles from open-source feeds",
    version="1.0.0",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost",
        "http://localhost:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(events_router)
app.include_router(articles_router)
app.include_router(writers_router)


@app.get("/")
def root() -> dict:
    """Root endpoint."""
    return {
        "message": "AI News Site API",
        "docs": "/docs",
        "health": "/api/health",
    }
