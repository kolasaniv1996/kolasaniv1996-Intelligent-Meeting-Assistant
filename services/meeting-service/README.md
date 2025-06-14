# Meeting Service
Responsible for managing meeting information, attendance, and real-time interactions. This includes calendar integration, scheduling, and eventually, agent participation in meetings.

## Setup and Running

This service uses Python with Flask. It's responsible for deciding which meetings an AI agent should attend and managing the agent's participation (currently placeholder).

1.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Copy `.env.sample` to a new file named `.env`:
    ```bash
    cp .env.sample .env
    ```
    Edit `.env` to ensure `INTEGRATION_SERVICE_URL` points to your running `integration-service` (e.g., `http://localhost:5001`).

4.  **Run the Flask application:**
    ```bash
    flask run --port=5002
    ```
    Or, if you want to run it directly using `python app.py`:
    ```bash
    python app.py
    ```
    The service will typically be available at `http://localhost:5002`.

## Endpoints

*   `/`: Basic info message for the service.
*   `/meetings/process-upcoming` (POST):
    *   Fetches calendar events for the authenticated user by calling the `integration-service`.
    *   Applies placeholder logic to decide agent "attendance" for these meetings.
    *   **Required Header**: `Authorization: Bearer <YOUR_ACCESS_TOKEN>`
    *   The access token must have calendar scopes, as it will be passed to the `integration-service`.

## Redis Integration (Events Publishing)

This service can publish messages to a Redis channel after processing meetings. This is used to notify other parts of the system (e.g., a `notification-service`).

### Configuration for Redis

Ensure the following environment variables are set in your `.env` file for this service if you want to enable publishing:

*   `REDIS_HOST`: Hostname of your Redis server (default: `localhost`).
*   `REDIS_PORT`: Port of your Redis server (default: `6379`).
*   `REDIS_NOTIFICATION_CHANNEL`: The Redis channel to publish messages to (default: `system_notifications`).

The service attempts to connect to Redis on startup. If the connection fails, publishing will be skipped.
