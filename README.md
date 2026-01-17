# Gmail Chat - AI-Powered Gmail Assistant

Query your Gmail using natural language with Claude AI. Search emails, extract information, and download attachments through a simple chat interface.

## Features

- Natural language queries to search Gmail
- Extract specific information from emails
- List and download email attachments
- Simple HTML/JavaScript frontend
- Python backend with Claude API integration
- Direct Gmail API integration (no separate MCP server needed)

## Architecture

```
Frontend (HTML/JS) → Backend (Flask/Python) → Claude API + Gmail API
```

The backend acts as both the API server and MCP-like service, providing Gmail tools to Claude.

## Prerequisites

- Python 3.8+
- Google Cloud account
- Anthropic API key
- Gmail account

## Setup Instructions

### 1. Google Cloud Setup

Follow the detailed guide in `docs/SETUP_GOOGLE_CLOUD.md` to:
- Create a Google Cloud project
- Enable Gmail API
- Create OAuth 2.0 credentials
- Download `credentials.json`

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Anthropic API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Place your credentials.json in the backend directory
# (downloaded from Google Cloud Console)

# Run the backend
python app.py
```

On first run, you'll be prompted to authorize the app via browser. This creates `token.json` for future use.

### 3. Frontend Setup

```bash
cd frontend

# Open in browser (simple HTTP server)
python -m http.server 8000
```

Or simply open `frontend/index.html` in your browser.

## Usage

### Example Queries

1. "What is the aadhar number of Tanmay Patil?"
2. "Search and summarize emails from yesterday"
3. "Find emails with attachments from last week"
4. "Show me emails about invoices"
5. "Get all emails from john@example.com"

### Gmail Search Syntax

The assistant understands Gmail's search operators:

- `from:email@example.com` - Emails from specific sender
- `to:email@example.com` - Emails to specific recipient
- `subject:keyword` - Subject contains keyword
- `has:attachment` - Has attachments
- `after:2024/01/01` - After date
- `before:2024/12/31` - Before date
- `newer_than:2d` - Newer than 2 days
- `older_than:1m` - Older than 1 month

### Downloading Attachments

When emails with attachments are found, the assistant will show download buttons. Click to download directly to your browser's download folder.

## Project Structure

```
gmail-chat/
├── backend/
│   ├── app.py              # Flask backend with Claude integration
│   ├── gmail_service.py    # Gmail API service
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   ├── credentials.json    # Google OAuth credentials (not in git)
│   └── token.json          # OAuth token (auto-generated, not in git)
├── frontend/
│   ├── index.html          # Main HTML page
│   ├── styles.css          # Styles
│   └── app.js              # Frontend JavaScript
├── docs/
│   ├── SETUP_GOOGLE_CLOUD.md
│   └── SETUP_MCP_SERVER.md
└── README.md
```

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Store `ANTHROPIC_API_KEY` in `.env` file only
- OAuth tokens are stored locally and refresh automatically
- The app only requests read-only Gmail access

## Troubleshooting

### Backend won't start
- Check that `ANTHROPIC_API_KEY` is set in `.env`
- Ensure `credentials.json` exists in backend directory
- Verify Python dependencies are installed

### Authentication fails
- Delete `token.json` and re-authenticate
- Check OAuth consent screen configuration in Google Cloud
- Ensure your email is added as a test user

### CORS errors
- Backend must be running on `http://localhost:5000`
- Frontend should be served via HTTP server (not file://)

### No results found
- Check Gmail search syntax
- Verify OAuth scopes include `gmail.readonly`
- Try simpler queries first

## API Endpoints

### POST /api/chat
Send a natural language query

**Request:**
```json
{
  "message": "Find emails from yesterday"
}
```

**Response:**
```json
{
  "response": "I found 5 emails from yesterday...",
  "attachments": []
}
```

### POST /api/download-attachment
Download an email attachment

**Request:**
```json
{
  "message_id": "...",
  "attachment_id": "...",
  "filename": "document.pdf"
}
```

**Response:** Binary file download

### GET /api/health
Health check

**Response:**
```json
{
  "status": "ok",
  "service": "gmail-chat-backend"
}
```

## How It Works

1. User enters a natural language query in the chat interface
2. Frontend sends query to Python backend
3. Backend calls Claude API with Gmail tools defined
4. Claude decides which Gmail tools to use based on the query
5. Backend executes Gmail API calls and returns results to Claude
6. Claude synthesizes a natural language response
7. Response is displayed to the user with any attachments

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask, Flask-CORS
- **AI**: Claude 3.5 Sonnet (Anthropic)
- **APIs**: Gmail API, Anthropic API
- **Auth**: Google OAuth 2.0

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please open an issue or PR.

## Support

For issues or questions, please open a GitHub issue.