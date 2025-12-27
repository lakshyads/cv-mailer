# Design Explanation & Architecture Overview

Comprehensive explanation of design decisions, patterns, and rationale.

> 📖 **Related Docs**: [Architecture Overview](ARCHITECTURE.md) | [Setup Guide](../SETUP_GUIDE.md) | [Quick Start](../QUICK_START.md)

## My Thought Process

When you asked me to help design and plan, I took a "build it right the first time" approach. Here's my reasoning:

1. **You had clear requirements** - The features were well-defined
2. **Best practices matter** - A well-architected foundation makes future changes easier
3. **Modular design** - Each component can be understood, tested, and modified independently
4. **Future-proofing** - The architecture supports adding a UI later without major refactoring

After the refactoring (December 2025), we've enhanced the architecture with:

- **Modern packaging** - Proper Python package with `pyproject.toml`
- **Organized structure** - Layered `src/` layout following best practices
- **REST API** - FastAPI foundation ready for web UI
- **Scalability** - Clear separation for easy extension

## Architecture Overview

### Layered Package Architecture

```
┌─────────────────────────────────────────┐
│   Presentation Layer                    │  ← User interaction
│   ├─ CLI (src/cv_mailer/cli/)           │    - Command parsing
│   │  ├─ commands.py                     │    - Progress display
│   │  ├─ app.py                          │    - Error handling
│   │  └─ display.py                      │
│   └─ API (src/cv_mailer/api/)           │    - REST endpoints
│      ├─ app.py                          │    - Request/response
│      └─ routers/                        │    - Serialization
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Business Logic Layer                  │
│   src/cv_mailer/services/               │
│   ├─ tracker.py (ApplicationTracker)    │  ← Core logic
│   ├─ template_service.py (EmailTemplate)│
│   └─ [future: analytics, scheduler]     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Integration Layer                     │
│   src/cv_mailer/integrations/           │
│   ├─ gmail/                             │  ← External APIs
│   │  ├─ auth.py                         │
│   │  └─ client.py (GmailSender)         │
│   └─ google_sheets/                     │
│      ├─ auth.py                         │
│      └─ client.py (GoogleSheetsClient)  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Core Layer                            │
│   src/cv_mailer/core/                   │
│   ├─ models.py (JobApplication, etc.)   │  ← Domain models
│   └─ enums.py (JobStatus, EmailType)    │     (framework-agnostic)
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Supporting Layers                     │
│   ├─ config/ (settings.py - Config)     │  ← Configuration
│   ├─ parsers/ (recruiter.py)            │  ← Data parsing
│   └─ utils/ (database.py, validators)   │  ← Utilities
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   External Services                     │
│   - Google Sheets API                   │
│   - Gmail API                           │
│   - SQLite Database (data/)             │
└─────────────────────────────────────────┘
```

### Why This Structure?

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Testability**: Can mock external services and test business logic
3. **Maintainability**: Changes in one layer don't cascade
4. **Extensibility**: Easy to add new features (CSV import, web UI, mobile app)
5. **Package-Ready**: Proper Python package installable with `pip`
6. **API-Ready**: FastAPI layer ready for web UI integration

## Package Structure Explained

### src/cv_mailer/ - The Main Package

```
src/cv_mailer/
├── __init__.py              # Public API exports
├── core/                    # Domain models (framework-agnostic)
│   ├── __init__.py
│   ├── models.py            # SQLAlchemy models
│   └── enums.py             # Status enums
├── config/                  # Configuration management
│   ├── __init__.py
│   └── settings.py          # Config class with validation
├── services/                # Business logic
│   ├── __init__.py
│   ├── tracker.py           # ApplicationTracker
│   └── template_service.py  # EmailTemplate
├── integrations/            # External API clients
│   ├── __init__.py
│   ├── gmail/
│   │   ├── __init__.py
│   │   ├── auth.py          # Gmail OAuth
│   │   └── client.py        # GmailSender
│   └── google_sheets/
│       ├── __init__.py
│       ├── auth.py          # Sheets OAuth
│       └── client.py        # GoogleSheetsClient
├── parsers/                 # Data parsing logic
│   ├── __init__.py
│   └── recruiter.py         # RecruiterParser
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── database.py          # DB setup & sessions
│   ├── date.py              # Date formatting
│   └── validators.py        # Email validation
├── cli/                     # Command-line interface
│   ├── __init__.py
│   ├── commands.py          # Argument parsing
│   ├── app.py               # CVMailer main app
│   └── display.py           # Rich console output
└── api/                     # REST API (FastAPI)
    ├── __init__.py
    ├── app.py               # FastAPI application
    ├── dependencies.py      # Dependency injection
    └── routers/
        ├── __init__.py
        ├── applications.py  # /api/v1/applications
        ├── emails.py        # /api/v1/emails
        ├── recruiters.py    # /api/v1/recruiters
        └── stats.py         # /api/v1/statistics
```

