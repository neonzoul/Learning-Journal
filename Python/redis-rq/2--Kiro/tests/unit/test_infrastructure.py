"""Unit tests for infrastructure layer components."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime

import redis
from rq import Queue
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from app.infrastructure.queue import RQService
from app.infrastructure.database import JobLog, DatabaseManager, get_database_session, init_database
from app.core.exceptions import QueueError


class TestRQService:
    """Test Redis Queue service implementation."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis connection."""
        mock = Mock(spec=redis.Redis)
        mock.ping.return_value = True
        return mock
    
    @pytest.fixture
    def mock_queue(self):
        """Create mock RQ Queue."""
        mock = Mock(spec=Queue)
        mock.enqueue.return_value = Mock(id="test-job-id")
        return mock
    
    @pytest.fixture
    def rq_service(self, mock_redis, mock_queue):
        """Create RQService instance with mocked dependencies."""
        with patch('app.infrastructure.queue.redis.from_url', return_value=mock_redis):
            with patch('app.infrastructure.queue.Queue', return_value=mock_queue):
                service = RQService(redis_url="redis://localhost:6379")
                service.redis_client = mock_redis
                service.queue = mock_queue
                return service
    
    def test_rq_service_initialization(self):
        """Test RQService initialization."""
        with patch('app.infrastructure.queue.redis.from_url') as mock_redis_from_url:
            with patch('app.infrastructure.queue.Queue') as mock_queue_class:
                mock_redis = Mock()
                mock_redis.ping.return_value = True
                mock_redis_from_url.return_value = mock_redis
                
                mock_queue = Mock()
                mock_queue_class.return_value = mock_queue
                
                service = RQService(redis_url="redis://test:6379")
                
                # Verify Redis connection was created
                mock_redis_from_url.assert_called_once_with("redis://test:6379")
                mock_redis.ping.assert_called_once()
                
                # Verify Queue was created
                mock_queue_class.assert_called_once_with(connection=mock_redis)
                
                assert service.redis_client == mock_redis
                assert service.queue == mock_queue
    
    def test_rq_service_initialization_connection_failure(self):
        """Test RQService initialization with Redis connection failure."""
        with patch('app.infrastructure.queue.redis.from_url') as mock_redis_from_url:
            mock_redis = Mock()
            mock_redis.ping.side_effect = redis.ConnectionError("Connection failed")
            mock_redis_from_url.return_value = mock_redis
            
            with pytest.raises(QueueError) as exc_info:
                RQService(redis_url="redis://localhost:6379")
            
            assert "Failed to connect to Redis" in str(exc_info.value)
            assert exc_info.value.operation == "redis_connection"
    
    def test_enqueue_job_success(self, rq_service, mock_queue):
        """Test successful job enqueueing."""
        job_id = uuid4()
        
        rq_service.enqueue_job(
            function_name="test_function",
            job_id=job_id,
            param1="value1",
            param2="value2"
        )
        
        # Verify queue.enqueue was called with correct parameters
        mock_queue.enqueue.assert_called_once_with(
            "test_function",
            job_id=job_id,
            param1="value1",
            param2="value2",
            timeout="10m"
        )
    
    def test_enqueue_job_with_custom_timeout(self, rq_service, mock_queue):
        """Test job enqueueing with custom timeout."""
        job_id = uuid4()
        
        rq_service.enqueue_job(
            function_name="long_running_function",
            job_id=job_id,
            timeout="30m",
            data="test_data"
        )
        
        mock_queue.enqueue.assert_called_once_with(
            "long_running_function",
            job_id=job_id,
            timeout="30m",
            data="test_data"
        )
    
    def test_enqueue_job_failure(self, rq_service, mock_queue):
        """Test job enqueueing failure."""
        job_id = uuid4()
        mock_queue.enqueue.side_effect = Exception("Queue is full")
        
        with pytest.raises(QueueError) as exc_info:
            rq_service.enqueue_job(
                function_name="test_function",
                job_id=job_id
            )
        
        assert "Failed to enqueue job" in str(exc_info.value)
        assert exc_info.value.operation == "enqueue_job"
        assert str(job_id) in str(exc_info.value.details)
    
    def test_health_check_success(self, rq_service, mock_redis):
        """Test successful health check."""
        mock_redis.ping.return_value = True
        
        result = rq_service.health_check()
        
        assert result is True
        mock_redis.ping.assert_called_once()
    
    def test_health_check_failure(self, rq_service, mock_redis):
        """Test health check failure."""
        mock_redis.ping.side_effect = redis.ConnectionError("Connection lost")
        
        result = rq_service.health_check()
        
        assert result is False
        mock_redis.ping.assert_called_once()


