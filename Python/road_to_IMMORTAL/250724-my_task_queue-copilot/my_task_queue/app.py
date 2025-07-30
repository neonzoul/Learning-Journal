# app.py : Task Queue Web App
# User makes request -> App adds task to queue -> Returns immediately
# Worker processes tasks in background
# WHY? Users hate waiting. This keeps web app fast while work happens later.

from fastapi import FastAPI # Web framework for API
from redis import Redis # Database for storing queue (fast & reliable)
from rq import Queue # Task queue manager (handles job serialization)
from tasks import send_fake_email # Our task function

# Create web app
app = FastAPI(title="Task Queue Demo")

# Connect to Redis (our queue storage)
# Why Redis? In-memory = fast, persistence = reliable, industry standard
redis_conn = Redis(host='localhost', port=6379)
q = Queue(connection=redis_conn)

# API endpoint: /send-email/{email_address}
@app.get("/send-email/{email}")
def trigger_email(email: str):
    """Add email task to queue and return immediately
    
    Why this approach?
    - User gets instant response (good UX)
    - Web server stays free for other users
    - Background worker does the slow work
    """
    
    # Add task to queue (doesn't wait for completion)
    # Why q.enqueue? Converts function call to storable job format
    job = q.enqueue(send_fake_email, email)
    
    # Return response immediately (the key benefit!)
    return {
        "message": "Email task queued",
        "job_id": job.id  # User can check status later if needed
    }

# To run:
# 1. Start Redis: redis-server
# 2. Start worker: python worker.py  
# 3. Start app: uvicorn app:app --reload
# 4. Test: http://localhost:8000/send-email/test@example.com
