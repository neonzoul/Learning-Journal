"""
FastAPI dependency injection functions.
Provides database sessions and service instances for request handling.
"""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_database_session
from app.infrastructure.queue import RQService, create_queue_service
from app.services.logging_service import LoggingService
from app.services.task_service import TaskService


def get_logging_service(
    db_session: Session = Depends(get_database_session)
) -> LoggingService:
    """
    FastAPI dependency for logging service injection.
    
    Args:
        db_session: Database session from dependency injection
        
    Returns:
        LoggingService instance configured with the database session
    """
    return LoggingService(db_session)


def get_queue_service() -> RQService:
    """
    FastAPI dependency for queue service injection.
    
    Returns:
        RQService instance configured with Redis connection
        
    Raises:
        QueueConnectionError: If unable to connect to Redis
    """
    return create_queue_service()


def get_task_service(
    queue_service: RQService = Depends(get_queue_service),
    logging_service: LoggingService = Depends(get_logging_service)
) -> TaskService:
    """
    FastAPI dependency for task service injection.
    
    Args:
        queue_service: Queue service from dependency injection
        logging_service: Logging service from dependency injection
        
    Returns:
        TaskService instance configured with protocol-based dependencies
    """
    return TaskService(
        queue_service=queue_service,
        logging_service=logging_service
    )