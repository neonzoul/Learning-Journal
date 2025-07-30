# Import necessary libraries
from fastapi import FastAPI
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from typing import List

# Import our task function (this will be in tasks.py)
# Make sure you have the tasks.py file in the same directory
from tasks import make_coffee_order

# Define a Pydantic model to validate the incoming order data.
# This ensures any request to /order has a "coffees" field that is a list of strings.
class Order(BaseModel):
    coffees: List[str]

# Create the main FastAPI application instance
app = FastAPI(title="Barista's Coffee Shop")

# --- Connections ---
# Connect to the Redis server, which acts as our queue's storage
redis_conn = Redis(host='localhost', port=6379)

# Create a queue named 'default' that uses our Redis connection
q = Queue(connection=redis_conn)

# --- API Endpoint ---
@app.post("/order")
def create_order(order: Order):
    """
    This endpoint acts as the Customer Service counter.
    It takes an order, assigns a queue number, and adds the job to the queue.
    """
    # Get the next queue number by incrementing a counter stored in Redis.
    # This is a robust way to handle a shared counter that persists.
    queue_number = redis_conn.incr('queue_counter')

    # Add the 'make_coffee_order' task to the queue.
    # We pass the function itself and its arguments (queue_number, order.coffees).
    # The job is created and stored in Redis but does not run here.
    job = q.enqueue(make_coffee_order, queue_number, order.coffees)

    # Return an immediate response to the customer.
    # The web server is now free to handle the next request.
    return {
        "message": "Order received! Please wait for your number to be called.",
        "your_queue_number": queue_number,
        "job_id": job.id # The job ID can be used to check status later
    }