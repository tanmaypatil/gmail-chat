"""
Flask Backend for Gmail Chat Application
Integrates Claude API with Gmail Service
"""

import os
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic
from gmail_service import GmailService

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, supports_credentials=False)

# Initialize services
gmail_service = GmailService()
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

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


def execute_tool(tool_name, tool_input):
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


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
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
                        result = execute_tool(tool_name, tool_input)

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
    return jsonify({"status": "ok", "service": "gmail-chat-backend"})


if __name__ == '__main__':
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please create a .env file with your API key")
        exit(1)

    print("Starting Gmail Chat Backend...")
    print("Gmail service initialized")
    print("Claude API connected")
    print("Server running on http://localhost:5001")

    app.run(debug=True, port=5001)
