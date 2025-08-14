"""
Protocol definitions for service interfaces.

This module defines structural typing protocols that establish contracts
for service implementations, enabling loose coupling and testability.
"""

from typing import Protocol, Any
from uuid import UUID


class QueueServiceProtocol(Protocol):
    """Protocol for queue service implementations.
    
    Defines the interface for enqueueing background jobs in a queue system.
    Implementations should handle job persistence and worker distribution.
    """
    
    def enqueue_job(
        self, 
        function_name: str, 
        job_id: UUID, 
        **kwargs: Any
    ) -> None:
        """Enqueue a background job for processing.
        
        Args:
            function_name: Name of the function to execute in the worker
            job_id: Unique identifier for the job
            **kwargs: Additional arguments to pass to the worker function
            
        Raises:
            QueueConnectionError: If unable to connect to queue backend
            JobEnqueueError: If job cannot be enqueued
        """
        ...


class LoggingServiceProtocol(Protocol):
    """Protocol for job logging service implementations.
    
    Defines the interface for persisting and updating job status information
    in a durable storage system.
    """
    
    def create_job_log(
        self, 
        job_id: UUID, 
        filename: str
    ) -> None:
        """Create initial job log entry.
        
        Args:
            job_id: Unique identifier for the job
            filename: Name of the uploaded file
            
        Raises:
            DatabaseError: If unable to create log entry
        """
        ...
    
    def update_job_status(
        self, 
        job_id: UUID, 
        status: str, 
        message: str | None = None,
        notion_page_url: str | None = None
    ) -> None:
        """Update job status and completion details.
        
        Args:
            job_id: Unique identifier for the job
            status: New status (success|failure)
            message: Optional status message or error details
            notion_page_url: Optional URL of created Notion page
            
        Raises:
            DatabaseError: If unable to update log entry
            JobNotFoundError: If job_id does not exist
        """
        ...