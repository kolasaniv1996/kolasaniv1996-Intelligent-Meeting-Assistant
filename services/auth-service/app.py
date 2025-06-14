import os
from flask import Flask, redirect, url_for, session, request, jsonify
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from neo4j import GraphDatabase, exceptions as neo4j_exceptions
# Make sure 'os' and 'json' (if needed for attributes) are also imported

load_dotenv()

# --- Neo4j Configuration ---
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD") # Ensure this is set in actual .env

_neo4j_driver = None

def get_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver is None:
        try:
            if not NEO4J_PASSWORD:
                print("Warning: NEO4J_PASSWORD is not set. Neo4j connection will likely fail.")
            _neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            # Verify connection (optional, but good for early feedback)
            with _neo4j_driver.session() as session:
                session.run("RETURN 1")
            print("Successfully connected to Neo4j.")
        except neo4j_exceptions.AuthError as e:
            print(f"Neo4j Authentication Error: {e}. Check credentials in .env file.")
            _neo4j_driver = None # Reset on failure
        except neo4j_exceptions.ServiceUnavailable as e:
            print(f"Neo4j Service Unavailable: {e}. Ensure Neo4j is running at {NEO4J_URI}.")
            _neo4j_driver = None # Reset on failure
        except Exception as e:
            print(f"An unexpected error occurred while connecting to Neo4j: {e}")
            _neo4j_driver = None
    return _neo4j_driver

# Attempt to initialize driver on startup (optional)
# get_neo4j_driver()

def close_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver:
        _neo4j_driver.close()
        _neo4j_driver = None
        print("Neo4j driver closed.")

# Consider adding app.teardown_appcontext(close_neo4j_driver) if managing driver per app context

def assign_or_verify_agent(user_email, user_name, user_google_id): # Added user_google_id
    # Placeholder for agent assignment logic
    print(f"AGENT_ASSIGNMENT: Ensuring agent exists for user: {user_email} (Name: {user_name})")
    agent_id = f"agent_for_{user_email.split('@')[0]}" # Dummy agent ID

    driver = get_neo4j_driver()
    if driver:
        with driver.session(database="neo4j") as session: # Specify database if not default
            try:
                # Create or Merge User Node
                user_node_cypher = (
                    "MERGE (u:User {email: $email}) "
                    "ON CREATE SET u.name = $name, u.google_id = $google_id, u.created_at = timestamp() "
                    "ON MATCH SET u.name = $name, u.last_seen = timestamp() " # Update name if changed
                    "RETURN u"
                )
                session.run(user_node_cypher, email=user_email, name=user_name, google_id=user_google_id)
                print(f"Neo4j: Ensured User node exists for {user_email}")

                # Create or Merge Agent Node and Relationship
                # Using the conceptual schema from agent_directory_schema.md
                agent_node_cypher = (
                    "MATCH (u:User {email: $user_email}) "
                    "MERGE (a:Agent {agent_id: $agent_id}) "
                    "ON CREATE SET a.user_id = u.email, a.agent_type = 'PRIMARY_PERSONAL', "
                    "              a.status = 'ACTIVE', a.display_name = $display_name, "
                    "              a.capabilities = ['CALENDAR_MANAGEMENT', 'JIRA_READER', 'CONFLUENCE_READER'], "
                    "              a.created_at = timestamp() "
                    "MERGE (u)-[r:HAS_AGENT]->(a) "
                    "ON CREATE SET r.assignment_date = timestamp() "
                    "RETURN a, r"
                )
                display_name_for_agent = f"{user_name}'s Primary Agent"
                session.run(agent_node_cypher, user_email=user_email, agent_id=agent_id, display_name=display_name_for_agent)
                print(f"Neo4j: Ensured Agent node '{agent_id}' exists and is related to User '{user_email}'.")

            except neo4j_exceptions.Neo4jError as e:
                print(f"Neo4j Error during agent/user creation or linking: {e}")
            except Exception as e:
                print(f"Generic error during Neo4j operations in assign_or_verify_agent: {e}")
    else:
        print("Neo4j driver not available. Skipping graph database operations for agent assignment.")

    return agent_id

def setup_initial_personalization(user_email, agent_id):
    # Placeholder for initial personalization setup
    # In a real system, this would:
    # 1. Check if personalization settings exist.
    # 2. If not, create default settings (e.g., communication style, default project).
    # 3. Store these settings in a database, associated with the user/agent.
    print(f"PERSONALIZATION: Setting up initial preferences for user: {user_email} with agent_id: {agent_id}")
    # For now, just return a dummy personalization object
    return {"communication_style": "neutral", "priority_areas": ["general"]}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# --- OAuth Configuration ---
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")

# OAuth 2 client setup
# Note: In a real app, ensure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set.
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("Warning: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is not set. OAuth will not function.")

# Authorization base URL and token URL
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid", # Required for OIDC
    "https://www.googleapis.com/auth/calendar.events.readonly" # Scope for reading calendar events
]

@app.route('/')
def index():
    user_email = session.get('user_email')
    if user_email:
        return f'Hello, {user_email}! <a href="/auth/logout">Logout</a>'
    return 'Welcome! <a href="/auth/google">Login with Google</a>'

@app.route('/auth/google')
def google_login():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REDIRECT_URI:
        return "OAuth credentials not configured.", 500

    google = OAuth2Session(GOOGLE_CLIENT_ID, scope=SCOPES, redirect_uri=GOOGLE_REDIRECT_URI)
    authorization_url, state = google.authorization_url(AUTHORIZATION_BASE_URL, access_type="offline", prompt="select_account")
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/auth/google/callback')
def google_callback():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REDIRECT_URI:
        return "OAuth credentials not configured.", 500

    # Ensure state matches to prevent CSRF
    if request.args.get('state') != session.get('oauth_state'):
        return 'State mismatch, possible CSRF attack.', 400

    google = OAuth2Session(GOOGLE_CLIENT_ID, state=session['oauth_state'], redirect_uri=GOOGLE_REDIRECT_URI)

    try:
        # Exchange authorization code for tokens
        token = google.fetch_token(TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET, authorization_response=request.url)
        session['oauth_token'] = token # Store the token in session (consider a more secure storage for production)

        # Fetch user info
        user_info_response = google.get(USER_INFO_URL)
        if user_info_response.ok:
            user_info = user_info_response.json()
            session['user_email'] = user_info.get('email')
            session['user_name'] = user_info.get('name')
                user_google_id = user_info.get('sub') # Google's unique ID for the user

                # Assign or verify agent for the user
                # agent_id = assign_or_verify_agent(user_email, user_name) # Old call
                agent_id = assign_or_verify_agent(session['user_email'], session['user_name'], user_google_id) # New call
                session['agent_id'] = agent_id
                print(f"User {session['user_email']} assigned agent_id: {agent_id}") # Server-side log

                # Setup initial personalization
                personalization_settings = setup_initial_personalization(session['user_email'], agent_id)
                session['personalization_settings'] = personalization_settings
                print(f"User {session['user_email']} initial personalization: {personalization_settings}") # Server-side log

            # Here you would typically find or create a user in your database
            # For now, just store in session
            print(f"User authenticated: {user_info.get('email')}") # Server-side log
        else:
            return f"Failed to fetch user info: {user_info_response.text}", 500

    except Exception as e:
        print(f"Error during token fetch or user info: {e}")
        return f"Authentication failed: {e}", 500

    return redirect(url_for('index'))

@app.route('/auth/logout')
def logout():
    session.clear() # Clear Flask session
    # Note: This doesn't log the user out of Google itself.
    # For a full logout, you might redirect to Google's logout URL or manage tokens more carefully.
    return redirect(url_for('index'))

@app.route('/auth/profile')
def profile():
    if 'oauth_token' not in session or 'user_email' not in session:
        return redirect(url_for('google_login'))

    # For demonstration, show some user info
    # In a real app, you might refresh the token if it's expired
    # and fetch more comprehensive profile data.
    return jsonify({
        "email": session.get('user_email'),
        "name": session.get('user_name'),
        "agent_id": session.get('agent_id'),
        "personalization_settings": session.get('personalization_settings'),
        "token_expires_at": session.get('oauth_token', {}).get('expires_at')
    })

if __name__ == "__main__":
    # Make sure to run with HTTPS in production if not behind a proxy that handles SSL
    # For local development, HTTP is usually fine.
    # The host '0.0.0.0' makes it accessible from other devices on the same network.
    app.run(host='0.0.0.0', port=5000, debug=True)
