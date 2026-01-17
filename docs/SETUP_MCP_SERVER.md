# Gmail MCP Server Setup

This guide explains how to set up the Gmail MCP (Model Context Protocol) server.

## Understanding MCP Architecture

The Gmail MCP server acts as a bridge between Claude and Gmail API. Here's how it works:

```
Your App → Claude API (with MCP) → Gmail MCP Server → Gmail API
```

## Installation Options

### Option 1: Use Anthropic's Official MCP Server (Recommended)

1. Install the Gmail MCP server via npm:
```bash
npm install -g @modelcontextprotocol/server-gmail
```

2. Configure MCP settings for Claude Desktop (if using Claude Desktop app):
   - Location: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
   - Add Gmail MCP server configuration

### Option 2: Use Python-based MCP Implementation

For this project, we'll integrate Gmail functionality directly into our Python backend, which simplifies the architecture.

## Our Approach: Direct Integration

Instead of running a separate MCP server, we'll:

1. **Python Backend**: Acts as the MCP server itself
   - Handles Gmail API authentication
   - Provides Gmail search and retrieval functions
   - Exposes these as tools to Claude via the Anthropic SDK

2. **Claude API**: Uses the tool calling feature
   - Receives natural language queries
   - Calls our Gmail functions as needed
   - Synthesizes responses

## Architecture Flow

```
Frontend (HTML/JS)
    ↓ (HTTP request)
Python Backend
    ├─→ Gmail API (read emails, attachments)
    ├─→ Claude API (process query)
    └─→ Tool calling (Gmail search functions)
```

## What We'll Build

The Python backend will expose these functions to Claude:

1. `search_emails(query, max_results)` - Search Gmail
2. `get_email_content(message_id)` - Get full email content
3. `list_attachments(message_id)` - List email attachments
4. `download_attachment(message_id, attachment_id)` - Download attachment

## Next Steps

Proceed to building the Python backend with Claude API integration.