### Benefits of This Structure

**For Development**:

- Clear where to find code
- Easy to navigate
- Consistent organization
- IDE-friendly

**For Maintenance**:

- Changes are localized
- Easy to test individual components
- Clear dependencies

**For Extension**:

- Add new integrations in `integrations/`
- Add new services in `services/`
- Add new API endpoints in `api/routers/`
- Add new CLI commands in `cli/`

## Design Patterns Explained

### 1. Repository Pattern (`services/tracker.py`)

**What it is**: A class that encapsulates database operations

**Why I used it**:

```python
# Instead of this scattered everywhere:
session.query(JobApplication).filter_by(...)

# We have this clean interface:
tracker.get_or_create_job_application(...)
tracker.record_email_sent(...)
```

**Benefits**:

- Business logic doesn't know about SQL
- Easy to swap SQLite for PostgreSQL
- Centralized data access logic
- Testable (mock the repository)

### 2. Strategy Pattern (`services/template_service.py`)

**What it is**: Different algorithms (strategies) for the same task

**Why I used it**:

```python
# Different email types, same interface
EmailTemplate.render_first_contact(...)  # Strategy 1
EmailTemplate.render_follow_up(...)       # Strategy 2
# Future: render_thank_you(...), render_interview_followup(...)
```

**Benefits**:

- Easy to add new email types
- No if/else chains
- Each strategy is independent

### 3. Factory Pattern (`utils/database.py`)

**What it is**: Functions that create objects with proper initialization

**Why I used it**:

```python
def get_session():
    engine = get_engine()
    Base.metadata.create_all(engine)  # Ensures tables exist
    Session = sessionmaker(bind=engine)
    return Session()

def init_database():
    # Initialize with proper setup
    # Create all tables
    # Run migrations (future)
```

**Benefits**:

- Ensures database is initialized
- Consistent session creation
- Single point of configuration
- Easy to add connection pooling

### 4. Template Method Pattern (`cli/app.py`)

**What it is**: Define algorithm skeleton, let subclasses/methods fill details

**Why I used it**:

```python
def process_new_applications(self, dry_run: bool = False):
    # Fixed algorithm:
    1. Read from Sheets
    2. For each row:
       a. Validate
       b. Generate email
       c. Send (or skip if dry_run)
       d. Record
    3. Return summary
```

**Benefits**:

- Algorithm is clear and consistent
- Easy to add steps (e.g., validation, filtering)
- Dry-run mode just skips the "send" step

### 5. Dependency Injection (`api/dependencies.py`)

**What it is**: Provide dependencies explicitly rather than creating them

**Why I used it**:

```python
def get_tracker() -> ApplicationTracker:
    """Dependency for FastAPI routes."""
    tracker = ApplicationTracker()
    try:
        yield tracker
    finally:
        tracker.cleanup()

@router.get("/applications")
async def list_applications(tracker: ApplicationTracker = Depends(get_tracker)):
    # tracker is injected automatically
```

**Benefits**:

- Easy to test (inject mocks)
- Clean separation
- FastAPI handles lifecycle
- Consistent across routes

## Component Deep Dive

### Configuration Management (`config/settings.py`)

**Design Decision**: Class-based with environment variables

**Why not a simple dict?**

- Type hints (IDE autocomplete)
- Validation at startup
- Default values
- Easy to extend
- Single source of truth

**Example**:

```python
class Config:
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    
    @classmethod
    def validate(cls) -> list[str]:
        # Catch configuration errors early
        errors = []
        if not cls.SPREADSHEET_ID:
            errors.append("SPREADSHEET_ID is required")
        return errors
```

**Future Enhancement**: Use Pydantic for validation

### Database Models (`core/models.py`)

**Design Decision**: SQLAlchemy ORM with Enums

**Why SQLAlchemy?**

