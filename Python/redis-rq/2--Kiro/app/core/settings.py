"""
Configuration management using Pydantic Settings.
Handles environment variable loading and validation.
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Accounting Automation Backend"
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for queue management"
    )
    
    # N8N Integration
    N8N_WEBHOOK_URL: str = Field(
        ...,
        description="N8N webhook URL for triggering workflows"
    )
    N8N_API_KEY: str = Field(
        ...,
        description="API key for N8N webhook authentication"
    )
    
    # Security
    CALLBACK_SECRET_TOKEN: str = Field(
        ...,
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
        description="Maximum file size in bytes"
    )
    ALLOWED_IMAGE_TYPES: list[str] = Field(
        default=["image/jpeg", "image/png", "image/jpg"],
        description="Allowed image MIME types"
    )
    
    # Queue Configuration
    QUEUE_DEFAULT_TIMEOUT: int = Field(
        default=300,  # 5 minutes
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()