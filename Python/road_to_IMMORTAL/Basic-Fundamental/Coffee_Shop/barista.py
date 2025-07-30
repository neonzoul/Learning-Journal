import redis
from rq import Worker, Queue, Connection

# This line is important. It tells the worker to listen to the 'default' queue.
listen = ['default']

# Connect to the Redis server.
redis_conn = redis.Redis(host='localhost', port=6379)

if __name__ == '__main__':
    # The 'with Connection(redis_conn):' block makes the connection available
    # to the worker.
    with Connection(redis_conn):
        # Create the worker and tell it which queues to listen to.
        worker = Worker(map(Queue, listen))
        print("Barista is ready and waiting for orders...")
        # The worker.work() method starts the listening loop. It will run forever.
        worker.work()