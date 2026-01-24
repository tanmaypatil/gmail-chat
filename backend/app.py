"""
Flask Backend for Gmail Chat Application
Integrates Claude API with Gmail Service
Supports multi-user OAuth authentication
"""

import os
import json
import secrets
from functools import wraps

# Allow OAuth over HTTP for local development (disable in production)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from flask import Flask, request, jsonify, send_file, redirect, make_response
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic
from gmail_service import GmailService
from auth import (
    create_oauth_flow,
    complete_oauth_flow,
    get_user_credentials,
    get_user_email_from_session,
    invalidate_session,
    verify_state
)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Generate a secret key for Flask sessions if not provided
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# Enable CORS with credentials support for session cookies
CORS(app,
     supports_credentials=True,
     origins=['http://localhost:8000', 'http://127.0.0.1:8000'],
     allow_headers=['Content-Type'],
     methods=['GET', 'POST', 'OPTIONS'])

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# OAuth redirect URI
OAUTH_REDIRECT_URI = 'http://localhost:5001/auth/callback'
FRONTEND_URL = 'http://localhost:8000'

# Define tools for Claude to use
TOOLS = [
    {
        "name": "search_emails",
        "description": "Search Gmail emails using Gmail search syntax. Supports queries like 'from:email@example.com', 'subject:keyword', 'has:attachment', 'after:2024/01/01', 'before:2024/12/31', 'newer_than:2d' (2 days), 'older_than:1m' (1 month), etc. Combine multiple criteria with spaces.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Gmail search query string"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_email_content",
        "description": "Get the full content of a specific email by its message ID. Returns complete email details including body, headers, and attachment info.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Gmail message ID"
                }
            },
            "required": ["message_id"]
        }
    },
    {
        "name": "list_attachments",
        "description": "List all attachments in a specific email. Returns attachment metadata including filename, size, type, and attachment IDs needed for downloading. ALWAYS use this tool when users ask about attachments or want to download files. The frontend will automatically show download buttons for the attachments.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Gmail message ID"
                }
            },
            "required": ["message_id"]
        }
    }
]


