"""
Receipt upload API endpoints.

This module provides endpoints for uploading receipt images and initiating
their processing through the asynchronous workflow system.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.settings import settings
from app.core.logging_config import get_logger, get_performance_logger
from app.core.exceptions import (
    FileValidationError,
    ValidationError,
    JobError
)
from app.core.dependencies import get_task_service
from app.domain.schemas import JobCreationResponse
from app.domain.error_schemas import (
    ErrorResponse,
    ValidationErrorResponse,
    InternalServerErrorResponse
)
from app.services.task_service import TaskService


logger = get_logger(__name__)
perf_logger = get_performance_logger(__name__)

router = APIRouter(prefix="/receipts", tags=["receipts"])


# File validation constants
ALLOWED_MIME_TYPES = set(settings.ALLOWED_IMAGE_TYPES)
MAX_FILE_SIZE = settings.MAX_FILE_SIZE

# Magic bytes for image format validation
IMAGE_MAGIC_BYTES = {
    b'\xff\xd8\xff': 'image/jpeg',  # JPEG
    b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': 'image/png',  # PNG
}


def validate_image_format(file_content: bytes, content_type: str, filename: str) -> str:
    """
    Validate image format using magic bytes and content type.
    
    Args:
        file_content: Raw file bytes
        content_type: Content-Type header from request
        filename: Original filename for extension checking
        
    Returns:
        Validated MIME type
        
    Raises:
        FileValidationError: If format validation fails
    """
    # Check magic bytes first (most reliable)
    detected_type = None
    for magic_bytes, mime_type in IMAGE_MAGIC_BYTES.items():
        if file_content.startswith(magic_bytes):
            detected_type = mime_type
            break
    
    # If magic bytes detection failed, check content type and file extension
    if not detected_type:
        # Normalize content type
        if content_type in ['image/jpg', 'image/jpeg']:
            content_type = 'image/jpeg'
        
        # Check if content type is allowed
        if content_type in ALLOWED_MIME_TYPES:
            detected_type = content_type
        else:
            # Check file extension as last resort
            if filename:
                extension = filename.lower().split('.')[-1] if '.' in filename else ''
                if extension in ['jpg', 'jpeg']:
                    detected_type = 'image/jpeg'
                elif extension == 'png':
                    detected_type = 'image/png'
    
    # If still no valid type detected, reject
    if not detected_type or detected_type not in ALLOWED_MIME_TYPES:
        raise FileValidationError(
            message=f"File format could not be validated as a supported image type. "
                   f"Allowed formats: {', '.join(ALLOWED_MIME_TYPES)}. "
                   f"Detected: {detected_type or 'unknown'}",
            filename=filename,
            content_type=content_type,
            details={
                "allowed_formats": list(ALLOWED_MIME_TYPES),
                "detected_format": detected_type
            }
        )
    
    return detected_type


def validate_file_size(file_size: int, filename: str = None) -> None:
    """
    Validate file size against maximum limit.
    
    Args:
        file_size: Size of file in bytes
        filename: Optional filename for error context
        
    Raises:
        FileValidationError: If file exceeds size limit
    """
    if file_size > MAX_FILE_SIZE:
        raise FileValidationError(
            message=f"File size {file_size} bytes exceeds maximum allowed size of {MAX_FILE_SIZE} bytes",
            filename=filename,
            file_size=file_size,
            details={
                "max_size_bytes": MAX_FILE_SIZE,
                "max_size_mb": MAX_FILE_SIZE // (1024 * 1024),
                "actual_size_mb": file_size // (1024 * 1024)
            }
        )


def validate_notion_database_id(notion_database_id: str) -> str:
    """
    Validate Notion database ID format.
    
    Args:
        notion_database_id: Database ID to validate
        
    Returns:
        Validated database ID
        
    Raises:
        ValidationError: If database ID format is invalid
    """
    if not notion_database_id or not notion_database_id.strip():
        raise ValidationError(
            message="notion_database_id cannot be empty",
            field="notion_database_id",
            value=notion_database_id
        )
    
    # Basic format validation - Notion database IDs are typically 32 character hex strings
    cleaned_id = notion_database_id.strip().replace('-', '')
    if len(cleaned_id) != 32 or not all(c in '0123456789abcdefABCDEF' for c in cleaned_id):
        raise ValidationError(
            message="notion_database_id must be a valid 32-character hexadecimal string",
            field="notion_database_id",
            value=notion_database_id,
            details={
                "expected_format": "32-character hexadecimal string",
                "actual_length": len(cleaned_id)
            }
        )
    
    return notion_database_id.strip()


@router.post(
    "/upload",
    response_model=JobCreationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload receipt image for processing",
    description="Upload a receipt image to be processed asynchronously. "
                "Returns a job ID that can be used to track processing status.",
    responses={
        202: {"model": JobCreationResponse},
        400: {"model": ValidationErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse},
        500: {"model": InternalServerErrorResponse}
    }
)
async def upload_receipt(
    file: Annotated[UploadFile, File(
        description="Receipt image file (JPEG or PNG format, max 10MB)"
    )],
    notion_database_id: Annotated[str, Form(
        description="Notion database ID where the processed data will be stored"
    )],
    task_service: TaskService = Depends(get_task_service)
) -> JobCreationResponse:
    """
    Upload and process a receipt image.
    
    This endpoint accepts a receipt image and initiates asynchronous processing
    to extract financial data and store it in the specified Notion database.
    
    Args:
        file: Uploaded image file (JPEG or PNG, max 10MB)
        notion_database_id: Target Notion database ID for processed data
        task_service: Injected task service for job orchestration
        
    Returns:
        JobCreationResponse with job_id and status "queued"
        
    Raises:
        FileValidationError: Invalid file format, size, or missing parameters
        ValidationError: Invalid notion_database_id format
        JobError: Job creation or enqueueing failed
    """
    # Start performance monitoring
    perf_logger.start_operation(
        "receipt_upload",
        filename=file.filename,
        content_type=file.content_type,
        notion_database_id=notion_database_id
    )
    
    logger.info(
        "Received upload request",
        extra={
            "filename": file.filename,
            "content_type": file.content_type,
            "notion_database_id": notion_database_id
        }
    )
    
    try:
        # Validate notion_database_id
        validated_db_id = validate_notion_database_id(notion_database_id)
        
        # Validate file presence and basic properties
        if not file.filename:
            raise FileValidationError(
                message="A file must be provided for upload",
                filename=None,
                details={"error_type": "missing_file"}
            )
        
        # Read file content for validation
        file_content = await file.read()
        file_size = len(file_content)
        
        # Reset file pointer for task service
        await file.seek(0)
        
        # Validate file size
        validate_file_size(file_size, file.filename)
        
        # Validate image format using magic bytes and content type
        validated_content_type = validate_image_format(
            file_content, 
            file.content_type, 
            file.filename
        )
        
        logger.info(
            "File validation passed",
            extra={
                "filename": file.filename,
                "file_size": file_size,
                "validated_content_type": validated_content_type,
                "notion_database_id": validated_db_id
            }
        )
        
        # Create and enqueue job
        try:
            response = await task_service.create_and_enqueue_job(
                file=file,
                notion_database_id=validated_db_id
            )
        except Exception as e:
            logger.error(
                "Job creation failed",
                extra={
                    "filename": file.filename,
                    "notion_database_id": validated_db_id,
                    "error": str(e)
                },
                exc_info=True
            )
            raise JobError(
                message=f"Failed to create and enqueue job: {str(e)}",
                details={
                    "filename": file.filename,
                    "notion_database_id": validated_db_id
                }
            )
        
        # End performance monitoring
        perf_logger.end_operation(
            success=True,
            job_id=str(response.job_id),
            filename=file.filename,
            status=response.status
        )
        
        logger.info(
            "Successfully created job",
            extra={
                "job_id": str(response.job_id),
                "filename": file.filename,
                "status": response.status
            }
        )
        
        return response
        
    except (FileValidationError, ValidationError, JobError):
        # Re-raise application errors as-is (middleware will handle them)
        perf_logger.end_operation(
            success=False,
            error_message="Validation or job creation failed"
        )
        raise
        
    except Exception as e:
        # Handle unexpected errors
        perf_logger.end_operation(
            success=False,
            error_message=f"Unexpected error: {str(e)}"
        )
        
        logger.error(
            "Unexpected error during upload",
            extra={
                "filename": file.filename,
                "notion_database_id": notion_database_id,
                "error": str(e)
            },
            exc_info=True
        )
        
        raise JobError(
            message="An unexpected error occurred while processing the upload",
            details={
                "filename": file.filename,
                "notion_database_id": notion_database_id,
                "error_type": e.__class__.__name__
            }
        )


@router.get(
    "/health",
    summary="Health check endpoint",
    description="Simple health check to verify the receipts service is operational"
)
async def health_check():
    """Health check endpoint for the receipts service."""
    return {"status": "healthy", "service": "receipts"}