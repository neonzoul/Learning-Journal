"""
Jobs API endpoints for callback handling.

This module provides endpoints for job status callbacks from N8N workflows,
including authentication and job status updates.
"""

from uuid import UUID
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, Header, status
from fastapi.responses import JSONResponse

from app.core.dependencies import get_logging_service
from app.core.settings import settings
from app.core.logging_config import get_logger, get_performance_logger
from app.core.exceptions import (
    AuthenticationError,
    ResourceNotFoundError,
    DatabaseError
)
from app.domain.schemas import JobCallbackPayload
from app.domain.error_schemas import (
    AuthenticationErrorResponse,
    ResourceNotFoundErrorResponse,
    InternalServerErrorResponse
)
from app.services.logging_service import LoggingService


# Create router for job-related endpoints
router = APIRouter(prefix="/jobs", tags=["jobs"])

logger = get_logger(__name__)
perf_logger = get_performance_logger(__name__)


def verify_callback_token(
    x_callback_token: Optional[str] = Header(None, alias="X-Callback-Token")
) -> str:
    """
    Verify callback authentication token from request headers.
    
    Args:
        x_callback_token: Token from X-Callback-Token header
        
    Returns:
        Verified token string
        
    Raises:
        AuthenticationError: If token is missing or invalid
    """
    if not x_callback_token:
        logger.warning(
            "Callback authentication failed: missing token",
            extra={"error_type": "missing_token"}
        )
        raise AuthenticationError(
            message="Missing X-Callback-Token header",
            details={"required_header": "X-Callback-Token"}
        )
    
    if x_callback_token != settings.CALLBACK_SECRET_TOKEN:
        logger.warning(
            "Callback authentication failed: invalid token",
            extra={
                "error_type": "invalid_token",
                "token_length": len(x_callback_token)
            }
        )
        raise AuthenticationError(
            message="Invalid callback token",
            details={"provided_token_length": len(x_callback_token)}
        )
    
    return x_callback_token


