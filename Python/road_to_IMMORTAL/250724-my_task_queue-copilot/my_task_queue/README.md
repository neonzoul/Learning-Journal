# Task Queue System with FastAPI and Redis

A demonstration of asynchronous task processing using FastAPI, Redis, and RQ (Redis Queue). This project shows how to build a responsive web API that can handle slow operations without blocking user requests.

## 🤖 AI-Assisted Development & Lab Experiment

### **Lab Project Purpose**

This is an **experimental lab project** to test whether GitHub Copilot Agent can successfully implement complex requirements from contextual descriptions. The goal is to validate AI-assisted development capabilities in building production-ready asynchronous systems.

## 🎓 Perfect for Learning Async Programming

This project teaches you the **core concept** behind modern web applications:

-   **Never make users wait** for slow operations
-   **Separate fast responses** from slow background work
-   **Scale your app** by processing tasks in parallel

Once you understand this pattern, you'll recognize it everywhere - from Instagram photo uploads to Gmail sending emails! 🚀

### **Development Collaboration**

-   **📋 Requirements Creation**: Problem and assignment brainstormed with **Gemini 2.5 Pro**
-   **🛠️ Full Implementation**: Complete code development using **GitHub Copilot Agent Mode** powered by **Claude Sonnet 4**
-   **🎯 Training Context**: Part of Python training for AutomateOS core engine development, focusing on **Asynchronous Programming** mastery

## 🎯 Project Overview

This system implements the classic **Producer-Consumer** pattern for handling time-consuming tasks:

-   **Producer**: FastAPI web server that receives requests and queues tasks
-   **Queue**: Redis acts as the message broker
-   **Consumer**: Background worker processes that execute tasks

### **Real Examples Where You'd Use This:**

-   **E-commerce**: Process orders instantly, handle payment/shipping in background
-   **Social Media**: Upload photo immediately, resize/filter it later
-   **Email Newsletter**: Queue thousands of emails instead of sending one by one
-   **File Sharing**: Accept file upload instantly, scan for viruses in background
-   **Analytics Dashboard**: Show "Report generating..." immediately, calculate data separately

## 🚀 Features

-   **Instant API Response**: Web server responds immediately without waiting for task completion
-   **Background Processing**: Time-consuming tasks run in separate worker processes
-   **Scalable**: Can handle multiple requests while tasks process in parallel
-   **Windows Compatible**: Uses SimpleWorker for Windows environment compatibility
-   **Real-time Monitoring**: Worker logs show task processing in real-time

## 🎯 Key Benefits

-   **No Blocking**: Web server never waits for slow operations
-   **User Experience**: Users get instant feedback, no long loading times
-   **Scalability**: Can handle many requests while tasks process separately
-   **Reliability**: Redis persists jobs even if workers restart
-   **Monitoring**: Real-time visibility into task processing

## 🏗️ Architecture

```
[User Request] → [FastAPI] → [Redis Queue] → [Worker Process]
      ↓              ↓             ↓              ↓
   Instant        Enqueue      Store Job      Process Task
   Response       Task         Message        (10 seconds)
```

## 📁 Project Structure

```
my_task_queue/
├── app.py          # FastAPI web server (Producer)
├── worker.py       # Background worker (Consumer)
├── tasks.py        # Task definitions
└── README.md       # This file
```

## 🛠️ Installation & Setup

### Prerequisites

-   Python 3.7+
-   Docker (for Redis)
-   Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd my_task_queue
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install fastapi "uvicorn[standard]" redis rq
```

### 4. Start Redis Server

```bash
docker run -d -p 6379:6379 redis
```

## 🚀 Running the System

### Step 1: Start the Worker

In your first terminal:

```bash
cd my_task_queue
python -c "
import redis
from rq import SimpleWorker, Queue
import sys
sys.path.insert(0, r'F:\\path\\to\\your\\project\\my_task_queue')
import tasks
redis_conn = redis.Redis(host='localhost', port=6379)
q = Queue(connection=redis_conn)
worker = SimpleWorker([q], connection=redis_conn)
print('Starting worker...')
worker.work()
"
```

### Step 2: Start the Web Server

In your second terminal:

```bash
cd my_task_queue
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### Step 3: Test the System

Open your browser or use curl:

```bash
# Send an email task
curl "http://127.0.0.1:8000/send-email/user@example.com"

# Response (immediate):
{
  "message": "Email sending task has been queued.",
  "job_id": "abc123-def456-ghi789"
}
```

## 📝 Code Components

### `app.py` - Web Server (Producer)

```python
from fastapi import FastAPI
from redis import Redis
from rq import Queue
from tasks import send_fake_email

# Initialize FastAPI application - creates the web server
app = FastAPI()

# Connect to Redis server - acts as message broker for job queue
redis_conn = Redis(host='localhost', port=6379)

# Create RQ queue - manages job storage and retrieval from Redis
q = Queue(connection=redis_conn)

@app.get("/send-email/{email}")
def trigger_email(email: str):
    # Enqueue task immediately - non-blocking operation returns instantly
    job = q.enqueue(send_fake_email, email)

    # Return job ID to client - allows tracking without waiting for completion
    return {
        "message": "Email sending task has been queued.",
        "job_id": job.id
    }
```

**Purpose**: Acts as the Producer in Producer-Consumer pattern. Receives HTTP requests and immediately queues tasks for background processing.
**Key Benefit**: Web server never blocks on slow operations, ensuring instant response times.

### `tasks.py` - Task Definitions

