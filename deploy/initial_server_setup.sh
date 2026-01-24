#!/bin/bash
# Run this ONCE on a fresh Lightsail instance to prepare for CI/CD
# This clones the repo and does initial setup

set -e

REPO_URL=$1

if [ -z "$REPO_URL" ]; then
    echo "Usage: ./initial_server_setup.sh https://github.com/username/gmail-chat.git"
    exit 1
fi

echo "=== Initial Server Setup for CI/CD ==="

# Update system
echo "[1/6] Updating system..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "[2/6] Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx git

# Clone repository
echo "[3/6] Cloning repository..."
cd ~
git clone $REPO_URL gmail-chat

# Setup application directory
echo "[4/6] Setting up application..."
sudo mkdir -p /var/www/gmail-chat
sudo chown ubuntu:ubuntu /var/www/gmail-chat

cp -r ~/gmail-chat/backend/* /var/www/gmail-chat/
mkdir -p /var/www/gmail-chat/static
cp -r ~/gmail-chat/frontend/* /var/www/gmail-chat/static/

# Create virtual environment
echo "[5/6] Creating Python environment..."
cd /var/www/gmail-chat
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Setup systemd service
echo "[6/6] Setting up services..."
sudo cp ~/gmail-chat/deploy/gmail-chat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gmail-chat

# Setup nginx
sudo cp ~/gmail-chat/deploy/nginx.conf /etc/nginx/sites-available/gmail-chat
sudo ln -sf /etc/nginx/sites-available/gmail-chat /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo ""
echo "=== Initial Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Create /var/www/gmail-chat/.env with your ANTHROPIC_API_KEY"
echo "2. Upload credentials_web.json to /var/www/gmail-chat/"
echo "3. Run: ./deploy/setup_domain.sh yourdomain.com"
echo "4. Run: ./deploy/setup_https.sh yourdomain.com"
echo "5. Start: sudo systemctl start gmail-chat && sudo systemctl restart nginx"
echo ""
echo "For CI/CD, add these GitHub secrets:"
echo "  LIGHTSAIL_HOST: $(curl -s ifconfig.me)"
echo "  LIGHTSAIL_SSH_KEY: (your private key)"
