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