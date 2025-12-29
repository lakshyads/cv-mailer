# Complete Setup Guide

Complete step-by-step setup guide for CV Mailer. For a quick start, see [Quick Start Guide](QUICK_START.md).

## Prerequisites

- Python 3.8 or higher
- Google account
- Google Sheet with job applications
- Resume file (PDF) or Google Drive link

## Step 1: Install the Package

### Option A: Automated Setup (Recommended)

```bash
./setup.sh
```

The script automatically:

- Creates virtual environment
- Installs package in editable mode
- Creates directories (`data/`, `logs/`, `assets/`)
- Sets up `.env` from template
- Makes `cv-mailer` command available

### Option B: Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -e .           # Basic install
# Or:
pip install -e ".[api]"    # With API dependencies
pip install -e ".[dev]"    # With dev tools
mkdir -p data logs assets
```

**Note**: Editable mode (`-e`) means code changes are immediately available without reinstalling.

## Step 2: Google Cloud Setup

### 2.1 Create Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click project dropdown → "New Project"
3. Name it "CV Mailer" → Click "Create"

### 2.2 Enable APIs

1. APIs & Services > Library
2. Enable:
   - **Google Sheets API**
   - **Gmail API**

### 2.3 Configure OAuth Consent Screen

1. APIs & Services > OAuth consent screen
2. User Type: **External** (personal Gmail) or **Internal** (Workspace)
3. Fill required fields:
   - App name: "CV Mailer"
   - Support email: Your email
   - Developer email: Your email
4. Click "Save and Continue"
5. Scopes → Add:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/gmail.send`
6. Click "Save and Continue"
7. Test users → Add your email
8. Click "Save and Continue"

> 💡 **Troubleshooting OAuth?** See [OAuth Fix Guide](OAUTH_FIX.md)

### 2.4 Create OAuth Credentials

1. APIs & Services > Credentials
2. Create Credentials > OAuth client ID
3. Application type: **Desktop app**
4. Name: "CV Mailer Desktop Client"
5. Click "Create" → "Download JSON"
6. Save as `credentials.json` in project root

## Step 3: Configure Environment Variables

Create `.env` file:

```bash
cp .env.example .env
```

### Required Settings

```env
SPREADSHEET_ID=your_spreadsheet_id_here
GMAIL_USER=your_email@gmail.com
SENDER_NAME=Your Full Name
```

### Optional Settings

```env
# Resume (at least one required)
RESUME_FILE_PATH=./assets/your_resume.pdf
RESUME_DRIVE_LINK=https://drive.google.com/file/d/...

# Contact info (for email signatures)
LINKEDIN_PROFILE=https://www.linkedin.com/in/your-handle
CONTACT_INFORMATION=your_email@gmail.com | +1-XXX-XXX-XXXX

# Multi-sheet support
PROCESS_ALL_SHEETS=true
SHEET_NAME_FILTER=2024  # Optional regex filter
WORKSHEET_NAME=Sheet1   # If PROCESS_ALL_SHEETS=false

# Rate limiting
EMAIL_DELAY_MIN=0.1     # Delay between emails (seconds)
EMAIL_DELAY_MAX=0.5
DAILY_EMAIL_LIMIT=50    # Max emails per day

# Follow-ups
FOLLOW_UP_DAYS=7        # Days before follow-up
MAX_FOLLOW_UPS=3        # Max follow-ups per application

# Paths
DATABASE_PATH=data/cv_mailer.db
LOG_FILE=logs/cv_mailer.log
LOG_LEVEL=INFO
```

### Getting Spreadsheet ID

From your Google Sheet URL:

```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
```

Copy the `SPREADSHEET_ID` part into `.env`.

### Resume Setup Options

**Option 1: Both (Recommended)**

- Place PDF in `assets/` folder
- Upload to Google Drive (shareable link)
- Set both `RESUME_FILE_PATH` and `RESUME_DRIVE_LINK`
- Email will have attachment AND link

**Option 2: File Only**

- Set `RESUME_FILE_PATH=./assets/resume.pdf`
- Leave `RESUME_DRIVE_LINK` empty

**Option 3: Drive Link Only**

- Set `RESUME_DRIVE_LINK=...`
- Leave `RESUME_FILE_PATH` empty

## Step 4: Set Up Google Sheet

### Required Columns

