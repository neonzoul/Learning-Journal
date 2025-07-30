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