- Database-agnostic (can switch SQLite → PostgreSQL)
- Type safety with Enums
- Relationship management (M2M for recruiters)
- Migration support (Alembic - future)
- Query builder

**Why Enums for Status? (`core/enums.py`)**

```python
class JobStatus(str, Enum):
    DRAFT = "draft"
    REACHED_OUT = "reached_out"
    APPLIED = "applied"
    # ...
```

Benefits:

- Prevents typos ("draf" vs "draft")
- IDE autocomplete
- Type checking
- Consistent across CLI and API

**Separation**: Enums in separate file for reusability

### Google Sheets Client (`integrations/google_sheets/`)

**Design Decision**: Abstraction layer over Google Sheets API

**Why?**

- Can swap for CSV/Excel reader
- Testable (mock the API)
- Handles authentication separately (`auth.py`)
- Returns clean dictionaries (not raw API responses)
- Multi-sheet support built-in

**Multi-Sheet Support**:

- `list_all_sheets()` - Lists all worksheets
- `read_all_sheets()` - Reads from all sheets
- `read_all_rows()` - Reads from single sheet (backward compatible)

**Authentication Separation** (`auth.py`):

- OAuth flow isolated
- Reusable credentials
- Easy to test client without auth

### Gmail Sender (`integrations/gmail/`)

**Design Decision**: Rate limiting built-in, auth separated

**Why?**

- Gmail has strict limits (500/day free, 2000/day Workspace)
- Random delays prevent detection
- Daily limit tracking in database
- Automatic throttling

**Rate Limiting Strategy**:

1. Check daily limit (database query)
2. Check time since last email
3. Random delay (0.1-0.5 seconds) - human-like
4. Send email
5. Update stats

**Separation**:

- `auth.py` - OAuth and token management
- `client.py` - Email sending logic

### Email Templates (`services/template_service.py`)

**Design Decision**: Jinja2 templating

**Why Jinja2?**

- Powerful (conditionals, loops, filters)
- Industry standard
- Can load from files later
- HTML email support (future)
- Easy to customize

**Template Structure**:

```python
FIRST_CONTACT_TEMPLATE = """
Dear {{ recruiter_name or 'Hiring Manager' }},
...
"""
```

Features:

- Variables: `{{ variable }}`
- Conditionals: `{% if condition %}`
- Filters: `{{ name|title }}`
- Defaults: `{{ var or 'default' }}`

### Application Tracker (`services/tracker.py`)

**Design Decision**: High-level business logic methods

**Why?**

- Encapsulates complex queries
- Business logic in one place
- Easy to test
- Context manager for cleanup
- Reusable across CLI and API

**Key Methods**:

- `get_or_create_job_application()` - Idempotent
- `get_applications_needing_follow_up()` - Complex logic
- `record_email_sent()` - Audit trail
- `get_statistics()` - Reporting
- `update_application_status()` - State management

### CLI Application (`cli/`)

**Design Decision**: Separated concerns

**Structure**:

- `commands.py` - Argument parsing, entry point
- `app.py` - Main application logic (`CVMailer` class)
- `display.py` - Rich console output (tables, progress)

**Why Separate?**

- Easy to test business logic (`app.py`)
- Clean display logic (`display.py`)
- Entry point is simple (`commands.py`)
- Can add new commands easily

**Entry Point**:

```python
# pyproject.toml
[project.scripts]
cv-mailer = "cv_mailer.cli.commands:main"

# Creates `cv-mailer` command automatically
```

### REST API (`api/`)

**Design Decision**: FastAPI with router pattern

**Why FastAPI?**

- Modern async support
- Automatic OpenAPI docs
- Type hints → validation
- Fast performance
- Easy to test

**Structure**:

- `app.py` - FastAPI app setup, CORS, middleware
- `dependencies.py` - Dependency injection (DB, services)
- `routers/` - Route handlers by resource

**Router Pattern**:

```python
# api/routers/applications.py
router = APIRouter(prefix="/applications", tags=["applications"])

@router.get("/")
async def list_applications(tracker: ApplicationTracker = Depends(get_tracker)):
    # Handle request

# api/app.py
app.include_router(applications.router, prefix="/api/v1")
```

Benefits:

- Organized by resource
- Easy to add new endpoints
- Consistent structure
- Automatic docs

## Data Flow Example

### Sending a New Application Email