- `Company Name` (required)
- `Position` (required)
- `Recruiter Name` or `Recruiter Names` (required)
- `Recruiter Email` (optional, can be in Name column)

### Optional Columns

- `Location`
- `Job Posting URL`
- `Status` (auto-updated)
- `Expected Salary`
- `Message` (custom message)

> 📋 **Detailed sheet format**: See [Google Sheets Template Guide](GOOGLE_SHEETS_TEMPLATE.md)

### Multi-Recruiter and Multi-Sheet Support

See [Google Sheets Template](GOOGLE_SHEETS_TEMPLATE.md) for complete details on:

- Multi-recruiter format
- Multi-sheet configuration
- Column requirements

## Step 5: First Authentication

Run a dry-run to authenticate:

```bash
cv-mailer --dry-run
```

This will:

1. Open browser for OAuth
2. Sign in with Google
3. Authorize Sheets and Gmail access
4. Save credentials (`token.pickle`, `gmail_token.pickle`)

**Note**: If you see "This app isn't verified", click "Advanced" → "Go to CV Mailer (unsafe)" - normal for personal projects.

## Step 6: Verify Setup

### Check Installation

```bash
cv-mailer --help
```

Should show command options.

### Test Connection

```bash
cv-mailer --stats
```

Should connect successfully (empty stats initially).

### Dry Run

```bash
cv-mailer --dry-run
```

Shows what emails would be sent without actually sending. Review carefully!

## Step 7: Send Your First Emails

After verifying:

```bash
cv-mailer              # Process new applications
cv-mailer --new        # New applications only
cv-mailer --follow-ups # Follow-ups only
```

## Using the REST API

### Install API Dependencies

```bash
pip install -e ".[api]"
```

### Start Server

```bash
cv-mailer-api
# Visit http://localhost:8000/docs
```

> 📚 **Complete API docs**: See [API Guide](API_GUIDE.md)

## Command Reference

See [Command Reference](COMMANDS.md) for complete list of all commands.

## Troubleshooting

See [Troubleshooting Guide](TROUBLESHOOTING.md) for solutions to all common issues.

**Quick fixes:**

- **Credentials not found** → Download from Google Cloud Console
- **Authentication failed** → Delete `token.pickle` and `gmail_token.pickle`, re-run
- **Cannot read Sheets** → Verify `SPREADSHEET_ID` and sheet sharing
- **Command not found** → Run `pip install -e .` again
- **OAuth issues** → See [OAuth Fix Guide](fix_enhancements/OAUTH_FIX.md)

## Project Structure

After installation:

```
cv-mailer/
├── src/cv_mailer/     # Package source code
├── data/              # Database files (cv_mailer.db)
├── logs/              # Application logs
├── assets/            # Resume files
├── credentials.json   # OAuth credentials
├── .env               # Configuration
└── docs/              # Documentation
```

> 🏗️ **Architecture details**: See [Architecture Overview](design/ARCHITECTURE.md)

## Development Setup

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

Includes: pytest, black, isort, flake8, mypy

### Code Quality

```bash
black src/        # Format
isort src/        # Sort imports
mypy src/         # Type check
flake8 src/       # Lint
pytest            # Test
```

## Security

- ✅ Never commit `credentials.json`, `.env`, or `*.pickle`
- ✅ Keep `.env` secure
- ✅ Don't share OAuth tokens
- ✅ Regular database backups
- ✅ Review sent emails before sending (`--dry-run`)

## Next Steps

1. ✅ Test thoroughly: `cv-mailer --dry-run`
2. ✅ Start small: 5-10 applications first
3. ✅ Monitor logs: `logs/cv_mailer.log`
4. ✅ Customize templates: `src/cv_mailer/services/template_service.py`
5. ✅ Explore API: `cv-mailer-api` → <http://localhost:8000/docs>

## Additional Resources

- **[Quick Start Guide](QUICK_START.md)** - 5-minute setup
- **[Google Sheets Template](GOOGLE_SHEETS_TEMPLATE.md)** - Sheet format reference
- **[API Guide](API_GUIDE.md)** - Complete API documentation
- **[Architecture](design/ARCHITECTURE.md)** - System design
- **[Feature Roadmap](design/FEATURE_SUGGESTIONS.md)** - Future enhancements

---

**Need help?** Check the troubleshooting section above or open an issue on GitHub.

Good luck with your job applications! 🚀
