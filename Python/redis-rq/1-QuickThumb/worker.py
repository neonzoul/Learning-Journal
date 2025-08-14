import redis
from rq import Queue
from rq.worker import SimpleWorker

# The worker will listen on the default queue.
listen = ['default']

# Connect to the same Redis instance as the API.
redis_conn = redis.Redis(host='localhost', port=6379)

if __name__ == '__main__':
    print("Chef is starting work (in simple mode for Windows)...")
    # Pass the connection directly to the worker.
    queues = [Queue(name, connection=redis_conn) for name in listen]
    worker = SimpleWorker(queues, connection=redis_conn)
    worker.work()
