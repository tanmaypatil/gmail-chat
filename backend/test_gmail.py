"""
Gmail API Test Script
Tests Gmail authentication and basic operations
"""

import os
import sys
from gmail_service import GmailService


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_authentication():
    """Test Gmail authentication"""
    print_section("Test 1: Authentication")

    try:
        # Check if credentials.json exists
        if not os.path.exists('credentials.json'):
            print("❌ FAILED: credentials.json not found")
            print("   Please download from Google Cloud Console")
            return None

        print("✓ credentials.json found")

        # Initialize Gmail service
        print("Authenticating with Gmail API...")
        gmail = GmailService()

        print("✓ Authentication successful!")

        # Check if token.json was created
        if os.path.exists('token.json'):
            print("✓ token.json created/updated")

        return gmail

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return None


def test_search_emails(gmail):
    """Test email search functionality"""
    print_section("Test 2: Search Emails")

    try:
        # Search for recent emails
        print("Searching for emails from the last 7 days...")
        results = gmail.search_emails("newer_than:7d", max_results=5)

        if results:
            print(f"✓ Found {len(results)} emails")
            print("\nRecent emails:")
            for i, msg in enumerate(results, 1):
                print(f"\n  [{i}] Subject: {msg['subject'][:60]}")
                print(f"      From: {msg['from']}")
                print(f"      Date: {msg['date']}")
                print(f"      Has attachments: {msg['hasAttachments']}")
            return results
        else:
            print("⚠ No emails found in the last 7 days")
            print("  This might be normal if your inbox is empty")
            return []

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return []


def test_get_email_content(gmail, messages):
    """Test getting full email content"""
    print_section("Test 3: Get Email Content")

    if not messages:
        print("⚠ Skipped: No messages to test")
        return

    try:
        message_id = messages[0]['id']
        print(f"Fetching full content of message: {message_id}")

        content = gmail.get_email_content(message_id)

        if content:
            print("✓ Successfully retrieved email content")
            print(f"\n  Subject: {content['subject']}")
            print(f"  From: {content['from']}")
            print(f"  To: {content['to']}")
            print(f"  Body preview: {content['body'][:100]}...")
            return content
        else:
            print("❌ FAILED: Could not retrieve email content")
            return None

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return None


def test_list_attachments(gmail):
    """Test listing attachments"""
    print_section("Test 4: List Attachments")

    try:
        print("Searching for emails with attachments...")
        results = gmail.search_emails("has:attachment", max_results=5)

        if results:
            print(f"✓ Found {len(results)} emails with attachments")

            for i, msg in enumerate(results, 1):
                print(f"\n  [{i}] {msg['subject'][:50]}")
                print(f"      Attachment count: {msg['attachmentCount']}")

                # List attachments for first email
                if i == 1:
                    attachments = gmail.list_attachments(msg['id'])
                    if attachments:
                        print(f"      Attachment details:")
                        for att in attachments:
                            size_kb = att['size'] / 1024
                            print(f"        - {att['filename']} ({size_kb:.1f} KB, {att['mimeType']})")
        else:
            print("⚠ No emails with attachments found")
            print("  This is normal if you don't have attachments")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")


def test_advanced_search(gmail):
    """Test advanced Gmail search queries"""
    print_section("Test 5: Advanced Search Queries")

    test_queries = [
        ("from:gmail.com", "Emails from Gmail"),
        ("is:unread", "Unread emails"),
        ("subject:test", "Emails with 'test' in subject"),
    ]

    for query, description in test_queries:
        try:
            print(f"\nTesting: {description} (query: '{query}')")
            results = gmail.search_emails(query, max_results=3)
            print(f"  ✓ Found {len(results)} results")
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")


def run_all_tests():
    """Run all Gmail API tests"""
    print("\n" + "🔧" * 30)
    print("Gmail API Test Suite")
    print("🔧" * 30)

    # Test 1: Authentication
    gmail = test_authentication()
    if not gmail:
        print("\n❌ Cannot proceed without authentication")
        return False

    # Test 2: Search emails
    messages = test_search_emails(gmail)

    # Test 3: Get email content
    test_get_email_content(gmail, messages)

    # Test 4: List attachments
    test_list_attachments(gmail)

    # Test 5: Advanced search
    test_advanced_search(gmail)

    # Summary
    print_section("Test Summary")
    print("✓ All basic tests completed!")
    print("\nYour Gmail API is configured and working correctly.")
    print("You can now proceed to test the full application.")

    return True


if __name__ == "__main__":
    # Change to backend directory if needed
    if not os.path.exists('credentials.json'):
        print("Looking for credentials.json...")
        if os.path.exists('backend/credentials.json'):
            os.chdir('backend')
            print("Changed to backend directory")

    success = run_all_tests()

    if success:
        print("\n" + "✨" * 30)
        print("Next steps:")
        print("1. Make sure you have ANTHROPIC_API_KEY in .env file")
        print("2. Run: python app.py")
        print("3. Open frontend in browser")
        print("✨" * 30 + "\n")
        sys.exit(0)
    else:
        print("\n⚠ Please fix the errors above before proceeding\n")
        sys.exit(1)
