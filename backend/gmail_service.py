"""
Gmail Service Module
Handles Gmail API operations
"""

import os
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes (kept for backwards compatibility with desktop flow)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailService:
    def __init__(self, credentials=None, credentials_file='credentials.json', token_file='token.json'):
        """
        Initialize Gmail service

        Args:
            credentials: Pre-authenticated Google credentials (for web OAuth flow)
            credentials_file: Path to credentials.json (for desktop flow, backwards compatible)
            token_file: Path to token.json (for desktop flow, backwards compatible)
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None

        if credentials:
            # Use provided credentials (web OAuth flow)
            self.service = build('gmail', 'v1', credentials=credentials)
            print("Gmail API initialized with provided credentials")
        else:
            # Backwards compatible: auto-authenticate with desktop flow
            self.authenticate()

    @classmethod
    def from_credentials(cls, credentials):
        """
        Create a GmailService instance from existing OAuth credentials

        Args:
            credentials: Google OAuth2 credentials object

        Returns:
            GmailService instance
        """
        return cls(credentials=credentials)

    def authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0 (desktop flow)"""
        creds = None

        # Check if token.json exists (previously authenticated)
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        print("Gmail API authenticated successfully (desktop flow)")

    def search_emails(self, query, max_results=10):
        """
        Search emails using Gmail search syntax

        Args:
            query: Gmail search query (e.g., "from:example@gmail.com subject:important")
            max_results: Maximum number of results to return

        Returns:
            List of email message objects with metadata
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return []

            # Fetch full message details for each result
            detailed_messages = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                detailed_messages.append(self._parse_message(msg))

            return detailed_messages

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def get_email_content(self, message_id):
        """
        Get full content of a specific email

        Args:
            message_id: Gmail message ID

        Returns:
            Parsed message object with full content
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            return self._parse_message(message)

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def list_attachments(self, message_id):
        """
        List all attachments in an email

        Args:
            message_id: Gmail message ID

        Returns:
            List of attachment metadata
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()

            attachments = []

            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part.get('filename') and part.get('body', {}).get('attachmentId'):
                        attachments.append({
                            'filename': part['filename'],
                            'mimeType': part['mimeType'],
                            'size': part['body'].get('size', 0),
                            'attachmentId': part['body']['attachmentId']
                        })

            return attachments

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def download_attachment(self, message_id, attachment_id, filename):
        """
        Download an attachment from an email

        Args:
            message_id: Gmail message ID
            attachment_id: Attachment ID
            filename: Desired filename for the downloaded file

        Returns:
            File path of downloaded attachment
        """
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()

            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

            # Save to downloads folder
            downloads_dir = os.path.join(os.path.dirname(__file__), 'downloads')
            os.makedirs(downloads_dir, exist_ok=True)

            file_path = os.path.join(downloads_dir, filename)

            with open(file_path, 'wb') as f:
                f.write(file_data)

            return file_path

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def _parse_message(self, message):
        """Parse Gmail message into a readable format"""
        headers = message['payload']['headers']

        # Extract common headers
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
        to = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Unknown')

        # Extract body
        body = self._get_message_body(message['payload'])

        # Check for attachments
        has_attachments = False
        attachment_count = 0
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    has_attachments = True
                    attachment_count += 1

        return {
            'id': message['id'],
            'threadId': message['threadId'],
            'subject': subject,
            'from': sender,
            'to': to,
            'date': date,
            'body': body,
            'snippet': message.get('snippet', ''),
            'hasAttachments': has_attachments,
            'attachmentCount': attachment_count
        }

    def _get_message_body(self, payload):
        """Extract message body from payload"""
        body = ""

        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

        return body


if __name__ == "__main__":
    # Test the Gmail service
    gmail = GmailService()

    # Search for recent emails
    print("Searching for recent emails...")
    results = gmail.search_emails("newer_than:1d", max_results=5)

    for msg in results:
        print(f"\nSubject: {msg['subject']}")
        print(f"From: {msg['from']}")
        print(f"Date: {msg['date']}")
        print(f"Has attachments: {msg['hasAttachments']}")
        print(f"Snippet: {msg['snippet'][:100]}...")
