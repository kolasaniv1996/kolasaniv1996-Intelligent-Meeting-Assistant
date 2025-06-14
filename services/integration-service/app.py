import os
from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import datetime
from jira import JIRA, JIRAError
from atlassian import Confluence
# JIRAError is already imported, Confluence might have its own error types but
# the library often raises generic requests.exceptions.HTTPError for API issues.

load_dotenv()

app = Flask(__name__)
# --- Jira Configuration ---
JIRA_SERVER_URL = os.environ.get("JIRA_SERVER_URL")
JIRA_USER_EMAIL = os.environ.get("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN")

def get_jira_client():
    if not JIRA_SERVER_URL or not JIRA_USER_EMAIL or not JIRA_API_TOKEN:
        raise ValueError("Jira server URL, user email, or API token not configured in environment.")

    # Basic authentication with email and API token for Jira Cloud
    options = {'server': JIRA_SERVER_URL}
    jira_client = JIRA(options, basic_auth=(JIRA_USER_EMAIL, JIRA_API_TOKEN))
    return jira_client

# --- Confluence Configuration ---
CONFLUENCE_SERVER_URL = os.environ.get("CONFLUENCE_SERVER_URL")
CONFLUENCE_USER_EMAIL = os.environ.get("CONFLUENCE_USER_EMAIL")
CONFLUENCE_API_TOKEN = os.environ.get("CONFLUENCE_API_TOKEN")

def get_confluence_client():
    if not CONFLUENCE_SERVER_URL or not CONFLUENCE_USER_EMAIL or not CONFLUENCE_API_TOKEN:
        raise ValueError("Confluence server URL, user email, or API token not configured in environment.")

    confluence_client = Confluence(
        url=CONFLUENCE_SERVER_URL,
        username=CONFLUENCE_USER_EMAIL,
        password=CONFLUENCE_API_TOKEN, # The library uses 'password' for the API token
        cloud=True # Assuming Confluence Cloud
    )
    return confluence_client
# It's good practice to have a secret key for Flask, though not strictly used in this simple example
app.secret_key = os.environ.get("SECRET_KEY", "a_default_integration_secret_key")


# --- Google Calendar API Integration ---

@app.route('/')
def index():
    return "Integration Service: Connects to Google Calendar and other tools."

@app.route('/calendar/events', methods=['GET'])
def get_calendar_events():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid Authorization Bearer token"}), 401

    access_token = auth_header.split('Bearer ')[1]

    if not access_token:
        return jsonify({"error": "Access token is empty"}), 401

    creds = Credentials(token=access_token) # We are assuming the token has the necessary calendar scopes

    try:
        # Check if token is valid (optional, but good practice)
        # This can be done by calling Google's tokeninfo endpoint,
        # but for simplicity, we'll proceed directly.
        # If the token is invalid or expired, the API call will fail.

        service = build('calendar', 'v3', credentials=creds, static_discovery=False)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId='primary', # Use 'primary' for the user's main calendar
            timeMin=now,
            maxResults=10,        # Get the next 10 events
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return jsonify({"message": "No upcoming events found."}), 200

        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            formatted_events.append({
                "summary": event.get('summary', 'No Title'),
                "start": start,
                "id": event['id']
            })
        return jsonify({"events": formatted_events}), 200

    except HttpError as error:
        error_details = error.resp.reason
        if error.resp.status == 401:
            error_details = "Token is invalid or expired, or lacks calendar scope."
        elif error.resp.status == 403:
            error_details = "Calendar API not enabled or access forbidden."

        print(f"An API error occurred: {error}")
        print(f"Error details: {error_details}")
        return jsonify({"error": f"Google Calendar API error: {error_details}"}), error.resp.status
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    # The host '0.0.0.0' makes it accessible from other devices on the same network.
    app.run(host='0.0.0.0', port=5001, debug=True) # Running on a different port than auth-service


# --- Jira API Endpoints ---

