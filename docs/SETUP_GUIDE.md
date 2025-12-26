# Complete Setup Guide

This guide will walk you through setting up the CV Mailer application step by step.

## Prerequisites

- Python 3.8 or higher
- A Google account
- Access to your Google Sheet with job applications
- Your resume file (PDF) or Google Drive link

## Step 1: Install Python Dependencies

### Option A: Using the Setup Script (Recommended)

```bash
./setup.sh
```

This will:

- Create a virtual environment
- Install all dependencies
- Check for credentials file
- Create .env file from template

### Option B: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 2: Google Cloud Setup

### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project name: "CV Mailer" (or any name you prefer)
5. Click "Create"

### 2.2 Enable Required APIs

1. In your project, go to "APIs & Services" > "Library"
2. Search for and enable:
   - **Google Sheets API**
   - **Gmail API**

### 2.3 Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: External (unless you have Workspace)
   - App name: "CV Mailer"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Click "Add or Remove Scopes", select:
     - `.../auth/spreadsheets` (Google Sheets API)
     - `.../auth/gmail.send` (Gmail API)
   - Click "Save and Continue"
   - Test users: Add your email address
   - Click "Save and Continue"
   - Click "Back to Dashboard"

4. Create OAuth Client ID:
   - Application type: **Desktop app**
   - Name: "CV Mailer Desktop Client"
   - Click "Create"

5. Download the credentials:
   - Click "Download JSON"
   - Save the file as `credentials.json` in the project root directory

## Step 3: Configure Environment Variables

1. Create a `.env` file in the project root (this file is gitignored) and add your settings.

2. Example `.env` file:

```env
# Google API Credentials (already downloaded)
GOOGLE_CREDENTIALS_FILE=credentials.json

# Google Sheets Configuration
SPREADSHEET_ID=your_spreadsheet_id_here
WORKSHEET_NAME=Sheet1
PROCESS_ALL_SHEETS=true
SHEET_NAME_FILTER=

# Gmail Configuration
GMAIL_USER=your_email@gmail.com
SENDER_NAME=Your Name

# Optional: signature fields used in templates
LINKEDIN_PROFILE=https://www.linkedin.com/in/your-handle
CONTACT_INFORMATION=your_email@gmail.com | +971 5X XXX XXXX

# Resume Configuration
# Recommended: set BOTH (attach the file + include a Drive link in the email)
RESUME_FILE_PATH=./resume.pdf
RESUME_DRIVE_LINK=

# Email Rate Limiting (seconds between emails)
# Recommended safe sending pattern: 100–500ms between sends
EMAIL_DELAY_MIN=0.1
EMAIL_DELAY_MAX=0.5

# Daily Email Limit (Gmail free: ~500/day, Workspace: ~2000/day)
DAILY_EMAIL_LIMIT=50

# Follow-up Configuration
FOLLOW_UP_DAYS=7
MAX_FOLLOW_UPS=3

# Database (default is fine)
DATABASE_PATH=cv_mailer.db

# Logging (default is fine)
LOG_LEVEL=INFO
LOG_FILE=cv_mailer.log
```

### Getting Your Spreadsheet ID

1. Open your Google Sheet
2. Look at the URL:

   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

3. Copy the `SPREADSHEET_ID` part
4. Paste it in `.env` file

### Resume Setup

**Option 1: Local File (Attachment)**

- Place your resume PDF in the project root
- Set `RESUME_FILE_PATH=./resume.pdf` (or your filename)
- Optionally also set `RESUME_DRIVE_LINK` (recommended)

**Option 2: Google Drive Link**

- Upload resume to Google Drive
- Right-click > Get link > Make it accessible to "Anyone with the link"
- Copy the link
- Set `RESUME_DRIVE_LINK=https://drive.google.com/file/d/...`
- Optionally also set `RESUME_FILE_PATH` to attach the resume (recommended)

## Step 4: Initialize Database

The database will be created automatically on first run, but you can initialize it manually:

```bash
python3 -c "from models import init_database; init_database(); print('Database initialized!')"
```

