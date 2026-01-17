// Gmail Chat Frontend Application

const API_BASE_URL = 'http://localhost:5001';

// Auto-resize textarea
const messageInput = document.getElementById('messageInput');
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Send message on Enter (Shift+Enter for new line)
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send message function
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) return;

    // Disable input while processing
    input.disabled = true;
    document.getElementById('sendButton').disabled = true;

    // Add user message to chat
    addMessage(message, 'user');

    // Clear input
    input.value = '';
    input.style.height = 'auto';

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        // Send request to backend
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Display response
        if (data.error) {
            addMessage(`Error: ${data.error}`, 'bot', true);
        } else {
            addMessage(data.response, 'bot', false, data.attachments);
        }

    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        addMessage(`Error: ${error.message}. Make sure the backend server is running on ${API_BASE_URL}`, 'bot', true);
    } finally {
        // Re-enable input
        input.disabled = false;
        document.getElementById('sendButton').disabled = false;
        input.focus();
    }
}

// Add message to chat
function addMessage(text, sender, isError = false, attachments = []) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (isError) {
        contentDiv.innerHTML = `<div class="error-message">${escapeHtml(text)}</div>`;
    } else {
        // Convert markdown-like formatting to HTML
        const formattedText = formatText(text);
        contentDiv.innerHTML = formattedText;
    }

    // Add attachments if any
    if (attachments && attachments.length > 0) {
        const attachmentList = createAttachmentList(attachments);
        contentDiv.appendChild(attachmentList);
    }

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingIndicator';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';

    typingDiv.appendChild(indicator);
    messagesContainer.appendChild(typingDiv);

    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return 'typingIndicator';
}

// Remove typing indicator
function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

// Format text (simple markdown-like formatting)
function formatText(text) {
    // Escape HTML first
    let formatted = escapeHtml(text);

    // Convert line breaks to <br>
    formatted = formatted.replace(/\n/g, '<br>');

    // Bold: **text** or __text__
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');

    // Italic: *text* or _text_
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/_(.*?)_/g, '<em>$1</em>');

    // Code: `text`
    formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');

    return formatted;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Create attachment list
function createAttachmentList(attachments) {
    const container = document.createElement('div');
    container.className = 'attachment-list';

    const title = document.createElement('div');
    title.innerHTML = '<strong>Attachments:</strong>';
    container.appendChild(title);

    attachments.forEach(attachment => {
        const item = document.createElement('div');
        item.className = 'attachment-item';

        const name = document.createElement('span');
        name.className = 'attachment-name';
        name.textContent = attachment.filename;

        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'download-btn';
        downloadBtn.textContent = 'Download';
        downloadBtn.onclick = () => downloadAttachment(
            attachment.message_id,
            attachment.attachment_id,
            attachment.filename
        );

        item.appendChild(name);
        item.appendChild(downloadBtn);
        container.appendChild(item);
    });

    return container;
}

// Download attachment
async function downloadAttachment(messageId, attachmentId, filename) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/download-attachment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message_id: messageId,
                attachment_id: attachmentId,
                filename: filename
            })
        });

        if (!response.ok) {
            throw new Error('Failed to download attachment');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        addMessage(`Downloaded: ${filename}`, 'bot');

    } catch (error) {
        console.error('Download error:', error);
        addMessage(`Failed to download ${filename}: ${error.message}`, 'bot', true);
    }
}

// Check backend health on load
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (response.ok) {
            console.log('Backend is healthy');
        }
    } catch (error) {
        console.warn('Backend is not running. Please start the backend server.');
        addMessage(
            'Warning: Backend server is not running. Please start the Python backend with: cd backend && python app.py',
            'bot',
            true
        );
    }
}

// Initialize
window.addEventListener('load', () => {
    checkBackendHealth();
    document.getElementById('messageInput').focus();
});
