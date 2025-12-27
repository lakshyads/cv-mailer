# CV Mailer - Architecture & Design Explanation

This document explains the architecture, design patterns, and thought process behind the CV Mailer application after the refactoring (December 2025).

> 📖 **Other Docs**: [Quick Start](../QUICK_START.md) | [Setup Guide](../SETUP_GUIDE.md) | [Design Explanation](DESIGN_EXPLANATION.md) | [Features](FEATURE_SUGGESTIONS.md)

## Overview

## High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                             │
├─────────────────────────────┬─────────────────────────────────────┤
│   CLI (src/cv_mailer/cli/)  │  API (src/cv_mailer/api/)          │
│   ├─ commands.py            │  ├─ app.py (FastAPI)                │
│   ├─ app.py (CVMailer)      │  ├─ dependencies.py                 │
│   └─ display.py (Rich UI)   │  └─ routers/ (endpoints)            │
└─────────────┬───────────────┴──────────────┬──────────────────────┘
              │                               │
              └───────────┬───────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────────┐
│                   Business Logic Layer                             │
│                  (src/cv_mailer/services/)                         │
│   ├─ tracker.py (ApplicationTracker - core logic)                 │
│   └─ template_service.py (EmailTemplate - email generation)       │
└────────────────────┬──────────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────────┐
│               Integration & Data Access Layer                       │
├──────────────────────────┬──────────────────────────┬──────────────┤
│  Gmail Integration       │  Sheets Integration      │  Database    │
│  (integrations/gmail/)   │  (integrations/google_   │  (utils/     │
│  ├─ auth.py              │   sheets/)               │   database)  │
│  └─ client.py            │  ├─ auth.py              │              │
│     (GmailSender)        │  └─ client.py            │              │
│                          │     (GoogleSheetsClient)  │              │
└──────────────┬───────────┴──────────────┬───────────┴──────────────┘
               │                          │
┌──────────────▼──────────────────────────▼───────────────────────────┐
│                       Core Layer                                     │
│                   (src/cv_mailer/core/)                              │
│   ├─ models.py (JobApplication, EmailRecord, Recruiter - ORM)       │
│   └─ enums.py (JobStatus, EmailType, EmailStatus)                   │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────────┐
│                    Supporting Components                              │
├────────────────────┬─────────────────────┬──────────────────────────┤
│  Configuration     │  Parsers            │  Utilities               │
│  (config/)         │  (parsers/)         │  (utils/)                │
│  └─ settings.py    │  └─ recruiter.py    │  ├─ database.py          │
│     (Config class) │     (RecruiterParser│  ├─ validators.py        │
│                    │      for multi-      │  └─ date.py              │
│                    │      recruiter)      │                          │
└────────────────────┴─────────────────────┴──────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────────┐
│                     External Services                                 │
│   - Google Sheets API (read/write application data)                  │
│   - Gmail API (send emails with rate limiting)                       │
│   - SQLite Database (data/ - tracking & history)                     │
└──────────────────────────────────────────────────────────────────────┘
```

## Package Structure

The application follows the modern `src/` layout:

```
src/cv_mailer/
├── __init__.py              # Public API exports
├── core/                    # Domain models (framework-agnostic)
├── config/                  # Configuration management
├── services/                # Business logic
├── integrations/            # External API clients
├── parsers/                 # Data parsing
├── utils/                   # Utility functions
├── cli/                     # CLI application
└── api/                     # REST API (FastAPI)
```

**Benefits**:
- Clear separation of concerns
- Easy to navigate and understand
- Supports both CLI and API
- Ready for testing (tests/ mirrors structure)
- Professional Python packaging

## Design Patterns Used

### 1. **Layered Architecture (Separation of Concerns)**

The application is divided into distinct layers:

- **Presentation Layer**: CLI (`cli/`) and API (`api/`) - User/client interaction
- **Business Logic Layer**: Services (`services/`) - Core business rules
- **Integration Layer**: External APIs (`integrations/`) - Gmail, Sheets
- **Data Access Layer**: Database utilities (`utils/database.py`)
- **Core Layer**: Domain models (`core/`) - Framework-agnostic data structures
- **Configuration Layer**: Settings (`config/`) - Environment configuration

**Why?** This separation makes the code:
- Testable (each layer can be tested independently)
- Maintainable (changes in one layer don't affect others)
- Extensible (added API without changing CLI)
- Reusable (same business logic for CLI and API)

### 2. **Repository Pattern**

The `ApplicationTracker` class acts as a repository for database operations:

```python
# src/cv_mailer/services/tracker.py
class ApplicationTracker:
    def get_or_create_job_application(...)
    def record_email_sent(...)
    def get_applications_needing_follow_up(...)
    def get_statistics(...)
