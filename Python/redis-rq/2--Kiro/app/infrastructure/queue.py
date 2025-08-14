"""
Redis Queue (RQ) implementation for background job processing.

This module provides the RQService class that implements the QueueServiceProtocol
using Redis as the backend for durable job queuing and worker coordination.
"""

import logging
from typing import Any
from uuid import UUID

import redis
from rq import Queue

from app.core.settings import settings
from app.domain.protocols import QueueServiceProtocol


logger = logging.getLogger(__name__)


class QueueConnectionError(Exception):
    """Raised when unable to connect to Redis queue backend."""
    pass


class JobEnqueueError(Exception):
    """Raised when a job cannot be enqueued."""
    pass


class RQService:
    """Redis Queue service implementation.
    
    Provides job enqueueing functionality using Redis as the backend.
    Handles connection management, error handling, and job timeout configuration.
    """
    
    def __init__(self, redis_url: str | None = None, queue_name: str = "default"):
        """Initialize RQ service with Redis connection.
        
        Args:
            redis_url: Redis connection URL. Uses settings.REDIS_URL if None
            queue_name: Name of the queue to use for jobs
            
        Raises:
            QueueConnectionError: If unable to connect to Redis
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.queue_name = queue_name
        self._redis_connection = None
        self._queue = None
        
        # Initialize connection and queue
        self._initialize_connection()
    
    def _initialize_connection(self) -> None:
        """Initialize Redis connection and RQ queue.
        
        Raises:
            QueueConnectionError: If unable to connect to Redis
        """
        try:
            # Create Redis connection with connection pooling
            self._redis_connection = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self._redis_connection.ping()
            
            # Initialize RQ queue
            self._queue = Queue(
                name=self.queue_name,
                connection=self._redis_connection
            )
            
            logger.info(f"Successfully connected to Redis at {self.redis_url}")
            
        except (redis.ConnectionError, redis.TimeoutError) as e:
            error_msg = f"Failed to connect to Redis at {self.redis_url}: {str(e)}"
            logger.error(error_msg)
            raise QueueConnectionError(error_msg) from e
    
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
        if not self._queue:
            raise QueueConnectionError("Queue not initialized")
        
        try:
            # Import the worker function dynamically to avoid circular imports
            if function_name == "trigger_n8n_workflow":
                from rq_worker import trigger_n8n_workflow
                worker_function = trigger_n8n_workflow
            else:
                # For other functions, try to import from a workers module
                worker_function = function_name
            
            # Enqueue job with timeout configuration
            job = self._queue.enqueue(
                worker_function,
                job_id,  # Pass job_id as first argument to the function
                **kwargs,
                job_timeout=settings.QUEUE_DEFAULT_TIMEOUT,
                job_id=str(job_id)  # Use job_id as RQ job ID for tracking
            )
            
            logger.info(
                f"Successfully enqueued job {job_id} with function {function_name}",
                extra={
                    "job_id": str(job_id),
                    "function_name": function_name,
                    "rq_job_id": job.id,
                    "queue_name": self.queue_name
                }
            )
            
        except (redis.ConnectionError, redis.TimeoutError) as e:
            error_msg = f"Failed to enqueue job {job_id}: {str(e)}"
            logger.error(error_msg, extra={"job_id": str(job_id)})
            
            # Try to reconnect once
            try:
                self._initialize_connection()
                
                # Import the worker function dynamically to avoid circular imports
                if function_name == "trigger_n8n_workflow":
                    from rq_worker import trigger_n8n_workflow
                    worker_function = trigger_n8n_workflow
                else:
                    # For other functions, try to import from a workers module
                    worker_function = function_name
                
                # Retry enqueueing after reconnection
                job = self._queue.enqueue(
                    worker_function,
                    job_id,  # Pass job_id as first argument to the function
                    **kwargs,
                    job_timeout=settings.QUEUE_DEFAULT_TIMEOUT,
                    job_id=str(job_id)  # Use job_id as RQ job ID for tracking
                )
                logger.info(f"Successfully enqueued job {job_id} after reconnection")
                
            except Exception as retry_error:
                error_msg = f"Failed to enqueue job {job_id} after retry: {str(retry_error)}"
                logger.error(error_msg, extra={"job_id": str(job_id)})
                raise JobEnqueueError(error_msg) from retry_error
                
        except Exception as e:
            error_msg = f"Unexpected error enqueueing job {job_id}: {str(e)}"
            logger.error(error_msg, extra={"job_id": str(job_id)})
            raise JobEnqueueError(error_msg) from e
    
    def get_queue_info(self) -> dict[str, Any]:
        """Get information about the current queue state.
        
        Returns:
            Dictionary containing queue statistics
            
        Raises:
            QueueConnectionError: If unable to connect to queue backend
        """
        if not self._queue:
            raise QueueConnectionError("Queue not initialized")
        
        try:
            return {
                "name": self.queue_name,
                "length": len(self._queue),
                "failed_job_count": self._queue.failed_job_registry.count,
                "scheduled_job_count": self._queue.scheduled_job_registry.count,
                "started_job_count": self._queue.started_job_registry.count,
                "deferred_job_count": self._queue.deferred_job_registry.count
            }
        except Exception as e:
            error_msg = f"Failed to get queue info: {str(e)}"
            logger.error(error_msg)
            raise QueueConnectionError(error_msg) from e
    
    def close(self) -> None:
        """Close Redis connection and cleanup resources."""
        if self._redis_connection:
            try:
                self._redis_connection.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {str(e)}")
            finally:
                self._redis_connection = None
                self._queue = None


# Factory function for dependency injection
def create_queue_service() -> RQService:
    """Create and return an RQService instance.
    
    Returns:
        Configured RQService instance
        
    Raises:
        QueueConnectionError: If unable to connect to Redis
    """
    return RQService()