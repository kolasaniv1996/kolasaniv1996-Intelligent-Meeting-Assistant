# Auth Service
Handles user authentication, authorization, and session management. This service will integrate with Google OAuth for sign-up and sign-in, and will be responsible for managing user profiles and issuing access tokens.

## Setup and Running

This service uses Python with Flask.

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
    Then, edit the `.env` file to include your actual Google Client ID, Client Secret, and Redirect URI. You will get these from the Google Cloud Console when you set up an OAuth 2.0 client.
    **Important**: The `GOOGLE_REDIRECT_URI` in your `.env` file must exactly match one of the "Authorized redirect URIs" you configure in your Google Cloud OAuth 2.0 client credentials. For local development, `http://localhost:5000/auth/google/callback` is common.

4.  **Run the Flask application:**
    ```bash
    flask run
    ```
    Or, if you want to run it directly using `python app.py` as configured with `FLASK_APP=app.py`:
    ```bash
    python app.py
    ```
    The service will typically be available at `http://localhost:5000`.

## Endpoints

*   `/`: Welcome page, shows login status.
*   `/auth/google`: Initiates the Google OAuth login flow.
*   `/auth/google/callback`: Handles the callback from Google after authentication.
*   `/auth/logout`: Clears the session and logs the user out of this application.
*   `/auth/profile`: (Protected) Displays some user information if logged in.

## Neo4j Integration (User and Agent Data)

This service can connect to a Neo4j graph database to store and manage relationships between users and their AI agents. This is a conceptual integration to demonstrate how graph data might be managed.

### Configuration for Neo4j

Ensure the following environment variables are set in your `.env` file for this service to enable Neo4j integration:

*   `NEO4J_URI`: The Bolt URI for your Neo4j instance (e.g., `bolt://localhost:7687`).
*   `NEO4J_USER`: The username for Neo4j (e.g., `neo4j`).
*   `NEO4J_PASSWORD`: The password for the Neo4j user.

### Functionality

*   On successful user authentication (via Google OAuth callback), the service attempts to:
    *   Create or update a `User` node in Neo4j with the user's email, name, and Google ID.
    *   Create or update an `Agent` node (e.g., `PRIMARY_PERSONAL` type) associated with that user.
    *   Establish a `HAS_AGENT` relationship between the `User` and `Agent` nodes.
*   This functionality is primarily within the `assign_or_verify_agent` function.
*   If Neo4j is not configured or unavailable, these steps are skipped, and the service logs a warning.

This helps in building a graph of users and agents, which can be extended later for more complex relationship mapping (e.g., agent-to-project, agent-to-agent).
