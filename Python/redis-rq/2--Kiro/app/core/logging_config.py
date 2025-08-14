"""
Structured logging configuration for the application.

This module provides comprehensive logging setup with structured JSON formatting,
performance metrics, and context-aware logging for better observability.
"""

import json
import logging
import logging.config
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from pythonjsonlogger import jsonlogger


class ContextFilter(logging.Filter):
    """Logging filter that adds request context to log records."""
    
    def __init__(self):
        """Initialize context filter."""
        super().__init__()
        self.request_id = None
        self.user_id = None
        self.job_id = None
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context information to log record.
        
        Args:
            record: Log record to enhance
            
        Returns:
            True to allow the record to be processed
        """
        # Add request ID if available
        if hasattr(record, 'request_id'):
            record.request_id = getattr(record, 'request_id')
        elif self.request_id:
            record.request_id = self.request_id
        else:
            record.request_id = None
        
        # Add job ID if available
        if hasattr(record, 'job_id'):
            record.job_id = getattr(record, 'job_id')
        elif self.job_id:
            record.job_id = self.job_id
        else:
            record.job_id = None
        
        # Add user ID if available
        if hasattr(record, 'user_id'):
            record.user_id = getattr(record, 'user_id')
        elif self.user_id:
            record.user_id = self.user_id
        else:
            record.user_id = None
        
        return True
    
    def set_request_context(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> None:
        """Set context for subsequent log messages.
        
        Args:
            request_id: Unique request identifier
            user_id: User identifier
            job_id: Job identifier
        """
        self.request_id = request_id
        self.user_id = user_id
        self.job_id = job_id


class CustomJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with enhanced fields and formatting."""
    
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        """Add custom fields to the log record.
        
        Args:
            log_record: Dictionary to be serialized as JSON
            record: Original log record
            message_dict: Message dictionary
        """
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add service information
        log_record['service'] = 'accounting-automation-backend'
        log_record['version'] = '1.0.0'
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add thread and process information
        log_record['thread_id'] = record.thread
        log_record['process_id'] = record.process
        
        # Add filename and line number for debugging
        log_record['source_filename'] = record.filename
        log_record['line_number'] = record.lineno
        log_record['function_name'] = record.funcName
        
        # Add context fields if available
        if hasattr(record, 'request_id') and record.request_id:
            log_record['request_id'] = record.request_id
        
        if hasattr(record, 'job_id') and record.job_id:
            log_record['job_id'] = record.job_id
        
        if hasattr(record, 'user_id') and record.user_id:
            log_record['user_id'] = record.user_id
        
        # Add performance metrics if available
        if hasattr(record, 'duration_ms'):
            log_record['duration_ms'] = record.duration_ms
        
        if hasattr(record, 'memory_usage_mb'):
            log_record['memory_usage_mb'] = record.memory_usage_mb
        
        # Add error information if available
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        # Add stack trace if available
        if record.stack_info:
            log_record['stack_trace'] = record.stack_info


class PerformanceLogger:
    """Logger for tracking performance metrics and timing."""
    
    def __init__(self, logger: logging.Logger):
        """Initialize performance logger.
        
        Args:
            logger: Logger instance to use for output
        """
        self.logger = logger
        self.start_time = None
        self.operation_name = None
    
    def start_operation(self, operation_name: str, **context: Any) -> None:
        """Start timing an operation.
        
        Args:
            operation_name: Name of the operation being timed
            **context: Additional context to log
        """
        self.operation_name = operation_name
        self.start_time = time.time()
        
        self.logger.info(
            f"Starting operation: {operation_name}",
            extra={
                "operation": operation_name,
                "operation_status": "started",
                **context
            }
        )
    
    def end_operation(
        self,
        success: bool = True,
        error_message: Optional[str] = None,
        **context: Any
    ) -> float:
        """End timing an operation and log the results.
        
        Args:
            success: Whether the operation succeeded
            error_message: Error message if operation failed
            **context: Additional context to log
            
        Returns:
            Duration of the operation in seconds
        """
        if self.start_time is None:
            self.logger.warning("end_operation called without start_operation")
            return 0.0
        
        duration = time.time() - self.start_time
        duration_ms = duration * 1000
        
        log_level = logging.INFO if success else logging.ERROR
        status = "completed" if success else "failed"
        
        log_extra = {
            "operation": self.operation_name,
            "operation_status": status,
            "duration_ms": round(duration_ms, 2),
            "duration_seconds": round(duration, 3),
            **context
        }
        
        if error_message:
            log_extra["error_message"] = error_message
        
        message = f"Operation {status}: {self.operation_name} ({duration_ms:.2f}ms)"
        if error_message:
            message += f" - {error_message}"
        
        self.logger.log(log_level, message, extra=log_extra)
        
        # Reset state
        self.start_time = None
        self.operation_name = None
        
        return duration


def setup_logging(
    log_level: str = "INFO",
    enable_json_logging: bool = True,
    log_file: Optional[str] = None
) -> None:
    """Setup structured logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json_logging: Whether to use JSON formatting
        log_file: Optional file path for file logging
    """
    # Create context filter instance
    context_filter = ContextFilter()
    
    # Configure formatters
    if enable_json_logging:
        formatter = CustomJSONFormatter(
            fmt='%(timestamp)s %(level)s %(logger)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Configure handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)
    handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Configure specific loggers
    configure_library_loggers()
    
    # Store context filter globally for access
    logging.getLogger().context_filter = context_filter


def configure_library_loggers() -> None:
    """Configure logging levels for third-party libraries."""
    
    # Reduce noise from HTTP libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Reduce noise from database libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Reduce noise from Redis/RQ
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("rq.worker").setLevel(logging.INFO)
    logging.getLogger("rq.job").setLevel(logging.INFO)
    
    # Keep FastAPI logs at INFO level
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def get_performance_logger(name: str) -> PerformanceLogger:
    """Get a performance logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Performance logger instance
    """
    logger = get_logger(name)
    return PerformanceLogger(logger)


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    job_id: Optional[str] = None
) -> None:
    """Set logging context for the current request.
    
    Args:
        request_id: Unique request identifier
        user_id: User identifier
        job_id: Job identifier
    """
    root_logger = logging.getLogger()
    if hasattr(root_logger, 'context_filter'):
        root_logger.context_filter.set_request_context(
            request_id=request_id,
            user_id=user_id,
            job_id=job_id
        )


def generate_request_id() -> str:
    """Generate a unique request ID.
    
    Returns:
        Unique request identifier
    """
    return f"req_{uuid4().hex[:12]}"


# Convenience function for structured logging with context
def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context: Any
) -> None:
    """Log a message with additional context.
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **context: Additional context fields
    """
    logger.log(level, message, extra=context)