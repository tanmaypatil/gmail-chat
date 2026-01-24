#!/bin/bash
# Quick setup script for germanwakad.click
# Run this on Lightsail after initial setup

set -e

DOMAIN="germanwakad.click"
APP_DIR="/var/www/gmail-chat"

echo "=== Configuring for $DOMAIN ==="

# Update backend URLs
echo "[1/5] Updating backend configuration..."
sed -i "s|OAUTH_REDIRECT_URI = .*|OAUTH_REDIRECT_URI = 'https://$DOMAIN/auth/callback'|g" $APP_DIR/app.py
sed -i "s|FRONTEND_URL = .*|FRONTEND_URL = 'https://$DOMAIN'|g" $APP_DIR/app.py
sed -i "s|'http://localhost:8000'|'https://$DOMAIN'|g" $APP_DIR/app.py
sed -i "s|'http://127.0.0.1:8000'|'https://$DOMAIN'|g" $APP_DIR/app.py
sed -i "s|OAUTHLIB_INSECURE_TRANSPORT = '1'|OAUTHLIB_INSECURE_TRANSPORT = '0'|g" $APP_DIR/app.py

# Update frontend URLs
echo "[2/5] Updating frontend configuration..."
sed -i "s|http://localhost:5001|https://$DOMAIN|g" $APP_DIR/static/auth.js
sed -i "s|http://127.0.0.1:5001|https://$DOMAIN|g" $APP_DIR/static/auth.js
sed -i "s|http://localhost:5001|https://$DOMAIN|g" $APP_DIR/static/app.js
sed -i "s|http://127.0.0.1:5001|https://$DOMAIN|g" $APP_DIR/static/app.js

# Update Nginx
echo "[3/5] Updating Nginx configuration..."
sudo sed -i "s|server_name _;|server_name $DOMAIN;|g" /etc/nginx/sites-available/gmail-chat
sudo nginx -t

# Setup HTTPS
echo "[4/5] Setting up HTTPS with Let's Encrypt..."
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

# Restart services
echo "[5/5] Restarting services..."
sudo systemctl restart gmail-chat
sudo systemctl restart nginx

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Your app is now live at: https://$DOMAIN"
echo ""
echo "Don't forget to update Google OAuth Console:"
echo "  Redirect URI: https://$DOMAIN/auth/callback"
echo "  JavaScript origin: https://$DOMAIN"
