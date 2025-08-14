"""
Task service for business logic orchestration.

This module provides the TaskService class that orchestrates job creation,
file handling, and enqueueing operations for receipt processing workflows.
"""

import logging
from typing import Optional
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.domain.protocols import QueueServiceProtocol, LoggingServiceProtocol
from app.domain.schemas import JobCreationResponse


logger = logging.getLogger(__name__)


class TaskService:
    """
    Service for orchestrating receipt processing tasks.
    
    Handles the business logic for creating jobs, validating files,
    and coordinating between logging and queue services.
    """
    
    def __init__(
        self,
        queue_service: QueueServiceProtocol,
        logging_service: LoggingServiceProtocol
    ):
        """Initialize task service with protocol-based dependencies.
        
        Args:
            queue_service: Service implementing QueueServiceProtocol for job enqueueing
            logging_service: Service implementing LoggingServiceProtocol for job logging
        """
        self.queue_service = queue_service
        self.logging_service = logging_service
    
    async def create_and_enqueue_job(
        self,
        file: UploadFile,
        notion_database_id: str,
        job_id: Optional[UUID] = None
    ) -> JobCreationResponse:
        """
        Create and enqueue a receipt processing job.
        
        This method orchestrates the complete job creation workflow:
        1. Generate unique job ID if not provided
        2. Validate and read file contents
        3. Create initial job log entry
        4. Enqueue job for background processing
        
        Args:
            file: Uploaded image file to process
            notion_database_id: Target Notion database ID for the processed data
            job_id: Optional job ID, generates UUID if not provided
            
        Returns:
            JobCreationResponse with job_id and status
            
        Raises:
            ValueError: If file validation fails
            Exception: If job creation or enqueueing fails
        """
        # Generate job ID if not provided
        if job_id is None:
            job_id = uuid4()
        
        logger.info(
            f"Creating job {job_id} for file {file.filename}",
            extra={
                "job_id": str(job_id),
                "filename": file.filename,
                "content_type": file.content_type,
                "notion_database_id": notion_database_id
            }
        )
        
        try:
            # Read file contents for processing
            file_contents = await self._read_file_contents(file)
            
            # Create initial job log entry
            self.logging_service.create_job_log(
                job_id=job_id,
                filename=file.filename
            )
            
            logger.info(
                f"Created job log entry for job {job_id}",
                extra={"job_id": str(job_id)}
            )
            
            # Enqueue job for background processing
            self.queue_service.enqueue_job(
                function_name="trigger_n8n_workflow",
                job_id=job_id,
                image_data=file_contents,
                filename=file.filename,
                notion_database_id=notion_database_id,
                content_type=file.content_type
            )
            
            logger.info(
                f"Successfully enqueued job {job_id} for processing",
                extra={
                    "job_id": str(job_id),
                    "filename": file.filename,
                    "notion_database_id": notion_database_id
                }
            )
            
            return JobCreationResponse(
                job_id=job_id,
                status="queued"
            )
            
        except Exception as e:
            logger.error(
                f"Failed to create and enqueue job {job_id}: {str(e)}",
                extra={
                    "job_id": str(job_id),
                    "filename": file.filename,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    async def _read_file_contents(self, file: UploadFile) -> bytes:
        """
        Read and validate file contents.
        
        Args:
            file: UploadFile object to read
            
        Returns:
            File contents as bytes
            
        Raises:
            ValueError: If file cannot be read or is empty
        """
        try:
            # Reset file pointer to beginning
            await file.seek(0)
            
            # Read file contents
            contents = await file.read()
            
            if not contents:
                raise ValueError(f"File {file.filename} is empty")
            
            logger.debug(
                f"Successfully read {len(contents)} bytes from {file.filename}",
                extra={
                    "filename": file.filename,
                    "file_size": len(contents),
                    "content_type": file.content_type
                }
            )
            
            return contents
            
        except Exception as e:
            error_msg = f"Failed to read file {file.filename}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
        finally:
            # Reset file pointer for potential future reads
            await file.seek(0)
    
    def get_job_status(self, job_id: UUID) -> Optional[dict]:
        """
        Get current status of a job.
        
        Args:
            job_id: Job identifier to query
            
        Returns:
            Dictionary with job status information or None if not found
        """
        try:
            job_log = self.logging_service.get_job_log(job_id)
            
            if not job_log:
                return None
            
            return {
                "job_id": job_log.job_id,
                "status": job_log.status,
                "filename": job_log.filename,
                "created_at": job_log.created_at,
                "completed_at": job_log.completed_at,
                "result_message": job_log.result_message,
                "notion_page_url": job_log.notion_page_url
            }
            
        except Exception as e:
            logger.error(
                f"Failed to get job status for {job_id}: {str(e)}",
                extra={"job_id": str(job_id)},
                exc_info=True
            )
            raise