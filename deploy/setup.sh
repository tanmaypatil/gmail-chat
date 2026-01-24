#!/bin/bash
# Lightsail Ubuntu Setup Script for Gmail Chat Application
# Run this script on a fresh Lightsail Ubuntu instance

set -e  # Exit on error

echo "=== Gmail Chat Deployment Setup ==="

# Update system
echo "[1/7] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "[2/7] Installing Python and Nginx..."
sudo apt install -y python3 python3-pip python3-venv nginx

# Create app directory
echo "[3/7] Setting up application directory..."
sudo mkdir -p /var/www/gmail-chat
sudo chown $USER:$USER /var/www/gmail-chat

# Copy application files (run from project root)
echo "[4/7] Copying application files..."
cp -r backend/* /var/www/gmail-chat/
mkdir -p /var/www/gmail-chat/static
cp -r frontend/* /var/www/gmail-chat/static/

# Create Python virtual environment
echo "[5/7] Setting up Python environment..."
cd /var/www/gmail-chat
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create .env file template
echo "[6/7] Creating environment template..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
ANTHROPIC_API_KEY=your_anthropic_api_key_here
FLASK_SECRET_KEY=your_random_secret_key_here
OAUTHLIB_INSECURE_TRANSPORT=0
EOF
    echo ">>> IMPORTANT: Edit /var/www/gmail-chat/.env with your API keys!"
fi

# Setup systemd service
echo "[7/7] Setting up systemd service..."
sudo cp /var/www/gmail-chat/gmail-chat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gmail-chat

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit /var/www/gmail-chat/.env with your ANTHROPIC_API_KEY"
echo "2. Upload credentials_web.json for Google OAuth"
echo "3. Update OAuth redirect URIs in Google Console to your Lightsail IP"
echo "4. Run: sudo systemctl start gmail-chat"
echo "5. Run: sudo systemctl restart nginx"
echo ""
