import os
import redis
import json
import time
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_CHANNEL = os.environ.get("REDIS_CHANNEL", "system_notifications")

def connect_to_redis():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        r.ping()
        print(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        return None

def message_handler(message):
    '''
    This function is called when a new message is received on the subscribed channel.
    '''
    print(f"NOTIFICATION_SERVICE: Received message at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        data = json.loads(message['data'])
        print(f"  Channel: {message['channel']}")
        print(f"  Type: {message['type']}")
        print(f"  Data: {json.dumps(data, indent=2)}")

        # Example: Process based on message content
        if data.get("event_type") == "MEETING_PROCESSED":
            print(f"  Action: Notifying user about meeting '{data.get('summary', 'N/A')}' being processed.")
        # Add more processing logic here based on different event_types

    except json.JSONDecodeError:
        print(f"  Error: Could not decode JSON from message data: {message['data']}")
    except Exception as e:
        print(f"  Error processing message: {e}")

def start_subscriber(redis_client):
    if not redis_client:
        print("NOTIFICATION_SERVICE: Cannot start subscriber, Redis client not available.")
        return

    pubsub = redis_client.pubsub()
    try:
        pubsub.subscribe(**{REDIS_CHANNEL: message_handler})
        print(f"NOTIFICATION_SERVICE: Subscribed to Redis channel '{REDIS_CHANNEL}'. Waiting for messages...")
        # Keep the subscriber running and listening for messages
        # In a real Flask app, this would run in a background thread or separate process.
        # For this example, it will block here.
        for message in pubsub.listen():
            # The message_handler is called directly by pubsub.subscribe in newer versions
            # This loop is more for older versions or direct pubsub.listen() usage.
            # With the handler registered, this loop might just be time.sleep() or health checks.
            if message['type'] == 'message':
                # If handler wasn't called automatically, call it here
                # message_handler(message)
                pass # message_handler is now called by pubsub.subscribe mechanism
            elif message['type'] == 'subscribe':
                print(f"  Successfully subscribed to channel: {message['channel']}")
            time.sleep(0.01) # Be nice to the CPU

    except redis.exceptions.ConnectionError as e:
        print(f"NOTIFICATION_SERVICE: Redis connection error during subscription: {e}. Attempting to reconnect...")
        # Implement reconnection logic if needed
    except Exception as e:
        print(f"NOTIFICATION_SERVICE: Error in subscriber loop: {e}")
    finally:
        print("NOTIFICATION_SERVICE: Unsubscribing and closing Redis connection.")
        if pubsub:
            pubsub.unsubscribe(REDIS_CHANNEL)
            pubsub.close()


if __name__ == "__main__":
    print("NOTIFICATION_SERVICE: Starting...")
    redis_client = connect_to_redis()
    if redis_client:
        # In a real service, you might run a Flask app on one thread/process
        # and the Redis subscriber in another.
        # For this example, we'll just start the subscriber directly.
        start_subscriber(redis_client)
    else:
        print("NOTIFICATION_SERVICE: Could not connect to Redis. Exiting.")
