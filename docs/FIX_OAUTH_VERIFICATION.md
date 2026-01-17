# Fix: "App Not Verified" Error

## The Problem

You're seeing this error:
```
Gmail Chat App has not completed the Google verification process.
The app is currently being tested, and can only be accessed by
developer-approved testers.
```

## The Solution

Your app is in "Testing" mode and you need to add yourself as a test user.

### Step-by-Step Fix

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select your project (`gmail-chat-app`)

2. **Navigate to OAuth Consent Screen**
   - In the left menu, click: **APIs & Services** > **OAuth consent screen**

3. **Add Test Users**
   - Scroll down to the **Test users** section
   - Click **+ ADD USERS**
   - Enter your Gmail address (the one you want to use with this app)
   - Click **SAVE**

4. **Verify Settings**
   - Publishing status should be: **Testing**
   - Your email should appear in the Test users list

5. **Retry Authentication**
   - Delete `token.json` if it exists: `rm backend/token.json`
   - Run the test again: `python test_gmail.py`
   - You should now be able to authorize the app

### Alternative: Publish the App (Optional)

If you want anyone to use the app (not recommended for personal use):

1. Go to **OAuth consent screen**
2. Click **PUBLISH APP**
3. Submit for Google verification (takes several weeks)

**Note:** For personal use, keeping it in "Testing" mode is fine!

### What Happens After Adding Test User?

- You can authorize the app with the test user's Gmail account
- The app will have access to that Gmail account
- No verification needed since you're the developer
- Up to 100 test users can be added

### Troubleshooting

**Still getting the error?**
- Make sure you added the EXACT email address you're trying to log in with
- Wait 1-2 minutes after adding the test user
- Clear browser cookies/cache
- Try in incognito mode

**Multiple Gmail accounts?**
- Add all accounts you want to test with as test users
- Or use only the account you added as a test user

## Next Steps

After fixing this:
1. Run: `python test_gmail.py` (in backend folder)
2. Browser will open for OAuth
3. Select your test user account
4. Click "Advanced" if you see a warning
5. Click "Go to Gmail Chat App (unsafe)" - this is safe, it's your own app!
6. Grant permissions
7. Tests will run successfully
