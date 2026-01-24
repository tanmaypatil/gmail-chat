# Gmail Chat - AWS Lightsail Deployment Guide

## Overview

This guide covers:
1. Initial Lightsail setup
2. Custom domain + HTTPS
3. CI/CD with GitHub Actions

---

## Part 1: Initial Lightsail Setup

### Step 1: Create Lightsail Instance

1. Go to [AWS Lightsail Console](https://lightsail.aws.amazon.com/)
2. Click **Create instance**
3. Select:
   - Region: Choose nearest to you
   - Platform: **Linux/Unix**
   - Blueprint: **Ubuntu 22.04 LTS**
   - Instance plan: **$5/month** (1 GB RAM) recommended
4. Create a new SSH key pair → **Download** the private key
5. Name it: `gmail-chat`
6. Click **Create instance**

### Step 2: Configure Networking

1. Go to your instance → **Networking** tab
2. Create a **Static IP** (free) and attach it
3. Under **IPv4 Firewall**, add rules:
   - **HTTP** (Port 80)
   - **HTTPS** (Port 443)

### Step 3: Initial Server Setup

SSH into your instance:
```bash
ssh -i ~/LightsailDefaultKey.pem ubuntu@YOUR_STATIC_IP
```

Run the initial setup:
```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/gmail-chat.git
cd gmail-chat
chmod +x deploy/*.sh

# Run initial setup
./deploy/initial_server_setup.sh https://github.com/YOUR_USERNAME/gmail-chat.git
```

### Step 4: Configure Secrets

```bash
# Create .env file
cat > /var/www/gmail-chat/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-your-key-here
FLASK_SECRET_KEY=generate-random-string-here
EOF

# Upload your Google OAuth credentials
# (copy credentials_web.json to /var/www/gmail-chat/)
```

---

## Part 2: Custom Domain + HTTPS

### Option A: Buy a Domain (~$10-15/year)
- **Namecheap**: namecheap.com
- **Cloudflare**: cloudflare.com/products/registrar
- **AWS Route 53**: ~$12/year for .com

### Option B: Free Subdomain
- **DuckDNS**: duckdns.org (e.g., `gmail-chat.duckdns.org`)
- **FreeDNS**: freedns.afraid.org

### Setup DNS

Point your domain to your Lightsail Static IP:
```
Type: A
Name: @ (or subdomain)
Value: YOUR_STATIC_IP
TTL: 300
```

### Configure Domain on Server

```bash
ssh ubuntu@YOUR_STATIC_IP
cd ~/gmail-chat

# Update app for your domain
./deploy/setup_domain.sh yourdomain.com

# Setup HTTPS (free SSL via Let's Encrypt)
./deploy/setup_https.sh yourdomain.com

# Restart services
sudo systemctl restart gmail-chat
sudo systemctl restart nginx
```

### Update Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Edit your OAuth 2.0 Client
3. Add:
   - Authorized redirect URI: `https://yourdomain.com/auth/callback`
   - Authorized JavaScript origin: `https://yourdomain.com`

---

## Part 3: CI/CD with GitHub Actions

### How It Works

```
Push to main → GitHub Actions → SSH to Lightsail → Deploy
```

### Step 1: Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `LIGHTSAIL_HOST` | Your Static IP or domain |
| `LIGHTSAIL_SSH_KEY` | Contents of your Lightsail private key (.pem file) |

To get your SSH key contents:
```bash
cat ~/LightsailDefaultKey.pem
```

### Step 2: Push to Deploy

The workflow (`.github/workflows/deploy.yml`) triggers on:
- Push to `main` branch
- Manual trigger (Actions → Deploy → Run workflow)

```bash
git add .
git commit -m "Update feature"
git push origin main
# → Automatically deploys!
```

### Step 3: Monitor Deployment

- Go to repo → **Actions** tab
- Click on the running workflow
- View logs in real-time

---

## Quick Reference

### Useful Commands

```bash
# View app logs
sudo journalctl -u gmail-chat -f

# Restart app
sudo systemctl restart gmail-chat

# Check status
sudo systemctl status gmail-chat

# Test locally
curl http://localhost:5001/api/health

# Renew SSL (auto, but manual test)
sudo certbot renew --dry-run
```

### File Locations

| What | Where |
|------|-------|
| App code | `/var/www/gmail-chat/` |
| Environment | `/var/www/gmail-chat/.env` |
| Nginx config | `/etc/nginx/sites-available/gmail-chat` |
| Service config | `/etc/systemd/system/gmail-chat.service` |
| SSL certs | `/etc/letsencrypt/live/yourdomain.com/` |

---

## Cost Summary

| Item | Cost |
|------|------|
| Lightsail ($5 plan) | $5/month |
| Static IP | Free (if attached) |
| Domain | ~$10-15/year |
| SSL Certificate | Free (Let's Encrypt) |
| **Total** | **~$6/month** |

### To Stop Costs

```bash
# Stop instance (keeps data, ~$0.05/GB storage cost)
Lightsail Console → Instance → Stop

# Delete everything (zero cost)
Lightsail Console → Delete: Instance, Static IP, Snapshots
```

---

## Troubleshooting

### 502 Bad Gateway
```bash
sudo systemctl status gmail-chat
sudo journalctl -u gmail-chat -n 50
sudo systemctl restart gmail-chat
```

### SSL Certificate Issues
```bash
sudo certbot certificates
sudo certbot renew --force-renewal
```

### OAuth Not Working
1. Check redirect URI matches exactly (including https://)
2. Verify credentials_web.json exists in /var/www/gmail-chat/
3. Check CORS origins in app.py match your domain

### GitHub Actions Failing
1. Check secrets are set correctly
2. Verify SSH key has no extra whitespace
3. Test SSH manually: `ssh -i key.pem ubuntu@host`
