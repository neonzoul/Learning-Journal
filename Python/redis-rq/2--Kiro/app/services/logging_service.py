"""
Logging service for job status management.
Handles database operations for job audit logging.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlmodel import select

from app.infrastructure.database import JobLog


class LoggingService:
    """
    Service for managing job status persistence.
    Provides methods for creating and updating job logs in the database.
    """
    
    def __init__(self, db_session: Session):
        """Initialize logging service with database session."""
        self.db_session = db_session
    
    def create_job_log(
        self,
        job_id: UUID,
        filename: Optional[str] = None,
        notion_database_id: Optional[str] = None
    ) -> JobLog:
        """
        Create initial job log entry.
        
        Args:
            job_id: Unique job identifier
            filename: Original filename of uploaded image
            notion_database_id: Target Notion database ID
            
        Returns:
            Created JobLog instance
            
        Raises:
            Exception: If job_id already exists or database operation fails
        """
        try:
            # Check if job already exists
            existing_job = self.db_session.get(JobLog, job_id)
            if existing_job:
                raise ValueError(f"Job with ID {job_id} already exists")
            
            # Create new job log
            job_log = JobLog(
                job_id=job_id,
                status="queued",
                filename=filename,
                notion_database_id=notion_database_id,
                created_at=datetime.utcnow()
            )
            
            self.db_session.add(job_log)
            self.db_session.commit()
            self.db_session.refresh(job_log)
            
            return job_log
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def update_job_status(
        self,
        job_id: UUID,
        status: str,
        result_message: Optional[str] = None,
        notion_page_url: Optional[str] = None
    ) -> Optional[JobLog]:
        """
        Update job status and completion details.
        
        Args:
            job_id: Job identifier to update
            status: New job status (success, failure, processing, etc.)
            result_message: Optional success or error message
            notion_page_url: Optional URL of created Notion page
            
        Returns:
            Updated JobLog instance or None if job not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Find existing job
            job_log = self.db_session.get(JobLog, job_id)
            if not job_log:
                return None
            
            # Update job status and completion details
            job_log.status = status
            job_log.completed_at = datetime.utcnow()
            
            if result_message:
                job_log.result_message = result_message
            
            if notion_page_url:
                job_log.notion_page_url = notion_page_url
            
            self.db_session.commit()
            self.db_session.refresh(job_log)
            
            return job_log
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def get_job_log(self, job_id: UUID) -> Optional[JobLog]:
        """
        Retrieve job log by ID.
        
        Args:
            job_id: Job identifier to retrieve
            
        Returns:
            JobLog instance or None if not found
        """
        return self.db_session.get(JobLog, job_id)
    
    def get_jobs_by_status(self, status: str, limit: int = 100) -> list[JobLog]:
        """
        Retrieve jobs by status with optional limit.
        
        Args:
            status: Job status to filter by
            limit: Maximum number of jobs to return
            
        Returns:
            List of JobLog instances matching the status
        """
        statement = (
            select(JobLog)
            .where(JobLog.status == status)
            .order_by(JobLog.created_at.desc())
            .limit(limit)
        )
        
        result = self.db_session.execute(statement)
        return list(result.scalars().all())
    
    def get_recent_jobs(self, limit: int = 50) -> list[JobLog]:
        """
        Retrieve most recent jobs regardless of status.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of JobLog instances ordered by creation time
        """
        statement = (
            select(JobLog)
            .order_by(JobLog.created_at.desc())
            .limit(limit)
        )
        
        result = self.db_session.execute(statement)
        return list(result.scalars().all())