def require_auth(f):
    """Decorator to require authentication for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow OPTIONS requests through for CORS preflight
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        session_id = request.cookies.get('session_id')

        if not session_id:
            return jsonify({"error": "Not authenticated", "code": "AUTH_REQUIRED"}), 401

        credentials = get_user_credentials(session_id)
        if not credentials:
            response = make_response(jsonify({"error": "Session expired", "code": "SESSION_EXPIRED"}), 401)
            response.set_cookie('session_id', '', expires=0)
            return response

        # Store credentials in request context for use by endpoint
        request.gmail_credentials = credentials
        request.user_email = get_user_email_from_session(session_id)

        return f(*args, **kwargs)
    return decorated_function


def get_gmail_service():
    """Get GmailService for the current authenticated user"""
    return GmailService.from_credentials(request.gmail_credentials)


def execute_tool(gmail_service, tool_name, tool_input):
    """Execute a Gmail tool and return results"""

    if tool_name == "search_emails":
        query = tool_input["query"]
        max_results = tool_input.get("max_results", 10)
        results = gmail_service.search_emails(query, max_results)
        return results

    elif tool_name == "get_email_content":
        message_id = tool_input["message_id"]
        content = gmail_service.get_email_content(message_id)
        return content

    elif tool_name == "list_attachments":
        message_id = tool_input["message_id"]
        attachments = gmail_service.list_attachments(message_id)
        return attachments

    else:
        return {"error": f"Unknown tool: {tool_name}"}


# ============== Auth Endpoints ==============

@app.route('/auth/login', methods=['GET', 'OPTIONS'])
def auth_login():
    """Initiate OAuth flow - returns authorization URL"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        auth_url, state = create_oauth_flow(OAUTH_REDIRECT_URI)
        return jsonify({
            "auth_url": auth_url,
            "state": state
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Error initiating OAuth: {e}")
        return jsonify({"error": "Failed to initiate login"}), 500


@app.route('/auth/callback', methods=['GET'])
def auth_callback():
    """Handle OAuth callback from Google"""
    try:
        # Get the full callback URL - fix for HTTP vs HTTPS mismatch
        authorization_response = request.url
        # Force HTTP for local development (Google sometimes returns HTTPS in URL)
        if authorization_response.startswith('https://localhost'):
            authorization_response = authorization_response.replace('https://', 'http://', 1)

        print(f"Callback URL: {authorization_response}")

        # Verify state parameter
        state = request.args.get('state')
        print(f"State param: {state}")
        if not verify_state(state):
            print("State verification failed")
            return redirect(f"{FRONTEND_URL}/login.html?error=invalid_state")

        # Check for errors from Google
        error = request.args.get('error')
        if error:
            print(f"Google returned error: {error}")
            return redirect(f"{FRONTEND_URL}/login.html?error={error}")

        # Complete the OAuth flow
        session_id, user_email = complete_oauth_flow(authorization_response, OAUTH_REDIRECT_URI)

        # Create response with redirect to frontend
        response = make_response(redirect(f"{FRONTEND_URL}/index.html"))

        # Set session cookie
        response.set_cookie(
            'session_id',
            session_id,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax',
            max_age=86400 * 7  # 7 days
        )

        print(f"User logged in: {user_email}")
        return response

    except Exception as e:
        import traceback
        print(f"OAuth callback error: {e}")
        print(traceback.format_exc())
        return redirect(f"{FRONTEND_URL}/login.html?error=auth_failed")


@app.route('/auth/user', methods=['GET', 'OPTIONS'])
def auth_user():
    """Get current user info"""
    if request.method == 'OPTIONS':
        return '', 200

    session_id = request.cookies.get('session_id')

    if not session_id:
        return jsonify({"authenticated": False})

    email = get_user_email_from_session(session_id)

    if not email:
        response = make_response(jsonify({"authenticated": False}))
        response.set_cookie('session_id', '', expires=0)
        return response

    return jsonify({
        "authenticated": True,
        "email": email
    })


@app.route('/auth/logout', methods=['POST', 'OPTIONS'])
def auth_logout():
    """Logout - invalidate session"""
    if request.method == 'OPTIONS':
        return '', 200

    session_id = request.cookies.get('session_id')

    if session_id:
        invalidate_session(session_id)

    response = make_response(jsonify({"success": True}))
    response.set_cookie('session_id', '', expires=0)

    return response


# ============== API Endpoints ==============

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
@require_auth
def chat():
    """
    Main chat endpoint
    Accepts user queries and returns Claude's response with Gmail data
    """
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Get Gmail service for current user
        gmail_service = get_gmail_service()

        # Initialize conversation with Claude
        messages = [{"role": "user", "content": user_message}]

        # Track all attachments found during the conversation
        all_attachments = []

        # Agentic loop: Keep calling Claude until it returns a final response
        while True:
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                tools=TOOLS,
                messages=messages
            )

            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Extract tool use blocks
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        print(f"Claude is using tool: {tool_name}")
                        print(f"Tool input: {json.dumps(tool_input, indent=2)}")

                        # Execute the tool
                        result = execute_tool(gmail_service, tool_name, tool_input)

                        # If listing attachments, collect them for the frontend
                        if tool_name == "list_attachments" and isinstance(result, list):
                            for att in result:
                                all_attachments.append({
                                    "filename": att["filename"],
                                    "message_id": tool_input["message_id"],
                                    "attachment_id": att["attachmentId"],
                                    "mimeType": att["mimeType"],
                                    "size": att["size"]
                                })

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result)
                        })

                # Add assistant's response and tool results to conversation
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            elif response.stop_reason == "end_turn":
                # Claude has finished - extract final text response
                final_response = ""

                for block in response.content:
                    if hasattr(block, "text"):
                        final_response += block.text

                return jsonify({
                    "response": final_response,
                    "attachments": all_attachments
                })

            else:
                # Unexpected stop reason
                return jsonify({
                    "error": f"Unexpected stop reason: {response.stop_reason}"
                }), 500

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/download-attachment', methods=['POST', 'OPTIONS'])
@require_auth
def download_attachment():
    """
    Download an attachment from Gmail
    """
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json
        message_id = data.get('message_id')
        attachment_id = data.get('attachment_id')
        filename = data.get('filename')

        if not all([message_id, attachment_id, filename]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Get Gmail service for current user
        gmail_service = get_gmail_service()

        # Download attachment
        file_path = gmail_service.download_attachment(message_id, attachment_id, filename)

        if file_path and os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({"error": "Failed to download attachment"}), 500

    except Exception as e:
        print(f"Error downloading attachment: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({"status": "ok", "service": "gmail-chat-backend", "version": "1.0.0"})


if __name__ == '__main__':
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please create a .env file with your API key")
        exit(1)

    print("Starting Gmail Chat Backend (Multi-User Mode)...")
    print("Claude API connected")
    print("Server running on http://localhost:5001")
    print("")
    print("IMPORTANT: Ensure your Google Cloud OAuth client has this redirect URI:")
    print("  http://localhost:5001/auth/callback")
    print("")
    print("Frontend: http://localhost:8000/login.html")

    app.run(debug=True, port=5001)
