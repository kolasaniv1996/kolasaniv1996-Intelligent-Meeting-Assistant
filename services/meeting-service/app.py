import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests # To potentially call integration-service
import redis # Added for Redis
import json  # Added for serializing data for Redis

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "a_default_meeting_secret_key")

INTEGRATION_SERVICE_URL = os.environ.get("INTEGRATION_SERVICE_URL")

# --- Redis Configuration for Publishing ---
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_NOTIFICATION_CHANNEL = os.environ.get("REDIS_NOTIFICATION_CHANNEL", "system_notifications")

def get_redis_client():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        r.ping()
        print(f"MEETING_SERVICE: Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT} for publishing.")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"MEETING_SERVICE: Error connecting to Redis for publishing: {e}")
        return None

# Get a Redis client instance when the app starts.
# In a production Flask app, you might manage this connection differently (e.g., per request or with a connection pool).
redis_publisher = get_redis_client()

@app.route('/')
def index():
    return "Meeting Service: Manages meeting attendance and participation logic."

def get_calendar_events_from_integration_service(access_token):
    '''
    Helper function to fetch calendar events from the integration-service.
    '''
    if not INTEGRATION_SERVICE_URL:
        return {"error": "INTEGRATION_SERVICE_URL not configured."}, None

    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{INTEGRATION_SERVICE_URL}/calendar/events", headers=headers)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json(), None
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error occurred while fetching events: {http_err} - {response.text}"
        print(error_msg)
        return {"error": error_msg, "status_code": response.status_code if hasattr(response, 'status_code') else 500}, None
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Request error occurred while fetching events: {req_err}"
        print(error_msg)
        return {"error": error_msg}, None


@app.route('/meetings/process-upcoming', methods=['POST'])
def process_upcoming_meetings():
    '''
    Placeholder endpoint to process upcoming meetings for a user.
    It would fetch events and then decide which ones the agent should "attend".
    '''
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid Authorization Bearer token"}), 401

    access_token = auth_header.split('Bearer ')[1]

    # 1. Fetch calendar events (using the helper function)
    events_data, error = get_calendar_events_from_integration_service(access_token)

    if error or not events_data or "error" in events_data:
        status_code = events_data.get("status_code", 500) if isinstance(events_data, dict) else 500
        error_details = events_data.get("error", "Unknown error") if isinstance(events_data, dict) else "Service communication error"
        return jsonify({"error": "Could not retrieve calendar events from integration service.", "details": error_details}), status_code

    upcoming_events = events_data.get('events', [])
    if not upcoming_events:
        return jsonify({"message": "No upcoming events to process."}), 200

    # 2. Placeholder for "Automated Meeting Attendance" logic
    processed_meetings = []
    for event in upcoming_events:
        summary = event.get('summary', 'No Title')
        start_time = event.get('start')
        meeting_id = event.get('id')

        agent_action = "MONITOR"

        print(f"MEETING_PROCESSING: Event '{summary}' (ID: {meeting_id}) at {start_time}. Agent action: {agent_action}")

        processed_meetings.append({
            "id": meeting_id,
            "summary": summary,
            "start_time": start_time,
            "agent_decision": agent_action,
            "details": "Placeholder: Agent will monitor this meeting."
        })


    # Publish an event to Redis after processing
    if redis_publisher and processed_meetings:
        try:
            # Example: publish a summary message for all processed meetings
            # Or publish individual messages per meeting
            message_payload = {
                "event_type": "MEETINGS_PROCESSED_SUMMARY",
                "service_origin": "meeting-service",
                "user_token_hint": access_token[:10] + "...", # For context, not the full token
                "num_meetings_processed": len(processed_meetings),
                "first_meeting_summary": processed_meetings[0].get("summary") if processed_meetings else None
            }
            redis_publisher.publish(REDIS_NOTIFICATION_CHANNEL, json.dumps(message_payload))
            print(f"MEETING_SERVICE: Published 'MEETINGS_PROCESSED_SUMMARY' event to Redis channel '{REDIS_NOTIFICATION_CHANNEL}'.")
        except redis.exceptions.RedisError as e:
            print(f"MEETING_SERVICE: Error publishing to Redis: {e}")
        except Exception as e:
            print(f"MEETING_SERVICE: Generic error during Redis publish: {e}")

    return jsonify({
        "message": "Upcoming meetings processed for agent attendance (placeholder).",
        "processed_meetings": processed_meetings
    }), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
