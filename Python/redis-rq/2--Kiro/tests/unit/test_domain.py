"""Unit tests for domain models and schemas."""
import pytest
from datetime import datetime
from uuid import uuid4, UUID
from pydantic import ValidationError

from app.domain.schemas import JobCreationResponse, JobCallbackPayload
from app.domain.models import JobStatus, JobInfo, FileUploadInfo


class TestJobCreationResponse:
    """Test JobCreationResponse schema validation and serialization."""
    
    def test_valid_job_creation_response(self):
        """Test creating a valid JobCreationResponse."""
        job_id = uuid4()
        response = JobCreationResponse(job_id=job_id, status="queued")
        
        assert response.job_id == job_id
        assert response.status == "queued"
    
    def test_job_creation_response_default_status(self):
        """Test JobCreationResponse with default status."""
        job_id = uuid4()
        response = JobCreationResponse(job_id=job_id)
        
        assert response.job_id == job_id
        assert response.status == "queued"
    
    def test_job_creation_response_serialization(self):
        """Test JobCreationResponse JSON serialization."""
        job_id = uuid4()
        response = JobCreationResponse(job_id=job_id, status="processing")
        
        json_data = response.model_dump()
        assert json_data["job_id"] == job_id
        assert json_data["status"] == "processing"
    
    def test_job_creation_response_json_encoding(self):
        """Test JobCreationResponse JSON encoding with UUID."""
        job_id = uuid4()
        response = JobCreationResponse(job_id=job_id)
        
        json_str = response.model_dump_json()
        assert str(job_id) in json_str
        assert "queued" in json_str


class TestJobCallbackPayload:
    """Test JobCallbackPayload schema validation and serialization."""
    
    def test_valid_success_callback(self):
        """Test creating a valid success callback payload."""
        payload = JobCallbackPayload(
            status="success",
            message="Receipt processed successfully",
            notion_page_url="https://notion.so/page/abc123"
        )
        
        assert payload.status == "success"
        assert payload.message == "Receipt processed successfully"
        assert payload.notion_page_url == "https://notion.so/page/abc123"
    
    def test_valid_failure_callback(self):
        """Test creating a valid failure callback payload."""
        payload = JobCallbackPayload(
            status="failure",
            message="Processing failed: invalid image format"
        )
        
        assert payload.status == "failure"
        assert payload.message == "Processing failed: invalid image format"
        assert payload.notion_page_url is None
    
    def test_minimal_callback_payload(self):
        """Test creating callback payload with only required fields."""
        payload = JobCallbackPayload(status="success")
        
        assert payload.status == "success"
        assert payload.message is None
        assert payload.notion_page_url is None
    
    def test_callback_payload_serialization(self):
        """Test JobCallbackPayload JSON serialization."""
        payload = JobCallbackPayload(
            status="success",
            message="Test message",
            notion_page_url="https://test.url"
        )
        
        json_data = payload.model_dump()
        assert json_data["status"] == "success"
        assert json_data["message"] == "Test message"
        assert json_data["notion_page_url"] == "https://test.url"
    
    def test_callback_payload_missing_status(self):
        """Test JobCallbackPayload validation with missing status."""
        with pytest.raises(ValidationError) as exc_info:
            JobCallbackPayload()
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("status",)
        assert errors[0]["type"] == "missing"


class TestJobStatus:
    """Test JobStatus enumeration."""
    
    def test_job_status_values(self):
        """Test JobStatus enum values."""
        assert JobStatus.QUEUED == "queued"
        assert JobStatus.PROCESSING == "processing"
        assert JobStatus.SUCCESS == "success"
        assert JobStatus.FAILURE == "failure"
    
    def test_job_status_membership(self):
        """Test JobStatus enum membership."""
        assert "queued" in JobStatus
        assert "processing" in JobStatus
        assert "success" in JobStatus
        assert "failure" in JobStatus
        assert "invalid" not in JobStatus


