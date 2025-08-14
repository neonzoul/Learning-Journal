"""
Error response schemas for consistent API error formatting.

This module defines Pydantic models for standardized error responses
that provide structured error information to API clients.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Individual error detail within an error response."""
    
    field: Optional[str] = Field(
        None,
        description="Field name that caused the error (for validation errors)"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    code: Optional[str] = Field(
        None,
        description="Machine-readable error code"
    )
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "code": "INVALID_FORMAT"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response format for all API endpoints."""
    
    error: str = Field(
        ...,
        description="Primary error type or category"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    error_code: str = Field(
        ...,
        description="Machine-readable error code for programmatic handling"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="ISO timestamp when the error occurred"
    )
    request_id: Optional[str] = Field(
        None,
        description="Unique request identifier for tracing"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context and details"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }
        schema_extra = {
            "example": {
                "error": "Validation Error",
                "message": "The provided file format is not supported",
                "error_code": "INVALID_FILE_FORMAT",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
                "details": {
                    "field": "file",
                    "allowed_formats": ["image/jpeg", "image/png"],
                    "detected_format": "image/gif"
                }
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Specialized error response for validation errors."""
    
    error: str = Field(default="Validation Error")
    error_code: str = Field(default="VALIDATION_ERROR")
    validation_errors: Optional[List[ErrorDetail]] = Field(
        None,
        description="List of specific validation errors"
    )
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "error": "Validation Error",
                "message": "Request validation failed",
                "error_code": "VALIDATION_ERROR",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
                "validation_errors": [
                    {
                        "field": "notion_database_id",
                        "message": "Field is required",
                        "code": "REQUIRED"
                    },
                    {
                        "field": "file",
                        "message": "File size exceeds maximum limit",
                        "code": "FILE_TOO_LARGE"
                    }
                ]
            }
        }


class AuthenticationErrorResponse(ErrorResponse):
    """Specialized error response for authentication errors."""
    
    error: str = Field(default="Authentication Error")
    error_code: str = Field(default="AUTHENTICATION_ERROR")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "error": "Authentication Error",
                "message": "Invalid or missing authentication token",
                "error_code": "AUTHENTICATION_ERROR",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
                "details": {
                    "required_header": "X-Callback-Token"
                }
            }
        }


class ResourceNotFoundErrorResponse(ErrorResponse):
    """Specialized error response for resource not found errors."""
    
    error: str = Field(default="Resource Not Found")
    error_code: str = Field(default="RESOURCE_NOT_FOUND")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "error": "Resource Not Found",
                "message": "Job with the specified ID was not found",
                "error_code": "RESOURCE_NOT_FOUND",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
                "details": {
                    "resource_type": "job",
                    "resource_id": "550e8400-e29b-41d4-a716-446655440000"
                }
            }
        }


class ServiceUnavailableErrorResponse(ErrorResponse):
    """Specialized error response for service unavailable errors."""
    
    error: str = Field(default="Service Unavailable")
    error_code: str = Field(default="SERVICE_UNAVAILABLE")
    retry_after: Optional[int] = Field(
        None,
        description="Seconds to wait before retrying the request"
    )
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "error": "Service Unavailable",
                "message": "Queue service is temporarily unavailable",
                "error_code": "SERVICE_UNAVAILABLE",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
                "retry_after": 30,
                "details": {
                    "service": "redis_queue",
                    "reason": "Connection timeout"
                }
            }
        }


class InternalServerErrorResponse(ErrorResponse):
    """Specialized error response for internal server errors."""
    
    error: str = Field(default="Internal Server Error")
    error_code: str = Field(default="INTERNAL_SERVER_ERROR")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing the request",
                "error_code": "INTERNAL_SERVER_ERROR",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
                "details": {
                    "support_message": "Please contact support if this error persists"
                }
            }
        }


class JobStatusResponse(BaseModel):
    """Response model for job status queries."""
    
    job_id: UUID = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Current job status")
    filename: Optional[str] = Field(None, description="Original filename")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    result_message: Optional[str] = Field(None, description="Result or error message")
    notion_page_url: Optional[str] = Field(None, description="Created Notion page URL")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() + "Z"
        }
        schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "success",
                "filename": "receipt_2024_01_15.jpg",
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:32:15Z",
                "result_message": "Receipt processed successfully",
                "notion_page_url": "https://notion.so/page/abc123"
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoints."""
    
    status: str = Field(..., description="Overall health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    checks: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Individual component health checks"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "Accounting Automation Backend",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z",
                "checks": {
                    "database": {
                        "status": "healthy",
                        "message": "Connected"
                    },
                    "redis_queue": {
                        "status": "healthy",
                        "message": "Connected",
                        "queue_info": {
                            "length": 5,
                            "failed_job_count": 0
                        }
                    }
                }
            }
        }