@router.post(
    "/{job_id}/callback",
    responses={
        200: {"description": "Job status updated successfully"},
        401: {"model": AuthenticationErrorResponse},
        404: {"model": ResourceNotFoundErrorResponse},
        500: {"model": InternalServerErrorResponse}
    }
)
async def job_callback(
    job_id: UUID,
    payload: JobCallbackPayload,
    logging_service: LoggingService = Depends(get_logging_service),
    token: str = Depends(verify_callback_token)
) -> JSONResponse:
    """
    Handle job status callback from N8N workflow.
    
    This endpoint receives status updates from the N8N workflow after
    receipt processing is complete. It authenticates the request using
    a secret token and updates the job status in the database.
    
    Args:
        job_id: UUID of the job to update
        payload: Job completion status and details
        logging_service: Service for database operations
        token: Verified callback token from dependency
        
    Returns:
        JSONResponse with success confirmation
        
    Raises:
        AuthenticationError: If authentication fails
        ResourceNotFoundError: If job not found
        DatabaseError: If database operation fails
    """
    # Start performance monitoring
    perf_logger.start_operation(
        "job_callback",
        job_id=str(job_id),
        status=payload.status,
        has_message=bool(payload.message),
        has_notion_url=bool(payload.notion_page_url)
    )
    
    logger.info(
        "Received job callback",
        extra={
            "job_id": str(job_id),
            "status": payload.status,
            "has_message": bool(payload.message),
            "has_notion_url": bool(payload.notion_page_url)
        }
    )
    
    try:
        # Update job status in database
        try:
            updated_job = logging_service.update_job_status(
                job_id=job_id,
                status=payload.status,
                result_message=payload.message,
                notion_page_url=payload.notion_page_url
            )
        except Exception as e:
            logger.error(
                "Database error during job status update",
                extra={
                    "job_id": str(job_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise DatabaseError(
                message=f"Failed to update job status in database: {str(e)}",
                operation="update_job_status",
                table="job_log",
                details={
                    "job_id": str(job_id),
                    "target_status": payload.status
                }
            )
        
        # Check if job was found and updated
        if not updated_job:
            logger.warning(
                "Job not found for callback",
                extra={"job_id": str(job_id)}
            )
            raise ResourceNotFoundError(
                message=f"Job with ID {job_id} not found",
                resource_type="job",
                resource_id=str(job_id)
            )
        
        # End performance monitoring
        perf_logger.end_operation(
            success=True,
            job_id=str(job_id),
            final_status=payload.status
        )
        
        logger.info(
            "Job status updated successfully",
            extra={
                "job_id": str(job_id),
                "status": payload.status,
                "completed_at": updated_job.completed_at.isoformat() if updated_job.completed_at else None
            }
        )
        
        # Return success response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Job status updated successfully",
                "job_id": str(job_id),
                "status": payload.status,
                "updated_at": updated_job.completed_at.isoformat() + "Z" if updated_job.completed_at else None
            }
        )
        
    except (AuthenticationError, ResourceNotFoundError, DatabaseError):
        # Re-raise application errors (middleware will handle them)
        perf_logger.end_operation(
            success=False,
            error_message="Application error during callback processing"
        )
        raise
        
    except Exception as e:
        # Handle unexpected errors
        perf_logger.end_operation(
            success=False,
            error_message=f"Unexpected error: {str(e)}"
        )
        
        logger.error(
            "Unexpected error during job callback",
            extra={
                "job_id": str(job_id),
                "error": str(e)
            },
            exc_info=True
        )
        
        raise DatabaseError(
            message="An unexpected error occurred while processing the callback",
            operation="job_callback",
            details={
                "job_id": str(job_id),
                "error_type": e.__class__.__name__
            }
        )


@router.get(
    "/{job_id}/status",
    response_model=Dict[str, Any],
    responses={
        200: {"description": "Job status retrieved successfully"},
        404: {"model": ResourceNotFoundErrorResponse},
        500: {"model": InternalServerErrorResponse}
    }
)
async def get_job_status(
    job_id: UUID,
    logging_service: LoggingService = Depends(get_logging_service)
) -> Dict[str, Any]:
    """
    Get the current status of a job.
    
    This endpoint allows clients to check the status of a previously
    submitted job using its unique identifier.
    
    Args:
        job_id: UUID of the job to query
        logging_service: Service for database operations
        
    Returns:
        Dictionary containing job status and details
        
    Raises:
        ResourceNotFoundError: If job not found
        DatabaseError: If database query fails
    """
    logger.info(
        "Job status requested",
        extra={"job_id": str(job_id)}
    )
    
    try:
        # Get job status from database
        try:
            job_log = logging_service.get_job_log(job_id)
        except Exception as e:
            logger.error(
                "Database error during job status query",
                extra={
                    "job_id": str(job_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise DatabaseError(
                message=f"Failed to query job status: {str(e)}",
                operation="get_job_log",
                table="job_log",
                details={"job_id": str(job_id)}
            )
        
        # Check if job was found
        if not job_log:
            logger.warning(
                "Job not found for status query",
                extra={"job_id": str(job_id)}
            )
            raise ResourceNotFoundError(
                message=f"Job with ID {job_id} not found",
                resource_type="job",
                resource_id=str(job_id)
            )
        
        logger.info(
            "Job status retrieved successfully",
            extra={
                "job_id": str(job_id),
                "status": job_log.status,
                "filename": job_log.filename
            }
        )
        
        # Return job status information
        return {
            "job_id": str(job_log.job_id),
            "status": job_log.status,
            "filename": job_log.filename,
            "notion_database_id": job_log.notion_database_id,
            "created_at": job_log.created_at.isoformat() + "Z",
            "completed_at": job_log.completed_at.isoformat() + "Z" if job_log.completed_at else None,
            "result_message": job_log.result_message,
            "notion_page_url": job_log.notion_page_url
        }
        
    except (ResourceNotFoundError, DatabaseError):
        # Re-raise application errors (middleware will handle them)
        raise
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(
            "Unexpected error during job status query",
            extra={
                "job_id": str(job_id),
                "error": str(e)
            },
            exc_info=True
        )
        
        raise DatabaseError(
            message="An unexpected error occurred while retrieving job status",
            operation="get_job_status",
            details={
                "job_id": str(job_id),
                "error_type": e.__class__.__name__
            }
        )