```
User runs: cv-mailer
    ↓
1. CLI Entry (cli/commands.py:main())
   ├─ Parse arguments
   ├─ Setup logging (logs/cv_mailer.log)
   └─ Create CVMailer instance
    ↓
2. CVMailer.__init__() (cli/app.py)
   ├─ Config.validate() → Fail fast if wrong
   ├─ init_database() → Create tables (data/cv_mailer.db)
   ├─ GoogleSheetsClient() → OAuth if first time
   ├─ GmailSender() → OAuth if first time
   └─ ApplicationTracker() → Ready for business logic
    ↓
3. process_new_applications() (cli/app.py)
   ├─ Read from Google Sheets
   │  └─ If PROCESS_ALL_SHEETS=true: read_all_sheets()
   │     ├─ list_all_sheets() → Get sheet metadata
   │     ├─ For each sheet: read_all_rows()
   │     └─ Returns rows with _sheet_name, _row_number
   │
   ├─ For each row (with progress bar):
   │  ├─ Parse: company, position, recruiters
   │  │  └─ RecruiterParser.parse_recruiters()
   │  │     └─ "Alice - alice@co.com, Bob - bob@co.com"
   │  │        → [{'name': 'Alice', 'email': 'alice@co.com'}, ...]
   │  │
   │  ├─ ApplicationTracker.get_or_create_job_application()
   │  │  ├─ unique_row_id = f"{sheet_name}_{row_number}"
   │  │  ├─ Check DB: Does this row_id exist?
   │  │  ├─ If yes: Update and return
   │  │  └─ If no: Create new JobApplication
   │  │
   │  ├─ For each recruiter:
   │  │  ├─ Check: Already sent? (EmailRecord query)
   │  │  │  └─ Skip if status=SENT
   │  │  │
   │  │  ├─ EmailTemplate.render_first_contact()
   │  │  │  ├─ Load Jinja2 template
   │  │  │  ├─ Substitute: recruiter_name, company, position, etc.
   │  │  │  └─ Return (subject, body)
   │  │  │
   │  │  ├─ GmailSender.send_email()
   │  │  │  ├─ Check rate limits (DailyEmailStats query)
   │  │  │  ├─ Wait: random(EMAIL_DELAY_MIN, EMAIL_DELAY_MAX)
   │  │  │  ├─ Create MIME message
   │  │  │  ├─ Attach resume (if RESUME_FILE_PATH) from assets/
   │  │  │  ├─ Add drive link (if RESUME_DRIVE_LINK)
   │  │  │  ├─ Send via Gmail API
   │  │  │  ├─ Update DailyEmailStats
   │  │  │  └─ Return message_id
   │  │  │
   │  │  ├─ ApplicationTracker.record_email_sent()
   │  │  │  ├─ Create EmailRecord (audit trail)
   │  │  │  ├─ Update JobApplication.status = REACHED_OUT
   │  │  │  └─ Commit to DB
   │  │  │
   │  │  └─ GoogleSheetsClient.update_cell()
   │  │     ├─ Parse unique_row_id → sheet_name, row_number
   │  │     ├─ Find "Status" column in correct sheet
   │  │     └─ Update to "Reached Out"
   │  │
   │  └─ Display: ✓ Sent to recruiter@company.com
   │
   └─ Return count of emails sent
    ↓
4. Display Summary (cli/display.py)
   └─ "Summary: X sent, Y skipped"
```

### API Request Flow

```
Client: GET /api/v1/applications
    ↓
1. FastAPI Router (api/routers/applications.py)
   ├─ Parse query params (status, limit, offset)
   ├─ Inject ApplicationTracker (via get_tracker dependency)
   └─ Call route handler
    ↓
2. ApplicationTracker (services/tracker.py)
   ├─ Query database (same as CLI)
   ├─ Apply filters
   └─ Return JobApplication objects
    ↓
3. Serialize to JSON
   ├─ Convert SQLAlchemy objects to dicts
   ├─ Format dates (ISO 8601)
   └─ Return JSON response
    ↓
Client receives: {"total": 10, "items": [...]}
```

**Key Point**: CLI and API **share the same business logic** (`ApplicationTracker`). Only presentation differs!

## Multi-Sheet & Multi-Recruiter Support

### Multi-Sheet (Your Use Case)

**Problem**: Spreadsheet has multiple sheets (one per date), original code only read one.

**Solution**:

1. **List all sheets**:

   ```python
   sheets = self.sheets_client.list_all_sheets()
   # [{'title': '2024-01-15', 'sheetId': 123}, ...]
   ```

2. **Read from all sheets**:

   ```python
   rows = self.sheets_client.read_all_sheets(sheet_filter='2024')
   # Each row: {'Company': '...', '_sheet_name': '2024-01-15', '_row_number': 5}
   ```

3. **Unique row identification**:

   ```python
   # Old: row_id = 5 (conflicts across sheets)
   # New: unique_row_id = "2024-01-15_5" (unique)
   ```

4. **Update correct sheet**:

   ```python
   # Automatically detects sheet and updates
   self.sheets_client.update_cell(5, 'Status', 'Reached Out', 
                                   worksheet_name='2024-01-15')
   ```

**Configuration**:

```env
PROCESS_ALL_SHEETS=true
SHEET_NAME_FILTER=2024.*  # Optional regex filter
```

### Multi-Recruiter

**Problem**: Multiple contacts for same job.

**Solution** (`parsers/recruiter.py`):

```python
# Input: "Alice - alice@co.com, Bob - bob@co.com"
RecruiterParser.parse_recruiters(...)
# Output: [
#   {'name': 'Alice', 'email': 'alice@co.com'},
#   {'name': 'Bob', 'email': 'bob@co.com'}
# ]
```

**Benefits**:

- Each recruiter gets personalized email
- Tracked separately in database
- Follow-ups sent to each
- No duplicates

## Error Handling Strategy

1. **Configuration Errors**: Fail fast at startup
   - `Config.validate()` in `__init__()`
   - Better to fail immediately than send wrong emails

2. **API Errors**: Log and continue
   - One failed email shouldn't stop the batch
   - Logged to `logs/cv_mailer.log`

3. **Database Errors**: Rollback transaction
   - SQLAlchemy session management
   - Maintain data consistency

4. **Rate Limit Errors**: Skip and log warning
   - Don't crash, just skip this email
   - User can retry later

5. **Authentication Errors**: Clear instructions
   - Delete old tokens
   - Re-run authentication flow

## Security Considerations

1. **Credentials**: Never committed
   - `.gitignore` includes: `credentials.json`, `.env`, `*.pickle`
   - Tokens in `token.pickle`, `gmail_token.pickle`

2. **Environment Variables**: Sensitive data in `.env`
   - Not in source control
   - Easy to manage per environment

3. **OAuth Tokens**: Stored locally
   - Encrypted by Google's OAuth library
   - Refresh tokens handled automatically

4. **Rate Limiting**: Prevents abuse detection
   - Random delays
   - Daily limits
   - Tracked in database

5. **Database**: SQLite with proper permissions
   - Located in `data/` directory
   - Regular backups recommended

## Extensibility Points

### Easy to Add

1. **New Email Types**:

   ```python
   # services/template_service.py
   @staticmethod
   def render_interview_thank_you(...):
       ...
   ```

2. **New Data Sources**:

   ```python
   # integrations/csv/client.py
   class CSVClient:
       def read_applications(self):
           ...
   ```

3. **New Statuses**:

   ```python
   # core/enums.py
   class JobStatus(str, Enum):
       OFFER_RECEIVED = "offer_received"
   ```

4. **New API Endpoints**:

   ```python
   # api/routers/analytics.py
   @router.get("/analytics/conversion")
   async def get_conversion_stats():
       ...
   ```

5. **New CLI Commands**:

   ```python
   # cli/commands.py
   parser.add_argument('--export-csv', ...)
   ```

### Would Require Refactoring (But Still Feasible)

1. **Multi-account**: Refactor to support multiple Gmail accounts
2. **Async Processing**: Add async/await throughout (FastAPI already supports)
3. **Distributed**: Add message queue (Celery, RQ)
4. **Real-time UI**: WebSockets (FastAPI supports)

## Trade-offs Made

| Decision | Chosen | Alternative | Reasoning |
|----------|--------|-------------|-----------|
| Database | SQLite | PostgreSQL | Simplicity, portability (can upgrade) |
| Sync/Async | Sync CLI, Async API | All async | Simpler CLI, API ready for async |
| UI | CLI first | GUI first | Faster to build, easier to test |
| Sheets | Multi-sheet | Single sheet | Your use case, backward compatible |
| Packaging | pip install | Script only | Professional, easier to use |
| API Framework | FastAPI | Flask | Modern, async, auto-docs |