@app.route('/jira/projects', methods=['GET'])
def list_jira_projects():
    try:
        jira = get_jira_client()
        projects = jira.projects()

        formatted_projects = []
        for project in projects:
            formatted_projects.append({
                "id": project.id,
                "key": project.key,
                "name": project.name
            })
        return jsonify({"projects": formatted_projects}), 200

    except ValueError as ve: # Handles missing Jira config
        return jsonify({"error": str(ve)}), 500
    except JIRAError as e:
        print(f"Jira API error: {e.text if hasattr(e, 'text') else e.status_code}")
        return jsonify({"error": f"Jira API error: {e.text if hasattr(e, 'text') else e.status_code}"}), e.status_code if hasattr(e, 'status_code') else 500
    except Exception as e:
        print(f"An unexpected error occurred with Jira: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# --- Confluence API Endpoints ---

@app.route('/confluence/spaces', methods=['GET'])
def list_confluence_spaces():
    try:
        confluence = get_confluence_client()
        # The atlassian-python-api for Confluence paginates by default (limit can be specified)
        spaces_generator = confluence.get_all_spaces(start=0, limit=50, expand=None)

        formatted_spaces = []
        # The generator might yield a dictionary with 'results' or just the list directly
        # Depending on the library version and exact call, inspect its structure.
        # Assuming 'results' key based on common patterns with this library.
        if 'results' in spaces_generator:
            for space in spaces_generator['results']:
                formatted_spaces.append({
                    "id": space['id'],
                    "key": space['key'],
                    "name": space['name'],
                    "type": space['type']
                })
        else: # Fallback if the structure is different (older versions might return list directly)
                for space in spaces_generator: # This might be the case if it's a direct list
                formatted_spaces.append({
                    "id": space['id'],
                    "key": space['key'],
                    "name": space['name'],
                    "type": space['type']
                })


        return jsonify({"spaces": formatted_spaces}), 200

    except ValueError as ve: # Handles missing Confluence config
        return jsonify({"error": str(ve)}), 500
    except requests.exceptions.HTTPError as e: # The Confluence lib often raises this
        error_message = f"Confluence API HTTP error: {e.response.status_code} - {e.response.text}"
        print(error_message)
        return jsonify({"error": error_message}), e.response.status_code
    except Exception as e:
        error_message = f"An unexpected error occurred with Confluence: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500

@app.route('/confluence/pages/<space_key>', methods=['GET'])
def list_confluence_pages(space_key):
    limit = request.args.get('limit', default=25, type=int)
    try:
        confluence = get_confluence_client()

        # First, verify the space exists to give a better error message
        if not confluence.space_exists(space_key):
            return jsonify({"error": f"Confluence space with key '{space_key}' not found or not accessible."}), 404

        pages_generator = confluence.get_all_pages_from_space(space_key, start=0, limit=limit, status=None, expand=None, content_type='page')

        formatted_pages = []
        # Similar to spaces, checking for 'results' key
        if isinstance(pages_generator, dict) and 'results' in pages_generator:
            page_list = pages_generator['results']
        elif isinstance(pages_generator, list):
            page_list = pages_generator
        else: # If it's an unexpected type or an empty generator that's not a list/dict
            page_list = list(pages_generator) # Attempt to convert if it's a generator object

        for page in page_list:
            formatted_pages.append({
                "id": page['id'],
                "title": page['title'],
                # "link": page['_links']['webui'] if '_links' in page and 'webui' in page['_links'] else None
                # Link format can vary, sometimes it's in metadata or needs construction.
                # For simplicity, keeping it basic.
            })
        return jsonify({"space_key": space_key, "pages": formatted_pages}), 200

    except ValueError as ve: # Handles missing Confluence config
        return jsonify({"error": str(ve)}), 500
    except requests.exceptions.HTTPError as e: # The Confluence lib often raises this
        error_message = f"Confluence API HTTP error: {e.response.status_code} - {e.response.text}"
        print(error_message)
        # Check if the error is specifically space not found, though space_exists should catch it
        if e.response.status_code == 404:
                return jsonify({"error": f"Confluence space '{space_key}' not found or access denied. Details: {e.response.text}"}), 404
        return jsonify({"error": error_message}), e.response.status_code
    except Exception as e:
        error_message = f"An unexpected error occurred with Confluence: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500
