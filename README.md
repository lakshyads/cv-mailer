# CV Mailer

An automated system for emailing resumes to recruiters with comprehensive tracking and follow-up management.

## 🚀 Quick Start

```bash
./setup.sh                    # Automated setup
source venv/bin/activate      # Activate virtual environment
cv-mailer --dry-run           # Test it out
cv-mailer                     # Start sending emails
```

👉 **New to CV Mailer?** Start with the [Quick Start Guide](docs/QUICK_START.md) (5 minutes)

## ✨ Features

- 🌐 **Web Dashboard** - Modern React UI for managing applications (NEW!)
- 📊 **Google Sheets Integration** - Read job applications from spreadsheets
- 📧 **Gmail Integration** - Send emails with built-in rate limiting
- 🔄 **Follow-up Management** - Automatic follow-ups based on your schedule
- 📈 **Comprehensive Tracking** - Track all communications and status updates
- 🎯 **Status Management**: Track applications through the entire lifecycle
- 📝 **Email Templates**: Professional email templates for first contact and follow-ups
- 👥 **Multi-Recruiter Support** - Contact multiple recruiters per job
- 📑 **Multi-Sheet Support** - Organize applications across multiple sheets
- 🚀 **REST API** - FastAPI-based API with OpenAPI docs
- 📦 **Modern Package** - Proper Python packaging with pip installation

## 📚 Documentation

**📖 [Complete Documentation Index](docs/INDEX.md)** - Start here for all documentation

### Quick Links

- **[Quick Start Guide](docs/QUICK_START.md)** ⚡ - Get running in 5 minutes
- **[Setup Guide](docs/SETUP_GUIDE.md)** 🔧 - Detailed setup instructions
- **[Web Dashboard Guide](docs/WEB_DASHBOARD_GUIDE.md)** 🌐 - Web UI usage
- **[API Guide](docs/API_GUIDE.md)** 🚀 - REST API documentation
- **[Changelog](docs/CHANGELOG.md)** 📝 - What's new and changed
- **[Architecture](docs/design/ARCHITECTURE.md)** 🏗️ - System design
- **[Roadmap](docs/design/FEATURE_SUGGESTIONS.md)** 🎯 - Planned features

## 🏗️ Architecture

**Production-ready, enterprise-grade architecture with single source of truth:**

```text
Presentation Layer (CLI + API)
    ↓ (Both call same services)
Service Layer (Business Logic) ⭐ SINGLE SOURCE OF TRUTH
    ↓
Repository Layer (Data Access)
    ↓
Database (SQLite with indexes)
```

**Key Principle:** All business logic resides in the service layer.  
Both CLI and API use the same service methods → No duplication, always in sync.

📖 **Architecture Docs:**
- **[Proper Architecture](PROPER_ARCHITECTURE.md)** ⭐ Complete architecture guide
- **[Architecture Summary](FINAL_ARCHITECTURE_SUMMARY.md)** Quick overview
- **[Design Details](docs/design/ARCHITECTURE.md)** Technical details

## 📦 Installation

### Quick Install (Recommended)

```bash
./setup.sh
```

### Manual Install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[api]"
```

See [Setup Guide](docs/SETUP_GUIDE.md) for complete instructions.

## 💻 Usage

### CLI Commands

> Activate virtual environment first
> `source venv/bin/activate`

```bash
cv-mailer                 # Process new applications
cv-mailer --dry-run       # Test without sending
cv-mailer --follow-ups    # Send follow-ups only
cv-mailer --stats         # Show statistics
```

### API Server

> Activate virtual environment first
> `source venv/bin/activate`

```bash
cv-mailer-api             # Start REST API
# Visit http://localhost:8000/docs for interactive docs
```

### Web Dashboard

> Start the API first, then run the dashboard

```bash
# Terminal 1: Start API
source venv/bin/activate
cv-mailer-api

# Terminal 2: Start Dashboard
cd frontend
npm install  # First time only
npm run dev
# Visit http://localhost:3000
```

See [Web Dashboard Guide](docs/WEB_DASHBOARD_GUIDE.md) for complete instructions.

## 🔧 Configuration

Create `.env` file (copy from `.env.example`):

```env
SPREADSHEET_ID=your_spreadsheet_id
GMAIL_USER=your_email@gmail.com
SENDER_NAME=Your Name
RESUME_FILE_PATH=./assets/resume.pdf
```

See [Setup Guide](docs/SETUP_GUIDE.md#step-3-configure-environment-variables) for all configuration options.

## 🗂️ Project Structure

```text
cv-mailer/
├── src/cv_mailer/     # Main package
├── docs/              # Documentation
├── data/              # Database files
├── logs/              # Application logs
└── assets/            # Resume files
```

## 🐛 Troubleshooting

| Issue | Solution |
| ----- | -------- |
| Authentication failed | See [OAuth Fix Guide](docs/OAUTH_FIX.md) |
| Command not found | Run `pip install -e .` again |
| Rate limit exceeded | Increase delays in `.env` |
| Can't read Sheets | Verify `SPREADSHEET_ID` and sharing |

See [Setup Guide - Troubleshooting](docs/SETUP_GUIDE.md#troubleshooting) for more help.

## 🔐 Security

- Never commit `credentials.json`, `.env`, or `*.pickle` files
- Use environment variables for sensitive data
- Keep OAuth tokens secure
- Regular database backups recommended

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow code style (Black, isort)
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support

- **Issues**: <https://github.com/lakshyads/cv-mailer/issues>
- **Documentation**: See `docs/` directory
- **Email**: <lakshyads.96@gmail.com>

## 🙏 Credits

Developed by **Lakshya Dev Singh**

- GitHub: [@lakshyads](https://github.com/lakshyads)
- Email: <lakshyads.96@gmail.com>

---

**Version**: 1.0.0 | **Status**: Production Ready
