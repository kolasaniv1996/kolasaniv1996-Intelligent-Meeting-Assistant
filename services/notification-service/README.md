# Notification Service (Conceptual)

This service is responsible for consuming events from a message queue (e.g., Redis Pub/Sub) and handling notifications.
Currently, it's a conceptual example demonstrating how a service might subscribe to messages.

## Setup and Running

1.  **Ensure Redis is running** and accessible at the host/port specified in the environment variables.

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scriptsctivate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Copy `.env.sample` to `.env` and update `REDIS_HOST`, `REDIS_PORT`, and `REDIS_CHANNEL` if they differ from the defaults.
    ```bash
    cp .env.sample .env
    ```

5.  **Run the application (subscriber script):**
    ```bash
    python app.py
    ```
    This will start the Redis subscriber, which will listen for messages on the configured channel.

## Functionality

*   Connects to a Redis server.
*   Subscribes to a specified Redis channel (`system_notifications` by default).
*   When a message is received, the `message_handler` function processes it (currently prints to console).
*   Includes basic error handling for Redis connection and message processing.

This service is intended to be a consumer in a Pub/Sub architecture. Other services would publish messages to the Redis channel it listens to.
