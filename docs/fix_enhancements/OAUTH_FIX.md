# Fixing OAuth "Access Blocked" Error

You're seeing "Error 403: access_denied" because your email isn't added as a test user in Google Cloud Console.

> 📖 **Complete OAuth Setup**: See [Setup Guide - Google Cloud Setup](SETUP_GUIDE.md#step-2-google-cloud-setup)

## Quick Fix Steps

### 1. Go to Google Cloud Console

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Select your "CV Mailer" project
3. Go to **"APIs & Services"** > **"OAuth consent screen"**

### 2. Add Your Email as Test User

1. Scroll down to **"Test users"** section
2. Click **"+ ADD USERS"**
3. Add your email: `lakshyads.96@gmail.com`
4. Click **"ADD"**

### 3. Verify OAuth Consent Screen Settings

Make sure these are set:

- **User Type**: External (unless you have Google Workspace)
- **Publishing status**: Testing (this is fine for personal use)
- **Scopes**: Should include:
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/gmail.send`

### 4. Try Again

After adding yourself as a test user, try running the application again:

```bash
# Using the new package command (recommended)
cv-mailer --dry-run

# Or using the traditional way
cd /Users/lds/Documents/Workspace/Projects/cv-mailer
python main.py --dry-run
```

## Alternative: Publish the App (Not Recommended for Personal Use)

If you want to avoid test users, you can publish the app, but this requires:

- Privacy policy URL
- Terms of service URL
- App verification (can take weeks)

**For personal use, just add yourself as a test user - it's much simpler!**

## Still Having Issues?

If you still see the error after adding yourself as a test user:

1. **Wait a few minutes** - Changes can take a moment to propagate
2. **Clear browser cache** - Try in an incognito/private window
3. **Check the email** - Make sure you're using the exact email you added
4. **Verify project** - Make sure you're in the correct Google Cloud project
