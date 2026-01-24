# Route 53 Setup for germanwakad.click

## Step 1: Get Your Lightsail Static IP

1. Go to [Lightsail Console](https://lightsail.aws.amazon.com/)
2. Instance → Networking → Create Static IP
3. Note the IP address (e.g., `54.123.45.67`)

## Step 2: Configure Route 53

1. Go to [Route 53 Console](https://console.aws.amazon.com/route53/)
2. Click **Hosted zones**
3. Click **germanwakad.click**
4. Click **Create record**

### Create A Record:
```
Record name: (leave empty for root, or use subdomain like "gmail")
Record type: A
Value: YOUR_LIGHTSAIL_STATIC_IP
TTL: 300
```

### If using subdomain (e.g., gmail.germanwakad.click):
```
Record name: gmail
Record type: A
Value: YOUR_LIGHTSAIL_STATIC_IP
TTL: 300
```

5. Click **Create records**

## Step 3: Verify DNS (wait 1-5 minutes)

```bash
# Check if DNS is working
nslookup germanwakad.click
# or
dig germanwakad.click
```

## Step 4: Configure Server

SSH into Lightsail and run:
```bash
cd ~/gmail-chat
./deploy/setup_domain.sh germanwakad.click
./deploy/setup_https.sh germanwakad.click
sudo systemctl restart gmail-chat
sudo systemctl restart nginx
```

## Step 5: Update Google OAuth

Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
- Authorized redirect URI: `https://germanwakad.click/auth/callback`
- Authorized JavaScript origin: `https://germanwakad.click`

---

Your app will be live at: **https://germanwakad.click**
