# Google Cloud Setup for Gmail API

This guide will walk you through setting up Google Cloud credentials for Gmail API access.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "NEW PROJECT"
4. Enter project name: `gmail-chat-app`
5. Click "CREATE"

## Step 2: Enable Gmail API

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "ENABLE"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "CREATE CREDENTIALS" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: Select "External" (unless you have a workspace)
   - Click "CREATE"
   - Fill in required fields:
     - App name: `Gmail Chat App`
     - User support email: Your email
     - Developer contact: Your email
   - Click "SAVE AND CONTINUE"
   - Scopes: Click "ADD OR REMOVE SCOPES"
     - Add: `https://www.googleapis.com/auth/gmail.readonly`
     - Add: `https://www.googleapis.com/auth/gmail.modify` (for marking as read)
   - Click "SAVE AND CONTINUE"
   - Test users: Add your Gmail address
   - Click "SAVE AND CONTINUE"

4. Now create the OAuth client ID:
   - Application type: Select "Desktop app"
   - Name: `Gmail Chat Desktop Client`
   - Click "CREATE"

5. Download the credentials:
   - Click the download icon (⬇) next to your newly created OAuth client
   - Save the file as `credentials.json` in the `backend/` directory

## Step 4: Verify Setup

You should now have:
- ✅ Google Cloud project created
- ✅ Gmail API enabled
- ✅ OAuth 2.0 credentials downloaded as `backend/credentials.json`

## Important Notes

- Keep `credentials.json` SECRET - never commit it to version control
- The first time you run the app, you'll be prompted to authorize access via browser
- A `token.json` file will be created to store your access tokens
- Both files are already in `.gitignore`

## Next Steps

Proceed to installing the Gmail MCP server.
