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

See [Changelog](docs/CHANGELOG.md) for complete feature list and recent improvements.

**Key Features:**

- 🌐 **Web Dashboard** - Modern React UI for managing applications
- 📊 **Google Sheets Integration** - Read job applications from spreadsheets
- 📧 **Gmail Integration** - Send emails with built-in rate limiting
- 🔄 **Follow-up Management** - Automatic follow-ups based on your schedule
- 🚀 **REST API** - FastAPI-based API with OpenAPI docs
- ⚡ **Production-Ready** - Enterprise-grade architecture and code quality

**For complete feature details:** See [Changelog](docs/CHANGELOG.md) | [Roadmap](docs/roadmap/ROADMAP.md)

## 📚 Documentation

**📖 [Complete Documentation Index](docs/INDEX.md)** - Start here for all documentation

### Quick Links

- **[Quick Start Guide](docs/QUICK_START.md)** ⚡ - Get running in 5 minutes
- **[Setup Guide](docs/SETUP_GUIDE.md)** 🔧 - Detailed setup instructions
- **[Web Dashboard Guide](docs/WEB_DASHBOARD_GUIDE.md)** 🌐 - Web UI usage
- **[API Guide](docs/API_GUIDE.md)** 🚀 - REST API documentation
- **[Changelog](docs/CHANGELOG.md)** 📝 - What's new and changed
- **[Architecture](docs/design/ARCHITECTURE.md)** 🏗️ - System design
- **[Roadmap](docs/roadmap/ROADMAP.md)** 🎯 - Planned features

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

- **[Architecture Guide](docs/design/ARCHITECTURE.md)** ⭐ Complete architecture documentation

## 📦 Installation

See [Quick Start Guide](docs/QUICK_START.md) for 5-minute setup or [Complete Setup Guide](docs/SETUP_GUIDE.md) for detailed instructions.

## 💻 Usage

See [Command Reference](docs/COMMANDS.md) for all available commands.

**Quick Commands:**

- `cv-mailer` - Process new applications
- `cv-mailer-api` - Start REST API server
- `cd frontend && npm run dev` - Start web dashboard

**For complete usage:** See [Command Reference](docs/COMMANDS.md) | [API Guide](docs/API_GUIDE.md) | [Web Dashboard Guide](docs/WEB_DASHBOARD_GUIDE.md)

## 🔧 Configuration

See [Setup Guide - Configuration](docs/SETUP_GUIDE.md#step-3-configure-environment-variables) for complete configuration options.

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

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for solutions to common issues.

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

**Version**: 1.1.0 | **Status**: Production Ready