class TestJobLogModel:
    """Test JobLog SQLModel database model."""
    
    def test_job_log_creation(self):
        """Test JobLog model creation with required fields."""
        job_id = uuid4()
        created_at = datetime.utcnow()
        
        job_log = JobLog(
            job_id=job_id,
            status="queued",
            filename="test_receipt.jpg",
            notion_database_id="test-db-id",
            created_at=created_at
        )
        
        assert job_log.job_id == job_id
        assert job_log.status == "queued"
        assert job_log.filename == "test_receipt.jpg"
        assert job_log.notion_database_id == "test-db-id"
        assert job_log.created_at == created_at
        assert job_log.completed_at is None
        assert job_log.result_message is None
        assert job_log.notion_page_url is None
    
    def test_job_log_default_values(self):
        """Test JobLog model with default values."""
        job_id = uuid4()
        
        job_log = JobLog(job_id=job_id)
        
        assert job_log.job_id == job_id
        assert job_log.status == "queued"  # Default status
        assert job_log.filename is None
        assert job_log.notion_database_id is None
        assert isinstance(job_log.created_at, datetime)  # Default factory
        assert job_log.completed_at is None
        assert job_log.result_message is None
        assert job_log.notion_page_url is None
    
    def test_job_log_completed_job(self):
        """Test JobLog model for completed job."""
        job_id = uuid4()
        created_at = datetime.utcnow()
        completed_at = datetime.utcnow()
        
        job_log = JobLog(
            job_id=job_id,
            status="success",
            filename="receipt.png",
            notion_database_id="db-123",
            created_at=created_at,
            completed_at=completed_at,
            result_message="Processing completed successfully",
            notion_page_url="https://notion.so/page/abc123"
        )
        
        assert job_log.status == "success"
        assert job_log.completed_at == completed_at
        assert job_log.result_message == "Processing completed successfully"
        assert job_log.notion_page_url == "https://notion.so/page/abc123"
    
    def test_job_log_table_configuration(self):
        """Test JobLog table configuration."""
        # Verify it's configured as a table
        assert JobLog.__table__ is not None
        assert JobLog.__tablename__ == "joblog"
        
        # Verify primary key
        primary_keys = [col.name for col in JobLog.__table__.primary_key.columns]
        assert primary_keys == ["job_id"]
        
        # Verify indexed columns
        indexed_columns = [col.name for col in JobLog.__table__.columns if col.index]
        assert "status" in indexed_columns


class TestDatabaseManager:
    """Test DatabaseManager class."""
    
    def test_database_manager_initialization(self):
        """Test DatabaseManager initialization."""
        db_manager = DatabaseManager(database_url="sqlite:///test.db")
        
        assert db_manager.database_url == "sqlite:///test.db"
        assert db_manager.engine is None
        assert db_manager.SessionLocal is None
    
    def test_database_manager_initialize_sqlite(self):
        """Test DatabaseManager initialization with SQLite."""
        db_manager = DatabaseManager(database_url="sqlite:///:memory:")
        
        with patch.object(db_manager, 'create_tables') as mock_create_tables:
            db_manager.initialize()
            
            # Verify engine was created
            assert db_manager.engine is not None
            assert db_manager.SessionLocal is not None
            
            # Verify create_tables was called
            mock_create_tables.assert_called_once()
    
    def test_database_manager_initialize_postgresql(self):
        """Test DatabaseManager initialization with PostgreSQL."""
        db_manager = DatabaseManager(database_url="postgresql://user:pass@localhost/db")
        
        with patch('app.infrastructure.database.create_engine') as mock_create_engine:
            with patch.object(db_manager, 'create_tables') as mock_create_tables:
                mock_engine = Mock()
                mock_create_engine.return_value = mock_engine
                
                db_manager.initialize()
                
                # Verify engine creation with no SQLite-specific args
                mock_create_engine.assert_called_once_with(
                    "postgresql://user:pass@localhost/db",
                    connect_args={},
                    echo=False
                )
                
                assert db_manager.engine == mock_engine
                mock_create_tables.assert_called_once()
    
    def test_create_tables(self):
        """Test table creation."""
        db_manager = DatabaseManager(database_url="sqlite:///:memory:")
        
        with patch('app.infrastructure.database.SQLModel.metadata.create_all') as mock_create_all:
            mock_engine = Mock()
            db_manager.engine = mock_engine
            
            db_manager.create_tables()
            
            mock_create_all.assert_called_once_with(bind=mock_engine)
    
    def test_create_tables_without_engine(self):
        """Test table creation without initialized engine."""
        db_manager = DatabaseManager()
        
        with pytest.raises(RuntimeError) as exc_info:
            db_manager.create_tables()
        
        assert "Database engine not initialized" in str(exc_info.value)
    
    def test_get_session(self):
        """Test database session creation."""
        db_manager = DatabaseManager(database_url="sqlite:///:memory:")
        db_manager.initialize()
        
        # Test session context manager
        sessions = []
        for session in db_manager.get_session():
            sessions.append(session)
            assert isinstance(session, Session)
            break
        
        assert len(sessions) == 1
    
    def test_get_session_without_initialization(self):
        """Test session creation without initialization."""
        db_manager = DatabaseManager()
        
        with pytest.raises(RuntimeError) as exc_info:
            next(db_manager.get_session())
        
        assert "Database not initialized" in str(exc_info.value)
    
    def test_health_check_success(self):
        """Test successful database health check."""
        db_manager = DatabaseManager(database_url="sqlite:///:memory:")
        db_manager.initialize()
        
        result = db_manager.health_check()
        
        assert result is True
    
    def test_health_check_failure(self):
        """Test database health check failure."""
        db_manager = DatabaseManager()
        
        # Without initialization, health check should fail
        result = db_manager.health_check()
        
        assert result is False


