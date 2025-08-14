## Backend Implementation Requirements

This document outlines the technical requirements and implementation details for the Python backend service. The backend is designed as a lean, robust, and scalable FastAPI application whose primary responsibilities are to ingest receipt images, trigger an external N8N workflow via a durable message queue, and log the final results.

### 1\. Project Dependencies

The system requires the following Python libraries. These should be listed in a `requirements.txt` file.

```
# requirements.txt

# Core web framework and server
fastapi
uvicorn[standard]

# Asynchronous task queue and broker
rq
redis

# Data validation and ORM
sqlmodel
pydantic
pydantic-settings

# File handling and validation
python-multipart
python-magic
Pillow

# HTTP client for worker
httpx

# Monitoring
rq-dashboard-fast
```

### 2\. Project Structure

The backend will be organized into a modular structure to enforce a strict Separation of Concerns (SoC).[1, 2, 3, 4] This architecture ensures that the application is maintainable, testable, and scalable.

```
accounting_service/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routers/
│   │           ├── __init__.py
│   │           ├── receipts.py
│   │           └── jobs.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── protocols.py
│   │   └── schemas.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── logging_db.py
│   │   └── queue.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── logging_service.py
│   │   └── task_service.py
│   └── main.py
├── rq_worker.py
└──.env.example
```

### 3\. Core Configuration (`app/core/config.py`)

All configuration will be managed via environment variables, loaded by Pydantic's `Settings` class. This provides type-safe access to configuration and avoids hardcoding sensitive values.[1, 2]

```python
# In app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application settings
    API_V1_STR: str = "/api/v1"
    
    # Redis and RQ configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # N8N configuration for the worker
    N8N_WEBHOOK_URL: str
    N8N_API_KEY: str
    
    # Callback security
    CALLBACK_SECRET_TOKEN: str
    
    # Database configuration
    DATABASE_URL: str = "sqlite:///./job_logs.db"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

### 4\. Domain Layer (`app/domain/`)

The domain layer defines the data structures (schemas) and behavioral contracts (protocols) of the application.

#### 4.1 Data Schemas (`app/domain/schemas.py`)

These Pydantic models define the data contracts for API endpoints, ensuring all incoming and outgoing data is validated.[2]

```python
# In app/domain/schemas.py
import uuid
from typing import Optional
from pydantic import BaseModel

class JobCreationResponse(BaseModel):
    job_id: uuid.UUID
    status: str = "queued"

class JobCallbackPayload(BaseModel):
    status: str  # e.g., "success", "failure"
    message: Optional[str] = None
    notion_page_url: Optional[str] = None
```

#### 4.2 Behavioral Protocols (`app/domain/protocols.py`)

To adhere to the protocol-driven style, we define an interface for our queueing service. This decouples the `TaskService` from the specific `rq` implementation, making the business logic more abstract and testable.[5, 6, 7, 8]

```python
# In app/domain/protocols.py
from typing import Protocol, Any, Dict
import uuid

class QueueServiceProtocol(Protocol):
    """
    A protocol defining the contract for a job queueing service.
    This ensures any queue implementation can be used as long as it
    adheres to this interface.
    """
    def enqueue_job(self, function_name: str, job_id: uuid.UUID, **kwargs: Any) -> None:
       ...
```

### 5\. Infrastructure Layer (`app/infrastructure/`)

This layer contains concrete implementations for interacting with external systems like Redis and the database.

#### 5.1 Queue Implementation (`app/infrastructure/queue.py`)

This module provides the concrete `rq` queue implementation that satisfies the `QueueServiceProtocol`.[9, 10, 11]

```python
# In app/infrastructure/queue.py
from redis import Redis
from rq import Queue
from typing import Any
import uuid

from app.core.config import settings
from app.domain.protocols import QueueServiceProtocol

class RQService:
    """Concrete implementation of QueueServiceProtocol using Redis Queue."""
    def __init__(self, connection: Redis):
        self.queue = Queue(connection=connection)

    def enqueue_job(self, function_name: str, job_id: uuid.UUID, **kwargs: Any) -> None:
        self.queue.enqueue(
            function_name,
            job_id=job_id,
            **kwargs,
            job_timeout='10m'
        )

