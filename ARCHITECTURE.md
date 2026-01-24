# Gmail Chat - Architecture Overview

This document provides a comprehensive technical overview of the Gmail Chat application architecture.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Components](#components)
- [Data Flow](#data-flow)
- [Authentication Flow](#authentication-flow)
- [API Design](#api-design)
- [Infrastructure](#infrastructure)
- [Security Model](#security-model)
- [Technology Stack](#technology-stack)

---

## System Overview

Gmail Chat is an AI-powered email assistant that allows users to query their Gmail using natural language. The application uses Claude AI to interpret user queries and translate them into Gmail API operations.

**Key Capabilities:**
- Natural language email search
- Email content extraction and summarization
- Attachment listing and downloading
- Multi-user OAuth authentication

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GMAIL CHAT SYSTEM                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐      HTTPS       ┌─────────────────────────────────────────────┐
│              │ ───────────────► │                   NGINX                      │
│    USER      │                  │            (Reverse Proxy + SSL)             │
│   BROWSER    │ ◄─────────────── │              Port 80/443                     │
│              │                  └──────────────────┬──────────────────────────┘
└──────────────┘                                     │
                                                     │ Proxy Pass
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS LIGHTSAIL INSTANCE                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         APPLICATION LAYER                            │    │
│  │                                                                      │    │
│  │  ┌─────────────────────┐    ┌─────────────────────────────────────┐ │    │
│  │  │      FRONTEND       │    │             BACKEND                  │ │    │
│  │  │   (Static Files)    │    │         (Flask + Gunicorn)          │ │    │
│  │  │                     │    │                                      │ │    │
│  │  │  • index.html       │    │  ┌─────────────────────────────┐    │ │    │
│  │  │  • login.html       │    │  │         app.py              │    │ │    │
│  │  │  • app.js           │    │  │   • API Endpoints           │    │ │    │
│  │  │  • auth.js          │    │  │   • Tool Execution          │    │ │    │
│  │  │  • styles.css       │    │  │   • Session Management      │    │ │    │
│  │  │                     │    │  └─────────────────────────────┘    │ │    │
│  │  │                     │    │                 │                    │ │    │
│  │  │                     │    │  ┌──────────────┼──────────────┐    │ │    │
│  │  │                     │    │  │              │              │    │ │    │
│  │  │                     │    │  ▼              ▼              ▼    │ │    │
│  │  │                     │    │ auth.py   gmail_service.py   .env  │ │    │
│  │  └─────────────────────┘    └─────────────────────────────────────┘ │    │
│  │           │                                   │                      │    │
│  └───────────┼───────────────────────────────────┼──────────────────────┘    │
│              │                                   │                           │
└──────────────┼───────────────────────────────────┼───────────────────────────┘
               │                                   │
               │ HTTP API                          │ HTTPS API Calls
               │ Requests                          │
               ▼                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             EXTERNAL SERVICES                                 │
│                                                                               │
│  ┌─────────────────────────┐          ┌────────────────────────────────────┐ │
│  │      ANTHROPIC API      │          │           GOOGLE APIS              │ │
│  │                         │          │                                    │ │
│  │  • Claude Sonnet 4.5    │          │  ┌────────────┐  ┌──────────────┐ │ │
│  │  • Tool Use Support     │          │  │ Gmail API  │  │  OAuth 2.0   │ │ │
│  │  • Agentic Loop         │          │  │            │  │              │ │ │
│  │                         │          │  │ • Search   │  │ • Auth Flow  │ │ │
│  │                         │          │  │ • Read     │  │ • Token Mgmt │ │ │
│  │                         │          │  │ • Download │  │ • User Info  │ │ │
│  │                         │          │  └────────────┘  └──────────────┘ │ │
│  └─────────────────────────┘          └────────────────────────────────────┘ │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### Frontend

| File | Purpose |
|------|---------|
| `index.html` | Main chat interface |
| `login.html` | OAuth login page |
| `app.js` | Chat logic, API calls, attachment handling |
| `auth.js` | Authentication state management |
| `styles.css` | UI styling |

**Responsibilities:**
- Render chat interface
- Handle user input
- Display AI responses with markdown formatting
- Show attachment download buttons
- Manage authentication state

### Backend

| File | Purpose |
|------|---------|
| `app.py` | Flask application, API routes, Claude integration |
| `auth.py` | OAuth flow, session management |
| `gmail_service.py` | Gmail API wrapper |

#### app.py - Core Application

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py                                │
├─────────────────────────────────────────────────────────────┤
│  Auth Endpoints          │  API Endpoints                    │
│  • /auth/login           │  • /api/chat (POST)              │
│  • /auth/callback        │  • /api/download-attachment       │
│  • /auth/user            │  • /api/health                   │
│  • /auth/logout          │                                   │
├─────────────────────────────────────────────────────────────┤
│  Claude Tools (defined for AI to use):                      │
│  • search_emails    - Gmail search with query syntax        │
│  • get_email_content - Fetch full email by ID               │
│  • list_attachments - List attachments for an email         │
└─────────────────────────────────────────────────────────────┘
```

#### auth.py - Authentication Module

```
┌─────────────────────────────────────────────────────────────┐
│                        auth.py                               │
├─────────────────────────────────────────────────────────────┤
│  In-Memory Storage:                                          │
│  • _sessions{}     - session_id → {email, credentials}      │
│  • _pending_states{} - CSRF state tokens                    │
├─────────────────────────────────────────────────────────────┤
│  Functions:                                                  │
│  • create_oauth_flow()    - Initiate OAuth                  │
│  • complete_oauth_flow()  - Handle callback                 │
│  • get_user_credentials() - Retrieve session credentials    │
│  • invalidate_session()   - Logout                          │
│  • verify_state()         - CSRF protection                 │
└─────────────────────────────────────────────────────────────┘
```

#### gmail_service.py - Gmail API Wrapper

```
┌─────────────────────────────────────────────────────────────┐
│                    GmailService Class                        │
├─────────────────────────────────────────────────────────────┤
│  Methods:                                                    │
│  • search_emails(query, max_results)                        │
│  • get_email_content(message_id)                            │
│  • list_attachments(message_id)                             │
│  • download_attachment(message_id, attachment_id, filename) │
├─────────────────────────────────────────────────────────────┤
│  Internal:                                                   │
│  • _parse_message() - Convert Gmail API response            │
│  • _get_message_body() - Extract email body text            │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Chat Query Flow

```
┌──────────┐    1. User Query     ┌──────────┐    2. POST /api/chat    ┌──────────┐
│  User    │ ──────────────────►  │ Frontend │ ─────────────────────►  │ Backend  │
│ Browser  │                      │  app.js  │                         │  app.py  │
└──────────┘                      └──────────┘                         └────┬─────┘
                                                                             │
     ┌───────────────────────────────────────────────────────────────────────┘
     │
     │  3. Send message + tools
     ▼
┌──────────────┐                                              ┌──────────────────┐
│   Claude AI  │  4. Tool request (e.g., search_emails)       │                  │
│  (Anthropic) │ ────────────────────────────────────────────►│     Backend      │
│              │                                              │    (execute)     │
│              │  5. Tool results                             │                  │
│              │ ◄────────────────────────────────────────────│                  │
└──────────────┘                                              └────────┬─────────┘
     │                                                                  │
     │                                                                  │
     │  6. May request more tools (agentic loop)                       │
     │     ────────────────────────────────────────────────────────────►
     │     ◄────────────────────────────────────────────────────────────
     │                                                                  │
     │  7. Final response                                               ▼
     │                                                         ┌──────────────────┐
     └────────────────────────────────────────────────────────►│    Gmail API     │
                                                               │    (Google)      │
                    8. Display to user                         └──────────────────┘
┌──────────┐    ◄───────────────────
│  User    │
│ Browser  │    + attachment download buttons
└──────────┘
```

### Agentic Loop Detail

The backend implements an **agentic loop** where Claude can make multiple tool calls:

```python
while True:
    response = claude.messages.create(tools=TOOLS, messages=messages)

    if response.stop_reason == "tool_use":
        # Execute tool, add results to messages
        # Continue loop
    elif response.stop_reason == "end_turn":
        # Return final response to user
        break
```

---

## Authentication Flow

### OAuth 2.0 Web Flow

```
┌────────────┐                    ┌────────────┐                    ┌────────────┐
│   User     │                    │   Backend  │                    │   Google   │
│  Browser   │                    │            │                    │            │
└─────┬──────┘                    └─────┬──────┘                    └─────┬──────┘
      │                                 │                                 │
      │  1. Click "Login with Google"   │                                 │
      │ ───────────────────────────────►│                                 │
      │                                 │                                 │
      │  2. Return auth URL + state     │                                 │
      │ ◄───────────────────────────────│                                 │
      │                                 │                                 │
      │  3. Redirect to Google OAuth    │                                 │
      │ ─────────────────────────────────────────────────────────────────►│
      │                                 │                                 │
      │  4. User consents               │                                 │
      │ ◄─────────────────────────────────────────────────────────────────│
      │                                 │                                 │
      │  5. Redirect to /auth/callback?code=XXX&state=YYY                 │
      │ ───────────────────────────────►│                                 │
      │                                 │                                 │
      │                                 │  6. Exchange code for tokens    │
      │                                 │ ───────────────────────────────►│
      │                                 │                                 │
      │                                 │  7. Return access + refresh     │
      │                                 │ ◄───────────────────────────────│
      │                                 │                                 │
      │  8. Set session cookie          │                                 │
      │ ◄───────────────────────────────│                                 │
      │                                 │                                 │
      │  9. Redirect to /index.html     │                                 │
      │ ◄───────────────────────────────│                                 │
      │                                 │                                 │
```

### Session Management

```
┌─────────────────────────────────────────────────────────────┐
│                    Session Storage (In-Memory)               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  _sessions = {                                               │
│      "abc123...": {                                          │
│          "email": "user@gmail.com",                          │
│          "credentials": <Google Credentials Object>          │
│      },                                                      │
│      "def456...": { ... }                                    │
│  }                                                           │
│                                                              │
│  Session ID stored in HTTP-only cookie                       │
│  Credentials auto-refresh when expired                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## API Design

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/login` | GET | No | Initiate OAuth, returns auth URL |
| `/auth/callback` | GET | No | OAuth callback from Google |
| `/auth/user` | GET | No | Check auth status, get user email |
| `/auth/logout` | POST | No | Invalidate session |
| `/api/chat` | POST | Yes | Main chat endpoint |
| `/api/download-attachment` | POST | Yes | Download email attachment |
| `/api/health` | GET | No | Health check |

### Chat Request/Response

**Request:**
```json
{
  "message": "Find emails from john@example.com last week"
}
```

**Response:**
```json
{
  "response": "I found 3 emails from john@example.com...",
  "attachments": [
    {
      "filename": "report.pdf",
      "message_id": "abc123",
      "attachment_id": "xyz789",
      "mimeType": "application/pdf",
      "size": 102400
    }
  ]
}
```

### Claude Tools Schema

```json
{
  "name": "search_emails",
  "description": "Search Gmail using query syntax",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "max_results": { "type": "integer", "default": 10 }
    },
    "required": ["query"]
  }
}
```

---

## Infrastructure

### Production Deployment (AWS Lightsail)

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS LIGHTSAIL INSTANCE                        │
│                    Ubuntu 22.04 LTS ($5/mo)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                        NGINX                             │    │
│  │  • SSL termination (Let's Encrypt)                       │    │
│  │  • Reverse proxy to Gunicorn                             │    │
│  │  • Static file serving                                   │    │
│  │  • Port 80 → 443 redirect                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                      GUNICORN                            │    │
│  │  • 1 worker process                                      │    │
│  │  • 120 second timeout                                    │    │
│  │  • Binds to 127.0.0.1:5001                              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   FLASK APPLICATION                      │    │
│  │  /var/www/gmail-chat/                                    │    │
│  │  • app.py, auth.py, gmail_service.py                    │    │
│  │  • static/ (frontend files)                             │    │
│  │  • venv/ (Python virtual environment)                   │    │
│  │  • .env (secrets)                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### File Locations (Production)

| What | Path |
|------|------|
| Application | `/var/www/gmail-chat/` |
| Environment | `/var/www/gmail-chat/.env` |
| Static files | `/var/www/gmail-chat/static/` |
| Nginx config | `/etc/nginx/sites-available/gmail-chat` |
| Systemd service | `/etc/systemd/system/gmail-chat.service` |
| SSL certificates | `/etc/letsencrypt/live/<domain>/` |

### CI/CD Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Developer  │     │    GitHub    │     │   Actions    │     │  Lightsail   │
│              │     │              │     │              │     │              │
│  git push    │────►│   release    │────►│  SSH Deploy  │────►│  Restart     │
│  to release  │     │   branch     │     │  Script      │     │  Service     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
                                          Health Check
                                          /api/health
```

---

## Security Model

### Authentication & Authorization

| Layer | Mechanism |
|-------|-----------|
| User Auth | Google OAuth 2.0 |
| Session | HTTP-only secure cookies |
| CSRF | State parameter validation |
| API Auth | `@require_auth` decorator |

### Secrets Management

```
┌─────────────────────────────────────────────────────────────┐
│                    SECRETS (Never in Git)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  .env file:                                                  │
│    ANTHROPIC_API_KEY=sk-ant-xxx                             │
│    FLASK_SECRET_KEY=<random-hex>                            │
│                                                              │
│  credentials_web.json:                                       │
│    Google OAuth client credentials                           │
│                                                              │
│  GitHub Secrets (CI/CD):                                     │
│    AWS_ACCESS_KEY_ID                                        │
│    AWS_SECRET_ACCESS_KEY                                    │
│    LIGHTSAIL_HOST                                           │
│    LIGHTSAIL_SSH_KEY                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### OAuth Scopes

| Scope | Purpose |
|-------|---------|
| `gmail.readonly` | Read email content |
| `gmail.modify` | Mark as read (future) |
| `userinfo.email` | Get user identity |
| `openid` | OpenID Connect |

### Security Considerations

1. **Token Storage**: OAuth tokens stored in-memory (lost on restart)
2. **Session Cookies**: HTTP-only, SameSite=Lax
3. **CORS**: Restricted to specific origins
4. **Input Validation**: Gmail API handles query sanitization
5. **Body Truncation**: Email bodies truncated to 2000 chars to prevent token overload

---

## Technology Stack

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API

### Backend
- Python 3.8+
- Flask (web framework)
- Flask-CORS (CORS handling)
- Gunicorn (WSGI server)
- python-dotenv (environment management)

### AI/ML
- Anthropic Claude Sonnet 4.5
- Tool Use / Function Calling

### APIs
- Gmail API v1
- Google OAuth 2.0
- Google People API (userinfo)

### Infrastructure
- AWS Lightsail (Ubuntu 22.04)
- Nginx (reverse proxy)
- Let's Encrypt (SSL)
- GitHub Actions (CI/CD)

### Development Tools
- Git
- Python venv
- pip

---

## Related Documentation

- [README.md](./README.md) - Quick start and usage
- [QUICKSTART.md](./QUICKSTART.md) - Getting started guide
- [deploy/DEPLOY_GUIDE.md](./deploy/DEPLOY_GUIDE.md) - Deployment instructions
- [docs/SETUP_GOOGLE_CLOUD.md](./docs/SETUP_GOOGLE_CLOUD.md) - Google Cloud setup
