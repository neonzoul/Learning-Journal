"""
Task service for business logic orchestration.

This module provides the TaskService class that orchestrates job creation,
file handling, and enqueueing operations for receipt processing workflows.
"""

from typing import Optional
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.core.logging_config import get_logger, get_performance_logger
from app.core.exceptions import (
    JobError,
    QueueError,
    DatabaseError,
    FileValidationError
)
from app.domain.protocols import QueueServiceProtocol, LoggingServiceProtocol
from app.domain.schemas import JobCreationResponse


logger = get_logger(__name__)
perf_logger = get_performance_logger(__name__)


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
            FileValidationError: If file validation fails
            DatabaseError: If job log creation fails
            QueueError: If job enqueueing fails
            JobError: If overall job creation fails
        """
        # Generate job ID if not provided
        if job_id is None:
            job_id = uuid4()
        
        # Start performance monitoring
        perf_logger.start_operation(
            "create_and_enqueue_job",
            job_id=str(job_id),
            filename=file.filename,
            content_type=file.content_type,
            notion_database_id=notion_database_id
        )
        
        logger.info(
            "Creating and enqueueing job",
            extra={
                "job_id": str(job_id),
                "filename": file.filename,
                "content_type": file.content_type,
                "notion_database_id": notion_database_id
            }
        )
        
        try:
            # Read file contents for processing
            try:
                file_contents = await self._read_file_contents(file)
            except Exception as e:
                raise FileValidationError(
                    message=f"Failed to read file contents: {str(e)}",
                    filename=file.filename,
                    details={"error_type": "file_read_error"}
                )
            
            # Create initial job log entry
            try:
                self.logging_service.create_job_log(
                    job_id=job_id,
                    filename=file.filename,
                    notion_database_id=notion_database_id
                )
                
                logger.info(
                    "Created job log entry",
                    extra={"job_id": str(job_id)}
                )
            except Exception as e:
                logger.error(
                    "Failed to create job log entry",
                    extra={
                        "job_id": str(job_id),
                        "error": str(e)
                    },
                    exc_info=True
                )
                raise DatabaseError(
                    message=f"Failed to create job log entry: {str(e)}",
                    operation="create_job_log",
                    table="job_log",
                    details={
                        "job_id": str(job_id),
                        "filename": file.filename
                    }
                )
            
            # Enqueue job for background processing
            try:
                self.queue_service.enqueue_job(
                    function_name="trigger_n8n_workflow",
                    job_id=job_id,
                    image_data=file_contents,
                    filename=file.filename,
                    notion_database_id=notion_database_id,
                    content_type=file.content_type
                )
                
                logger.info(
                    "Successfully enqueued job for processing",
                    extra={
                        "job_id": str(job_id),
                        "filename": file.filename,
                        "notion_database_id": notion_database_id,
                        "file_size": len(file_contents)
                    }
                )
            except Exception as e:
                logger.error(
                    "Failed to enqueue job",
                    extra={
                        "job_id": str(job_id),
                        "error": str(e)
                    },
                    exc_info=True
                )
                raise QueueError(
                    message=f"Failed to enqueue job for processing: {str(e)}",
                    operation="enqueue_job",
                    details={
                        "job_id": str(job_id),
                        "filename": file.filename,
                        "function_name": "trigger_n8n_workflow"
                    }
                )
            
            # End performance monitoring
            perf_logger.end_operation(
                success=True,
                job_id=str(job_id),
                filename=file.filename,
                file_size=len(file_contents)
            )
            
            return JobCreationResponse(
                job_id=job_id,
                status="queued"
            )
            
        except (FileValidationError, DatabaseError, QueueError):
            # Re-raise application errors as-is
            perf_logger.end_operation(
                success=False,
                error_message="Application error during job creation"
            )
            raise
            
        except Exception as e:
            # Handle unexpected errors
            perf_logger.end_operation(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
            
            logger.error(
                "Unexpected error during job creation",
                extra={
                    "job_id": str(job_id),
                    "filename": file.filename,
                    "error": str(e)
                },
                exc_info=True
            )
            
            raise JobError(
                message=f"Failed to create and enqueue job: {str(e)}",
                job_id=job_id,
                details={
                    "filename": file.filename,
                    "notion_database_id": notion_database_id,
                    "error_type": e.__class__.__name__
                }
            )
    
    async def _read_file_contents(self, file: UploadFile) -> bytes:
        """
        Read and validate file contents.
        
        Args:
            file: UploadFile object to read
            
        Returns:
            File contents as bytes
            
        Raises:
            FileValidationError: If file cannot be read or is empty
        """
        try:
            # Reset file pointer to beginning
            await file.seek(0)
            
            # Read file contents
            contents = await file.read()
            
            if not contents:
                raise FileValidationError(
                    message="File is empty",
                    filename=file.filename,
                    file_size=0,
                    details={"error_type": "empty_file"}
                )
            
            logger.debug(
                "Successfully read file contents",
                extra={
                    "filename": file.filename,
                    "file_size": len(contents),
                    "content_type": file.content_type
                }
            )
            
            return contents
            
        except FileValidationError:
            # Re-raise file validation errors as-is
            raise
            
        except Exception as e:
            logger.error(
                "Failed to read file contents",
                extra={
                    "filename": file.filename,
                    "error": str(e)
                },
                exc_info=True
            )
            raise FileValidationError(
                message=f"Failed to read file contents: {str(e)}",
                filename=file.filename,
                details={
                    "error_type": "file_read_error",
                    "original_error": str(e)
                }
            )
        finally:
            # Reset file pointer for potential future reads
            try:
                await file.seek(0)
            except Exception as e:
                logger.warning(
                    "Failed to reset file pointer",
                    extra={
                        "filename": file.filename,
                        "error": str(e)
                    }
                )
    
    def get_job_status(self, job_id: UUID) -> Optional[dict]:
        """
        Get current status of a job.
        
        Args:
            job_id: Job identifier to query
            
        Returns:
            Dictionary with job status information or None if not found
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            job_log = self.logging_service.get_job_log(job_id)
            
            if not job_log:
                logger.info(
                    "Job not found",
                    extra={"job_id": str(job_id)}
                )
                return None
            
            logger.debug(
                "Retrieved job status",
                extra={
                    "job_id": str(job_id),
                    "status": job_log.status,
                    "filename": job_log.filename
                }
            )
            
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
                "Failed to get job status",
                extra={
                    "job_id": str(job_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise DatabaseError(
                message=f"Failed to retrieve job status: {str(e)}",
                operation="get_job_log",
                table="job_log",
                details={
                    "job_id": str(job_id)
                }
            )