## Why This Architecture Works

### 1. Modular

Each piece can be understood independently:

- Change email templates without touching database
- Add new API endpoint without changing CLI
- Switch Gmail for SMTP without changing business logic

### 2. Testable

Can test each component in isolation:

```python
# Test tracker without real database
def test_tracker():
    mock_session = MagicMock()
    tracker = ApplicationTracker(session=mock_session)
    ...

# Test API without real services
def test_api():
    app.dependency_overrides[get_tracker] = mock_tracker
    ...
```

### 3. Maintainable

Changes are localized:

- Bug in Gmail? → `integrations/gmail/client.py`
- New email template? → `services/template_service.py`
- API response format? → `api/routers/*.py`

### 4. Extensible

Easy to add features:

- New integration? → `integrations/new_service/`
- New service? → `services/new_service.py`
- New CLI command? → Update `cli/commands.py`

### 5. Professional

Follows industry best practices:

- SOLID principles
- Design patterns
- Modern packaging
- API-first design
- Comprehensive documentation

## Migration from Old Structure

The refactoring maintained:

- ✅ Database compatibility (no schema changes)
- ✅ OAuth tokens (same files)
- ✅ Configuration (same `.env` format)
- ✅ Backward compatibility (`python main.py` still works)

New benefits:

- ✅ Package installation: `pip install -e .`
- ✅ Global commands: `cv-mailer`, `cv-mailer-api`
- ✅ Organized directories: `data/`, `logs/`, `assets/`
- ✅ REST API ready for web UI
- ✅ Better testability and maintainability

## Next Steps for Web UI

The architecture is **ready** for a web UI:

### 1. Use Existing API

```javascript
// Frontend (React/Vue/Svelte)
fetch('/api/v1/applications')
  .then(r => r.json())
  .then(data => {
    // data.items has all applications
    // Uses same ApplicationTracker as CLI!
  });
```

### 2. No Backend Refactoring Needed

All business logic is in `services/`:

- `ApplicationTracker` - Used by both CLI and API
- `EmailTemplate` - Reusable
- `GmailSender` - Reusable

### 3. Just Add Frontend

```
cv-mailer/
├── src/cv_mailer/       # Backend (done)
├── frontend/            # New: React/Vue/Svelte
│   ├── src/
│   ├── public/
│   └── package.json
└── docker-compose.yml   # Optional: containerize
```

### 4. Example: Dashboard

```typescript
// frontend/src/components/Dashboard.tsx
import { useApplications } from './hooks/useApplications';

export default function Dashboard() {
  const { applications, loading } = useApplications();
  
  return (
    <div>
      <h1>Applications</h1>
      {applications.map(app => (
        <ApplicationCard key={app.id} application={app} />
      ))}
    </div>
  );
}
```

API endpoint already exists: `GET /api/v1/applications` ✅

## Summary

I built a **production-ready, maintainable, extensible** application following software engineering best practices.

### Original Architecture (v1.0)

- ✅ Modular flat structure
- ✅ SOLID principles
- ✅ Design patterns
- ✅ Multi-sheet support
- ✅ Multi-recruiter support

### Refactored Architecture (v1.0 - December 2025)

- ✅ Modern package structure (`src/` layout)
- ✅ Proper Python packaging (`pyproject.toml`)
- ✅ REST API with FastAPI
- ✅ Organized directories (`data/`, `logs/`, `assets/`)
- ✅ Global CLI commands (`cv-mailer`)
- ✅ Enhanced testability (structure ready for `tests/`)
- ✅ API documentation (automatic Swagger/ReDoc)
- ✅ Ready for web UI integration

The code is well-documented, follows industry standards, and is **ready to use and ready to grow**!

## Documentation Map

- **README.md**: Overview, features, quick start
- **docs/QUICK_START.md**: 5-minute setup guide
- **docs/SETUP_GUIDE.md**: Detailed setup instructions
- **docs/GOOGLE_SHEETS_TEMPLATE.md**: Sheet format guide
- **docs/design/DESIGN_EXPLANATION.md**: This file (architecture)
- **docs/design/FEATURE_SUGGESTIONS.md**: Future enhancements
- **docs/design/refactoring_modernization/**: Refactoring details
- **API Docs**: <http://localhost:8000/docs> (when running `cv-mailer-api`)
