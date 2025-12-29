# Quick Start Guide

Get CV Mailer running in 5 minutes! 🚀

> 📖 **Need more details?** See the [Complete Setup Guide](SETUP_GUIDE.md)

## Prerequisites

- Python 3.8+
- Google account
- Google Sheet with job applications
- Resume file (PDF)

## Step 1: Install (1 minute)

```bash
./setup.sh
```

This automatically:

- Creates virtual environment
- Installs the package
- Sets up directories
- Creates `.env` from template

## Step 2: Google Cloud Setup (3 minutes)

1. **Create Project**
   - Go to <https://console.cloud.google.com/>
   - Create new project

2. **Enable APIs**
   - APIs & Services > Library
   - Enable: **Google Sheets API** + **Gmail API**

3. **Get Credentials**
   - APIs & Services > Credentials
   - Create Credentials > OAuth client ID
   - Choose "Desktop app"
   - Download JSON → save as `credentials.json` in project root

> 💡 **OAuth Consent Screen**: See [Setup Guide](SETUP_GUIDE.md#step-2-google-cloud-setup) for detailed OAuth setup

## Step 3: Configure (30 seconds)

Edit `.env`:

```env
SPREADSHEET_ID=your_spreadsheet_id_here
GMAIL_USER=your_email@gmail.com
SENDER_NAME=Your Name
RESUME_FILE_PATH=./assets/your_resume.pdf
```

> 📋 **Need all options?** See [Setup Guide - Configuration](SETUP_GUIDE.md#step-3-configure-environment-variables)

## Step 4: Set Up Google Sheet (30 seconds)

Required columns:

- `Company Name` (required)
- `Position` (required)
- `Recruiter Name` or `Recruiter Names` (required)

> 📊 **Sheet format details**: See [Google Sheets Template Guide](GOOGLE_SHEETS_TEMPLATE.md)

## Step 5: Test & Run

```bash
# Test without sending emails
cv-mailer --dry-run

# First run will open browser for OAuth
# Authorize access → credentials saved

# Send emails
cv-mailer
```

## Common Commands

See [Command Reference](COMMANDS.md) for all available commands.

**Quick Commands:**
- `cv-mailer --dry-run` - Test mode
- `cv-mailer --follow-ups` - Send follow-ups
- `cv-mailer --stats` - View statistics

## Quick Troubleshooting

See [Troubleshooting Guide](TROUBLESHOOTING.md) for solutions to common issues.

**Common Issues:**
- `credentials.json not found` → Download from Google Cloud Console
- `Authentication failed` → Delete `token.pickle` and `gmail_token.pickle`, re-run
- `Cannot read Sheets` → Check `SPREADSHEET_ID` and sheet sharing
- `cv-mailer command not found` → Run `pip install -e .` again

## Next Steps

- ✅ **Customize templates**: `src/cv_mailer/services/template_service.py`
- ✅ **Start API server**: `cv-mailer-api` → <http://localhost:8000/docs>
- ✅ **Read full docs**: [Setup Guide](SETUP_GUIDE.md), [API Guide](API_GUIDE.md)

## Multi-Features

**Multi-Sheet** and **Multi-Recruiter** support: See [Google Sheets Template](GOOGLE_SHEETS_TEMPLATE.md) for complete details.

---

**That's it!** You're ready to automate your job applications. 🎉

**Need help?** Check the [Complete Setup Guide](SETUP_GUIDE.md) for detailed instructions.