```

**Why?**
- Encapsulates database logic
- Makes it easy to swap SQLite for PostgreSQL later
- Provides a clean interface for business logic
- Same repository used by CLI and API

### 3. **Strategy Pattern**

Email templates use the Strategy pattern:

```python
# src/cv_mailer/services/template_service.py
class EmailTemplate:
    @staticmethod
    def render_first_contact(...)  # Strategy 1
    @staticmethod
    def render_follow_up(...)      # Strategy 2
    # Future: render_interview_thank_you(...)
```

**Why?** Easy to add new email types without modifying existing code (Open/Closed Principle).

### 4. **Factory Pattern**

Database session creation uses a factory:

```python
# src/cv_mailer/utils/database.py
def get_session():
    engine = get_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def init_database():
    # Initialize database with proper setup
    ...
```

**Why?** Centralizes database session creation and ensures proper initialization.

### 5. **Singleton Pattern (Implicit)**

The `Config` class uses class-level attributes, acting like a singleton:

```python
# src/cv_mailer/config/settings.py
class Config:
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    # ... all config is class-level
    
    @classmethod
    def validate(cls) -> list[str]:
        # Validate configuration at startup
        ...
```

**Why?** Single source of truth for configuration across the application.

### 6. **Dependency Injection (New in API)**

FastAPI routes use dependency injection:

```python
# src/cv_mailer/api/dependencies.py
def get_tracker() -> ApplicationTracker:
    tracker = ApplicationTracker()
    try:
        yield tracker
    finally:
        tracker.cleanup()

# src/cv_mailer/api/routers/applications.py
@router.get("/applications")
async def list_applications(
    tracker: ApplicationTracker = Depends(get_tracker)
):
    # tracker is injected automatically
    ...
```

**Why?** 
- Easy to test (inject mocks)
- Clean separation of concerns
- Automatic resource management
- Type-safe

### 7. **Observer Pattern (Implicit)**

The application implicitly uses Observer pattern for status updates:

```python
# When email is sent:
1. GmailSender.send_email() → Sends email
2. ApplicationTracker.record_email_sent() → Updates database
3. GoogleSheetsClient.update_cell() → Updates sheet status

# All observers react to the "email sent" event
```

## Component Deep Dive

### Configuration Management (`config/settings.py`)

**Design Decision**: Class-based with environment variables and validation

**Why not a simple dict?**
- Type hints (IDE autocomplete)
- Validation at startup (fail fast)
- Default values
- Easy to extend
- Single source of truth

**Example**:

```python
class Config:
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    
    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.SPREADSHEET_ID:
            errors.append("SPREADSHEET_ID is required")
        return errors
```

**Future Enhancement**: Migrate to Pydantic for advanced validation.

### Database Models (`core/models.py` & `core/enums.py`)

**Design Decision**: SQLAlchemy ORM with separate enums

**Why SQLAlchemy?**
- Database-agnostic (can switch SQLite → PostgreSQL)
- Type safety with Enums
- Relationship management (M2M for recruiters)
- Migration support (Alembic - future)
- Query builder

**Why Separate Enums?**

```python
# core/enums.py
class JobStatus(str, Enum):
    DRAFT = "draft"
    REACHED_OUT = "reached_out"
    APPLIED = "applied"
    # ...
