# Quick Start Guide

Get up and running with CV Mailer in 5 minutes!

## Step 1: Install Dependencies

```bash
# Run the setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Google Cloud Setup (5 minutes)

1. **Create/Select Project**
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing

2. **Enable APIs**
   - Go to "APIs & Services" > "Library"
   - Enable "Google Sheets API"
   - Enable "Gmail API"

3. **Create Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "CV Mailer"
   - Click "Create"
   - Click "Download JSON"
   - Save as `credentials.json` in project root

## Step 3: Prepare Google Sheet

1. Create a Google Sheet with columns:
   - Company Name
   - Position
   - Recruiter Email
   - (Optional) Recruiter Name, Location, Job Posting URL

2. Get Spreadsheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

3. Share sheet with your Google account (if using OAuth)

## Step 4: Configure

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env`:
   ```env
   SPREADSHEET_ID=your_spreadsheet_id_here
   GMAIL_USER=your_email@gmail.com
   SENDER_NAME=Your Name
   RESUME_FILE_PATH=./resume.pdf
   ```

3. Place your resume PDF in project root (or use Google Drive link)

## Step 5: Test Run

**⚠️ Important: Activate virtual environment first!**

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Dry run (no emails sent)
python main.py --dry-run

# Check what will be sent
```

## Step 6: First Authentication

On first run:
1. Browser will open for OAuth
2. Sign in with your Google account
3. Authorize access to Sheets and Gmail
4. Credentials saved for future use

## Step 7: Send Emails

**⚠️ Remember: Activate virtual environment first!**

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Send emails to new applications
python main.py

# Or with options:
python main.py --new          # Process new only
python main.py --follow-ups    # Send follow-ups only
python main.py --stats         # View statistics
```

## Common Commands

**Always activate virtual environment before running:**

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Test without sending
python main.py --dry-run

# Send follow-ups
python main.py --follow-ups

# View statistics
python main.py --stats

# Process new applications
python main.py --new
```

## Virtual Environment Cheat Sheet

```bash
# Activate virtual environment
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# Deactivate (when done)
deactivate

# Check if active (you'll see (venv) in your prompt)
# Example: (venv) user@computer:~/cv-mailer$

# Install dependencies
pip install -r requirements.txt

# Create new venv (if needed)
python3 -m venv venv
```

## Troubleshooting

**"Credentials file not found"**
- Ensure `credentials.json` is in project root
- Check file name spelling

**"Authentication failed"**
- Delete `token.pickle` and `gmail_token.pickle`
- Re-run to re-authenticate

**"Cannot read from Google Sheets"**
- Verify Spreadsheet ID is correct
- Ensure sheet is shared with your account
- Check worksheet name matches

**"Rate limit exceeded"**
- Increase delays in `.env`
- Reduce `DAILY_EMAIL_LIMIT`
- Wait 24 hours

## Next Steps

- Customize email templates in `email_templates.py`
- Adjust rate limits in `.env`
- Review tracking in database: `cv_mailer.db`
- Check logs: `cv_mailer.log`

## Safety Tips

1. **Always test with `--dry-run` first**
2. **Start with low email limits** (10-20/day)
3. **Review emails before sending** (check templates)
4. **Backup your Google Sheet** before first run
5. **Monitor logs** for errors

Happy job hunting! 🚀

