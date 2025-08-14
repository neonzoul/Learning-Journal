"""
Jobs API endpoints for callback handling.

This module provides endpoints for job status callbacks from N8N workflows,
including authentication and job status updates.
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.responses import JSONResponse

from app.core.dependencies import get_logging_service
from app.core.settings import settings
from app.domain.schemas import JobCallbackPayload
from app.services.logging_service import LoggingService


# Create router for job-related endpoints
router = APIRouter(prefix="/jobs", tags=["jobs"])


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
        HTTPException: If token is missing or invalid (401 Unauthorized)
    """
    if not x_callback_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Callback-Token header"
        )
    
    if x_callback_token != settings.CALLBACK_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid callback token"
        )
    
    return x_callback_token


@router.post("/{job_id}/callback")
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
        HTTPException: 
            - 401 if authentication fails
            - 404 if job not found
            - 500 if database operation fails
    """
    try:
        # Update job status in database
        updated_job = logging_service.update_job_status(
            job_id=job_id,
            status=payload.status,
            result_message=payload.message,
            notion_page_url=payload.notion_page_url
        )
        
        # Check if job was found and updated
        if not updated_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found"
            )
        
        # Return success response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Job status updated successfully",
                "job_id": str(job_id),
                "status": payload.status
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (404, etc.)
        raise
    except Exception as e:
        # Handle unexpected database or system errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job status: {str(e)}"
        )