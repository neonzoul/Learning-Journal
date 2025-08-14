"""
Middleware for error handling, logging, and request processing.

This module provides FastAPI middleware for comprehensive error handling,
request/response logging, and performance monitoring.
"""

import json
import logging
import time
import traceback
from typing import Callable, Dict, Any
from uuid import uuid4

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.exceptions import BaseApplicationError
from app.core.logging_config import set_request_context, get_logger
from app.domain.error_schemas import (
    ErrorResponse,
    ValidationErrorResponse,
    AuthenticationErrorResponse,
    ResourceNotFoundErrorResponse,
    ServiceUnavailableErrorResponse,
    InternalServerErrorResponse
)


logger = get_logger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global exception handling and error response formatting."""
    
    def __init__(self, app: ASGIApp):
        """Initialize error handling middleware.
        
        Args:
            app: ASGI application instance
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle any exceptions.
        
        Args:
            request: HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response with proper error formatting if needed
        """
        try:
            response = await call_next(request)
            return response
            
        except BaseApplicationError as e:
            # Handle custom application errors
            return await self._handle_application_error(request, e)
            
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            return await self._handle_http_exception(request, e)
            
        except Exception as e:
            # Handle unexpected errors
            return await self._handle_unexpected_error(request, e)
    
    async def _handle_application_error(
        self,
        request: Request,
        error: BaseApplicationError
    ) -> JSONResponse:
        """Handle custom application errors.
        
        Args:
            request: HTTP request
            error: Application error instance
            
        Returns:
            JSON error response
        """
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the error with context
        logger.error(
            f"Application error: {error.message}",
            extra={
                "error_code": error.error_code,
                "status_code": error.status_code,
                "error_details": error.details,
                "request_id": request_id,
                "path": str(request.url),
                "method": request.method
            }
        )
        
        # Create appropriate error response based on status code
        if error.status_code == 400:
            error_response = ValidationErrorResponse(
                message=error.message,
                error_code=error.error_code,
                request_id=request_id,
                details=error.details
            )
        elif error.status_code == 401:
            error_response = AuthenticationErrorResponse(
                message=error.message,
                error_code=error.error_code,
                request_id=request_id,
                details=error.details
            )
        elif error.status_code == 404:
            error_response = ResourceNotFoundErrorResponse(
                message=error.message,
                error_code=error.error_code,
                request_id=request_id,
                details=error.details
            )
        elif error.status_code == 503:
            error_response = ServiceUnavailableErrorResponse(
                message=error.message,
                error_code=error.error_code,
                request_id=request_id,
                details=error.details
            )
        else:
            error_response = ErrorResponse(
                error=error.__class__.__name__.replace('Error', ' Error'),
                message=error.message,
                error_code=error.error_code,
                request_id=request_id,
                details=error.details
            )
        
        return JSONResponse(
            status_code=error.status_code,
            content=error_response.dict()
        )
    
    async def _handle_http_exception(
        self,
        request: Request,
        error: HTTPException
    ) -> JSONResponse:
        """Handle FastAPI HTTP exceptions.
        
        Args:
            request: HTTP request
            error: HTTP exception instance
            
        Returns:
            JSON error response
        """
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the error
        logger.warning(
            f"HTTP exception: {error.detail}",
            extra={
                "status_code": error.status_code,
                "request_id": request_id,
                "path": str(request.url),
                "method": request.method
            }
        )
        
        # Map status codes to error types
        error_code_map = {
            400: "VALIDATION_ERROR",
            401: "AUTHENTICATION_ERROR",
            403: "AUTHORIZATION_ERROR",
            404: "RESOURCE_NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            413: "PAYLOAD_TOO_LARGE",
            422: "UNPROCESSABLE_ENTITY",
            429: "RATE_LIMIT_ERROR",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
            504: "GATEWAY_TIMEOUT"
        }
        
        error_code = error_code_map.get(error.status_code, "HTTP_ERROR")
        
        # Handle detail as dict or string
        if isinstance(error.detail, dict):
            message = error.detail.get("message", str(error.detail))
            details = error.detail
        else:
            message = str(error.detail)
            details = None
        
        # Create appropriate error response
        if error.status_code == 401:
            error_response = AuthenticationErrorResponse(
                message=message,
                error_code=error_code,
                request_id=request_id,
                details=details
            )
        elif error.status_code == 404:
            error_response = ResourceNotFoundErrorResponse(
                message=message,
                error_code=error_code,
                request_id=request_id,
                details=details
            )
        elif error.status_code == 503:
            error_response = ServiceUnavailableErrorResponse(
                message=message,
                error_code=error_code,
                request_id=request_id,
                details=details
            )
        else:
            error_response = ErrorResponse(
                error="HTTP Error",
                message=message,
                error_code=error_code,
                request_id=request_id,
                details=details
            )
        
        return JSONResponse(
            status_code=error.status_code,
            content=error_response.dict()
        )
    
    async def _handle_unexpected_error(
        self,
        request: Request,
        error: Exception
    ) -> JSONResponse:
        """Handle unexpected errors.
        
        Args:
            request: HTTP request
            error: Exception instance
            
        Returns:
            JSON error response
        """
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the error with full traceback
        logger.error(
            f"Unexpected error: {str(error)}",
            extra={
                "error_type": error.__class__.__name__,
                "request_id": request_id,
                "path": str(request.url),
                "method": request.method,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        # Create internal server error response
        error_response = InternalServerErrorResponse(
            message="An unexpected error occurred while processing the request",
            request_id=request_id,
            details={
                "support_message": "Please contact support if this error persists",
                "error_type": error.__class__.__name__
            }
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging and performance monitoring."""
    
    def __init__(self, app: ASGIApp, log_requests: bool = True, log_responses: bool = True):
        """Initialize request logging middleware.
        
        Args:
            app: ASGI application instance
            log_requests: Whether to log incoming requests
            log_responses: Whether to log outgoing responses
        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging and performance monitoring.
        
        Args:
            request: HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        # Generate request ID
        request_id = f"req_{uuid4().hex[:12]}"
        request.state.request_id = request_id
        
        # Set logging context
        set_request_context(request_id=request_id)
        
        # Record start time
        start_time = time.time()
        
        # Log incoming request
        if self.log_requests:
            await self._log_request(request, request_id)
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        process_time_ms = process_time * 1000
        
        # Add performance headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
        
        # Log outgoing response
        if self.log_responses:
            await self._log_response(request, response, request_id, process_time_ms)
        
        return response
    
    async def _log_request(self, request: Request, request_id: str) -> None:
        """Log incoming request details.
        
        Args:
            request: HTTP request
            request_id: Unique request identifier
        """
        # Get request body size
        body_size = 0
        if hasattr(request, '_body'):
            body_size = len(request._body) if request._body else 0
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get user agent
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length"),
                "body_size": body_size,
                "headers": dict(request.headers) if logger.isEnabledFor(logging.DEBUG) else None
            }
        )
    
    async def _log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        process_time_ms: float
    ) -> None:
        """Log outgoing response details.
        
        Args:
            request: HTTP request
            response: HTTP response
            request_id: Unique request identifier
            process_time_ms: Processing time in milliseconds
        """
        # Get response body size
        body_size = 0
        if hasattr(response, 'body') and response.body:
            body_size = len(response.body)
        
        # Determine log level based on status code
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
        
        logger.log(
            log_level,
            f"Outgoing response: {response.status_code} for {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time_ms, 2),
                "response_size": body_size,
                "content_type": response.headers.get("content-type"),
                "headers": dict(response.headers) if logger.isEnabledFor(logging.DEBUG) else None
            }
        )


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting application metrics."""
    
    def __init__(self, app: ASGIApp):
        """Initialize metrics middleware.
        
        Args:
            app: ASGI application instance
        """
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
        self.total_process_time = 0.0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics.
        
        Args:
            request: HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        # Increment request counter
        self.request_count += 1
        
        # Record start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        self.total_process_time += process_time
        
        # Count errors
        if response.status_code >= 400:
            self.error_count += 1
        
        # Log metrics periodically (every 100 requests)
        if self.request_count % 100 == 0:
            avg_process_time = self.total_process_time / self.request_count
            error_rate = (self.error_count / self.request_count) * 100
            
            logger.info(
                "Application metrics update",
                extra={
                    "total_requests": self.request_count,
                    "total_errors": self.error_count,
                    "error_rate_percent": round(error_rate, 2),
                    "avg_process_time_ms": round(avg_process_time * 1000, 2),
                    "total_process_time_seconds": round(self.total_process_time, 2)
                }
            )
        
        return response
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current application metrics.
        
        Returns:
            Dictionary containing current metrics
        """
        avg_process_time = (
            self.total_process_time / self.request_count
            if self.request_count > 0 else 0
        )
        error_rate = (
            (self.error_count / self.request_count) * 100
            if self.request_count > 0 else 0
        )
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "avg_process_time_ms": round(avg_process_time * 1000, 2),
            "total_process_time_seconds": round(self.total_process_time, 2)
        }