```

Benefits:
- Prevents typos
- IDE autocomplete
- Type checking
- Reusable across modules
- API can use same enums

### Integration Layers

**Gmail Integration** (`integrations/gmail/`)
- `auth.py` - OAuth2 authentication
- `client.py` - `GmailSender` with rate limiting

**Google Sheets Integration** (`integrations/google_sheets/`)
- `auth.py` - OAuth2 authentication (separate from Gmail)
- `client.py` - `GoogleSheetsClient` with multi-sheet support

**Why Separate Auth Files?**
- Different scopes (Gmail send vs. Sheets read/write)
- Different token files (`gmail_token.pickle` vs. `token.pickle`)
- Independent authentication flows
- Testable in isolation

### Services Layer (`services/`)

**ApplicationTracker** (`tracker.py`)
- Core business logic
- Database operations
- Status management
- Statistics generation
- **Shared by CLI and API** ✓

**EmailTemplate** (`template_service.py`)
- Jinja2-based templating
- First contact emails
- Follow-up emails
- **Shared by CLI and API** ✓

### CLI Application (`cli/`)

**Structure**:
- `commands.py` - Entry point, argument parsing
- `app.py` - Main application logic (`CVMailer` class)
- `display.py` - Rich console output (tables, progress bars)

**Entry Point** (`pyproject.toml`):
```toml
[project.scripts]
cv-mailer = "cv_mailer.cli.commands:main"
```

Creates global `cv-mailer` command automatically.

### REST API (`api/`)

**Structure**:
- `app.py` - FastAPI application setup, CORS, middleware
- `dependencies.py` - Dependency injection (DB sessions, services)
- `routers/` - Route handlers by resource

**Router Pattern**:
```python
# api/routers/applications.py
router = APIRouter()

@router.get("/applications")
async def list_applications(...):
    # Uses same ApplicationTracker as CLI!
    ...

# api/app.py
app.include_router(applications.router, prefix="/api/v1")
```

**Benefits**:
- Organized by resource
- Consistent structure
- Automatic OpenAPI docs
- **Reuses all business logic from CLI** ✓

## Data Flow Examples

### CLI: Sending Application Emails

```
User: cv-mailer --new
    ↓
1. cli/commands.py:main()
   - Parse arguments
   - Setup logging (logs/cv_mailer.log)
   - Create CVMailer instance
    ↓
2. cli/app.py:CVMailer.__init__()
   - Config.validate() → Fail fast if misconfigured
   - init_database() → Create tables (data/cv_mailer.db)
   - GoogleSheetsClient() → OAuth if first time
   - GmailSender() → OAuth if first time
   - ApplicationTracker() → Business logic ready
    ↓
3. cli/app.py:process_new_applications()
   - Read from Google Sheets (multi-sheet if enabled)
   - For each row:
     ├─ RecruiterParser.parse_recruiters() → Handle multi-recruiter
     ├─ ApplicationTracker.get_or_create_job_application()
     ├─ For each recruiter:
     │  ├─ Check if already sent (EmailRecord query)
     │  ├─ EmailTemplate.render_first_contact()
     │  ├─ GmailSender.send_email() → Rate limiting, attach resume
     │  ├─ ApplicationTracker.record_email_sent()
     │  └─ GoogleSheetsClient.update_cell() → Update status
     └─ Display progress (display.py)
    ↓
4. Summary displayed via Rich console
```

### API: Fetching Applications

```
Client: GET /api/v1/applications?status=reached_out
    ↓
1. api/routers/applications.py:list_applications()
   - Parse query params (status, limit, offset)
   - Inject ApplicationTracker (via get_tracker dependency)
    ↓
2. services/tracker.py:ApplicationTracker (same as CLI!)
   - Query database with filters
   - Return JobApplication objects
    ↓
3. FastAPI serialization
   - Convert SQLAlchemy objects to JSON
   - Format dates (ISO 8601)
   - Return paginated response
    ↓