# Dependency for FastAPI
def get_queue_service() -> QueueServiceProtocol:
    redis_conn = Redis.from_url(settings.REDIS_URL)
    return RQService(connection=redis_conn)
```

#### 5.2 Logging Database (`app/infrastructure/logging_db.py`)

This module sets up the `SQLModel` for the audit log database.[12, 13]

```python
# In app/infrastructure/logging_db.py
import uuid
import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session

from app.core.config import settings

class JobLog(SQLModel, table=True):
    job_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: str = Field(index=True, default="queued")
    filename: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    completed_at: Optional[datetime.datetime] = None
    result_message: Optional[str] = None
    notion_page_url: Optional[str] = None

engine = create_engine(settings.DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency for getting a database session
def get_session():
    with Session(engine) as session:
        yield session
```

### 6\. Service Layer (`app/services/`)

The service layer contains the core business logic, orchestrating interactions between the API and infrastructure layers.

#### 6.1 Task Service (`app/services/task_service.py`)

This service handles the logic for creating and enqueueing a new processing job. It depends on the `QueueServiceProtocol`, not a concrete implementation.

```python
# In app/services/task_service.py
import uuid
from fastapi import UploadFile, Depends
from sqlmodel import Session

from app.domain.protocols import QueueServiceProtocol
from app.infrastructure.queue import get_queue_service
from app.services.logging_service import LoggingService, get_logging_service

class TaskService:
    def __init__(
        self,
        queue_service: QueueServiceProtocol,
        logging_service: LoggingService
    ):
        self.queue_service = queue_service
        self.logging_service = logging_service

    async def create_and_enqueue_task(
        self, file: UploadFile, notion_database_id: str
    ) -> uuid.UUID:
        job_id = uuid.uuid4()
        
        # Read file into memory; essential for passing to a background process
        image_bytes = await file.read()
        
        # Create initial log entry
        self.logging_service.create_initial_log(
            job_id=job_id,
            filename=file.filename
        )
        
        # Enqueue the job using the protocol
        self.queue_service.enqueue_job(
            'rq_worker.trigger_n8n_workflow',
            job_id=job_id,
            image_bytes=image_bytes,
            notion_database_id=notion_database_id,
            filename=file.filename
        )
        return job_id

# Dependency for FastAPI
def get_task_service(
    queue_service: QueueServiceProtocol = Depends(get_queue_service),
    logging_service: LoggingService = Depends(get_logging_service)
) -> TaskService:
    return TaskService(queue_service, logging_service)
```

#### 6.2 Logging Service (`app/services/logging_service.py`)

This service encapsulates all database operations for the `JobLog` table.

```python
# In app/services/logging_service.py
import uuid
import datetime
from typing import Optional
from sqlmodel import Session
from fastapi import Depends

from app.infrastructure.logging_db import JobLog, get_session
from app.domain.schemas import JobCallbackPayload

class LoggingService:
    def __init__(self, session: Session):
        self.session = session

    def create_initial_log(self, job_id: uuid.UUID, filename: Optional[str]):
        db_log = JobLog(job_id=job_id, filename=filename)
        self.session.add(db_log)
        self.session.commit()

    def update_job_status_from_callback(self, job_id: uuid.UUID, payload: JobCallbackPayload):
        db_log = self.session.get(JobLog, job_id)
        if db_log:
            db_log.status = payload.status
            db_log.result_message = payload.message
            db_log.notion_page_url = payload.notion_page_url
            db_log.completed_at = datetime.datetime.utcnow()
            self.session.add(db_log)
            self.session.commit()

# Dependency for FastAPI
def get_logging_service(session: Session = Depends(get_session)) -> LoggingService:
    return LoggingService(session)
```

### 7\. API Layer (`app/api/v1/`)

This layer defines the HTTP endpoints, handling requests and responses. It relies on the service layer for all business logic.

#### 7.1 Receipts Router (`app/api/v1/routers/receipts.py`)

Handles the initial file upload.

```python
# In app/api/v1/routers/receipts.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.domain.schemas import JobCreationResponse
from app.services.task_service import TaskService, get_task_service
import magic

router = APIRouter()

@router.post("/receipts/upload", response_model=JobCreationResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_receipt(
    file: UploadFile = File(...),
    notion_database_id: str = Form(...),
    task_service: TaskService = Depends(get_task_service)
):
    # Basic file validation [14]
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    # More robust validation with python-magic
    file_content = await file.read()
    await file.seek(0) # Reset file pointer after reading
    mime_type = magic.from_buffer(file_content, mime=True)
    if not mime_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File content is not a valid image format.")

    job_id = await task_service.create_and_enqueue_task(file, notion_database_id)
    return JobCreationResponse(job_id=job_id)
```

#### 7.2 Jobs Router (`app/api/v1/routers/jobs.py`)

Handles the callback from the N8N workflow.

```python
# In app/api/v1/routers/jobs.py
import uuid
from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.domain.schemas import JobCallbackPayload
from app.services.logging_service import LoggingService, get_logging_service
from app.core.config import settings

router = APIRouter()

# Security Dependency
async def verify_token(x_callback_token: str = Header(...)):
    if x_callback_token!= settings.CALLBACK_SECRET_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Callback Token")

@router.post("/jobs/{job_id}/callback", dependencies=)
def job_callback(
    job_id: uuid.UUID,
    payload: JobCallbackPayload,
    logging_service: LoggingService = Depends(get_logging_service)
):
    logging_service.update_job_status_from_callback(job_id, payload)
    return {"status": "received"}
```

### 8\. Application Entrypoint (`app/main.py`)

This file ties everything together: it creates the FastAPI app instance, includes the routers, and sets up startup events.[2, 3, 12]

```python
# In app/main.py
from fastapi import FastAPI
from rq_dashboard_fast.rq_dashboard_fast import RQDashboard

from app.api.v1.routers import receipts, jobs
from app.infrastructure.logging_db import create_db_and_tables
from app.core.config import settings

# Initialize RQ Dashboard for monitoring [10]
redis_url = settings.REDIS_URL
rq_dashboard = RQDashboard(redis_url=redis_url, prefix="/rq")

app = FastAPI(title="Accounting Automation Service")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(receipts.router, prefix=settings.API_V1_STR, tags=)
app.include_router(jobs.router, prefix=settings.API_V1_STR, tags=["Jobs"])
app.mount('/rq', rq_dashboard) # Mount the dashboard

@app.get("/")
def read_root():
    return {"message": "Service is running."}
```

### 9\. RQ Worker (`rq_worker.py`)

This is the standalone script for the background worker process. It is responsible for making the HTTP request to the N8N workflow.[9, 10]

```python
# In rq_worker.py
import os
import httpx
import base64
import uuid
from redis import Redis
from rq import Worker, Queue, Connection

# It's crucial that the worker can import the app's config
from app.core.config import settings

listen = ['default']
redis_conn = Redis.from_url(settings.REDIS_URL)

def trigger_n8n_workflow(
    job_id: uuid.UUID,
    image_bytes: bytes,
    notion_database_id: str,
    filename: str
):
    """
    The main task function executed by the RQ worker.
    It triggers the N8N workflow.
    """
    print(f"Triggering N8N for job {job_id}...")
    try:
        callback_url = f"http://host.docker.internal:8000{settings.API_V1_STR}/jobs/{job_id}/callback"
        
        n8n_payload = {
            "job_id": str(job_id),
            "image_data": base64.b64encode(image_bytes).decode('utf-8'),
            "filename": filename,
            "notion_database_id": notion_database_id,
            "callback_url": callback_url
        }

        with httpx.Client() as client:
            response = client.post(
                settings.N8N_WEBHOOK_URL,
                json=n8n_payload,
                headers={"X-N8N-Api-Key": settings.N8N_API_KEY},
                timeout=60.0 # Allow a longer timeout for the webhook trigger
            )
            response.raise_for_status()

        print(f"Job {job_id} successfully submitted to N8N.")

    except Exception as e:
        print(f"Error triggering N8N for job {job_id}: {e}")
        raise # Let RQ handle the failure and move to failed queue

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()
```

### 10\. Running the System

To run the complete backend system, you will need three separate processes:

1.  **Redis Server:** (Assumed to be running, e.g., via Docker)
2.  **FastAPI Application Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
3.  **RQ Worker Process:**
    ```bash
    python rq_worker.py
    ```