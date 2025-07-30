**Addition using async**

-   coffee_shop_server { run for open shop simulator, display status after open "Shop Is Opening" until ctrl+c show close shop and then summary **orders**. }
-   Customer Service (condotion Casher can work only while coffee_shop_server is running) { say hello -> collect info,order -> }

    -   customer_order = {
        "card_no": str only number.
        "available_menu": tuble[str, ...] = ('coffee', 'non-coffee') // using inquirer
        "selected_order": str = ""
        "order_amout": int = 0
        "order_number": count start from 1...re start at coffe_shop_server start running, end order_number after coffee_shop_server is close.
        } return as customer_data JSON & + order return to coffee_shop_server {orders}+{order_amount}

-   Brewing Station (customer_order JSON) { wait 1.25 sec simulate brewing coffee. } return print" 🎐 Oder{order_numer} {order_details,} IS FINISHED 🍵"

order_details =
customer card: xxxxx
Order: {selected_order} amout {order_amout}

# Implementation

# File: requirements.txt

#

# Lists the external Python libraries needed for this project.

# Install them by running: pip install -r requirements.txt

redis
rq
inquirer

````python
# File: coffee_shop_server.py
#
# This is the main process for the coffee shop.
# It "opens" the shop by resetting the counters and runs until you stop it.
# When stopped, it prints a summary of the day's business.

import redis
import time
import sys

# Connect to our Redis database. This is the shared brain for all our scripts.
try:
    redis_conn = redis.Redis(host='localhost', port=6379, decode_responses=True)
    # Ping the server to ensure a connection is established.
    redis_conn.ping()
except redis.exceptions.ConnectionError as e:
    print("Could not connect to Redis. Is the Redis server running?", file=sys.stderr)
    sys.exit(1)


def open_shop():
    """Resets the daily counters to start a new business day."""
    print(" barista is preparing the shop...")
    # Set the counters for today to 0.
    redis_conn.set("order_number_counter", 0)
    redis_conn.set("total_orders_amount", 0)
    print("✅ Shop is now OPEN!")
    print("---------------------------------")
    print("(Press Ctrl+C to close the shop at the end of the day)")


def close_shop():
    """Retrieves final counts and prints the summary."""
    print("\n---------------------------------")
    print(" shop is closing...")
    # Get the final values from Redis.
    final_order_count = int(redis_conn.get("order_number_counter") or 0)
    final_total_amount = int(redis_conn.get("total_orders_amount") or 0)

    print("\n--- End of Day Summary ---")
    print(f"Total Orders Processed: {final_order_count}")
    print(f"Total Items Sold: {final_total_amount}")
    print("----------------------------")
    print("✅ Shop is now CLOSED.")


if __name__ == "__main__":
    open_shop()
    try:
        # This loop keeps the script running. It does nothing but wait.
        # This simulates the shop being open all day.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # This block runs when you press Ctrl+C.
        close_shop()
```python
# File: brewing_station.py
#
# This file defines the actual "work" to be done.
# It contains the function that simulates the time it takes to brew an order.

import time

def brew_order(customer_order: dict):
    """
    Simulates the time it takes to brew a coffee order and prints the result.
    This is the function our background worker (the Barista) will run.
    """
    print(f" brewing order #{customer_order['order_number']}...")

    # Simulate the brewing time.
    time.sleep(1.25)

    # Prepare the final formatted message.
    order_details = f"""
    customer card: {customer_order['card_no']}
    Order: {customer_order['selected_order']} amount {customer_order['order_amount']}
    """

    finished_message = f"""
🎐 Order {customer_order['order_number']} {order_details.strip()} IS FINISHED 🍵
    """
    print(finished_message)

    return finished_message
```python
# File: coffee_shop_worker.py
#
# This is the "Barista". It's a background worker process.
# Its only job is to watch the queue for new orders and run the brewing task.
# It needs to run in its own terminal window.

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
```python
# File: customer_service.py
#
# This is the "Casher". You run this script every time a new customer
# wants to place an order. It collects the order details and adds the
# job to the queue for the Barista.

import inquirer
import redis
from rq import Queue
import sys

# Import the task function from our other file.
from brewing_station import brew_order

# --- Data and Validation ---
AVAILABLE_MENU = ('coffee', 'non-coffee')

def validate_card_number(answers, current):
    """Checks if the card number contains only digits."""
    if not current.isdigit():
        raise inquirer.errors.ValidationError('', reason='Card number must contain only digits.')
    return True

# --- Main Script ---
if __name__ == "__main__":
    print("👋 Hello! Welcome to the Coffee Shop.")

    # Check if the shop is "open" by trying to connect to Redis.
    try:
        redis_conn = redis.Redis(host='localhost', port=6379)
        redis_conn.ping()
    except redis.exceptions.ConnectionError:
        print("Sorry, the coffee shop appears to be closed. (Cannot connect to Redis)", file=sys.stderr)
        sys.exit(1)

    # --- Collect Order Info using Inquirer ---
    questions = [
        inquirer.Text('card_no', message="Please enter your card number", validate=validate_card_number),
        inquirer.List('menu_choice', message="What type of drink would you like?", choices=AVAILABLE_MENU),
        inquirer.Text('selected_order', message="What is the specific order name?"),
        inquirer.Text('order_amount', message="How many?", validate=lambda _, x: x.isdigit(), default='1'),
    ]
    answers = inquirer.prompt(questions)
    if not answers: # Handles case where user presses Ctrl+C during prompt
        print("\nOrder cancelled.")
        sys.exit(0)

    # --- Prepare the Job for the Queue ---
    # Get the next unique order number from Redis.
    order_number = redis_conn.incr("order_number_counter")
    # Update the total amount of items sold today.
    redis_conn.incrby("total_orders_amount", int(answers['order_amount']))

    # Create the customer data dictionary.
    customer_data = {
        "card_no": answers['card_no'],
        "selected_order": answers['selected_order'],
        "order_amount": int(answers['order_amount']),
        "order_number": order_number,
    }

    # --- Add the Job to the Queue ---
    # Connect to the queue.
    q = Queue(connection=redis_conn)
    # Enqueue the job. This sends the task to the worker (Barista).
    q.enqueue(brew_order, customer_data)

    print("\n✅ Thank you! Your order has been placed.")
    print(f"Your order number is: {order_number}")
````