Client receives: {"total": 42, "items": [...]}
```

**Key Insight**: CLI and API **share the same business logic**. Only presentation differs!

## Design Principles (SOLID)

### 1. Single Responsibility Principle (SRP)
- `GmailSender` only sends emails
- `GoogleSheetsClient` only interacts with Sheets
- `ApplicationTracker` only manages business logic
- `EmailTemplate` only generates email content

### 2. Open/Closed Principle (OCP)
- Easy to add new email types without modifying `EmailTemplate`
- Easy to add new API endpoints without changing business logic
- Easy to add new integrations (CSV, LinkedIn) without changing core

### 3. Liskov Substitution Principle (LSP)
- Can swap `GmailSender` with `SMTPSender` (future)
- Can swap `GoogleSheetsClient` with `CSVReader` (future)

### 4. Interface Segregation Principle (ISP)
- Small, focused interfaces
- CLI only uses what it needs
- API only uses what it needs

### 5. Dependency Inversion Principle (DIP)
- Business logic (`ApplicationTracker`) doesn't depend on Gmail/Sheets
- Business logic depends on abstractions (method calls)
- Can mock dependencies for testing

## Multi-Sheet & Multi-Recruiter Architecture

### Multi-Sheet Support

**Implementation** (`integrations/google_sheets/client.py`):
1. `list_all_sheets()` - Get all sheet metadata
2. `read_all_sheets(sheet_filter)` - Read from all/filtered sheets
3. Unique row ID: `{sheet_name}_{row_number}`
4. Update correct sheet automatically

**Configuration** (`.env`):
```env
PROCESS_ALL_SHEETS=true
SHEET_NAME_FILTER=2024  # Optional regex
```

### Multi-Recruiter Support

**Implementation** (`parsers/recruiter.py`):
```python
RecruiterParser.parse_recruiters(
    "Alice - alice@co.com, Bob - bob@co.com"
)
# Returns: [
#   {'name': 'Alice', 'email': 'alice@co.com'},
#   {'name': 'Bob', 'email': 'bob@co.com'}
# ]
```

**Database Design**:
- Many-to-Many relationship (`job_application_recruiter` table)
- Track emails per recruiter
- Follow-ups per recruiter

## Error Handling Strategy

1. **Configuration Errors**: Fail fast at startup
   - `Config.validate()` in `__init__()`
   - Better to fail before sending emails

2. **API Errors**: Log and continue (CLI) / Return error (API)
   - One failed email shouldn't stop batch (CLI)
   - Return 404/400/500 appropriately (API)

3. **Database Errors**: Rollback transaction
   - SQLAlchemy session management
   - Maintain data consistency

4. **Rate Limit Errors**: Skip and log warning
   - Don't crash, just skip email
   - User can retry later

## Security Architecture

1. **Credentials**: Never committed
   - `.gitignore`: `credentials.json`, `.env`, `*.pickle`
   - OAuth tokens in `token.pickle`, `gmail_token.pickle`

2. **Environment Variables**: `.env` for configuration
   - Not in source control
   - Easy to manage per environment

3. **OAuth Tokens**: Encrypted by Google
   - Automatic refresh handling
   - Separate tokens for Gmail and Sheets

4. **Rate Limiting**: Prevents abuse
   - Random delays (human-like)
   - Daily limits tracked in database

5. **API Security** (Future):
   - Add authentication (OAuth2/JWT)
   - Rate limiting per client
   - CORS configured properly

## Extensibility Points

### Easy to Add

1. **New Email Types**:
   ```python
   # services/template_service.py
   @staticmethod
   def render_interview_thank_you(...):
       ...
   ```

2. **New Integrations**:
   ```python
   # integrations/linkedin/client.py
   class LinkedInClient:
       def get_recruiter_info(self, profile_url):
           ...
   ```

3. **New API Endpoints**:
   ```python
   # api/routers/analytics.py
   @router.get("/analytics/conversion-rate")
   async def get_conversion_rate():
       ...
   ```

4. **New CLI Commands**:
   ```python
   # cli/commands.py
   parser.add_argument('--export-csv', ...)
   ```

### Would Require Refactoring (But Feasible)

1. **Async Throughout**: Add async/await (FastAPI ready, CLI needs update)
2. **Multi-Account**: Refactor to support multiple Gmail accounts
3. **Real-time Updates**: Add WebSockets (FastAPI supports)
4. **Message Queue**: Add Celery for distributed email sending

## Testing Strategy

Structure ready for comprehensive testing:

```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_tracker.py
│   └── test_email_template.py
├── integration/
│   ├── test_gmail_integration.py
│   ├── test_sheets_integration.py
│   └── test_database.py
└── e2e/
    ├── test_cli_workflow.py
    └── test_api_endpoints.py