## Step 5: First Authentication

On first run, the application will:

1. Open your browser for OAuth authentication
2. Sign in with your Google account
3. Review permissions (Sheets and Gmail access)
4. Click "Allow"
5. Save credentials for future use (creates `token.pickle` and `gmail_token.pickle`)

**Note**: If you see "This app isn't verified", click "Advanced" > "Go to CV Mailer (unsafe)" - this is normal for personal projects.

## Step 6: Test the Setup

### ⚠️ Important: Activate Virtual Environment First

**Before running any commands, activate the virtual environment:**

```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# You should see (venv) in your terminal prompt
# Example: (venv) user@computer:~/cv-mailer$
```

### Dry Run (Recommended First)

Test without sending any emails:

```bash
# Make sure venv is activated first!
python main.py --dry-run
```

This will:

- Connect to Google Sheets
- Parse your data
- Show what emails would be sent
- Not actually send anything

### Check Configuration

```bash
# Make sure venv is activated first!
python main.py --stats
```

Shows current statistics (will be empty on first run).

## Step 7: Verify Your Google Sheet Format

Make sure your Google Sheet has these columns (names are flexible):

- **Company Name** (required)
- **Position** (required)
- **Recruiter Name** (required - can contain multiple recruiters)
- **Location** (optional)
- **Job Posting URL** (optional)
- **Status** (optional - will be auto-updated)

### Example Row

```
Company Name: Presight
Position: Software Engineer
Recruiter Name: Salman Khan - salman.khan@presight.ai, Alia Alkatheeri - alia.alkatheeri@presight.ai
Location: Dubai
Job Posting URL: https://...
Status: (leave empty)
```

## Troubleshooting

### "Credentials file not found"

- Make sure `credentials.json` is in the project root
- Check the filename spelling (must be exactly `credentials.json`)

### "Authentication failed"

- Delete `token.pickle` and `gmail_token.pickle`
- Re-run the application to re-authenticate

### "Cannot read from Google Sheets"

- Verify `SPREADSHEET_ID` is correct
- Make sure the sheet is shared with your Google account
- Check that Google Sheets API is enabled

### "Rate limit exceeded"

- Increase `EMAIL_DELAY_MIN` and `EMAIL_DELAY_MAX` in `.env`
- Reduce `DAILY_EMAIL_LIMIT`
- Wait 24 hours before resuming

### "Module not found" errors

- **Activate virtual environment first**: `source venv/bin/activate`
- You should see `(venv)` in your terminal prompt
- Run `pip install -r requirements.txt` again if needed
- If the error persists, recreate the venv: `rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

### Permission errors

- Make sure you granted all requested permissions during OAuth
- Check that APIs are enabled in Google Cloud Console

## Next Steps

Once setup is complete:

**⚠️ Remember: Always activate virtual environment first!**

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Then:

1. **Test with dry-run**: `python main.py --dry-run`
2. **Review the output**: Check which emails will be sent
3. **Send emails**: `python main.py` (removes `--dry-run`)
4. **Check statistics**: `python main.py --stats`
5. **Send follow-ups**: `python main.py --follow-ups`

## Virtual Environment Quick Reference

```bash
# Activate virtual environment
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# Deactivate virtual environment
deactivate

# Check if active (you'll see (venv) in your prompt)
# If you don't see (venv), you need to activate it!

# Install/update dependencies
pip install -r requirements.txt

# Create new virtual environment (if needed)
python3 -m venv venv

# Verify Python and packages
python --version
pip list
```

**Tip**: You need to activate the virtual environment every time you open a new terminal session. The activation only lasts for that terminal session.

## Security Reminders

- Never commit `credentials.json`, `.env`, or `*.pickle` files
- Keep your `.env` file secure
- Don't share your OAuth tokens
- Regularly backup your database file (`cv_mailer.db`)

## Getting Help

If you encounter issues:

1. Check the logs: `cv_mailer.log`
2. Review error messages in the console
3. Verify all configuration in `.env`
4. Test with `--dry-run` first

Good luck with your job applications! 🚀
