#!/bin/bash
# Update application for custom domain
# Usage: ./setup_domain.sh yourdomain.com

if [ -z "$1" ]; then
    echo "Usage: ./setup_domain.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1
APP_DIR="/var/www/gmail-chat"

echo "Configuring application for domain: $DOMAIN"

# Update backend
sed -i "s|OAUTH_REDIRECT_URI = .*|OAUTH_REDIRECT_URI = 'https://$DOMAIN/auth/callback'|g" $APP_DIR/app.py
sed -i "s|FRONTEND_URL = .*|FRONTEND_URL = 'https://$DOMAIN'|g" $APP_DIR/app.py

# Update CORS origins in app.py - replace localhost entries
sed -i "s|'http://localhost:8000'|'https://$DOMAIN'|g" $APP_DIR/app.py
sed -i "s|'http://127.0.0.1:8000'|'https://$DOMAIN'|g" $APP_DIR/app.py

# Update frontend
sed -i "s|http://localhost:5001|https://$DOMAIN|g" $APP_DIR/static/auth.js
sed -i "s|http://127.0.0.1:5001|https://$DOMAIN|g" $APP_DIR/static/auth.js
sed -i "s|http://localhost:5001|https://$DOMAIN|g" $APP_DIR/static/app.js
sed -i "s|http://127.0.0.1:5001|https://$DOMAIN|g" $APP_DIR/static/app.js

echo ""
echo "Done! Now:"
echo "1. Update Google OAuth redirect URI to: https://$DOMAIN/auth/callback"
echo "2. Run: sudo systemctl restart gmail-chat"
echo "3. Run: ./setup_https.sh $DOMAIN"
