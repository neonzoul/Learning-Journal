# worker.py : Worker - processes tasks from the queue in background
# WHY separate process? Web server = fast responses, Worker = slow tasks
# This separation prevents slow work from blocking user requests

import redis
from rq import SimpleWorker, Queue
import sys
import os

# Let Python find our tasks.py file
# Why this path setup? Worker runs separately, needs to find task functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    import tasks
    
    # Connect to Redis (same one as web app uses)
    # Why same Redis? Shared queue between web app and worker
    redis_conn = redis.Redis(host='localhost', port=6379)
    
    # Create queue (worker reads from here)
    q = Queue(connection=redis_conn)
    
    # Start worker (uses SimpleWorker for Windows compatibility)
    # Why SimpleWorker? Regular Worker uses Unix features Windows doesn't have
    worker = SimpleWorker([q], connection=redis_conn)
    print("Worker started. Waiting for tasks...")
    worker.work()   # Runs forever until Ctrl+C, checking queue constantly