class TestDatabaseFunctions:
    """Test database utility functions."""
    
    def test_get_database_session(self):
        """Test get_database_session dependency function."""
        with patch('app.infrastructure.database.db_manager') as mock_db_manager:
            mock_session = Mock()
            mock_db_manager.get_session.return_value = iter([mock_session])
            
            # Test the generator function
            sessions = list(get_database_session())
            
            assert len(sessions) == 1
            assert sessions[0] == mock_session
            mock_db_manager.get_session.assert_called_once()
    
    def test_init_database(self):
        """Test init_database function."""
        with patch('app.infrastructure.database.db_manager') as mock_db_manager:
            init_database()
            
            mock_db_manager.initialize.assert_called_once()


class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    @pytest.fixture
    def in_memory_db(self):
        """Create in-memory database for testing."""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)
        return engine
    
    def test_job_log_crud_operations(self, in_memory_db):
        """Test CRUD operations on JobLog model."""
        job_id = uuid4()
        
        with Session(in_memory_db) as session:
            # Create
            job_log = JobLog(
                job_id=job_id,
                status="queued",
                filename="test.jpg",
                notion_database_id="db-123"
            )
            session.add(job_log)
            session.commit()
            session.refresh(job_log)
            
            # Read
            retrieved_job = session.get(JobLog, job_id)
            assert retrieved_job is not None
            assert retrieved_job.job_id == job_id
            assert retrieved_job.status == "queued"
            assert retrieved_job.filename == "test.jpg"
            
            # Update
            retrieved_job.status = "success"
            retrieved_job.completed_at = datetime.utcnow()
            retrieved_job.result_message = "Completed successfully"
            session.commit()
            
            # Verify update
            updated_job = session.get(JobLog, job_id)
            assert updated_job.status == "success"
            assert updated_job.completed_at is not None
            assert updated_job.result_message == "Completed successfully"
            
            # Delete
            session.delete(updated_job)
            session.commit()
            
            # Verify deletion
            deleted_job = session.get(JobLog, job_id)
            assert deleted_job is None
    
    def test_job_log_constraints(self, in_memory_db):
        """Test JobLog model constraints."""
        job_id = uuid4()
        
        with Session(in_memory_db) as session:
            # Create first job
            job_log1 = JobLog(job_id=job_id, status="queued")
            session.add(job_log1)
            session.commit()
            
            # Try to create duplicate job (should fail due to primary key constraint)
            job_log2 = JobLog(job_id=job_id, status="processing")
            session.add(job_log2)
            
            with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
                session.commit()
            
            session.rollback()
    
    def test_job_log_query_by_status(self, in_memory_db):
        """Test querying JobLog by status."""
        from sqlmodel import select
        
        with Session(in_memory_db) as session:
            # Create multiple jobs with different statuses
            jobs = [
                JobLog(job_id=uuid4(), status="queued", filename="job1.jpg"),
                JobLog(job_id=uuid4(), status="processing", filename="job2.jpg"),
                JobLog(job_id=uuid4(), status="queued", filename="job3.jpg"),
                JobLog(job_id=uuid4(), status="success", filename="job4.jpg"),
            ]
            
            for job in jobs:
                session.add(job)
            session.commit()
            
            # Query jobs by status
            queued_jobs = session.exec(
                select(JobLog).where(JobLog.status == "queued")
            ).all()
            
            assert len(queued_jobs) == 2
            assert all(job.status == "queued" for job in queued_jobs)
            
            # Query jobs by different status
            processing_jobs = session.exec(
                select(JobLog).where(JobLog.status == "processing")
            ).all()
            
            assert len(processing_jobs) == 1
            assert processing_jobs[0].status == "processing"