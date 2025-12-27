# Migration Guide: Old → New Structure

## Overview

The CV Mailer project has been refactored from a flat structure to a modern, scalable package structure. This document explains what changed, how to use the new structure, and ensures backward compatibility.

## What Changed?

### Old Structure (Flat)

```sh
cv-mailer/
├── config.py
├── models.py
├── tracker.py
├── gmail_sender.py
├── google_sheets.py
├── email_templates.py
├── recruiter_parser.py
├── main.py
└── utils.py
```

### New Structure (Modular)

```sh
cv-mailer/
├── src/cv_mailer/          # Main package
│   ├── core/               # Domain models & enums
│   ├── config/             # Configuration
│   ├── services/           # Business logic
│   ├── integrations/       # External APIs
│   │   ├── gmail/
│   │   └── google_sheets/
│   ├── parsers/            # Data parsers
│   ├── utils/              # Utilities
│   ├── cli/                # CLI application
│   └── api/                # REST API (new!)
│       └── routers/
├── tests/                  # Test suite
├── docs/                   # Documentation
├── data/                   # Database files
├── logs/                   # Log files
├── pyproject.toml          # Modern package config
├── setup.py                # Package setup
└── main.py                 # Entry point (backward compatible)
```

## Benefits of New Structure

1. **Clear Separation**: Each directory has a single responsibility
2. **API-Ready**: FastAPI skeleton ready for web UI
3. **Testable**: Proper structure for unit/integration tests
4. **Scalable**: Easy to add new features without clutter
5. **Professional**: Follows Python packaging best practices
6. **Installable**: Can install as `pip install -e .`

## How to Use

### Installation

```bash
# Install in editable mode (for development)
pip install -e .

# Or with API dependencies
pip install -e ".[api]"

# Or with development dependencies
pip install -e ".[dev]"
```

### Running the CLI

```bash
# Old way (still works!)
python main.py

# New way (after install)
cv-mailer --help
cv-mailer --dry-run
cv-mailer --stats
```

### Running the API (New!)

```bash
# Install with API dependencies first
pip install -e ".[api]"

# Run the API server
cv-mailer-api
# Or
python -m cv_mailer.api.app
```

API will be available at:

- **Docs**: <http://localhost:8000/docs>
- **Health**: <http://localhost:8000/health>
- **Applications**: <http://localhost:8000/api/v1/applications>
- **Statistics**: <http://localhost:8000/api/v1/statistics>

## Import Changes

### For Python Code

Old imports still work via compatibility layer:

```python
# Old way (still works)
from config import Config
from models import JobApplication, JobStatus
from tracker import ApplicationTracker
from gmail_sender import GmailSender

# New way (recommended)
from cv_mailer.config import Config
from cv_mailer.core import JobApplication, JobStatus
from cv_mailer.services import ApplicationTracker
from cv_mailer.integrations import GmailSender
```

### Public API

```python
# You can import directly from cv_mailer
from cv_mailer import (
    Config,
    JobStatus,
    ApplicationTracker,
    GmailSender,
    GoogleSheetsClient,
    init_database,
)
```

## Database Location

Database files now go in `data/` directory (configurable):

```env
# In .env file
DATABASE_PATH=data/cv_mailer.db
LOG_FILE=logs/cv_mailer.log
```

## API Endpoints

The new API provides RESTful endpoints:

### Applications

- `GET /api/v1/applications` - List all applications
- `GET /api/v1/applications/{id}` - Get specific application
- `PUT /api/v1/applications/{id}/status` - Update status

### Emails

- `GET /api/v1/applications/{id}/emails` - Get emails for application
- `GET /api/v1/emails` - List all emails

### Recruiters

- `GET /api/v1/recruiters` - List recruiters
- `GET /api/v1/recruiters/{id}` - Get recruiter details

### Statistics

- `GET /api/v1/statistics` - Get full statistics
- `GET /api/v1/statistics/summary` - Get summary stats

## Development Workflow

### Adding New Features

1. **Add a new service**:

   ```sh
   src/cv_mailer/services/my_service.py
   ```

2. **Add a new API endpoint**:

   ```sh
   src/cv_mailer/api/routers/my_resource.py
   ```

3. **Add a new integration**:

   ```sh
   src/cv_mailer/integrations/linkedin/
   ```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (when added)
pytest
pytest --cov=cv_mailer
```

### Code Quality

```bash
# Format code
black src/

# Check types
mypy src/

# Lint
flake8 src/

# Sort imports
isort src/
```

## Breaking Changes

### None

All existing functionality works exactly as before. The CLI commands are identical. Database format is unchanged.

### Optional Upgrades

1. **Use new imports** for cleaner code
2. **Install package** for easier command access
3. **Use API** for web UI integration

## Migration Checklist

- [x] ✅ Directory structure created
- [x] ✅ Core models migrated
- [x] ✅ Configuration migrated
- [x] ✅ Services migrated
- [x] ✅ Integrations migrated
- [x] ✅ CLI migrated
- [x] ✅ Package config created
- [x] ✅ API skeleton created
- [x] ✅ Entry points configured
- [x] ✅ Backward compatibility maintained
- [x] ✅ Installation tested
- [x] ✅ CLI tested

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:

```bash
pip install -e .
```

### Command Not Found

If `cv-mailer` command is not found:

```bash
# Reinstall with scripts
pip install --force-reinstall -e .

# Or use python -m
python -m cv_mailer.cli.commands
```

### Database Path Issues

Update your `.env`:

```env
DATABASE_PATH=data/cv_mailer.db  # New location
# Or keep old location
DATABASE_PATH=cv_mailer.db       # Old location
```

## Next Steps

1. **Use the new structure** for all new development
2. **Add tests** in `tests/` directory
3. **Extend API** as needed for web UI
4. **Update documentation** with examples
5. **Add frontend** when ready (structure supports it!)

## Questions?

- Check the code structure in `src/cv_mailer/`
- See `pyproject.toml` for package configuration
- Review API docs at `/docs` when server is running
- Read design documents in `docs/design/`

---

**Summary**: Everything works as before, but now with a professional structure ready for growth! 🚀
