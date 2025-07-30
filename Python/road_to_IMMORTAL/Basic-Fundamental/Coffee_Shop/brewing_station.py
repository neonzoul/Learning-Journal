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