"""Unit tests for service layer classes."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4, UUID
from datetime import datetime
from io import BytesIO

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.services.task_service import TaskService
from app.services.logging_service import LoggingService
from app.domain.schemas import JobCreationResponse
from app.infrastructure.database import JobLog
from app.core.exceptions import (
    FileValidationError,
    DatabaseError,
    QueueError,
    JobError
)


# Patch the loggers to avoid conflicts with test execution
@pytest.fixture(autouse=True)
def mock_loggers():
    """Mock loggers to avoid conflicts during testing."""
    with patch('app.services.task_service.logger') as mock_logger, \
         patch('app.services.task_service.perf_logger') as mock_perf_logger:
        yield mock_logger, mock_perf_logger


class TestTaskService:
    """Test TaskService business logic and orchestration."""
    
    @pytest.fixture
    def mock_queue_service(self):
        """Create mock queue service."""
        mock = Mock()
        mock.enqueue_job = Mock()
        return mock
    
    @pytest.fixture
    def mock_logging_service(self):
        """Create mock logging service."""
        mock = Mock()
        mock.create_job_log = Mock()
        mock.get_job_log = Mock()
        return mock
    
    @pytest.fixture
    def task_service(self, mock_queue_service, mock_logging_service):
        """Create TaskService instance with mocked dependencies."""
        return TaskService(
            queue_service=mock_queue_service,
            logging_service=mock_logging_service
        )
    
    @pytest.fixture
    def sample_upload_file(self, sample_image_bytes):
        """Create a sample UploadFile for testing."""
        file_obj = BytesIO(sample_image_bytes)
        
        # Create a mock UploadFile with the necessary attributes
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test_receipt.jpg"
        mock_file.content_type = "image/jpeg"
        mock_file.file = file_obj
        mock_file.read = AsyncMock(return_value=sample_image_bytes)
        mock_file.seek = AsyncMock()
        
        return mock_file
    
    @pytest.mark.asyncio
    async def test_create_and_enqueue_job_success(
        self, 
        task_service, 
        sample_upload_file, 
        mock_queue_service, 
        mock_logging_service
    ):
        """Test successful job creation and enqueueing."""
        notion_db_id = "test-database-id"
        
        # Execute the method
        response = await task_service.create_and_enqueue_job(
            file=sample_upload_file,
            notion_database_id=notion_db_id
        )
        
        # Verify response
        assert isinstance(response, JobCreationResponse)
        assert isinstance(response.job_id, UUID)
        assert response.status == "queued"
        
        # Verify logging service was called
        mock_logging_service.create_job_log.assert_called_once()
        call_args = mock_logging_service.create_job_log.call_args
        assert call_args[1]["job_id"] == response.job_id
        assert call_args[1]["filename"] == "test_receipt.jpg"
        assert call_args[1]["notion_database_id"] == notion_db_id
        
        # Verify queue service was called
        mock_queue_service.enqueue_job.assert_called_once()
        queue_call_args = mock_queue_service.enqueue_job.call_args
        assert queue_call_args[1]["function_name"] == "trigger_n8n_workflow"
        assert queue_call_args[1]["job_id"] == response.job_id
        assert queue_call_args[1]["filename"] == "test_receipt.jpg"
        assert queue_call_args[1]["notion_database_id"] == notion_db_id
        assert "image_data" in queue_call_args[1]
    
    @pytest.mark.asyncio
    async def test_create_and_enqueue_job_with_custom_job_id(
        self, 
        task_service, 
        sample_upload_file, 
        mock_queue_service, 
        mock_logging_service
    ):
        """Test job creation with custom job ID."""
        custom_job_id = uuid4()
        notion_db_id = "test-database-id"
        
        response = await task_service.create_and_enqueue_job(
            file=sample_upload_file,
            notion_database_id=notion_db_id,
            job_id=custom_job_id
        )
        
        assert response.job_id == custom_job_id
        assert response.status == "queued"
        
        # Verify services were called with custom job ID
        mock_logging_service.create_job_log.assert_called_once()
        call_args = mock_logging_service.create_job_log.call_args
        assert call_args[1]["job_id"] == custom_job_id
    
    @pytest.mark.asyncio
    async def test_create_and_enqueue_job_empty_file(
        self, 
        task_service, 
        mock_queue_service, 
        mock_logging_service
    ):
        """Test job creation with empty file."""
        # Create mock empty file
        mock_empty_file = Mock(spec=UploadFile)
        mock_empty_file.filename = "empty.jpg"
        mock_empty_file.content_type = "image/jpeg"
        mock_empty_file.file = BytesIO(b"")
        mock_empty_file.read = AsyncMock(return_value=b"")
        mock_empty_file.seek = AsyncMock()
        empty_file = mock_empty_file
        
        with pytest.raises(FileValidationError) as exc_info:
            await task_service.create_and_enqueue_job(
                file=empty_file,
                notion_database_id="test-db-id"
            )
        
        assert "File is empty" in str(exc_info.value)
        assert exc_info.value.filename == "empty.jpg"
        
        # Verify services were not called
        mock_logging_service.create_job_log.assert_not_called()
        mock_queue_service.enqueue_job.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_and_enqueue_job_logging_failure(
        self, 
        task_service, 
        sample_upload_file, 
        mock_queue_service, 
        mock_logging_service
    ):
        """Test job creation when logging service fails."""
        mock_logging_service.create_job_log.side_effect = Exception("Database connection failed")
        
        with pytest.raises(DatabaseError) as exc_info:
            await task_service.create_and_enqueue_job(
                file=sample_upload_file,
                notion_database_id="test-db-id"
            )
        
        assert "Failed to create job log entry" in str(exc_info.value)
        assert exc_info.value.operation == "create_job_log"
        assert exc_info.value.table == "job_log"
        
        # Verify queue service was not called
        mock_queue_service.enqueue_job.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_and_enqueue_job_queue_failure(
        self, 
        task_service, 
        sample_upload_file, 
        mock_queue_service, 
        mock_logging_service
    ):
        """Test job creation when queue service fails."""
        mock_queue_service.enqueue_job.side_effect = Exception("Redis connection failed")
        
        with pytest.raises(QueueError) as exc_info:
            await task_service.create_and_enqueue_job(
                file=sample_upload_file,
                notion_database_id="test-db-id"
            )
        
        assert "Failed to enqueue job for processing" in str(exc_info.value)
        assert exc_info.value.operation == "enqueue_job"
        
        # Verify logging service was called (job log created before queue failure)
        mock_logging_service.create_job_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_read_file_contents_success(self, task_service, sample_upload_file):
        """Test successful file content reading."""
        contents = await task_service._read_file_contents(sample_upload_file)
        
        assert isinstance(contents, bytes)
        assert len(contents) > 0
        assert contents.startswith(b'\xff\xd8\xff')  # JPEG magic bytes
    
    @pytest.mark.asyncio
    async def test_read_file_contents_empty_file(self, task_service):
        """Test reading empty file contents."""
        # Create mock empty file
        mock_empty_file = Mock(spec=UploadFile)
        mock_empty_file.filename = "empty.jpg"
        mock_empty_file.content_type = "image/jpeg"
        mock_empty_file.file = BytesIO(b"")
        mock_empty_file.read = AsyncMock(return_value=b"")
        mock_empty_file.seek = AsyncMock()
        empty_file = mock_empty_file
        
        with pytest.raises(FileValidationError) as exc_info:
            await task_service._read_file_contents(empty_file)
        
        assert "File is empty" in str(exc_info.value)
        assert exc_info.value.filename == "empty.jpg"
        assert exc_info.value.file_size == 0
    
    def test_get_job_status_success(
        self, 
        task_service, 
        mock_logging_service, 
        sample_job_log
    ):
        """Test successful job status retrieval."""
        job_id = sample_job_log.job_id
        mock_logging_service.get_job_log.return_value = sample_job_log
        
        result = task_service.get_job_status(job_id)
        
        assert result is not None
        assert result["job_id"] == job_id
        assert result["status"] == "queued"
        assert result["filename"] == "test_receipt.jpg"
        assert "created_at" in result
        
        mock_logging_service.get_job_log.assert_called_once_with(job_id)
    
    def test_get_job_status_not_found(
        self, 
        task_service, 
        mock_logging_service
    ):
        """Test job status retrieval when job not found."""
        job_id = uuid4()
        mock_logging_service.get_job_log.return_value = None
        
        result = task_service.get_job_status(job_id)
        
        assert result is None
        mock_logging_service.get_job_log.assert_called_once_with(job_id)
    
    def test_get_job_status_database_error(
        self, 
        task_service, 
        mock_logging_service
    ):
        """Test job status retrieval with database error."""
        job_id = uuid4()
        mock_logging_service.get_job_log.side_effect = Exception("Database error")
        
        with pytest.raises(DatabaseError) as exc_info:
            task_service.get_job_status(job_id)
        
        assert "Failed to retrieve job status" in str(exc_info.value)
        assert exc_info.value.operation == "get_job_log"


class TestLoggingService:
    """Test LoggingService database operations."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        mock = Mock(spec=Session)
        mock.get = Mock()
        mock.add = Mock()
        mock.commit = Mock()
        mock.refresh = Mock()
        mock.rollback = Mock()
        mock.execute = Mock()
        return mock
    
    @pytest.fixture
    def logging_service(self, mock_session):
        """Create LoggingService instance with mocked session."""
        return LoggingService(db_session=mock_session)
    
    def test_create_job_log_success(self, logging_service, mock_session):
        """Test successful job log creation."""
        job_id = uuid4()
        filename = "test_receipt.jpg"
        notion_db_id = "test-database-id"
        
        # Mock session.get to return None (no existing job)
        mock_session.get.return_value = None
        
        result = logging_service.create_job_log(
            job_id=job_id,
            filename=filename,
            notion_database_id=notion_db_id
        )
        
        # Verify database operations
        mock_session.get.assert_called_once_with(JobLog, job_id)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
        # Verify the created job log
        assert isinstance(result, JobLog)
        assert result.job_id == job_id
        assert result.filename == filename
        assert result.notion_database_id == notion_db_id
        assert result.status == "queued"
        assert isinstance(result.created_at, datetime)
    
    def test_create_job_log_duplicate(self, logging_service, mock_session, sample_job_log):
        """Test job log creation with duplicate job ID."""
        job_id = sample_job_log.job_id
        
        # Mock session.get to return existing job
        mock_session.get.return_value = sample_job_log
        
        with pytest.raises(DatabaseError) as exc_info:
            logging_service.create_job_log(
                job_id=job_id,
                filename="new_file.jpg"
            )
        
        assert f"Job with ID {job_id} already exists" in str(exc_info.value)
        assert exc_info.value.operation == "create_job_log"
        assert exc_info.value.table == "job_log"
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()
        mock_session.add.assert_not_called()
    
    def test_create_job_log_database_error(self, logging_service, mock_session):
        """Test job log creation with database error."""
        job_id = uuid4()
        
        # Mock session.get to return None, but commit to raise exception
        mock_session.get.return_value = None
        mock_session.commit.side_effect = Exception("Database connection lost")
        
        with pytest.raises(DatabaseError) as exc_info:
            logging_service.create_job_log(job_id=job_id, filename="test.jpg")
        
        assert "Failed to create job log entry" in str(exc_info.value)
        mock_session.rollback.assert_called_once()
    
    def test_update_job_status_success(self, logging_service, mock_session, sample_job_log):
        """Test successful job status update."""
        job_id = sample_job_log.job_id
        new_status = "success"
        message = "Processing completed successfully"
        notion_url = "https://notion.so/page/abc123"
        
        # Mock session.get to return existing job
        mock_session.get.return_value = sample_job_log
        
        result = logging_service.update_job_status(
            job_id=job_id,
            status=new_status,
            result_message=message,
            notion_page_url=notion_url
        )
        
        # Verify database operations
        mock_session.get.assert_called_once_with(JobLog, job_id)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
        # Verify the updated job log
        assert result == sample_job_log
        assert sample_job_log.status == new_status
        assert sample_job_log.result_message == message
        assert sample_job_log.notion_page_url == notion_url
        assert isinstance(sample_job_log.completed_at, datetime)
    
    def test_update_job_status_not_found(self, logging_service, mock_session):
        """Test job status update when job not found."""
        job_id = uuid4()
        
        # Mock session.get to return None
        mock_session.get.return_value = None
        
        result = logging_service.update_job_status(
            job_id=job_id,
            status="success"
        )
        
        assert result is None
        mock_session.get.assert_called_once_with(JobLog, job_id)
        mock_session.commit.assert_not_called()
    
    def test_update_job_status_database_error(self, logging_service, mock_session, sample_job_log):
        """Test job status update with database error."""
        job_id = sample_job_log.job_id
        
        # Mock session.get to return job, but commit to raise exception
        mock_session.get.return_value = sample_job_log
        mock_session.commit.side_effect = Exception("Database error")
        
        with pytest.raises(DatabaseError) as exc_info:
            logging_service.update_job_status(job_id=job_id, status="success")
        
        assert "Failed to update job status" in str(exc_info.value)
        mock_session.rollback.assert_called_once()
    
    def test_get_job_log_success(self, logging_service, mock_session, sample_job_log):
        """Test successful job log retrieval."""
        job_id = sample_job_log.job_id
        mock_session.get.return_value = sample_job_log
        
        result = logging_service.get_job_log(job_id)
        
        assert result == sample_job_log
        mock_session.get.assert_called_once_with(JobLog, job_id)
    
    def test_get_job_log_not_found(self, logging_service, mock_session):
        """Test job log retrieval when not found."""
        job_id = uuid4()
        mock_session.get.return_value = None
        
        result = logging_service.get_job_log(job_id)
        
        assert result is None
        mock_session.get.assert_called_once_with(JobLog, job_id)
    
    def test_get_jobs_by_status(self, logging_service, mock_session):
        """Test retrieving jobs by status."""
        # Mock execute result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [Mock(), Mock()]
        mock_session.execute.return_value = mock_result
        
        jobs = logging_service.get_jobs_by_status("queued", limit=10)
        
        assert len(jobs) == 2
        mock_session.execute.assert_called_once()
    
    def test_get_recent_jobs(self, logging_service, mock_session):
        """Test retrieving recent jobs."""
        # Mock execute result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [Mock(), Mock(), Mock()]
        mock_session.execute.return_value = mock_result
        
        jobs = logging_service.get_recent_jobs(limit=3)
        
        assert len(jobs) == 3
        mock_session.execute.assert_called_once()