// Authentication JavaScript for Login Page

const API_BASE_URL = '';

// Check if user is already authenticated on page load
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/user`, {
            credentials: 'include'
        });

        const data = await response.json();

        if (data.authenticated) {
            // Already logged in, redirect to chat
            window.location.href = 'index.html';
        }
    } catch (error) {
        console.error('Error checking auth:', error);
        // Backend not running, show error
        showError('Backend server is not running. Please start it with: cd backend && python app.py');
    }
}

// Initiate Google OAuth login
async function initiateLogin() {
    const btn = document.getElementById('googleSignInBtn');
    btn.disabled = true;
    btn.innerHTML = '<span>Redirecting...</span>';

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            credentials: 'include'
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to initiate login');
        }

        const data = await response.json();

        if (data.auth_url) {
            // Redirect to Google OAuth
            window.location.href = data.auth_url;
        } else {
            throw new Error('No authorization URL received');
        }

    } catch (error) {
        console.error('Login error:', error);
        showError(error.message);
        btn.disabled = false;
        btn.innerHTML = `
            <svg class="google-icon" viewBox="0 0 24 24" width="24" height="24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            <span>Sign in with Google</span>
        `;
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// Handle OAuth errors from URL parameters
function handleOAuthErrors() {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');

    if (error) {
        let message = 'Authentication failed';

        switch (error) {
            case 'access_denied':
                message = 'Access denied. You need to grant permission to access your Gmail.';
                break;
            case 'invalid_state':
                message = 'Invalid authentication state. Please try again.';
                break;
            case 'auth_failed':
                message = 'Authentication failed. Please try again.';
                break;
            default:
                message = `Authentication error: ${error}`;
        }

        showError(message);

        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// Initialize on page load
window.addEventListener('load', () => {
    handleOAuthErrors();
    checkAuth();
});
