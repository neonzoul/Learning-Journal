"""
Pydantic schemas for API request/response models.

This module defines the data structures used for API communication,
providing validation and serialization capabilities.
"""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class JobCreationResponse(BaseModel):
    """Response model for job creation endpoint."""
    
    job_id: UUID = Field(..., description="Unique identifier for the created job")
    status: str = Field(default="queued", description="Initial status of the job")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str
        }


class JobCallbackPayload(BaseModel):
    """Payload model for job status callback from N8N workflow."""
    
    status: str = Field(..., description="Job completion status (success|failure)")
    message: Optional[str] = Field(None, description="Optional status message or error details")
    notion_page_url: Optional[str] = Field(None, description="URL of created Notion page on success")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Receipt processed successfully",
                "notion_page_url": "https://notion.so/page/abc123"
            }
        }