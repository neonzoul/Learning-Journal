"""
Domain models and data structures.

This module defines core domain entities and value objects used throughout
the application, with strong typing and validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Enumeration of possible job statuses."""
    
    QUEUED = "queued"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILURE = "failure"


class JobInfo(BaseModel):
    """Domain model representing job information."""
    
    job_id: UUID = Field(..., description="Unique identifier for the job")
    status: JobStatus = Field(default=JobStatus.QUEUED, description="Current job status")
    filename: Optional[str] = Field(None, description="Original filename of uploaded file")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    result_message: Optional[str] = Field(None, description="Result message or error details")
    notion_page_url: Optional[str] = Field(None, description="URL of created Notion page")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class FileUploadInfo(BaseModel):
    """Domain model for file upload information."""
    
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")
    size: int = Field(..., description="File size in bytes")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "filename": "receipt.jpg",
                "content_type": "image/jpeg",
                "size": 1024000
            }
        }