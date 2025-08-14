"""
Main application entry point for the Accounting Automation Backend.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis

from app.api.v1.api import api_router
from app.core.settings import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.middleware import (
    ErrorHandlingMiddleware,
    RequestLoggingMiddleware,
    MetricsMiddleware
)
from app.infrastructure.database import init_database
from app.infrastructure.queue import create_queue_service, QueueConnectionError


# Setup structured logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    enable_json_logging=settings.ENABLE_JSON_LOGGING,
    log_file=settings.LOG_FILE
)
logger = get_logger(__name__)

# Optional RQ Dashboard import
try:
    import rq_dashboard
    RQ_DASHBOARD_AVAILABLE = True
except ImportError:
    RQ_DASHBOARD_AVAILABLE = False
    logger.warning("RQ Dashboard not available - install rq-dashboard package for queue monitoring")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    logger.info("Starting up Accounting Automation Backend...")
    
    # Startup: Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Test Redis connection
    try:
        queue_service = create_queue_service()
        queue_info = queue_service.get_queue_info()
        logger.info(f"Redis queue connected successfully: {queue_info}")
        queue_service.close()
    except QueueConnectionError as e:
        logger.error(f"Failed to connect to Redis queue: {e}")
        raise
    
    logger.info("Application startup completed successfully")
    
    yield
    
    # Shutdown: Cleanup if needed
    logger.info("Shutting down Accounting Automation Backend...")


# Create FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    description="Backend API for automated receipt processing and Notion integration",
    lifespan=lifespan
)

# Add middleware in reverse order (last added = first executed)
# Error handling middleware (outermost)
app.add_middleware(ErrorHandlingMiddleware)

# Request logging middleware
app.add_middleware(
    RequestLoggingMiddleware,
    log_requests=settings.LOG_REQUESTS,
    log_responses=settings.LOG_RESPONSES
)

# Metrics collection middleware
app.add_middleware(MetricsMiddleware)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount RQ Dashboard for queue monitoring (if available)
if RQ_DASHBOARD_AVAILABLE:
    try:
        # Create Redis connection for RQ Dashboard
        redis_conn = redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # Configure RQ Dashboard
        rq_dashboard.default_settings.REDIS_URL = settings.REDIS_URL
        rq_dashboard.default_settings.REDIS_HOST = redis_conn.connection_pool.connection_kwargs.get('host', 'localhost')
        rq_dashboard.default_settings.REDIS_PORT = redis_conn.connection_pool.connection_kwargs.get('port', 6379)
        rq_dashboard.default_settings.REDIS_DB = redis_conn.connection_pool.connection_kwargs.get('db', 0)
        
        # Mount RQ Dashboard at /rq endpoint
        app.mount("/rq", rq_dashboard.web)
        logger.info("RQ Dashboard mounted at /rq endpoint")
        
    except Exception as e:
        logger.warning(f"Failed to mount RQ Dashboard: {e}")
else:
    logger.info("RQ Dashboard not available - queue monitoring via /monitoring/queue endpoint only")


# Health check endpoint
@app.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Checks database connectivity, Redis queue status, and overall system health.
    
    Returns:
        Dict containing health status information
    """
    health_status = {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check database connectivity
    try:
        from app.infrastructure.database import db_manager
        db_healthy = db_manager.health_check()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "message": "Connected" if db_healthy else "Connection failed"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Error: {str(e)}"
        }
        health_status["status"] = "degraded"
    
    # Check Redis queue connectivity
    try:
        queue_service = create_queue_service()
        queue_info = queue_service.get_queue_info()
        health_status["checks"]["redis_queue"] = {
            "status": "healthy",
            "message": "Connected",
            "queue_info": queue_info
        }
        queue_service.close()
    except QueueConnectionError as e:
        health_status["checks"]["redis_queue"] = {
            "status": "unhealthy",
            "message": f"Connection failed: {str(e)}"
        }
        health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["redis_queue"] = {
            "status": "unhealthy",
            "message": f"Error: {str(e)}"
        }
        health_status["status"] = "degraded"
    
    # Set overall status based on critical components
    if health_status["checks"].get("database", {}).get("status") == "unhealthy":
        health_status["status"] = "unhealthy"
    
    return health_status


# Queue monitoring endpoint
@app.get("/monitoring/queue")
async def queue_status() -> Dict[str, Any]:
    """
    Get detailed queue status and metrics.
    
    Returns:
        Dict containing queue statistics and worker information
        
    Raises:
        HTTPException: If unable to connect to queue backend
    """
    try:
        queue_service = create_queue_service()
        queue_info = queue_service.get_queue_info()
        queue_service.close()
        
        return {
            "queue_status": queue_info,
            "dashboard_url": "/rq",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except QueueConnectionError as e:
        logger.error(f"Queue status check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Queue service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in queue status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Application metrics endpoint
@app.get("/monitoring/metrics")
async def application_metrics() -> Dict[str, Any]:
    """
    Get application performance metrics.
    
    Returns:
        Dict containing application metrics and statistics
    """
    try:
        # Simple metrics for now - can be enhanced later
        return {
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": {
                "message": "Detailed metrics collection available via structured logs"
            },
            "uptime_info": {
                "message": "Application is running"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect application metrics: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Accounting Automation Backend server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )