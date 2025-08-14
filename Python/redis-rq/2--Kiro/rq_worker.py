"""
RQ Worker entry point for background job processing.
"""

import redis
from rq import Worker, Queue, Connection
from app.core.settings import settings

# Redis connection
redis_conn = redis.from_url(settings.REDIS_URL)

if __name__ == "__main__":
    # Create worker with default queue
    with Connection(redis_conn):
        worker = Worker(Queue())
        worker.work()