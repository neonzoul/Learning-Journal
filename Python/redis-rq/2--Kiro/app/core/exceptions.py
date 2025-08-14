"""
Custom exception classes for the application.

This module defines application-specific exceptions that provide
structured error handling with appropriate HTTP status codes.
"""

from typing import Any, Dict, Optional
from uuid import UUID


class BaseApplicationError(Exception):
    """Base exception class for all application errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize base application error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            status_code: HTTP status code for the error
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class ValidationError(BaseApplicationError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            details: Additional validation details
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["invalid_value"] = str(value)
            
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=error_details
        )
        self.field = field
        self.value = value


class FileValidationError(ValidationError):
    """Raised when file validation fails."""
    
    def __init__(
        self,
        message: str,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        content_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize file validation error.
        
        Args:
            message: Error message
            filename: Name of the invalid file
            file_size: Size of the file in bytes
            content_type: MIME type of the file
            details: Additional validation details
        """
        error_details = details or {}
        if filename:
            error_details["filename"] = filename
        if file_size is not None:
            error_details["file_size"] = file_size
        if content_type:
            error_details["content_type"] = content_type
            
        super().__init__(
            message=message,
            field="file",
            details=error_details
        )
        self.filename = filename
        self.file_size = file_size
        self.content_type = content_type


class AuthenticationError(BaseApplicationError):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize authentication error.
        
        Args:
            message: Error message
            details: Additional authentication details
        """
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(BaseApplicationError):
    """Raised when authorization fails."""
    
    def __init__(
        self,
        message: str = "Access denied",
        resource: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize authorization error.
        
        Args:
            message: Error message
            resource: Resource being accessed
            action: Action being performed
            details: Additional authorization details
        """
        error_details = details or {}
        if resource:
            error_details["resource"] = resource
        if action:
            error_details["action"] = action
            
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=error_details
        )
        self.resource = resource
        self.action = action


class ResourceNotFoundError(BaseApplicationError):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize resource not found error.
        
        Args:
            message: Error message
            resource_type: Type of resource (e.g., "job", "file")
            resource_id: ID of the resource
            details: Additional resource details
        """
        error_details = details or {}
        if resource_type:
            error_details["resource_type"] = resource_type
        if resource_id:
            error_details["resource_id"] = resource_id
            
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=error_details
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class JobError(BaseApplicationError):
    """Raised when job processing fails."""
    
    def __init__(
        self,
        message: str,
        job_id: Optional[UUID] = None,
        job_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize job error.
        
        Args:
            message: Error message
            job_id: ID of the failed job
            job_status: Current status of the job
            details: Additional job details
        """
        error_details = details or {}
        if job_id:
            error_details["job_id"] = str(job_id)
        if job_status:
            error_details["job_status"] = job_status
            
        super().__init__(
            message=message,
            error_code="JOB_ERROR",
            status_code=500,
            details=error_details
        )
        self.job_id = job_id
        self.job_status = job_status


class QueueError(BaseApplicationError):
    """Raised when queue operations fail."""
    
    def __init__(
        self,
        message: str,
        queue_name: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize queue error.
        
        Args:
            message: Error message
            queue_name: Name of the queue
            operation: Operation that failed
            details: Additional queue details
        """
        error_details = details or {}
        if queue_name:
            error_details["queue_name"] = queue_name
        if operation:
            error_details["operation"] = operation
            
        super().__init__(
            message=message,
            error_code="QUEUE_ERROR",
            status_code=503,
            details=error_details
        )
        self.queue_name = queue_name
        self.operation = operation


class DatabaseError(BaseApplicationError):
    """Raised when database operations fail."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize database error.
        
        Args:
            message: Error message
            operation: Database operation that failed
            table: Database table involved
            details: Additional database details
        """
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        if table:
            error_details["table"] = table
            
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=error_details
        )
        self.operation = operation
        self.table = table


class ExternalServiceError(BaseApplicationError):
    """Raised when external service calls fail."""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize external service error.
        
        Args:
            message: Error message
            service_name: Name of the external service
            status_code: HTTP status code from the service
            response_body: Response body from the service
            details: Additional service details
        """
        error_details = details or {}
        if service_name:
            error_details["service_name"] = service_name
        if status_code:
            error_details["service_status_code"] = status_code
        if response_body:
            error_details["service_response"] = response_body[:500]  # Limit size
            
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=error_details
        )
        self.service_name = service_name
        self.service_status_code = status_code
        self.response_body = response_body


class ConfigurationError(BaseApplicationError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that's invalid
            details: Additional configuration details
        """
        error_details = details or {}
        if config_key:
            error_details["config_key"] = config_key
            
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details=error_details
        )
        self.config_key = config_key


class RateLimitError(BaseApplicationError):
    """Raised when rate limits are exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            details: Additional rate limit details
        """
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after
            
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=429,
            details=error_details
        )
        self.retry_after = retry_after