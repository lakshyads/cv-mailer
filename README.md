# CV Mailer

An automated system for emailing resumes to recruiters with comprehensive tracking and follow-up management.

## Features

- 📊 **Google Sheets Integration**: Read job postings and recruiter details from Google Sheets
- 📧 **Gmail Integration**: Send emails directly from your Gmail account
- 📎 **Resume Attachments**: Attach resume files or include Google Drive links
- 🔄 **Follow-up Management**: Automatically track and send follow-up emails
- 📈 **Comprehensive Tracking**: Track all communications, responses, and application status
- ⚡ **Rate Limiting**: Built-in rate limiting to avoid Gmail throttling
- 🎯 **Status Management**: Track applications through the entire lifecycle (draft → reached out → interview → closed)
- 📝 **Email Templates**: Professional email templates for first contact and follow-ups

## Architecture

The application is built with a modular architecture:

- **`config.py`**: Configuration management with environment variables
- **`models.py`**: Database models for tracking (SQLite)
- **`google_sheets.py`**: Google Sheets API integration
- **`gmail_sender.py`**: Gmail API integration with rate limiting
- **`email_templates.py`**: Email template system (Jinja2)
- **`tracker.py`**: Application tracking and status management
- **`main.py`**: Main orchestrator and CLI interface

## Prerequisites

1. **Python 3.8+**
2. **Virtual Environment** (recommended - will be created during setup)
3. **Google Cloud Project** with APIs enabled:
   - Google Sheets API
   - Gmail API
4. **Google OAuth Credentials** (download as `credentials.json`)

**Note**: This project uses a Python virtual environment to manage dependencies. Always activate it before running commands (see Usage section below).

## Setup

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Sheets API
   - Gmail API
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app"
   - Download the JSON file and save it as `credentials.json` in the project root

### 3. Google Sheets Setup

1. Create a Google Sheet with the following columns (adjust as needed):
   - `Company Name`
   - `Position`
   - `Recruiter Name`
   - `Recruiter Email`
   - `Location` (optional)
   - `Job Posting URL` (optional)
   - `Status` (optional - will be auto-updated)

2. Share the sheet with the service account email (if using service account) or ensure your OAuth account has access

3. Get the Spreadsheet ID from the URL:

   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

### 4. Configuration

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings:

   ```env
   SPREADSHEET_ID=your_spreadsheet_id_here
   WORKSHEET_NAME=Sheet1
   GMAIL_USER=your_email@gmail.com
   SENDER_NAME=Your Name
   RESUME_FILE_PATH=./resume.pdf
   # OR
   RESUME_DRIVE_LINK=https://drive.google.com/file/d/...
   ```

### 5. Resume Setup

You can either:

- Place your resume PDF in the project directory and set `RESUME_FILE_PATH`
- Upload to Google Drive and set `RESUME_DRIVE_LINK` (make sure it's shareable)

## Usage

### ⚠️ Important: Activate Virtual Environment First

**Always activate the virtual environment before running commands:**

```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# You should see (venv) in your terminal prompt
```

### Basic Usage

Process new applications from Google Sheets:

```bash
# Make sure venv is activated first!
python main.py
```

### Command Line Options

```bash
# Dry run (test without sending emails)
python main.py --dry-run

# Send follow-up emails only
python main.py --follow-ups

# Show statistics
python main.py --stats

# Process new applications only
python main.py --new
```

### Virtual Environment Quick Reference

```bash
# Activate virtual environment
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# Deactivate virtual environment
deactivate

# Check if venv is active (look for (venv) in prompt)
# If you don't see (venv), activate it first!

# Install/update dependencies
pip install -r requirements.txt

# Create new virtual environment (if needed)
python3 -m venv venv
```

### First Run

On first run, the application will:

1. Open a browser for OAuth authentication
2. Ask you to authorize access to Google Sheets and Gmail
3. Save the credentials for future use

## Gmail Rate Limits

Gmail has rate limits to prevent abuse:

- **Free Gmail accounts**: ~500 emails/day
- **Google Workspace**: ~2000 emails/day

The application includes:

- Configurable delays between emails (default: 60-120 seconds)
- Daily email limit tracking (default: 50/day, adjust in `.env`)
- Automatic rate limiting

**Important**: Start with conservative limits and gradually increase. Gmail may throttle or suspend accounts that send too many emails too quickly.

## Database

The application uses SQLite to track:

- Job applications
- Email records (sent, failed, bounced)
- Follow-up tracking
- Response records
- Daily email statistics

Database file: `cv_mailer.db` (created automatically)

## Email Templates

### First Contact Email

Includes:

- Personalized greeting
- Position and company information
- Resume attachment or drive link
- Professional closing

### Follow-up Email

Includes:

- Reference to previous email
- Continued interest expression
- Request for updates

Templates can be customized in `email_templates.py`.

## Application Status Flow

```
DRAFT → REACHED_OUT → APPLIED → INTERVIEW_SCHEDULED → IN_PROGRESS → CLOSED
                                                      ↓
                                                   REJECTED
                                                   ACCEPTED
```

## Tracking Features

The system tracks:

- ✅ When emails were sent
- ✅ Email type (first contact vs follow-up)
- ✅ Follow-up count and timing
- ✅ Application status
- ✅ Response tracking
- ✅ Daily email statistics

## Future Enhancements

Planned features:

- Web UI for managing applications
- Email response parsing
- Calendar integration for interviews
- Analytics dashboard
- Multi-resume support
- Custom email templates per job type

## Troubleshooting

### Authentication Issues

If you see authentication errors:

1. Delete `token.pickle` and `gmail_token.pickle`
2. Re-run the application to re-authenticate
3. Ensure `credentials.json` is in the project root

### Rate Limiting

If emails are being throttled:

1. Increase `EMAIL_DELAY_MIN` and `EMAIL_DELAY_MAX` in `.env`
2. Decrease `DAILY_EMAIL_LIMIT`
3. Wait 24 hours before resuming

### Google Sheets Access

If you can't read from Google Sheets:

1. Ensure the sheet is shared with your Google account
2. Check that `SPREADSHEET_ID` is correct
3. Verify `WORKSHEET_NAME` matches your sheet tab name

## Security Best Practices

1. **Never commit credentials**: `credentials.json`, `.env`, and `*.pickle` files are in `.gitignore`
2. **Use environment variables**: Keep sensitive data in `.env`
3. **Limit permissions**: Only grant necessary OAuth scopes
4. **Regular backups**: Backup your database file regularly

## License

This project is open source and available for personal use.

## Contributing

Feel free to submit issues and enhancement requests!

## Support

For issues or questions, please open an issue on the project repository.
