"""Test configuration and fixtures."""
import asyncio
import io
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from app.core.settings import Settings
from app.infrastructure.database import JobLog
from app.domain.protocols import LoggingServiceProtocol, QueueServiceProtocol
from app.infrastructure.database import get_database_session
from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with safe defaults."""
    return Settings(
        API_V1_STR="/api/v1",
        REDIS_URL="redis://localhost:6379",
        N8N_WEBHOOK_URL="https://test.n8n.webhook.url",
        N8N_API_KEY="test-api-key",
        CALLBACK_SECRET_TOKEN="test-secret-token",
        DATABASE_URL="sqlite:///:memory:",
        MAX_FILE_SIZE_MB=10,
        ALLOWED_IMAGE_TYPES=["image/jpeg", "image/png", "image/gif"],
    )


@pytest.fixture
def test_engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(test_session, test_settings) -> TestClient:
    """Create a test client with dependency overrides."""
    
    def get_test_session():
        return test_session
    
    def get_test_settings():
        return test_settings
    
    app.dependency_overrides[get_database_session] = get_test_session
    # Note: Settings is a global instance, not a dependency in this app
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_queue_service() -> Mock:
    """Create a mock queue service."""
    mock = Mock(spec=QueueServiceProtocol)
    mock.enqueue_job = Mock()
    return mock


@pytest.fixture
def mock_logging_service() -> Mock:
    """Create a mock logging service."""
    mock = Mock(spec=LoggingServiceProtocol)
    mock.create_job_log = AsyncMock()
    mock.update_job_status = AsyncMock()
    mock.get_job_log = AsyncMock()
    return mock


@pytest.fixture
def sample_job_id() -> UUID:
    """Generate a sample job ID for testing."""
    return uuid4()


@pytest.fixture
def sample_job_log(sample_job_id) -> JobLog:
    """Create a sample job log for testing."""
    return JobLog(
        job_id=sample_job_id,
        status="queued",
        filename="test_receipt.jpg",
    )


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Create sample image bytes for testing."""
    # Create a minimal JPEG header for testing
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
    jpeg_data = jpeg_header + b'\x00' * 100  # Minimal JPEG data
    jpeg_footer = b'\xff\xd9'
    return jpeg_header + jpeg_data + jpeg_footer


@pytest.fixture
def sample_png_bytes() -> bytes:
    """Create sample PNG bytes for testing."""
    # PNG signature and minimal IHDR chunk
    png_signature = b'\x89PNG\r\n\x1a\n'
    ihdr_chunk = b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
    iend_chunk = b'\x00\x00\x00\x00IEND\xaeB`\x82'
    return png_signature + ihdr_chunk + iend_chunk


@pytest.fixture
def sample_image_file(sample_image_bytes):
    """Create a sample image file-like object."""
    return io.BytesIO(sample_image_bytes)


@pytest.fixture
def large_image_bytes() -> bytes:
    """Create large image bytes for testing file size limits."""
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
    # Create 15MB of data (exceeds 10MB limit)
    large_data = b'\x00' * (15 * 1024 * 1024)
    jpeg_footer = b'\xff\xd9'
    return jpeg_header + large_data + jpeg_footer


@pytest.fixture
def invalid_file_bytes() -> bytes:
    """Create invalid file bytes for testing."""
    return b'This is not an image file'


@pytest.fixture
def mock_n8n_response():
    """Mock N8N webhook response."""
    return {
        "status": "success",
        "message": "Workflow executed successfully",
        "execution_id": "test-execution-id"
    }