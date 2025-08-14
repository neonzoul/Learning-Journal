"""
FastAPI dependency injection functions.
Provides database sessions and service instances for request handling.
"""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_database_session
from app.services.logging_service import LoggingService


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