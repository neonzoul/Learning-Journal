"""Unit tests for API endpoints."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from io import BytesIO

from fastapi.testclient import TestClient
from fastapi import UploadFile, status

from app.domain.schemas import JobCreationResponse, JobCallbackPayload
from app.core.exceptions import (
    FileValidationError,
    ValidationError,
    AuthenticationError,
    ResourceNotFoundError,
    DatabaseError,
    JobError
)


class TestReceiptsAPI:
    """Test receipts upload API endpoints."""
    
    def test_upload_receipt_success(self, client, sample_image_bytes):
        """Test successful receipt upload."""
        with patch('app.api.v1.receipts.get_task_service') as mock_get_service:
            # Mock task service
            mock_task_service = Mock()
            mock_task_service.create_and_enqueue_job = AsyncMock(
                return_value=JobCreationResponse(
                    job_id=uuid4(),
                    status="queued"
                )
            )
            mock_get_service.return_value = mock_task_service
            
            # Prepare test data
            files = {
                "file": ("test_receipt.jpg", BytesIO(sample_image_bytes), "image/jpeg")
            }
            data = {
                "notion_database_id": "12345678901234567890123456789012"
            }
            
            # Make request
            response = client.post("/api/v1/receipts/upload", files=files, data=data)
            
            # Verify response
            assert response.status_code == status.HTTP_202_ACCEPTED
            response_data = response.json()
            assert "job_id" in response_data
            assert response_data["status"] == "queued"
            
            # Verify task service was called
            mock_task_service.create_and_enqueue_job.assert_called_once()
    
    def test_upload_receipt_missing_file(self, client):
        """Test upload with missing file."""
        data = {
            "notion_database_id": "12345678901234567890123456789012"
        }
        
        response = client.post("/api/v1/receipts/upload", data=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = response.json()
        assert "detail" in response_data
    
    def test_upload_receipt_missing_notion_database_id(self, client, sample_image_bytes):
        """Test upload with missing notion_database_id."""
        files = {
            "file": ("test_receipt.jpg", BytesIO(sample_image_bytes), "image/jpeg")
        }
        
        response = client.post("/api/v1/receipts/upload", files=files)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = response.json()
        assert "detail" in response_data
    
    def test_upload_receipt_invalid_notion_database_id(self, client, sample_image_bytes):
        """Test upload with invalid notion_database_id format."""
        files = {
            "file": ("test_receipt.jpg", BytesIO(sample_image_bytes), "image/jpeg")
        }
        data = {
            "notion_database_id": "invalid-id"
        }
        
        response = client.post("/api/v1/receipts/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "notion_database_id must be a valid" in response_data["message"]
    
    def test_upload_receipt_empty_notion_database_id(self, client, sample_image_bytes):
        """Test upload with empty notion_database_id."""
        files = {
            "file": ("test_receipt.jpg", BytesIO(sample_image_bytes), "image/jpeg")
        }
        data = {
            "notion_database_id": ""
        }
        
        response = client.post("/api/v1/receipts/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "notion_database_id cannot be empty" in response_data["message"]
    
    def test_upload_receipt_large_file(self, client, large_image_bytes):
        """Test upload with file exceeding size limit."""
        files = {
            "file": ("large_receipt.jpg", BytesIO(large_image_bytes), "image/jpeg")
        }
        data = {
            "notion_database_id": "12345678901234567890123456789012"
        }
        
        response = client.post("/api/v1/receipts/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        response_data = response.json()
        assert "exceeds maximum allowed size" in response_data["message"]
    
    def test_upload_receipt_invalid_file_format(self, client, invalid_file_bytes):
        """Test upload with invalid file format."""
        files = {
            "file": ("not_an_image.txt", BytesIO(invalid_file_bytes), "text/plain")
        }
        data = {
            "notion_database_id": "12345678901234567890123456789012"
        }
        
        response = client.post("/api/v1/receipts/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "File format could not be validated" in response_data["message"]
    
    def test_upload_receipt_png_format(self, client, sample_png_bytes):
        """Test successful upload with PNG format."""
        with patch('app.api.v1.receipts.get_task_service') as mock_get_service:
            # Mock task service
            mock_task_service = Mock()
            mock_task_service.create_and_enqueue_job = AsyncMock(
                return_value=JobCreationResponse(
                    job_id=uuid4(),
                    status="queued"
                )
            )
            mock_get_service.return_value = mock_task_service
            
            files = {
                "file": ("test_receipt.png", BytesIO(sample_png_bytes), "image/png")
            }
            data = {
                "notion_database_id": "12345678901234567890123456789012"
            }
            
            response = client.post("/api/v1/receipts/upload", files=files, data=data)
            
            assert response.status_code == status.HTTP_202_ACCEPTED
            response_data = response.json()
            assert "job_id" in response_data
            assert response_data["status"] == "queued"
    
    def test_upload_receipt_task_service_error(self, client, sample_image_bytes):
        """Test upload when task service fails."""
        with patch('app.api.v1.receipts.get_task_service') as mock_get_service:
            # Mock task service to raise error
            mock_task_service = Mock()
            mock_task_service.create_and_enqueue_job = AsyncMock(
                side_effect=JobError("Task service failed")
            )
            mock_get_service.return_value = mock_task_service
            
            files = {
                "file": ("test_receipt.jpg", BytesIO(sample_image_bytes), "image/jpeg")
            }
            data = {
                "notion_database_id": "12345678901234567890123456789012"
            }
            
            response = client.post("/api/v1/receipts/upload", files=files, data=data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            response_data = response.json()
            assert "Task service failed" in response_data["message"]
    
    def test_receipts_health_check(self, client):
        """Test receipts health check endpoint."""
        response = client.get("/api/v1/receipts/health")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert response_data["service"] == "receipts"


class TestJobsAPI:
    """Test jobs callback and status API endpoints."""
    
    def test_job_callback_success(self, client, test_settings):
        """Test successful job callback."""
        job_id = uuid4()
        
        with patch('app.api.v1.jobs.get_logging_service') as mock_get_service:
            # Mock logging service
            mock_logging_service = Mock()
            mock_job_log = Mock()
            mock_job_log.completed_at = Mock()
            mock_job_log.completed_at.isoformat.return_value = "2023-01-01T12:00:00"
            mock_logging_service.update_job_status.return_value = mock_job_log
            mock_get_service.return_value = mock_logging_service
            
            # Prepare callback payload
            payload = {
                "status": "success",
                "message": "Processing completed successfully",
                "notion_page_url": "https://notion.so/page/abc123"
            }
            
            headers = {
                "X-Callback-Token": test_settings.CALLBACK_SECRET_TOKEN
            }
            
            # Make request
            response = client.post(
                f"/api/v1/jobs/{job_id}/callback",
                json=payload,
                headers=headers
            )
            
            # Verify response
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["message"] == "Job status updated successfully"
            assert response_data["job_id"] == str(job_id)
            assert response_data["status"] == "success"
            
            # Verify logging service was called
            mock_logging_service.update_job_status.assert_called_once_with(
                job_id=job_id,
                status="success",
                result_message="Processing completed successfully",
                notion_page_url="https://notion.so/page/abc123"
            )
    
    def test_job_callback_failure(self, client, test_settings):
        """Test job callback with failure status."""
        job_id = uuid4()
        
        with patch('app.api.v1.jobs.get_logging_service') as mock_get_service:
            # Mock logging service
            mock_logging_service = Mock()
            mock_job_log = Mock()
            mock_job_log.completed_at = Mock()
            mock_job_log.completed_at.isoformat.return_value = "2023-01-01T12:00:00"
            mock_logging_service.update_job_status.return_value = mock_job_log
            mock_get_service.return_value = mock_logging_service
            
            payload = {
                "status": "failure",
                "message": "Processing failed: invalid image format"
            }
            
            headers = {
                "X-Callback-Token": test_settings.CALLBACK_SECRET_TOKEN
            }
            
            response = client.post(
                f"/api/v1/jobs/{job_id}/callback",
                json=payload,
                headers=headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["status"] == "failure"
            
            # Verify logging service was called with failure details
            mock_logging_service.update_job_status.assert_called_once_with(
                job_id=job_id,
                status="failure",
                result_message="Processing failed: invalid image format",
                notion_page_url=None
            )
    
    def test_job_callback_missing_token(self, client):
        """Test job callback without authentication token."""
        job_id = uuid4()
        payload = {"status": "success"}
        
        response = client.post(f"/api/v1/jobs/{job_id}/callback", json=payload)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = response.json()
        assert "Missing X-Callback-Token header" in response_data["message"]
    
    def test_job_callback_invalid_token(self, client):
        """Test job callback with invalid authentication token."""
        job_id = uuid4()
        payload = {"status": "success"}
        headers = {"X-Callback-Token": "invalid-token"}
        
        response = client.post(
            f"/api/v1/jobs/{job_id}/callback",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = response.json()
        assert "Invalid callback token" in response_data["message"]
    
    def test_job_callback_job_not_found(self, client, test_settings):
        """Test job callback for non-existent job."""
        job_id = uuid4()
        
        with patch('app.api.v1.jobs.get_logging_service') as mock_get_service:
            # Mock logging service to return None (job not found)
            mock_logging_service = Mock()
            mock_logging_service.update_job_status.return_value = None
            mock_get_service.return_value = mock_logging_service
            
            payload = {"status": "success"}
            headers = {"X-Callback-Token": test_settings.CALLBACK_SECRET_TOKEN}
            
            response = client.post(
                f"/api/v1/jobs/{job_id}/callback",
                json=payload,
                headers=headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            response_data = response.json()
            assert f"Job with ID {job_id} not found" in response_data["message"]
    
    def test_job_callback_database_error(self, client, test_settings):
        """Test job callback with database error."""
        job_id = uuid4()
        
        with patch('app.api.v1.jobs.get_logging_service') as mock_get_service:
            # Mock logging service to raise database error
            mock_logging_service = Mock()
            mock_logging_service.update_job_status.side_effect = Exception("Database connection failed")
            mock_get_service.return_value = mock_logging_service
            
            payload = {"status": "success"}
            headers = {"X-Callback-Token": test_settings.CALLBACK_SECRET_TOKEN}
            
            response = client.post(
                f"/api/v1/jobs/{job_id}/callback",
                json=payload,
                headers=headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            response_data = response.json()
            assert "Failed to update job status in database" in response_data["message"]
    
    def test_get_job_status_success(self, client, sample_job_log):
        """Test successful job status retrieval."""
        job_id = sample_job_log.job_id
        
        with patch('app.api.v1.jobs.get_logging_service') as mock_get_service:
            # Mock logging service
            mock_logging_service = Mock()
            mock_logging_service.get_job_log.return_value = sample_job_log
            mock_get_service.return_value = mock_logging_service
            
            response = client.get(f"/api/v1/jobs/{job_id}/status")
            
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["job_id"] == str(job_id)
            assert response_data["status"] == sample_job_log.status
            assert response_data["filename"] == sample_job_log.filename
            assert "created_at" in response_data
    
    def test_get_job_status_not_found(self, client):
        """Test job status retrieval for non-existent job."""
        job_id = uuid4()
        
        with patch('app.api.v1.jobs.get_logging_service') as mock_get_service:
            # Mock logging service to return None
            mock_logging_service = Mock()
            mock_logging_service.get_job_log.return_value = None
            mock_get_service.return_value = mock_logging_service
            
            response = client.get(f"/api/v1/jobs/{job_id}/status")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            response_data = response.json()
            assert f"Job with ID {job_id} not found" in response_data["message"]
    
    def test_get_job_status_database_error(self, client):
        """Test job status retrieval with database error."""
        job_id = uuid4()
        
        with patch('app.api.v1.jobs.get_logging_service') as mock_get_service:
            # Mock logging service to raise database error
            mock_logging_service = Mock()
            mock_logging_service.get_job_log.side_effect = Exception("Database query failed")
            mock_get_service.return_value = mock_logging_service
            
            response = client.get(f"/api/v1/jobs/{job_id}/status")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            response_data = response.json()
            assert "Failed to query job status" in response_data["message"]


class TestFileValidation:
    """Test file validation functions."""
    
    def test_validate_image_format_jpeg_magic_bytes(self, sample_image_bytes):
        """Test JPEG validation using magic bytes."""
        from app.api.v1.receipts import validate_image_format
        
        result = validate_image_format(
            sample_image_bytes, 
            "image/jpeg", 
            "test.jpg"
        )
        
        assert result == "image/jpeg"
    
    def test_validate_image_format_png_magic_bytes(self, sample_png_bytes):
        """Test PNG validation using magic bytes."""
        from app.api.v1.receipts import validate_image_format
        
        result = validate_image_format(
            sample_png_bytes, 
            "image/png", 
            "test.png"
        )
        
        assert result == "image/png"
    
    def test_validate_image_format_invalid_magic_bytes(self, invalid_file_bytes):
        """Test validation with invalid magic bytes."""
        from app.api.v1.receipts import validate_image_format
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_image_format(
                invalid_file_bytes, 
                "text/plain", 
                "test.txt"
            )
        
        assert "File format could not be validated" in str(exc_info.value)
        assert exc_info.value.filename == "test.txt"
    
    def test_validate_file_size_valid(self):
        """Test file size validation with valid size."""
        from app.api.v1.receipts import validate_file_size
        
        # Should not raise exception
        validate_file_size(1024000, "test.jpg")  # 1MB
    
    def test_validate_file_size_too_large(self):
        """Test file size validation with oversized file."""
        from app.api.v1.receipts import validate_file_size
        
        large_size = 15 * 1024 * 1024  # 15MB
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_size(large_size, "large.jpg")
        
        assert "exceeds maximum allowed size" in str(exc_info.value)
        assert exc_info.value.filename == "large.jpg"
        assert exc_info.value.file_size == large_size
    
    def test_validate_notion_database_id_valid(self):
        """Test valid notion database ID validation."""
        from app.api.v1.receipts import validate_notion_database_id
        
        valid_id = "12345678901234567890123456789012"
        result = validate_notion_database_id(valid_id)
        
        assert result == valid_id
    
    def test_validate_notion_database_id_with_dashes(self):
        """Test notion database ID validation with dashes."""
        from app.api.v1.receipts import validate_notion_database_id
        
        id_with_dashes = "12345678-9012-3456-7890-123456789012"
        result = validate_notion_database_id(id_with_dashes)
        
        assert result == id_with_dashes
    
    def test_validate_notion_database_id_empty(self):
        """Test notion database ID validation with empty string."""
        from app.api.v1.receipts import validate_notion_database_id
        
        with pytest.raises(ValidationError) as exc_info:
            validate_notion_database_id("")
        
        assert "notion_database_id cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "notion_database_id"
    
    def test_validate_notion_database_id_invalid_format(self):
        """Test notion database ID validation with invalid format."""
        from app.api.v1.receipts import validate_notion_database_id
        
        with pytest.raises(ValidationError) as exc_info:
            validate_notion_database_id("invalid-id")
        
        assert "must be a valid 32-character hexadecimal string" in str(exc_info.value)
        assert exc_info.value.field == "notion_database_id"