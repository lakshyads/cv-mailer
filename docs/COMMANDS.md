# Command Reference

**Complete reference for all CV Mailer commands.**

> 📖 **Quick Links**: [Quick Start](QUICK_START.md) | [Setup Guide](SETUP_GUIDE.md) | [API Guide](API_GUIDE.md)

---

## CLI Commands

### Basic Commands

#### Process New Applications

```bash
cv-mailer
```

Processes new job applications from Google Sheets and sends first contact emails.

**What it does:**

- Reads applications from Google Sheets
- Creates/updates records in database
- Sends first contact emails to recruiters
- Updates sheet status to "Reached Out"

**Options:**

- `--dry-run` - Test mode (don't send emails)
- `--new` - Process only new applications

**Example:**

```bash
cv-mailer --dry-run  # Test first
cv-mailer             # Then send
```

---

#### Send Follow-ups

```bash
cv-mailer --follow-ups
```

Sends follow-up emails to applications that need them.

**What it does:**

- Finds applications needing follow-up (based on `FOLLOW_UP_DAYS`)
- Validates timing and status
- Sends follow-up emails
- Respects `MAX_FOLLOW_UPS` limit

**Options:**

- `--dry-run` - Test mode

**Example:**

```bash
cv-mailer --follow-ups --dry-run  # Test first
cv-mailer --follow-ups             # Then send
```

---

#### View Statistics

```bash
cv-mailer --stats
```

Displays application statistics in the terminal.

**Shows:**

- Total applications
- Applications by status
- Total emails sent
- Follow-up statistics
- Interview and offer statistics

**Example:**

```bash
cv-mailer --stats
```

---

#### Repair Follow-up Numbers

```bash
cv-mailer --repair-followups [--dry-run]
```

Repairs follow-up numbering for multi-recruiter applications.

**What it does:**

- Scans all applications with follow-ups
- Renumbers follow-up "waves" sequentially
- Preserves chronological order

**Options:**

- `--dry-run` - Show what would change without making changes

**Example:**

```bash
cv-mailer --repair-followups --dry-run  # Preview changes
cv-mailer --repair-followups             # Apply fixes
```

---

#### Help

```bash
cv-mailer --help
```

Shows all available commands and options.

---

## API Commands

### Start API Server

```bash
cv-mailer-api
```

Starts the FastAPI server on `http://localhost:8000`.

**Options:**

- Default port: 8000
- Auto-reload: Enabled in development
- Interactive docs: <http://localhost:8000/docs>

**Example:**

```bash
# Start server
cv-mailer-api

# In another terminal, test it
curl http://localhost:8000/health
```

**Using uvicorn directly:**

```bash
uvicorn cv_mailer.api.app:app --reload
uvicorn cv_mailer.api.app:app --host 0.0.0.0 --port 8080
```

---

## Package Management Commands

### Installation

```bash
# Basic installation
pip install -e .

# With API dependencies
pip install -e ".[api]"

# With development tools
pip install -e ".[dev]"

# Force reinstall
pip install -e . --force-reinstall
```

### Uninstallation

```bash
pip uninstall cv-mailer
```

### Verify Installation

```bash
# Check if installed
pip show cv-mailer

# Test command availability
cv-mailer --help
```

---

## Environment Setup Commands

### Activate Virtual Environment

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Deactivate Virtual Environment

```bash
deactivate
```

### Create Virtual Environment

```bash
python3 -m venv venv
```

---

## Development Commands

### Code Quality

```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/

# Linting
flake8 src/

# Run tests
pytest
```

### Database Management

```bash
# Initialize database
python -c "from cv_mailer.utils import init_database; init_database()"

# Check database
sqlite3 data/cv_mailer.db ".tables"
```

---

## Common Workflows

### First-Time Setup

```bash
# 1. Setup
./setup.sh

# 2. Activate environment
source venv/bin/activate

# 3. Test connection
cv-mailer --stats

# 4. Dry run
cv-mailer --dry-run

# 5. Send emails
cv-mailer
```

### Daily Workflow

```bash
# 1. Check stats
cv-mailer --stats

# 2. Process new applications
cv-mailer --dry-run  # Review first
cv-mailer             # Then send

# 3. Send follow-ups
cv-mailer --follow-ups
```

### Development Workflow

```bash
# 1. Start API
cv-mailer-api

# 2. In another terminal, start frontend
cd frontend
npm run dev

# 3. Access dashboard
# http://localhost:3000
```

---

## Command Options Reference

### Global Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Test mode (no emails sent, no database changes) |
| `--help` | Show help message |
| `--version` | Show version number |

### Environment Variables

Commands respect these environment variables (from `.env`):

- `SPREADSHEET_ID` - Google Sheet ID
- `GMAIL_USER` - Gmail address
- `SENDER_NAME` - Your name
- `RESUME_FILE_PATH` - Path to resume PDF
- `FOLLOW_UP_DAYS` - Days before follow-up
- `DAILY_EMAIL_LIMIT` - Max emails per day
- `EMAIL_DELAY_MIN` / `EMAIL_DELAY_MAX` - Delay between emails

See [Setup Guide - Configuration](SETUP_GUIDE.md#step-3-configure-environment-variables) for all options.

---

## Troubleshooting Commands

### Authentication Issues

```bash
# Delete tokens and re-authenticate
rm token.pickle gmail_token.pickle
cv-mailer --dry-run  # Will prompt for OAuth
```

### Command Not Found

```bash
# Reinstall package
pip install -e . --force-reinstall

# Or activate virtual environment
source venv/bin/activate
```

### Check Installation

```bash
# Verify package
pip show cv-mailer

# Test command
cv-mailer --help

# Check Python path
which python
python --version
```

---

## Related Documentation

- **[Quick Start](QUICK_START.md)** - Get started in 5 minutes
- **[Setup Guide](SETUP_GUIDE.md)** - Complete setup instructions
- **[API Guide](API_GUIDE.md)** - REST API documentation
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

---

**Need help?** Check [Troubleshooting Guide](TROUBLESHOOTING.md) or [Setup Guide](SETUP_GUIDE.md).
