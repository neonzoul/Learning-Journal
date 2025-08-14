"""
RQ Worker for N8N Integration and Background Job Processing.

This module implements the background worker that processes receipt analysis jobs
by triggering N8N workflows via HTTP webhooks. It handles image data encoding,
error handling, and comprehensive logging for job processing.
"""

import base64
import sys
from typing import Any, Dict, Optional
from uuid import UUID

import httpx
import redis
from rq import Worker, Queue, Connection

from app.core.settings import settings
from app.core.logging_config import setup_logging, get_logger, get_performance_logger
from app.core.exceptions import ExternalServiceError


# Setup structured logging for worker
setup_logging(
    log_level=settings.LOG_LEVEL,
    enable_json_logging=settings.ENABLE_JSON_LOGGING,
    log_file="worker.log"
)
logger = get_logger(__name__)
perf_logger = get_performance_logger(__name__)


# Custom exceptions are now imported from app.core.exceptions


def trigger_n8n_workflow(
    job_id: UUID,
    image_data: bytes,
    filename: str,
    notion_database_id: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Trigger N8N workflow for receipt processing.
    
    This function is executed by RQ workers to process receipt analysis jobs.
    It encodes the image data as base64 and sends it to the N8N webhook endpoint
    along with the necessary metadata.
    
    Args:
        job_id: Unique identifier for the job
        image_data: Raw image bytes to be processed
        filename: Original filename of the uploaded image
        notion_database_id: Target Notion database ID for storing results
        **kwargs: Additional arguments (for extensibility)
        
    Returns:
        Dict containing the N8N response data
        
    Raises:
        ExternalServiceError: If image encoding or N8N webhook call fails
    """
    job_id_str = str(job_id)
    
    # Start performance monitoring
    perf_logger.start_operation(
        "trigger_n8n_workflow",
        job_id=job_id_str,
        filename=filename,
        notion_database_id=notion_database_id,
        image_size_bytes=len(image_data)
    )
    
    logger.info(
        "Starting N8N workflow trigger",
        extra={
            "job_id": job_id_str,
            "filename": filename,
            "notion_database_id": notion_database_id,
            "image_size_bytes": len(image_data)
        }
    )
    
    try:
        # Encode image data as base64
        try:
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            logger.debug(
                "Successfully encoded image",
                extra={
                    "job_id": job_id_str,
                    "encoded_size": len(encoded_image)
                }
            )
        except Exception as e:
            logger.error(
                "Failed to encode image data",
                extra={
                    "job_id": job_id_str,
                    "error": str(e)
                },
                exc_info=True
            )
            raise ExternalServiceError(
                message=f"Failed to encode image data: {str(e)}",
                service_name="base64_encoder",
                details={
                    "job_id": job_id_str,
                    "image_size": len(image_data),
                    "error_type": "encoding_error"
                }
            )
        
        # Prepare webhook payload
        webhook_payload = {
            "job_id": job_id_str,
            "image_data": encoded_image,
            "filename": filename,
            "notion_database_id": notion_database_id,
            "callback_url": f"{settings.API_V1_STR}/jobs/{job_id_str}/callback"
        }
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.N8N_API_KEY}",
            "User-Agent": f"{settings.PROJECT_NAME}/1.0.0"
        }
        
        # Configure HTTP client with timeout and SSL settings
        timeout = httpx.Timeout(
            connect=10.0,  # Connection timeout
            read=60.0,     # Read timeout (N8N processing can take time)
            write=10.0,    # Write timeout
            pool=5.0       # Pool timeout
        )
        
        # Make HTTP request to N8N webhook
        logger.info(
            "Sending webhook request to N8N",
            extra={
                "job_id": job_id_str,
                "webhook_url": settings.N8N_WEBHOOK_URL,
                "payload_size": len(str(webhook_payload))
            }
        )
        
        try:
            with httpx.Client(
                timeout=timeout,
                verify=settings.VERIFY_SSL,
                follow_redirects=True
            ) as client:
                response = client.post(
                    settings.N8N_WEBHOOK_URL,
                    json=webhook_payload,
                    headers=headers
                )
                
                # Check response status
                if response.status_code not in [200, 201, 202]:
                    logger.error(
                        "N8N webhook returned error status",
                        extra={
                            "job_id": job_id_str,
                            "status_code": response.status_code,
                            "response_text": response.text[:500]  # Limit log size
                        }
                    )
                    raise ExternalServiceError(
                        message=f"N8N webhook returned status {response.status_code}",
                        service_name="n8n_webhook",
                        status_code=response.status_code,
                        response_body=response.text,
                        details={
                            "job_id": job_id_str,
                            "webhook_url": settings.N8N_WEBHOOK_URL
                        }
                    )
                
                # Parse response
                try:
                    response_data = response.json()
                except Exception:
                    # If response is not JSON, create a simple response
                    response_data = {
                        "status": "accepted",
                        "message": "N8N webhook triggered successfully",
                        "status_code": response.status_code
                    }
                
                # End performance monitoring
                perf_logger.end_operation(
                    success=True,
                    job_id=job_id_str,
                    status_code=response.status_code,
                    response_size=len(response.text)
                )
                
                logger.info(
                    "Successfully triggered N8N workflow",
                    extra={
                        "job_id": job_id_str,
                        "status_code": response.status_code,
                        "response_data": response_data
                    }
                )
                
                return response_data
        
        except httpx.TimeoutException as e:
            logger.error(
                "Timeout calling N8N webhook",
                extra={
                    "job_id": job_id_str,
                    "error": str(e)
                }
            )
            raise ExternalServiceError(
                message=f"Timeout calling N8N webhook: {str(e)}",
                service_name="n8n_webhook",
                details={
                    "job_id": job_id_str,
                    "error_type": "timeout",
                    "webhook_url": settings.N8N_WEBHOOK_URL
                }
            )
        
        except httpx.RequestError as e:
            logger.error(
                "HTTP request error calling N8N webhook",
                extra={
                    "job_id": job_id_str,
                    "error": str(e)
                }
            )
            raise ExternalServiceError(
                message=f"HTTP request error calling N8N webhook: {str(e)}",
                service_name="n8n_webhook",
                details={
                    "job_id": job_id_str,
                    "error_type": "request_error",
                    "webhook_url": settings.N8N_WEBHOOK_URL
                }
            )
    
    except ExternalServiceError:
        # Re-raise external service errors as-is
        perf_logger.end_operation(
            success=False,
            error_message="External service error"
        )
        raise
    
    except Exception as e:
        # Handle unexpected errors
        perf_logger.end_operation(
            success=False,
            error_message=f"Unexpected error: {str(e)}"
        )
        
        logger.error(
            "Unexpected error triggering N8N workflow",
            extra={
                "job_id": job_id_str,
                "error": str(e)
            },
            exc_info=True
        )
        
        raise ExternalServiceError(
            message=f"Unexpected error triggering N8N workflow: {str(e)}",
            service_name="n8n_webhook",
            details={
                "job_id": job_id_str,
                "error_type": e.__class__.__name__
            }
        )


def setup_worker_logging() -> None:
    """Configure enhanced logging for worker processes."""
    
    # Set log levels for external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("rq.worker").setLevel(logging.INFO)
    
    logger.info("Worker logging configured successfully")


def create_worker_connection() -> redis.Redis:
    """
    Create Redis connection for worker with proper error handling.
    
    Returns:
        Configured Redis connection
        
    Raises:
        redis.ConnectionError: If unable to connect to Redis
    """
    try:
        redis_conn = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection
        redis_conn.ping()
        logger.info(f"Worker connected to Redis at {settings.REDIS_URL}")
        
        return redis_conn
        
    except (redis.ConnectionError, redis.TimeoutError) as e:
        error_msg = f"Failed to connect to Redis at {settings.REDIS_URL}: {str(e)}"
        logger.error(error_msg)
        raise redis.ConnectionError(error_msg) from e


if __name__ == "__main__":
    """
    Main entry point for RQ worker process.
    
    This script starts an RQ worker that listens for jobs on the default queue
    and processes them using the trigger_n8n_workflow function.
    """
    
    # Setup logging
    setup_worker_logging()
    
    logger.info("Starting RQ Worker for N8N Integration...")
    logger.info(f"Worker configuration: Redis URL={settings.REDIS_URL}")
    logger.info(f"N8N Webhook URL: {settings.N8N_WEBHOOK_URL}")
    logger.info(f"SSL Verification: {settings.VERIFY_SSL}")
    
    try:
        # Create Redis connection
        redis_conn = create_worker_connection()
        
        # Start worker with connection context
        with Connection(redis_conn):
            # Create worker for default queue
            worker = Worker(
                Queue(),
                name=f"n8n-worker-{redis_conn.client_id()}",
                default_result_ttl=3600,  # Keep job results for 1 hour
                default_worker_ttl=1800   # Worker TTL of 30 minutes
            )
            
            logger.info(f"Worker {worker.name} starting to process jobs...")
            
            # Start processing jobs (this blocks)
            worker.work(
                with_scheduler=True,  # Enable job scheduling
                logging_level="INFO"
            )
            
    except KeyboardInterrupt:
        logger.info("Worker shutdown requested by user")
        sys.exit(0)
        
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error starting worker: {e}", exc_info=True)
        sys.exit(1)