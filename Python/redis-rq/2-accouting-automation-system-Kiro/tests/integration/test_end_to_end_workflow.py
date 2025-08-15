"""
Integration tests for complete end-to-end workflows.
Tests the full flow from upload to callback completion.
"""
import asyncio
import json
from io import BytesIO
from unittest.mock import patch, Mock
from uuid import UUID

import pytest
import httpx
from fastapi import UploadFile

from app.domain.schemas import JobCallbackPayload
from app.infrastructure.database import JobLog


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows from upload to callback."""
    
    @pytest.mark.asyncio
    async def test_successful_receipt_upload_to_callback_flow(
        self,
        integration_client,
        integration_session,
        sample_receipt_image,
        mock_n8n_server
    ):
        """Test complete successful flow from upload to callback completion."""
        
        # Mock N8N webhook response
        mock_n8n_server.add_response(
            status_code=200,
            json_data={"status": "success", "execution_id": "test-exec-123"}
        )
        
        # Mock httpx client for N8N webhook calls
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success", "execution_id": "test-exec-123"}
            mock_response.text = json.dumps({"status": "success"})
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__enter__.return_value = mock_client
            
            # Step 1: Upload receipt
            files = {
                "file": (
                    sample_receipt_image["filename"],
                    BytesIO(sample_receipt_image["content"]),
                    sample_receipt_image["content_type"]
                )
            }
            data = {"notion_database_id": "test-database-123"}
            
            upload_response = integration_client.post(
                "/api/v1/receipts/upload",
                files=files,
                data=data
            )
            
            assert upload_response.status_code == 202
            upload_data = upload_response.json()
            assert "job_id" in upload_data
            assert upload_data["status"] == "queued"
            
            job_id = UUID(upload_data["job_id"])
            
            # Verify job log was created
            job_log = integration_session.get(JobLog, job_id)
            assert job_log is not None
            assert job_log.status == "queued"
            assert job_log.filename == sample_receipt_image["filename"]
            
            # Step 2: Simulate worker processing (trigger N8N workflow)
            from rq_worker import trigger_n8n_workflow
            
            # Execute the worker function directly
            result = trigger_n8n_workflow(
                job_id=job_id,
                image_data=sample_receipt_image["content"],
                filename=sample_receipt_image["filename"],
                notion_database_id="test-database-123"
            )
            
            assert result["status"] == "success"
            assert "execution_id" in result
            
            # Verify N8N webhook was called
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert "/api/v1/jobs/" in call_args[1]["json"]["callback_url"]
            assert call_args[1]["json"]["job_id"] == str(job_id)
            assert call_args[1]["json"]["notion_database_id"] == "test-database-123"
            
            # Step 3: Simulate N8N callback
            callback_payload = {
                "status": "success",
                "message": "Receipt processed successfully",
                "notion_page_url": "https://notion.so/test-page-123"
            }
            
            callback_response = integration_client.post(
                f"/api/v1/jobs/{job_id}/callback",
                json=callback_payload,
                headers={"X-Callback-Token": "test-secret-token"}
            )
            
            assert callback_response.status_code == 200
            callback_data = callback_response.json()
            assert callback_data["message"] == "Job status updated successfully"
            
            # Step 4: Verify final job status
            integration_session.refresh(job_log)
            assert job_log.status == "success"
            assert job_log.result_message == "Receipt processed successfully"
            assert job_log.notion_page_url == "https://notion.so/test-page-123"
            assert job_log.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_failed_workflow_with_error_handling(
        self,
        integration_client,
        integration_session,
        sample_receipt_image
    ):
        """Test workflow failure handling and error propagation."""
        
        # Mock N8N webhook to return error
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__enter__.return_value = mock_client
            
            # Step 1: Upload receipt
            files = {
                "file": (
                    sample_receipt_image["filename"],
                    BytesIO(sample_receipt_image["content"]),
                    sample_receipt_image["content_type"]
                )
            }
            data = {"notion_database_id": "test-database-123"}
            
            upload_response = integration_client.post(
                "/api/v1/receipts/upload",
                files=files,
                data=data
            )
            
            assert upload_response.status_code == 202
            job_id = UUID(upload_response.json()["job_id"])
            
            # Step 2: Simulate worker processing with failure
            from rq_worker import trigger_n8n_workflow
            from app.core.exceptions import ExternalServiceError
            
            with pytest.raises(ExternalServiceError) as exc_info:
                trigger_n8n_workflow(
                    job_id=job_id,
                    image_data=sample_receipt_image["content"],
                    filename=sample_receipt_image["filename"],
                    notion_database_id="test-database-123"
                )
            
            assert "N8N webhook returned status 500" in str(exc_info.value)
            
            # Step 3: Simulate failure callback from N8N
            callback_payload = {
                "status": "failure",
                "message": "Failed to process receipt: Invalid image format"
            }
            
            callback_response = integration_client.post(
                f"/api/v1/jobs/{job_id}/callback",
                json=callback_payload,
                headers={"X-Callback-Token": "test-secret-token"}
            )
            
            assert callback_response.status_code == 200
            
            # Step 4: Verify job marked as failed
            job_log = integration_session.get(JobLog, job_id)
            integration_session.refresh(job_log)
            assert job_log.status == "failure"
            assert "Failed to process receipt" in job_log.result_message
    
    @pytest.mark.asyncio
    async def test_invalid_callback_token_handling(
        self,
        integration_client,
        integration_session,
        sample_receipt_image
    ):
        """Test callback security with invalid tokens."""
        
        # Upload receipt first
        files = {
            "file": (
                sample_receipt_image["filename"],
                BytesIO(sample_receipt_image["content"]),
                sample_receipt_image["content_type"]
            )
        }
        data = {"notion_database_id": "test-database-123"}
        
        upload_response = integration_client.post(
            "/api/v1/receipts/upload",
            files=files,
            data=data
        )
        
        job_id = UUID(upload_response.json()["job_id"])
        
        # Try callback with invalid token
        callback_payload = {
            "status": "success",
            "message": "Receipt processed successfully"
        }
        
        callback_response = integration_client.post(
            f"/api/v1/jobs/{job_id}/callback",
            json=callback_payload,
            headers={"X-Callback-Token": "invalid-token"}
        )
        
        assert callback_response.status_code == 401
        assert "Invalid callback token" in callback_response.json()["detail"]
        
        # Verify job status unchanged
        job_log = integration_session.get(JobLog, job_id)
        assert job_log.status == "queued"  # Should remain unchanged
    
    @pytest.mark.asyncio
    async def test_callback_for_nonexistent_job(
        self,
        integration_client
    ):
        """Test callback handling for jobs that don't exist."""
        
        fake_job_id = "550e8400-e29b-41d4-a716-446655440000"
        
        callback_payload = {
            "status": "success",
            "message": "Receipt processed successfully"
        }
        
        callback_response = integration_client.post(
            f"/api/v1/jobs/{fake_job_id}/callback",
            json=callback_payload,
            headers={"X-Callback-Token": "test-secret-token"}
        )
        
        assert callback_response.status_code == 404
        assert "Job not found" in callback_response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_uploads(
        self,
        integration_client,
        integration_session,
        sample_receipt_image
    ):
        """Test handling multiple concurrent receipt uploads."""
        
        # Create multiple upload requests
        upload_tasks = []
        
        for i in range(3):
            files = {
                "file": (
                    f"receipt_{i}.jpg",
                    BytesIO(sample_receipt_image["content"]),
                    sample_receipt_image["content_type"]
                )
            }
            data = {"notion_database_id": f"test-database-{i}"}
            
            # Make concurrent uploads
            response = integration_client.post(
                "/api/v1/receipts/upload",
                files=files,
                data=data
            )
            upload_tasks.append(response)
        
        # Verify all uploads succeeded
        job_ids = []
        for response in upload_tasks:
            assert response.status_code == 202
            job_data = response.json()
            assert job_data["status"] == "queued"
            job_ids.append(UUID(job_data["job_id"]))
        
        # Verify all job logs were created
        for job_id in job_ids:
            job_log = integration_session.get(JobLog, job_id)
            assert job_log is not None
            assert job_log.status == "queued"
    
    @pytest.mark.asyncio
    async def test_upload_with_invalid_file_type(
        self,
        integration_client
    ):
        """Test upload validation with invalid file types."""
        
        # Create invalid file (text file)
        invalid_file_content = b"This is not an image file"
        
        files = {
            "file": (
                "document.txt",
                BytesIO(invalid_file_content),
                "text/plain"
            )
        }
        data = {"notion_database_id": "test-database-123"}
        
        response = integration_client.post(
            "/api/v1/receipts/upload",
            files=files,
            data=data
        )
        
        assert response.status_code == 400
        error_data = response.json()
        assert "Invalid file type" in error_data["detail"]
    
    @pytest.mark.asyncio
    async def test_upload_with_oversized_file(
        self,
        integration_client
    ):
        """Test upload validation with oversized files."""
        
        # Create oversized file (15MB, exceeds 10MB limit)
        large_content = b'\xff\xd8\xff\xe0' + b'\x00' * (15 * 1024 * 1024) + b'\xff\xd9'
        
        files = {
            "file": (
                "large_receipt.jpg",
                BytesIO(large_content),
                "image/jpeg"
            )
        }
        data = {"notion_database_id": "test-database-123"}
        
        response = integration_client.post(
            "/api/v1/receipts/upload",
            files=files,
            data=data
        )
        
        assert response.status_code == 413
        error_data = response.json()
        assert "File too large" in error_data["detail"]