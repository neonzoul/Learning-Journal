"""
Main application entry point for the Accounting Automation Backend.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.settings import settings
from app.infrastructure.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database
    init_database()
    yield
    # Shutdown: Cleanup if needed
    pass


# Create FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    description="Backend API for automated receipt processing and Notion integration",
    lifespan=lifespan
)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity check."""
    from app.infrastructure.database import db_manager
    
    db_healthy = db_manager.health_check()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": settings.PROJECT_NAME,
        "database": "connected" if db_healthy else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )