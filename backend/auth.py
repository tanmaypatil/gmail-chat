"""
OAuth Authentication Module
Handles Google OAuth web flow and session management for multi-user access
"""

import os
import json
import secrets
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# OAuth scopes - includes email for user identification
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

# In-memory storage for sessions and user tokens
# Key: session_id -> Value: {'email': str, 'credentials': Credentials}
_sessions = {}

# Pending OAuth states (to prevent CSRF)
# Key: state -> Value: True
_pending_states = {}


def _load_client_config(redirect_uri):
    """
    Load OAuth client config, supporting both 'web' and 'installed' credential types.
    Converts 'installed' credentials to work with web OAuth flow.

    Returns:
        dict: Client config in the format expected by Flow.from_client_config
    """
    # Try credentials_web.json first, then fall back to credentials.json
    credentials_file = os.path.join(os.path.dirname(__file__), 'credentials_web.json')
    if not os.path.exists(credentials_file):
        credentials_file = os.path.join(os.path.dirname(__file__), 'credentials.json')

    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            "No credentials file found. Please download OAuth credentials "
            "from Google Cloud Console and save as backend/credentials.json"
        )

    with open(credentials_file, 'r') as f:
        creds_data = json.load(f)

    # If it's already a web credential, use it directly
    if 'web' in creds_data:
        return creds_data

    # Convert 'installed' credentials to 'web' format for the Flow
    if 'installed' in creds_data:
        installed = creds_data['installed']
        return {
            'web': {
                'client_id': installed['client_id'],
                'client_secret': installed['client_secret'],
                'auth_uri': installed['auth_uri'],
                'token_uri': installed['token_uri'],
                'redirect_uris': [redirect_uri]
            }
        }

    raise ValueError("Invalid credentials file format")


def create_oauth_flow(redirect_uri):
    """
    Create an OAuth flow for web-based authentication

    Args:
        redirect_uri: The callback URL after Google auth

    Returns:
        Tuple of (authorization_url, state)
    """
    client_config = _load_client_config(redirect_uri)

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

    # Generate authorization URL with state for CSRF protection
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    # Store state to verify callback
    _pending_states[state] = True

    return authorization_url, state


def complete_oauth_flow(authorization_response, redirect_uri):
    """
    Complete the OAuth flow after callback

    Args:
        authorization_response: The full callback URL with code and state
        redirect_uri: The same redirect URI used in create_oauth_flow

    Returns:
        Tuple of (session_id, user_email) on success, or raises exception
    """
    client_config = _load_client_config(redirect_uri)

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

    # Exchange authorization code for tokens
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    # Get user email from Google
    user_email = get_user_email(credentials)

    if not user_email:
        raise ValueError("Could not retrieve user email from Google")

    # Create session
    session_id = create_session(user_email, credentials)

    return session_id, user_email


def get_user_email(credentials):
    """
    Get user email from Google userinfo endpoint

    Args:
        credentials: Google OAuth credentials

    Returns:
        User email string or None
    """
    from googleapiclient.discovery import build

    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info.get('email')
    except Exception as e:
        print(f"Error getting user email: {e}")
        return None


def create_session(email, credentials):
    """
    Create a new session for an authenticated user

    Args:
        email: User's email address
        credentials: Google OAuth credentials

    Returns:
        Session ID string
    """
    session_id = secrets.token_urlsafe(32)

    _sessions[session_id] = {
        'email': email,
        'credentials': credentials
    }

    print(f"Created session for user: {email}")
    return session_id


def get_session(session_id):
    """
    Get session data by session ID

    Args:
        session_id: The session ID from cookie

    Returns:
        Session dict with 'email' and 'credentials', or None if not found
    """
    session = _sessions.get(session_id)

    if not session:
        return None

    # Check if credentials need refresh
    credentials = session['credentials']
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            session['credentials'] = credentials
        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            # Remove invalid session
            invalidate_session(session_id)
            return None

    return session


def get_user_credentials(session_id):
    """
    Get OAuth credentials for a session

    Args:
        session_id: The session ID from cookie

    Returns:
        Google Credentials object or None
    """
    session = get_session(session_id)
    if session:
        return session['credentials']
    return None


def get_user_email_from_session(session_id):
    """
    Get user email for a session

    Args:
        session_id: The session ID from cookie

    Returns:
        Email string or None
    """
    session = get_session(session_id)
    if session:
        return session['email']
    return None


def invalidate_session(session_id):
    """
    Remove a session (logout)

    Args:
        session_id: The session ID to remove
    """
    if session_id in _sessions:
        email = _sessions[session_id].get('email', 'unknown')
        del _sessions[session_id]
        print(f"Invalidated session for user: {email}")


def verify_state(state):
    """
    Verify OAuth state to prevent CSRF

    Args:
        state: The state parameter from callback

    Returns:
        True if valid, False otherwise
    """
    if state in _pending_states:
        del _pending_states[state]
        return True
    return False
