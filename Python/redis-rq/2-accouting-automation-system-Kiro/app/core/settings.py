"""
Configuration management using Pydantic Settings.
Handles environment variable loading and validation.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables with comprehensive validation."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Accounting Automation Backend"
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for queue management"
    )
    
    # N8N Integration (Required)
    N8N_WEBHOOK_URL: str = Field(
        ...,
        description="N8N webhook URL for triggering workflows"
    )
    N8N_API_KEY: str = Field(
        ...,
        min_length=8,
        description="API key for N8N webhook authentication"
    )
    
    # Security (Required)
    CALLBACK_SECRET_TOKEN: str = Field(
        ...,
        min_length=16,
        description="Secret token for authenticating callback requests"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./job_logs.db",
        description="Database URL for job logging"
    )
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        ge=1024,  # Minimum 1KB
        le=100 * 1024 * 1024,  # Maximum 100MB
        description="Maximum file size in bytes"
    )
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/jpg"],
        description="Allowed image MIME types"
    )
    
    # Queue Configuration
    QUEUE_DEFAULT_TIMEOUT: int = Field(
        default=300,  # 5 minutes
        ge=30,  # Minimum 30 seconds
        le=3600,  # Maximum 1 hour
        description="Default job timeout in seconds"
    )
    
    # SSL Configuration
    VERIFY_SSL: bool = Field(
        default=True,
        description="Whether to verify SSL certificates for HTTPS requests"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    ENABLE_JSON_LOGGING: bool = Field(
        default=True,
        description="Whether to use structured JSON logging"
    )
    LOG_FILE: Optional[str] = Field(
        default=None,
        description="Optional log file path"
    )
    
    # Request Logging Configuration
    LOG_REQUESTS: bool = Field(
        default=True,
        description="Whether to log incoming requests"
    )
    LOG_RESPONSES: bool = Field(
        default=True,
        description="Whether to log outgoing responses"
    )
    
    # Development Configuration
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )
    
    # Production Configuration
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    PORT: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port"
    )
    WORKERS: int = Field(
        default=1,
        ge=1,
        le=32,
        description="Number of worker processes"
    )
    
    # Monitoring Configuration
    ENABLE_RQ_DASHBOARD: bool = Field(
        default=True,
        description="Enable RQ Dashboard for queue monitoring"
    )
    ENABLE_HEALTH_CHECKS: bool = Field(
        default=True,
        description="Enable health check endpoints"
    )
    ENABLE_METRICS: bool = Field(
        default=True,
        description="Enable metrics collection"
    )
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in allowed_levels:
            raise ValueError(f'LOG_LEVEL must be one of: {", ".join(allowed_levels)}')
        return v.upper()
    
    @field_validator('REDIS_URL')
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        try:
            parsed = urlparse(v)
            if parsed.scheme not in ('redis', 'rediss'):
                raise ValueError('Redis URL must use redis:// or rediss:// scheme')
            if not parsed.hostname:
                raise ValueError('Redis URL must include hostname')
            return v
        except Exception as e:
            raise ValueError(f'Invalid Redis URL format: {e}')
    
    @field_validator('N8N_WEBHOOK_URL')
    @classmethod
    def validate_n8n_webhook_url(cls, v: str) -> str:
        """Validate N8N webhook URL format."""
        try:
            parsed = urlparse(v)
            if parsed.scheme not in ('http', 'https'):
                raise ValueError('N8N webhook URL must use http:// or https:// scheme')
            if not parsed.hostname:
                raise ValueError('N8N webhook URL must include hostname')
            return v
        except Exception as e:
            raise ValueError(f'Invalid N8N webhook URL format: {e}')
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        try:
            parsed = urlparse(v)
            if parsed.scheme not in ('sqlite', 'postgresql', 'mysql'):
                raise ValueError('Database URL must use sqlite://, postgresql://, or mysql:// scheme')
            return v
        except Exception as e:
            raise ValueError(f'Invalid database URL format: {e}')
    
    @field_validator('ALLOWED_IMAGE_TYPES')
    @classmethod
    def validate_image_types(cls, v: List[str]) -> List[str]:
        """Validate allowed image types."""
        valid_types = {'image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/webp'}
        for mime_type in v:
            if mime_type not in valid_types:
                raise ValueError(f'Invalid image type: {mime_type}. Allowed: {", ".join(valid_types)}')
        return v
    
    @field_validator('LOG_FILE')
    @classmethod
    def validate_log_file(cls, v: Optional[str]) -> Optional[str]:
        """Validate log file path and ensure directory exists."""
        if v is None:
            return v
        
        log_path = Path(v)
        
        # Create parent directories if they don't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if we can write to the directory
        if not os.access(log_path.parent, os.W_OK):
            raise ValueError(f'Cannot write to log file directory: {log_path.parent}')
        
        return v
    
    @model_validator(mode='after')
    def validate_production_settings(self) -> 'Settings':
        """Validate production-specific settings."""
        # In production, ensure secure configurations
        if not self.DEBUG:
            # Warn about insecure CORS settings in production
            if "*" in self.CORS_ORIGINS:
                logging.warning(
                    "CORS_ORIGINS contains '*' which is insecure for production. "
                    "Consider specifying exact origins."
                )
            
            # Ensure SSL verification is enabled for production
            if not self.VERIFY_SSL:
                logging.warning(
                    "SSL verification is disabled. This is insecure for production environments."
                )
            
            # Ensure strong tokens in production
            if len(self.CALLBACK_SECRET_TOKEN) < 32:
                logging.warning(
                    "CALLBACK_SECRET_TOKEN is shorter than 32 characters. "
                    "Consider using a longer token for better security."
                )
        
        return self
    
    def validate_startup_requirements(self) -> None:
        """Validate that all required configurations are properly set for startup."""
        errors = []
        
        # Check required environment variables
        required_vars = ['N8N_WEBHOOK_URL', 'N8N_API_KEY', 'CALLBACK_SECRET_TOKEN']
        for var in required_vars:
            if not getattr(self, var, None):
                errors.append(f'Required environment variable {var} is not set')
        
        # Validate database directory exists and is writable
        if self.DATABASE_URL.startswith('sqlite:///'):
            db_path = Path(self.DATABASE_URL.replace('sqlite:///', ''))
            db_dir = db_path.parent
            if not db_dir.exists():
                try:
                    db_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f'Cannot create database directory {db_dir}: {e}')
            elif not os.access(db_dir, os.W_OK):
                errors.append(f'Database directory {db_dir} is not writable')
        
        # Validate log file directory if specified
        if self.LOG_FILE:
            log_path = Path(self.LOG_FILE)
            if not log_path.parent.exists():
                try:
                    log_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f'Cannot create log directory {log_path.parent}: {e}')
        
        if errors:
            raise ValueError(f'Configuration validation failed:\n' + '\n'.join(f'  - {error}' for error in errors))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()

# Validate startup requirements when settings are loaded
try:
    settings.validate_startup_requirements()
except ValueError as e:
    logging.error(f"Configuration validation failed: {e}")
    raise