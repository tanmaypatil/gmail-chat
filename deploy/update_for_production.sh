#!/bin/bash
# Run this on Lightsail to update URLs for production
# Usage: ./update_for_production.sh YOUR_PUBLIC_IP

if [ -z "$1" ]; then
    echo "Usage: ./update_for_production.sh YOUR_PUBLIC_IP"
    echo "Example: ./update_for_production.sh 54.123.45.67"
    exit 1
fi

PUBLIC_IP=$1
APP_DIR="/var/www/gmail-chat"

echo "Updating application for production with IP: $PUBLIC_IP"

# Update backend app.py
sed -i "s|http://localhost:5001/auth/callback|http://$PUBLIC_IP/auth/callback|g" $APP_DIR/app.py
sed -i "s|http://localhost:8000|http://$PUBLIC_IP|g" $APP_DIR/app.py
sed -i "s|http://127.0.0.1:8000|http://$PUBLIC_IP|g" $APP_DIR/app.py

# Update frontend auth.js
sed -i "s|http://localhost:5001|http://$PUBLIC_IP|g" $APP_DIR/static/auth.js
sed -i "s|http://127.0.0.1:5001|http://$PUBLIC_IP|g" $APP_DIR/static/auth.js

# Update frontend app.js
sed -i "s|http://localhost:5001|http://$PUBLIC_IP|g" $APP_DIR/static/app.js
sed -i "s|http://127.0.0.1:5001|http://$PUBLIC_IP|g" $APP_DIR/static/app.js

# Disable insecure OAuth transport
sed -i "s|OAUTHLIB_INSECURE_TRANSPORT = '1'|OAUTHLIB_INSECURE_TRANSPORT = '0'|g" $APP_DIR/app.py

echo "Done! Restart the service:"
echo "  sudo systemctl restart gmail-chat"
