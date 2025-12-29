# Troubleshooting Guide

**Solutions to common CV Mailer issues.**

> 📖 **Quick Links**: [Quick Start](QUICK_START.md) | [Setup Guide](SETUP_GUIDE.md) | [Commands](COMMANDS.md)

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Authentication Issues](#authentication-issues)
- [Google Sheets Issues](#google-sheets-issues)
- [Gmail Issues](#gmail-issues)
- [Database Issues](#database-issues)
- [API Issues](#api-issues)
- [Frontend Issues](#frontend-issues)
- [General Issues](#general-issues)

---

## Installation Issues

### Command Not Found

**Problem:** `cv-mailer: command not found`

**Solutions:**

1. **Reinstall package:**

   ```bash
   pip install -e . --force-reinstall
   ```

2. **Activate virtual environment:**

   ```bash
   source venv/bin/activate
   ```

3. **Check installation:**

   ```bash
   pip show cv-mailer
   which cv-mailer
   ```

4. **Verify Python path:**

   ```bash
   python --version  # Should be 3.8+
   which python
   ```

---

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'cv_mailer'`

**Solutions:**

1. **Reinstall in editable mode:**

   ```bash
   pip uninstall cv-mailer
   pip install -e .
   ```

2. **Check virtual environment:**

   ```bash
   which python  # Should point to venv/bin/python
   source venv/bin/activate
   ```

3. **Verify installation:**

   ```bash
   pip show cv-mailer
   python -c "import cv_mailer; print(cv_mailer.__file__)"
   ```

---

### Permission Errors

**Problem:** Permission denied errors during installation

**Solutions:**

1. **Use virtual environment (recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Check file permissions:**

   ```bash
   chmod +x setup.sh
   ```

3. **Use user install (if needed):**

   ```bash
   pip install -e . --user
   ```

---

## Authentication Issues

### Credentials File Not Found

**Problem:** `FileNotFoundError: credentials.json not found`

**Solutions:**

1. **Download from Google Cloud Console:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - APIs & Services > Credentials
   - Create OAuth client ID (Desktop app)
   - Download JSON
   - Save as `credentials.json` in project root

2. **Verify file location:**

   ```bash
   ls -la credentials.json  # Should be in project root
   pwd  # Should show project root
   ```

3. **Check filename:**
   - Must be exactly `credentials.json` (case-sensitive)
   - Not `credentials.JSON` or `Credentials.json`

> 🔧 **Detailed OAuth setup:** See [OAuth Fix Guide](fix_enhancements/OAUTH_FIX.md)

---

### Authentication Failed

**Problem:** OAuth authentication fails or tokens expired

**Solutions:**

1. **Delete old tokens and re-authenticate:**

   ```bash
   rm token.pickle gmail_token.pickle
   cv-mailer --dry-run  # Will prompt for OAuth
   ```

2. **Check OAuth consent screen:**
   - Go to Google Cloud Console
   - APIs & Services > OAuth consent screen
   - Ensure app is configured
   - Add your email as test user

3. **Verify API scopes:**
   - Ensure these scopes are added:
     - `https://www.googleapis.com/auth/spreadsheets`
     - `https://www.googleapis.com/auth/gmail.send`

4. **Check credentials:**
   - Verify `credentials.json` is valid
   - Ensure OAuth client ID is "Desktop app" type

> 🔧 **OAuth troubleshooting:** See [OAuth Fix Guide](fix_enhancements/OAUTH_FIX.md)

---

### "This App Isn't Verified" Warning

**Problem:** Google shows "This app isn't verified" during OAuth

**Solution:**

This is **normal for personal projects**. Click:

1. "Advanced"
2. "Go to CV Mailer (unsafe)"
3. Continue with authorization

**To remove warning (optional):**

- Publish your app in Google Cloud Console
- Complete OAuth verification process
- See [Google OAuth Verification](https://support.google.com/cloud/answer/9110914)

---

## Google Sheets Issues

### Cannot Read from Google Sheets

**Problem:** `Error reading from Google Sheets` or empty data

**Solutions:**

1. **Verify Spreadsheet ID:**

   ```bash
   # Check .env file
   cat .env | grep SPREADSHEET_ID
   
   # Extract from URL:
   # https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

2. **Check sheet sharing:**
   - Open Google Sheet
   - Click "Share"
   - Ensure your Google account has access
   - Try "Anyone with the link" temporarily for testing

3. **Verify API is enabled:**
   - Go to Google Cloud Console
   - APIs & Services > Library
   - Ensure "Google Sheets API" is enabled

4. **Check worksheet name:**

   ```bash
   # If using single sheet mode
   cat .env | grep WORKSHEET_NAME
   # Should match exact sheet name (case-sensitive)
   ```

5. **Test connection:**

   ```bash
   cv-mailer --stats  # Should connect successfully
   ```

---

### Wrong Data Read from Sheets

**Problem:** Application reads incorrect columns or data

**Solutions:**

1. **Check column names:**
   - Required: `Company Name`, `Position`, `Recruiter Names`
   - See [Google Sheets Template](GOOGLE_SHEETS_TEMPLATE.md) for format

2. **Verify first row is headers:**
   - First row must contain column names
   - Data starts from row 2

3. **Check for empty rows:**
   - Remove completely empty rows
   - Ensure required fields are filled

4. **Multi-sheet mode:**

   ```bash
   # If using PROCESS_ALL_SHEETS=true
   # Ensure all sheets have same column structure
   ```

---

## Gmail Issues

### Rate Limit Exceeded

**Problem:** `Daily email limit reached` or Gmail API errors

**Solutions:**

1. **Check current limit:**

   ```bash
   cat .env | grep DAILY_EMAIL_LIMIT
   ```

2. **Increase delays:**

   ```env
   EMAIL_DELAY_MIN=1.0
   EMAIL_DELAY_MAX=2.0
   DAILY_EMAIL_LIMIT=20
   ```

3. **Wait 24 hours:**
   - Gmail has daily sending limits
   - Wait until next day to resume

4. **Check rate limit stats:**

   ```bash
   # Check database
   sqlite3 data/cv_mailer.db "SELECT * FROM daily_email_stats ORDER BY date DESC LIMIT 5;"
   ```

---

### Email Not Sending

**Problem:** Emails not being sent or no errors shown

**Solutions:**

1. **Check logs:**

   ```bash
   tail -f logs/cv_mailer.log
   ```

2. **Verify Gmail API:**
   - Check Google Cloud Console
   - Ensure "Gmail API" is enabled
   - Verify OAuth scopes include `gmail.send`

3. **Test with dry-run:**

   ```bash
   cv-mailer --dry-run  # Should show what would be sent
   ```

4. **Check email format:**
   - Verify recipient emails are valid
   - Check for typos in email addresses

5. **Verify resume file:**

   ```bash
   ls -la assets/your_resume.pdf  # Should exist
   cat .env | grep RESUME_FILE_PATH
   ```

---

## Database Issues

### Database Locked

**Problem:** `OperationalError: database is locked`

**Solutions:**

1. **Close other connections:**
   - Stop any running `cv-mailer` processes
   - Close database viewers
   - Wait a few seconds

2. **Check for running processes:**

   ```bash
   ps aux | grep cv-mailer
   kill <process_id>  # If found
   ```

3. **Restart:**

   ```bash
   # Close all connections, then retry
   cv-mailer --stats
   ```

---

### Database Not Found

**Problem:** `No such file or directory: data/cv_mailer.db`

**Solutions:**

1. **Create database:**

   ```bash
   mkdir -p data
   python -c "from cv_mailer.utils import init_database; init_database()"
   ```

2. **Check database path:**

   ```bash
   cat .env | grep DATABASE_PATH
   # Should be: data/cv_mailer.db
   ```

3. **Verify directory exists:**

   ```bash
   ls -la data/
   ```

---

## API Issues

### API Not Starting

**Problem:** `cv-mailer-api` command fails or server won't start

**Solutions:**

1. **Install API dependencies:**

   ```bash
   pip install -e ".[api]"
   ```

2. **Check port availability:**

   ```bash
   lsof -i :8000  # Check if port is in use
   # If in use, kill process or use different port
   ```

3. **Start with uvicorn directly:**

   ```bash
   uvicorn cv_mailer.api.app:app --reload
   ```

4. **Check logs:**

   ```bash
   tail -f logs/cv_mailer.log
   ```

---

### CORS Errors

**Problem:** Frontend can't connect to API (CORS errors)

**Solutions:**

1. **Verify API is running:**

   ```bash
   curl http://localhost:8000/health
   ```

2. **Check CORS settings:**
   - CORS is enabled by default
   - If issues persist, check `src/cv_mailer/api/app.py`

3. **Verify frontend proxy:**
   - Check `frontend/vite.config.ts`
   - Ensure proxy points to `http://localhost:8000`

---

## Frontend Issues

### Frontend Won't Start

**Problem:** `npm run dev` fails or errors

**Solutions:**

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Check Node.js version:**

   ```bash
   node --version  # Should be 18+
   ```

3. **Clear cache:**

   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Check API is running:**
   - Frontend requires API on port 8000
   - Start API first: `cv-mailer-api`

---

### Frontend Can't Connect to API

**Problem:** Frontend shows connection errors

**Solutions:**

1. **Verify API is running:**

   ```bash
   curl http://localhost:8000/health
   ```

2. **Check proxy configuration:**
   - See `frontend/vite.config.ts`
   - Ensure proxy target is correct

3. **Check browser console:**
   - Open browser DevTools
   - Check Network tab for errors
   - Look for CORS or connection errors

---

## General Issues

### Configuration Not Loading

**Problem:** Changes to `.env` not taking effect

**Solutions:**

1. **Restart application:**

   ```bash
   # Stop and restart
   cv-mailer --stats
   ```

2. **Verify .env location:**

   ```bash
   ls -la .env  # Should be in project root
   ```

3. **Check .env format:**

   ```bash
   # No spaces around =
   SPREADSHEET_ID=your_id  # ✅ Correct
   SPREADSHEET_ID = your_id  # ❌ Wrong
   ```

4. **Reload environment:**

   ```bash
   source venv/bin/activate
   ```

---

### Logs Not Appearing

**Problem:** No log output or log file not created

**Solutions:**

1. **Check log directory:**

   ```bash
   mkdir -p logs
   ls -la logs/
   ```

2. **Verify log path:**

   ```bash
   cat .env | grep LOG_FILE
   # Should be: logs/cv_mailer.log
   ```

3. **Check permissions:**

   ```bash
   touch logs/cv_mailer.log
   chmod 666 logs/cv_mailer.log
   ```

4. **Check log level:**

   ```bash
   cat .env | grep LOG_LEVEL
   # Try: DEBUG for more verbose logs
   ```

---

## Still Having Issues?

1. **Check logs:**

   ```bash
   tail -f logs/cv_mailer.log
   ```

2. **Review documentation:**
   - [Quick Start](QUICK_START.md)
   - [Setup Guide](SETUP_GUIDE.md)
   - [Commands](COMMANDS.md)

3. **Search existing issues:**
   - GitHub Issues: <https://github.com/lakshyads/cv-mailer/issues>

4. **Create new issue:**
   - Include error messages
   - Include log output
   - Describe steps to reproduce

---

## Related Documentation

- **[Quick Start](QUICK_START.md)** - Get started quickly
- **[Setup Guide](SETUP_GUIDE.md)** - Complete setup instructions
- **[Commands](COMMANDS.md)** - All available commands
- **[OAuth Fix Guide](fix_enhancements/OAUTH_FIX.md)** - OAuth-specific troubleshooting

---

**Need more help?** Check the [Setup Guide](SETUP_GUIDE.md) or open an issue on GitHub.
