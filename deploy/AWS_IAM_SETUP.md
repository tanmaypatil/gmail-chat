# AWS IAM Setup for GitHub Actions

## Step 1: Create IAM Policy (Least Privilege)

1. Go to [IAM Console](https://console.aws.amazon.com/iam/) → **Policies** → **Create policy**

2. Click **JSON** tab and paste:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "LightsailAccess",
            "Effect": "Allow",
            "Action": [
                "lightsail:GetInstance",
                "lightsail:GetInstanceState",
                "lightsail:GetInstances",
                "lightsail:StartInstance",
                "lightsail:StopInstance"
            ],
            "Resource": "*"
        }
    ]
}
```

3. Click **Next** → Name: `GithubActionsLightsailPolicy` → **Create policy**

## Step 2: Create IAM User

1. Go to **IAM** → **Users** → **Create user**

2. User name: `github-actions-deploy`

3. Click **Next**

4. Select **Attach policies directly** → Search and select:
   - `GithubActionsLightsailPolicy` (the one you just created)

5. Click **Next** → **Create user**

## Step 3: Create Access Keys

1. Click on the user `github-actions-deploy`

2. Go to **Security credentials** tab

3. Scroll to **Access keys** → **Create access key**

4. Select **Command Line Interface (CLI)**

5. Check the acknowledgment → **Next** → **Create access key**

6. **IMPORTANT**: Copy both values now (you won't see the secret again):
   - Access key ID: `AKIA...`
   - Secret access key: `...`

## Step 4: Add GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your Access Key ID (AKIA...) |
| `AWS_SECRET_ACCESS_KEY` | Your Secret Access Key |
| `LIGHTSAIL_HOST` | `germanwakad.click` or your Static IP |
| `LIGHTSAIL_SSH_KEY` | Contents of your Lightsail .pem file |

### To get SSH key contents:
```bash
cat ~/LightsailDefaultKey.pem
```
Copy the entire output including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`

## Step 5: Update Region (if needed)

Edit `.github/workflows/deploy.yml` and change the region:

```yaml
env:
  AWS_REGION: ap-south-1  # Change to your region
```

Common regions:
- `us-east-1` - N. Virginia
- `us-west-2` - Oregon
- `eu-west-1` - Ireland
- `ap-south-1` - Mumbai
- `ap-southeast-1` - Singapore

## Step 6: Test Deployment

```bash
git checkout release
git merge main
git push origin release
```

Go to **Actions** tab to monitor the deployment.

---

## Security Notes

- The IAM policy only grants **read** access to Lightsail
- Actual deployment happens via SSH (more secure)
- Rotate access keys periodically (every 90 days recommended)
- Never commit credentials to your repository

## Troubleshooting

### "Unable to locate credentials"
- Check secrets are named exactly: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

### "Instance not found"
- Verify `INSTANCE_NAME` in workflow matches your Lightsail instance name
- Check `AWS_REGION` is correct

### SSH Connection Failed
- Verify `LIGHTSAIL_HOST` is correct
- Ensure SSH key has no extra whitespace
- Check Lightsail firewall allows SSH (port 22)
