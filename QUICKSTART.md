# Quick Start Guide

Get your Gmail Chat app running in 10 minutes!

## Step 1: Google Cloud Setup (5 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: `gmail-chat-app`
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search "Gmail API" and click "Enable"
4. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "CREATE CREDENTIALS" > "OAuth client ID"
   - Configure consent screen if prompted (use External, add your email as test user)
   - Create Desktop app credentials
   - Download as `credentials.json`
5. Move `credentials.json` to `backend/` folder

## Step 2: Get Anthropic API Key (2 minutes)

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Go to "API Keys"
4. Create a new key
5. Copy the key (starts with `sk-ant-...`)

## Step 3: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "ANTHROPIC_API_KEY=your_actual_key_here" > .env

# Start the backend
python app.py
```

First run will open a browser for Gmail authorization. Authorize the app.

## Step 4: Frontend Setup (1 minute)

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Start simple HTTP server
python -m http.server 8000
```

Open browser to: `http://localhost:8000`

## Step 5: Try It Out!

Type in the chat:
- "Find emails from yesterday"
- "Search for emails with attachments"
- "What emails did I get from [someone's name]?"

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you created `.env` file in `backend/` directory
- Check that the key starts with `sk-ant-`

**"credentials.json not found"**
- Download from Google Cloud Console
- Place in `backend/` directory (same folder as `app.py`)

**"CORS error in browser"**
- Make sure backend is running on port 5000
- Access frontend via `http://localhost:8000` (not file://)

**"Failed to connect to backend"**
- Check that `python app.py` is running
- Backend should show: "Running on http://localhost:5000"

## Next Steps

Read the full [README.md](README.md) for:
- Advanced Gmail search syntax
- API documentation
- Architecture details
- Security best practices

## Example Queries to Try

1. "Find all emails from last week with attachments"
2. "Search for emails about invoices"
3. "Get emails from john@example.com from last month"
4. "Find emails with subject containing 'meeting'"
5. "Show me unread emails from today"

Enjoy your AI-powered Gmail assistant!