class TestJobInfo:
    """Test JobInfo domain model validation and serialization."""
    
    def test_valid_job_info_creation(self):
        """Test creating a valid JobInfo instance."""
        job_id = uuid4()
        created_at = datetime.utcnow()
        
        job_info = JobInfo(
            job_id=job_id,
            status=JobStatus.QUEUED,
            filename="test_receipt.jpg",
            created_at=created_at
        )
        
        assert job_info.job_id == job_id
        assert job_info.status == JobStatus.QUEUED
        assert job_info.filename == "test_receipt.jpg"
        assert job_info.created_at == created_at
        assert job_info.completed_at is None
        assert job_info.result_message is None
        assert job_info.notion_page_url is None
    
    def test_job_info_default_values(self):
        """Test JobInfo with default values."""
        job_id = uuid4()
        job_info = JobInfo(job_id=job_id)
        
        assert job_info.job_id == job_id
        assert job_info.status == JobStatus.QUEUED
        assert job_info.filename is None
        assert isinstance(job_info.created_at, datetime)
        assert job_info.completed_at is None
    
    def test_job_info_completed_job(self):
        """Test JobInfo for a completed job."""
        job_id = uuid4()
        created_at = datetime.utcnow()
        completed_at = datetime.utcnow()
        
        job_info = JobInfo(
            job_id=job_id,
            status=JobStatus.SUCCESS,
            filename="receipt.png",
            created_at=created_at,
            completed_at=completed_at,
            result_message="Successfully processed",
            notion_page_url="https://notion.so/page/xyz789"
        )
        
        assert job_info.status == JobStatus.SUCCESS
        assert job_info.completed_at == completed_at
        assert job_info.result_message == "Successfully processed"
        assert job_info.notion_page_url == "https://notion.so/page/xyz789"
    
    def test_job_info_serialization(self):
        """Test JobInfo JSON serialization."""
        job_id = uuid4()
        job_info = JobInfo(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            filename="test.jpg"
        )
        
        json_data = job_info.model_dump()
        assert json_data["job_id"] == job_id
        assert json_data["status"] == "processing"  # Enum value serialized
        assert json_data["filename"] == "test.jpg"
        assert "created_at" in json_data
    
    def test_job_info_json_encoders(self):
        """Test JobInfo custom JSON encoders."""
        job_id = uuid4()
        job_info = JobInfo(job_id=job_id, status=JobStatus.SUCCESS)
        
        json_str = job_info.model_dump_json()
        assert str(job_id) in json_str
        assert "success" in json_str
        # Check ISO format datetime
        assert job_info.created_at.isoformat() in json_str


class TestFileUploadInfo:
    """Test FileUploadInfo domain model validation and serialization."""
    
    def test_valid_file_upload_info(self):
        """Test creating a valid FileUploadInfo instance."""
        file_info = FileUploadInfo(
            filename="receipt.jpg",
            content_type="image/jpeg",
            size=1024000
        )
        
        assert file_info.filename == "receipt.jpg"
        assert file_info.content_type == "image/jpeg"
        assert file_info.size == 1024000
    
    def test_file_upload_info_validation(self):
        """Test FileUploadInfo field validation."""
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            FileUploadInfo()
        
        errors = exc_info.value.errors()
        assert len(errors) == 3  # filename, content_type, size
        
        required_fields = {error["loc"][0] for error in errors}
        assert required_fields == {"filename", "content_type", "size"}
    
    def test_file_upload_info_serialization(self):
        """Test FileUploadInfo JSON serialization."""
        file_info = FileUploadInfo(
            filename="test.png",
            content_type="image/png",
            size=2048000
        )
        
        json_data = file_info.model_dump()
        assert json_data["filename"] == "test.png"
        assert json_data["content_type"] == "image/png"
        assert json_data["size"] == 2048000
    
    def test_file_upload_info_invalid_size(self):
        """Test FileUploadInfo with invalid size."""
        with pytest.raises(ValidationError) as exc_info:
            FileUploadInfo(
                filename="test.jpg",
                content_type="image/jpeg",
                size="invalid"  # Should be int
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("size",)
        assert errors[0]["type"] == "int_parsing"