#!/bin/bash
# Setup HTTPS with Let's Encrypt
# Usage: ./setup_https.sh yourdomain.com

if [ -z "$1" ]; then
    echo "Usage: ./setup_https.sh yourdomain.com"
    echo "Example: ./setup_https.sh gmail-chat.example.com"
    exit 1
fi

DOMAIN=$1

echo "=== Setting up HTTPS for $DOMAIN ==="

# Install Certbot
echo "[1/4] Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Update Nginx config with domain
echo "[2/4] Updating Nginx config..."
sudo sed -i "s|server_name _;|server_name $DOMAIN;|g" /etc/nginx/sites-available/gmail-chat
sudo nginx -t

# Get SSL certificate
echo "[3/4] Obtaining SSL certificate..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

# Setup auto-renewal
echo "[4/4] Setting up auto-renewal..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo ""
echo "=== HTTPS Setup Complete ==="
echo "Your app is now available at: https://$DOMAIN"
echo ""
echo "Certificate will auto-renew. To test renewal:"
echo "  sudo certbot renew --dry-run"
