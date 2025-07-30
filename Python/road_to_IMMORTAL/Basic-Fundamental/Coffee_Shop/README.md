# Coffee Shop Async System

This is an asynchronous coffee shop simulation system implemented in Python using async/await.

## Components

### 1. Coffee Shop Server (`coffee_shop_server.py`)

-   Main server that manages the shop status
-   Displays "Shop Is Opening" when started
-   Handles Ctrl+C to close shop and show order summary
-   Manages order counter and revenue tracking

### 2. Customer Service (`customer_service.py`)

-   Only works while coffee_shop_server is running
-   Greets customers and collects order information
-   Handles customer orders with the following structure:
    ```python
    customer_order = {
        "card_no": str,  # numbers only
        "available_menu": tuple,  # ('coffee', 'non-coffee')
        "selected_order": str,
        "order_amount": int,  # quantity
        "order_number": int  # auto-generated, starts from 1
    }
    ```

### 3. Brewing Station (`brewing_station.py`)

-   Processes customer orders
-   Simulates brewing with 1.25 seconds delay
-   Prints completion message: "🎐 Order{order_number} {order_details} IS FINISHED 🍵"

## How to Run

1. Navigate to the Coffee_Shop directory:

    ```bash
    cd "f:\Coding-Area\Learn\Python\road_to_IMMORTAL\level-1\Coffee_Shop"
    ```

2. Run the coffee shop system:

    ```bash
    python run_coffee_shop.py
    ```

    OR directly:

    ```bash
    python coffee_shop_server.py
    ```

3. Follow the prompts to:

    - Enter customer card numbers (numbers only)
    - Select items from the menu (coffee or non-coffee)
    - Specify quantities

4. Press Ctrl+C to close the shop and see the summary

## Features

-   ✅ Async/await implementation
-   ✅ Shop status management
-   ✅ Order counter (resets when shop restarts)
-   ✅ Customer service with input validation
-   ✅ Brewing simulation with realistic timing
-   ✅ Order summary with revenue tracking
-   ✅ Graceful shutdown with Ctrl+C
-   ✅ JSON-compatible order data structure

## Example Output

```
🏪 Shop Is Opening
☕ Welcome to our Coffee Shop!
Press Ctrl+C to close the shop

👋 Customer Service is ready!

========================================
🛎️  New Customer Arrived!
👋 Hello! Welcome to our Coffee Shop!
How can I help you today?

📇 Please provide your information:
Enter your card number (numbers only): 1234567890

📋 Our Menu:
--------------------
• Coffee: $5
• Non-coffee: $3

What would you like to order? coffee
How many would you like? 2

📋 Order Summary:
   Card: 1234567890
   Item: coffee
   Quantity: 2
   Unit Price: $5
   Total: $10

Confirm order? (y/n): y
✅ Order confirmed! Please wait while we prepare your order.
📝 New order received: Order #1
🔥 Brewing Station: Starting order #1...
🎐 Order 1
  Customer card: ******7890
  Order: coffee amount 2 IS FINISHED 🍵
```

## Requirements

-   Python 3.7+
-   No external dependencies required (uses only built-in modules)