```

**Mocking Strategy**:
- Mock Gmail API for testing email sending
- Mock Sheets API for testing data reading
- Mock database for testing business logic
- FastAPI TestClient for API testing

## Performance Considerations

### Database
- SQLite for simplicity (sufficient for personal use)
- Can upgrade to PostgreSQL for production
- Add connection pooling for API

### Rate Limiting
- Built-in Gmail rate limiting
- Random delays (0.1-0.5s) prevent detection
- Daily limits tracked

### API Optimization
- Pagination support (limit/offset)
- Future: Redis caching for statistics
- Future: Database indexes for queries

## Migration & Backward Compatibility

The refactoring maintained:
- ✅ Database schema (no migrations needed)
- ✅ OAuth tokens (same file locations)
- ✅ Configuration (same `.env` format)
- ✅ `python main.py` still works

New capabilities:
- ✅ `pip install -e .` package installation
- ✅ `cv-mailer` global command
- ✅ REST API with OpenAPI docs
- ✅ Organized directories (`data/`, `logs/`, `assets/`)

## Documentation Architecture

```
docs/
├── README.md (overview)
├── QUICK_START.md (5-min setup)
├── SETUP_GUIDE.md (detailed setup)
├── API_GUIDE.md (REST API docs)
├── GOOGLE_SHEETS_TEMPLATE.md (sheet format)
├── EMAIL_TEMPLATE_SAMPLES.md (examples)
├── OAUTH_FIX.md (troubleshooting)
└── design/
    ├── ARCHITECTURE.md (this file)
    ├── DESIGN_EXPLANATION.md (comprehensive)
    ├── FEATURE_SUGGESTIONS.md (roadmap)
    └── refactoring_modernization/ (migration)
```

## Trade-offs & Decisions

| Decision | Chosen | Alternative | Reasoning |
|----------|--------|-------------|-----------|
| Database | SQLite | PostgreSQL | Simplicity, portability (can upgrade) |
| Sync/Async | Sync CLI, Async API | All async | Simpler CLI, API ready for async |
| Packaging | `src/` layout | Flat structure | Professional, testable, standard |
| API Framework | FastAPI | Flask/Django | Modern, async, auto-docs |
| Templates | Jinja2 | String format | Powerful, industry standard |
| Auth | OAuth2 | API keys | Secure, user-owned credentials |

## Summary

The CV Mailer architecture is:

### Production-Ready
- ✅ Modern Python packaging
- ✅ Professional structure
- ✅ Comprehensive error handling
- ✅ Logging and monitoring

### Maintainable
- ✅ Clear separation of concerns
- ✅ SOLID principles
- ✅ Design patterns
- ✅ Well-documented

### Extensible
- ✅ Easy to add features
- ✅ Multiple presentation layers (CLI + API)
- ✅ Ready for web UI
- ✅ Ready for mobile app

### Scalable
- ✅ Can handle thousands of applications
- ✅ Can upgrade to PostgreSQL
- ✅ Can add caching/queue
- ✅ Can add authentication

The architecture supports both **current needs** (automated email sending) and **future growth** (web UI, mobile app, advanced analytics).
