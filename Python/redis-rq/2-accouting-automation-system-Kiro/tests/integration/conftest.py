"""Integration test configuration and fixtures."""
import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
import redis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel
from fakeredis import FakeRedis
from rq import Queue

from app.core.settings import Settings
from app.infrastructure.database import JobLog, DatabaseManager, get_database_session
from app.infrastructure.queue import RQService
from app.services.logging_service import LoggingService
from app.services.task_service import TaskService
from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def integration_settings() -> Settings:
    """Create integration test settings."""
    return Settings(
        API_V1_STR="/api/v1",
        REDIS_URL="redis://localhost:6379/15",  # Use test database
        N8N_WEBHOOK_URL="https://test.n8n.webhook.url",
        N8N_API_KEY="test-api-key",
        CALLBACK_SECRET_TOKEN="test-secret-token",
        DATABASE_URL="sqlite:///:memory:",
        MAX_FILE_SIZE_MB=10,
        ALLOWED_IMAGE_TYPES=["image/jpeg", "image/png", "image/gif"],
        QUEUE_DEFAULT_TIMEOUT=300,
        PROJECT_NAME="Test Accounting Backend",
        LOG_LEVEL="INFO",
        ENABLE_JSON_LOGGING=False,
        VERIFY_SSL=False
    )


@pytest.fixture
def integration_engine():
    """Create in-memory SQLite engine for integration testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def integration_session(integration_engine) -> Generator[Session, None, None]:
    """Create a test database session for integration tests."""
    with Session(integration_engine) as session:
        yield session


@pytest.fixture
def fake_redis():
    """Create a fake Redis instance for testing."""
    return FakeRedis(decode_responses=True)


@pytest.fixture
def integration_queue_service(fake_redis):
    """Create RQService with fake Redis for integration testing."""
    with patch('app.infrastructure.queue.redis.from_url', return_value=fake_redis):
        service = RQService(redis_url="redis://fake:6379", queue_name="test")
        yield service
        service.close()


@pytest.fixture
def integration_logging_service(integration_session):
    """Create LoggingService for integration testing."""
    return LoggingService(session=integration_session)


@pytest.fixture
def integration_task_service(integration_queue_service, integration_logging_service):
    """Create TaskService with real dependencies for integration testing."""
    return TaskService(
        queue_service=integration_queue_service,
        logging_service=integration_logging_service
    )


@pytest.fixture
def integration_client(integration_session, fake_redis):
    """Create a TestClient wired to in-memory DB and fake Redis, with test settings."""

    # Use the shared in-memory DB session for all app DB access
    def get_test_session():
        return integration_session

    app.dependency_overrides[get_database_session] = get_test_session

    # Patch the existing singleton settings object attributes so other modules see changes
    from app.core.settings import settings as global_settings

    settings_patches = [
        patch.object(global_settings, 'API_V1_STR', '/api/v1'),
        patch.object(global_settings, 'REDIS_URL', 'redis://localhost:6379/15'),
        patch.object(global_settings, 'N8N_WEBHOOK_URL', 'https://test.n8n.webhook.url'),
        patch.object(global_settings, 'N8N_API_KEY', 'test-api-key'),
        patch.object(global_settings, 'CALLBACK_SECRET_TOKEN', 'test-secret-token'),
        patch.object(global_settings, 'VERIFY_SSL', False),
        # Keep default 10MB limit unless overridden
    ]

    # Stub Redis for RQ so we don’t require a real Redis server
    redis_patch = patch('app.infrastructure.queue.redis.from_url', return_value=fake_redis)

    with redis_patch:
        with settings_patches[0], settings_patches[1], settings_patches[2], settings_patches[3], settings_patches[4], settings_patches[5]:
            with TestClient(app) as test_client:
                yield test_client

    # Cleanup overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_n8n_server():
    """Mock N8N webhook server responses."""
    responses = []
    
    def add_response(status_code=200, json_data=None):
        if json_data is None:
            json_data = {"status": "success", "message": "Workflow triggered"}
        responses.append({"status_code": status_code, "json": json_data})
    
    def get_responses():
        return responses.copy()
    
    def clear_responses():
        responses.clear()
    
    mock_server = Mock()
    mock_server.add_response = add_response
    mock_server.get_responses = get_responses
    mock_server.clear_responses = clear_responses
    
    return mock_server


@pytest.fixture
def sample_receipt_image():
    """Create a sample receipt image file for testing."""
    # Create a minimal JPEG for testing
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
    jpeg_data = b'\x00' * 500  # Some image data
    jpeg_footer = b'\xff\xd9'
    
    return {
        "filename": "test_receipt.jpg",
        "content": jpeg_header + jpeg_data + jpeg_footer,
        "content_type": "image/jpeg"
    }


@pytest.fixture
def temp_database():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    yield f"sqlite:///{db_path}"
    
    # Cleanup
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def real_redis_available():
    """Check if real Redis is available for testing."""
    try:
        r = redis.Redis(host='localhost', port=6379, db=15)
        r.ping()
        return True
    except (redis.ConnectionError, redis.TimeoutError):
        return False


@pytest.fixture
def integration_database_manager(temp_database):
    """Create DatabaseManager with temporary database."""
    manager = DatabaseManager(database_url=temp_database)
    manager.initialize()
    yield manager