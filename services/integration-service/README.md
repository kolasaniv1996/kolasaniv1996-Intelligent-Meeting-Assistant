# Integration Service
Manages connections and data synchronization with third-party productivity tools like Jira, Confluence, and calendar platforms. It acts as a bridge between the AI Work Buddy and external systems.

## Setup and Running

This service uses Python with Flask to integrate with external services like Google Calendar.

1.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables (optional for this service's current state):**
    Copy `.env.sample` to a new file named `.env` if you need to set any specific environment variables like `FLASK_APP` or `FLASK_ENV` (though the app.py has defaults).
    ```bash
    cp .env.sample .env
    ```
    Currently, this service doesn't require specific API keys in its `.env` for calendar access as it expects a Bearer token to be provided in requests. However, ensure your Google Cloud project (the one associated with the OAuth client ID used in `auth-service`) has the "Google Calendar API" enabled.

4.  **Run the Flask application:**
    ```bash
    flask run --port=5001
    ```
    Or, if you want to run it directly using `python app.py`:
    ```bash
    python app.py
    ```
    The service will typically be available at `http://localhost:5001`.

## Endpoints

*   `/`: Basic info message for the service.
*   `/calendar/events` (GET): Retrieves upcoming events from the user's primary Google Calendar.
    *   **Required Header**: `Authorization: Bearer <YOUR_ACCESS_TOKEN>`
    *   The access token must have the necessary Google Calendar API scopes (e.g., `https://www.googleapis.com/auth/calendar.readonly` or `https://www.googleapis.com/auth/calendar.events.readonly`). This token would typically be obtained via the `auth-service` after user consent.

## Important Note on OAuth Scopes:

For this service to access Google Calendar data, the OAuth token provided in the `Authorization` header must have been granted with Google Calendar scopes. When setting up the OAuth consent screen and client in `auth-service` (or a similar OAuth provider), you would need to include scopes like:
*   `https://www.googleapis.com/auth/calendar.readonly` (for reading events)
*   `https://www.googleapis.com/auth/calendar.events.readonly` (more specific for reading events)

If the `auth-service` is responsible for generating these tokens, its OAuth flow would need to request these scopes from the user.

## Jira Integration

This service can connect to Jira to read project and issue data.

### Configuration for Jira

Ensure the following environment variables are set in your `.env` file for the `integration-service`:

*   `JIRA_SERVER_URL`: The URL of your Jira Cloud instance (e.g., `https://your-domain.atlassian.net`).
*   `JIRA_USER_EMAIL`: The email address associated with your Atlassian account.
*   `JIRA_API_TOKEN`: Your Jira API token. You can generate this from your Atlassian account settings under "Security" > "API token".

### Jira API Endpoints

*   `/jira/projects` (GET): Lists all projects accessible by the configured Jira user.
    *   **Authentication**: Uses the Jira credentials configured in the service's environment. No separate Bearer token is needed for these specific Jira routes if the service is configured.
*   `/jira/issues/<project_key>` (GET): Lists issues for a given Jira project key.
    *   Example: `/jira/issues/KAN`
    *   Query Parameters:
        *   `max_results` (optional, default: 50): Maximum number of issues to return.
    *   **Authentication**: Uses the Jira credentials configured in the service's environment.

## Confluence Integration

This service can connect to Confluence to read space and page data.

### Configuration for Confluence

Ensure the following environment variables are set in your `.env` file for the `integration-service`:

*   `CONFLUENCE_SERVER_URL`: The URL of your Confluence Cloud instance (e.g., `https://your-domain.atlassian.net/wiki`).
*   `CONFLUENCE_USER_EMAIL`: The email address associated with your Atlassian account.
*   `CONFLUENCE_API_TOKEN`: Your Confluence API token. You can generate this from your Atlassian account settings under "Security" > "API token".

### Confluence API Endpoints

*   `/confluence/spaces` (GET): Lists all spaces accessible by the configured Confluence user.
    *   Query Parameters:
        *   `limit` (optional, default: 50): Maximum number of spaces to return. (Note: The app.py currently hardcodes limit for spaces, this is a documentation note for future enhancement)
    *   **Authentication**: Uses the Confluence credentials configured in the service's environment.
*   `/confluence/pages/<space_key>` (GET): Lists pages within a given Confluence space key.
    *   Example: `/confluence/pages/MYSPACE`
    *   Query Parameters:
        *   `limit` (optional, default: 25): Maximum number of pages to return.
    *   **Authentication**: Uses the Confluence credentials configured in the service's environment.