```python
import time

def send_fake_email(email_address: str):
    """Simulates sending an email with a 10-second delay"""
    # Log task start - useful for monitoring and debugging
    print(f"Starting to send email to {email_address}...")

    # Simulate slow operation - represents real-world API calls, file processing, etc.
    time.sleep(10)  # This would be actual email sending logic in production

    # Log task completion - confirms successful execution
    print(f"Email sent to {email_address}!")

    # Return result - can be stored for job status tracking
    return f"Task complete: Email sent to {email_address}"
```

**Purpose**: Contains the actual business logic that takes time to execute. Isolated from web layer for clean separation of concerns.
**Key Benefit**: Can be modified, tested, and scaled independently of the web server.

### `worker.py` - Background Worker (Consumer)

```python
import redis
from rq import SimpleWorker, Queue
import sys
import os

# Ensure tasks module can be imported - critical for worker to find job functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tasks

# Connect to same Redis instance as web server - shared job queue
redis_conn = redis.Redis(host='localhost', port=6379)

# Create queue connection - worker monitors this for new jobs
q = Queue(connection=redis_conn)

# Create SimpleWorker for Windows compatibility - handles job execution
worker = SimpleWorker([q], connection=redis_conn)

# Start infinite loop - continuously polls queue and processes jobs
worker.work()  # This blocks and runs forever, processing jobs as they arrive
```

**Purpose**: Acts as the Consumer in Producer-Consumer pattern. Continuously monitors Redis queue and executes tasks in the background.
**Key Benefit**: Runs independently of web server, enabling true asynchronous processing and horizontal scaling.

## 🐛 Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
docker ps

# Restart Redis if needed
docker run -d -p 6379:6379 redis
```

### Import Errors

-   Ensure you're in the correct directory
-   Check that all files are in the same folder
-   Verify Python path is set correctly

### Worker Not Processing Jobs

-   Confirm worker is running and connected to Redis
-   Check for import errors in worker terminal
-   Verify Redis is accessible on localhost:6379

## 🔍 How It Works

1. **User Request**: Browser/client sends GET request to `/send-email/{email}`
2. **Instant Response**: FastAPI immediately enqueues the task and returns a job ID
3. **Background Processing**: Worker picks up the job from Redis queue
4. **Task Execution**: Worker runs the slow `send_fake_email` function (10 seconds)
5. **Completion**: Task completes in background while server remains responsive

## ⚡ Performance Impact Examples

### **Before Task Queue (Blocking)**

```
User Action: Upload 100MB video
API Response Time: 45 seconds (user waits)
Concurrent Users: Limited (server busy processing)
User Experience: Loading spinner hell 😱
```

### **After Task Queue (Non-blocking)**

```
User Action: Upload 100MB video
API Response Time: 200ms (instant feedback)
Concurrent Users: Unlimited (server always responsive)
User Experience: Smooth, professional 🚀
```

### **How Task Queues Fix This:**

**❌ Without Task Queue (Bad Experience):**

```
User clicks "Send Email" → Wait 5 seconds → Page responds
```

**✅ With Task Queue (Good Experience):**

```
User clicks "Send Email" → Instant "Email queued!" → Email sends in background
```

## 📚 Learning Objectives

This project demonstrates:

-   **Asynchronous Task Processing**
-   **Producer-Consumer Pattern**
-   **Message Queue Architecture**
-   **FastAPI Web Development**
-   **Redis Integration**
-   **Background Job Processing**

## 🎯 When You Should Use This Pattern

### ✅ **Perfect For:**

-   **Email/SMS sending** - External APIs are slow
-   **File processing** - Image/video compression, PDF generation
-   **Data exports** - Large CSV/Excel file generation
-   **External API calls** - Payment processing, social media posting
-   **Database migrations** - Heavy data transformations
-   **Report generation** - Complex analytics queries
-   **Batch operations** - Processing thousands of records

### ❌ **Not Needed For:**

-   Simple database lookups
-   Basic CRUD operations
-   Real-time chat features (use WebSockets instead)
-   Small calculations that finish in milliseconds

## 🏢 Production Examples

### **Stripe (Payment Processing)**

```python
# Stripe doesn't make you wait for webhook processing
@app.post("/webhook/stripe")
def handle_stripe_webhook(webhook_data):
    q.enqueue(process_payment_confirmation, webhook_data)
    return {"status": "received"}  # Instant response to Stripe
```

### **GitHub (Repository Operations)**

```python
# GitHub doesn't block when you create a repo
@app.post("/repositories")
def create_repository(repo_data):
    q.enqueue(setup_git_repository, repo_data)
    q.enqueue(create_default_files, repo_data)
    q.enqueue(setup_webhooks, repo_data)
    return {"message": "Repository creation started"}
```

This pattern is **everywhere** in modern web applications - from Netflix video processing to Uber's ride matching algorithms. Master this, and you'll build applications that feel fast and professional! 🚀

## 📈 Next Steps

To extend this system, consider:

-   Adding job status endpoints (`/job/{job_id}/status`)
-   Implementing job result storage
-   Adding job retry mechanisms
-   Creating a web dashboard for monitoring
-   Setting up multiple worker processes
-   Adding job priority levels
-   Implementing job scheduling

## 📄 License

This project is for educational purposes and demonstrates modern task queue patterns in Python web applications.

---

**Built with ❤️ using FastAPI, Redis, and RQ**
</br>
(README by Copilot - Claude Sonnet 4)
