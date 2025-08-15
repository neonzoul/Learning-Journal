"""
Database infrastructure with SQLModel for audit logging.
Provides database connection utilities, session management, and table creation.
"""

from datetime import datetime
from typing import Optional, Generator
from uuid import UUID

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlmodel import SQLModel, Field, select

from app.core.settings import settings


class JobLog(SQLModel, table=True):
    """
    SQLModel for job audit logging.
    Tracks job status, timing, and results throughout the processing lifecycle.
    """
    
    job_id: UUID = Field(primary_key=True, description="Unique job identifier")
    status: str = Field(
        index=True, 
        default="queued",
        description="Current job status (queued, processing, success, failure)"
    )
    filename: Optional[str] = Field(
        default=None,
        description="Original filename of uploaded image"
    )
    notion_database_id: Optional[str] = Field(
        default=None,
        description="Target Notion database ID for the job"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when job was created"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when job was completed"
    )
    result_message: Optional[str] = Field(
        default=None,
        description="Success or error message from job processing"
    )
    notion_page_url: Optional[str] = Field(
        default=None,
        description="URL of created Notion page (on success)"
    )


class DatabaseManager:
    """
    Database connection and session management utilities.
    Handles engine creation, session lifecycle, and table initialization.
    """
    
    def __init__(self, database_url: str = settings.DATABASE_URL):
        """Initialize database manager with connection URL."""
        self.database_url = database_url
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
    
    def initialize(self) -> None:
        """
        Initialize database engine and session factory.
        Creates tables if they don't exist.
        """
        # Create engine with appropriate settings for SQLite
        connect_args = {}
        if self.database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        
        self.engine = create_engine(
            self.database_url,
            connect_args=connect_args,
            echo=False  # Set to True for SQL query logging in development
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create all tables
        self.create_tables()
    
    def create_tables(self) -> None:
        """Create all database tables if they don't exist."""
        if self.engine is None:
            raise RuntimeError("Database engine not initialized. Call initialize() first.")
        
        SQLModel.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session with automatic cleanup.
        Yields a session and ensures it's properly closed.
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """
        Perform database health check.
        Returns True if database is accessible, False otherwise.
        """
        try:
            with next(self.get_session()) as session:
                # Simple query to test connection
                session.execute(select(1))
                return True
        except Exception:
            return False


# Global database manager instance
db_manager = DatabaseManager()


def get_database_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session injection.
    Provides a database session that's automatically cleaned up.
    """
    yield from db_manager.get_session()


def init_database() -> None:
    """
    Initialize database on application startup.
    Creates tables and prepares connection pool.
    """
    db_manager.initialize()