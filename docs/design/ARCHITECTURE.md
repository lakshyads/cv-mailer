# CV Mailer - Architecture & Design Explanation

## Overview

This document explains the architecture, design patterns, and thought process behind the CV Mailer application.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface (main.py)                 │
│                    CVMailer Orchestrator                      │
└────────────┬────────────────────────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼────┐    ┌──────▼──────┐    ┌──────────────┐
│ Sheets  │    │   Gmail     │    │   Tracker    │
│ Client  │    │   Sender    │    │  (Database)  │
└─────────┘    └─────────────┘    └──────────────┘
     │                │                  │
     │                │                  │
┌────▼───────────────▼──────────────────▼────────────┐
│         Google APIs (Sheets, Gmail)                │
│         SQLite Database (Tracking)                 │
└────────────────────────────────────────────────────┘
```

## Design Patterns Used

### 1. **Layered Architecture (Separation of Concerns)**

The application is divided into distinct layers:

- **Presentation Layer**: `main.py` - CLI interface, user interaction
- **Business Logic Layer**: `tracker.py`, `email_templates.py` - Core business rules
- **Data Access Layer**: `models.py`, `google_sheets.py`, `gmail_sender.py` - Data persistence and external APIs
- **Configuration Layer**: `config.py` - Configuration management

**Why?** This separation makes the code:

- Testable (each layer can be tested independently)
- Maintainable (changes in one layer don't affect others)
- Extensible (easy to add UI without changing business logic)

### 2. **Repository Pattern**

The `ApplicationTracker` class acts as a repository for database operations:

```python
class ApplicationTracker:
    def get_or_create_job_application(...)
    def record_email_sent(...)
    def get_applications_needing_follow_up(...)
```

**Why?**

- Encapsulates database logic
- Makes it easy to swap SQLite for PostgreSQL later
- Provides a clean interface for business logic

### 3. **Strategy Pattern**

Email templates use the Strategy pattern:

```python
class EmailTemplate:
    @classmethod
    def render_first_contact(...)  # Strategy 1
    @classmethod
    def render_follow_up(...)      # Strategy 2
```

**Why?** Easy to add new email types (e.g., `render_rejection_response`) without modifying existing code.

### 4. **Factory Pattern**

The `get_session()` function in `models.py` is a factory:

```python
def get_session():
    engine = get_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
```

**Why?** Centralizes database session creation and ensures proper initialization.

### 5. **Singleton Pattern (Implicit)**

The `Config` class uses class-level attributes, acting like a singleton:

```python
class Config:
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    # ... all config is class-level
```

**Why?** Configuration should be consistent across the application.

### 6. **Template Method Pattern**

The `CVMailer.process_new_applications()` method defines the algorithm:

```python
def process_new_applications(self):
    1. Read from Sheets
    2. For each row:
        a. Validate data
        b. Check if already processed
        c. Generate email
        d. Send email
        e. Record in database
        f. Update spreadsheet
```

**Why?** The algorithm is fixed, but individual steps can be customized.

### 7. **Observer Pattern (Implicit)**

Rate limiting tracks daily stats and "observes" email sends:

```python
def _update_rate_limit_stats(self):
    stats.emails_sent += 1  # Observing email sends
```

## Component Breakdown

### 1. Configuration Management (`config.py`)

**Purpose**: Centralized configuration with validation

**Design Decisions**:

- Uses environment variables (12-factor app principle)
- Class-based for type hints and IDE support
- Validation method to catch errors early
- Default values for optional settings

**Why not a simple dict?**

- Type safety
- IDE autocomplete
- Validation at startup
- Easy to extend

### 2. Database Models (`models.py`)

**Purpose**: Define data structure and relationships

**Design Decisions**:

- SQLAlchemy ORM (not raw SQL)
- Enum types for status fields (type safety)
- Relationships defined (EmailRecord → JobApplication)
- Timestamps on all records

**Why SQLAlchemy?**

- Database-agnostic (can switch from SQLite to PostgreSQL)
- Type safety
- Relationship management
- Migration support (Alembic)

**Data Model**:

```
JobApplication (1) ──< (many) EmailRecord
JobApplication (1) ──< (many) ResponseRecord
DailyEmailStats (standalone)
```

### 3. Google Sheets Client (`google_sheets.py`)

**Purpose**: Abstract Google Sheets API interactions

**Design Decisions**:

- Single responsibility: only handles Sheets operations
- Returns dictionaries (not raw API responses)
- Handles authentication internally
- Flexible column name matching

**Why a separate class?**

- Can be swapped for CSV/Excel reader
- Testable in isolation
- Reusable in other projects

**Authentication Flow**:

1. Check for saved token
2. If expired, refresh
3. If missing, OAuth flow
4. Save token for next time

### 4. Gmail Sender (`gmail_sender.py`)

**Purpose**: Send emails with rate limiting

**Design Decisions**:

- Rate limiting built-in (not external)
- Random delays (human-like behavior)
- Daily limit tracking in database
- Resume attachment OR drive link

**Rate Limiting Strategy**:

1. Check daily limit (database)
2. Check time since last email
3. Random delay (60-120 seconds)
4. Send email
5. Update stats

**Why random delays?**

- Avoids detection patterns
- More human-like
- Reduces throttling risk

### 5. Email Templates (`email_templates.py`)

**Purpose**: Generate email content

**Design Decisions**:

- Jinja2 templating (not string formatting)
- HTML emails (professional appearance)
- Separate templates for first contact vs follow-up
- Class methods (no instance needed)

**Why Jinja2?**

- Powerful templating (conditionals, loops)
- Easy to customize
- Industry standard
- Can load from files later

### 6. Application Tracker (`tracker.py`)

**Purpose**: Business logic for tracking applications

**Design Decisions**:

- Context manager pattern (`with ApplicationTracker()`)
- High-level methods (not raw SQL)
- Follow-up detection logic
- Statistics aggregation

**Key Methods**:

- `get_or_create_job_application()` - Idempotent creation
- `get_applications_needing_follow_up()` - Business logic
- `record_email_sent()` - Audit trail
- `get_statistics()` - Reporting

**Why context manager?**

- Ensures database session cleanup
- Prevents connection leaks
- Cleaner code

### 7. Main Orchestrator (`main.py`)

**Purpose**: Coordinate all components

**Design Decisions**:

- Rich library for beautiful CLI
- Progress bars for long operations
- Dry-run mode for safety
- Separate methods for different operations

**Workflow**:

```
User runs: python main.py
    ↓
CVMailer.__init__()
    ├─ Validate config
    ├─ Initialize database
    ├─ Initialize Sheets client
    ├─ Initialize Gmail client
    └─ Initialize tracker
    ↓
process_new_applications()
    ├─ Read from Sheets
    ├─ For each row:
    │   ├─ Validate
    │   ├─ Check if sent
    │   ├─ Generate email
    │   ├─ Send (with rate limiting)
    │   ├─ Record in DB
    │   └─ Update sheet
    └─ Return count
    ↓
send_follow_ups() (if enabled)
    ├─ Query applications needing follow-up
    ├─ Generate follow-up email
    ├─ Send
    └─ Record
```

## Data Flow

### Sending a New Application Email

```
1. User: python main.py
   ↓
2. CVMailer reads Google Sheet
   ↓
3. For each row:
   a. Extract: company, position, email, etc.
   b. Tracker: get_or_create_job_application()
      → Check DB if exists
      → Create if new
   c. Check: Has email been sent? (DB query)
   d. EmailTemplate: render_first_contact()
      → Generate subject & body
   e. GmailSender: send_email()
      → Check rate limits (DB query)
      → Wait if needed
      → Create MIME message
      → Attach resume
      → Send via Gmail API
      → Update daily stats (DB)
   f. Tracker: record_email_sent()
      → Save to EmailRecord table
      → Update JobApplication status
   g. Sheets: update_cell()
      → Update "Status" column
```

### Sending a Follow-up

```
1. Tracker: get_applications_needing_follow_up()
   → Query: status = REACHED_OUT or APPLIED
   → For each: Check last email date
   → Filter: last_email > 7 days ago
   → Filter: follow_up_count < MAX_FOLLOW_UPS
   ↓
2. For each application:
   a. Get follow-up number (count existing + 1)
   b. EmailTemplate: render_follow_up()
   c. GmailSender: send_email()
   d. Tracker: record_email_sent(is_follow_up=True)
```

## Design Principles Applied

### 1. **SOLID Principles**

- **Single Responsibility**: Each class has one job
  - `GoogleSheetsClient` → only Sheets operations
  - `GmailSender` → only email sending
  - `ApplicationTracker` → only tracking logic

- **Open/Closed**: Open for extension, closed for modification
  - New email types: extend `EmailTemplate`
  - New data sources: implement new client class
  - New statuses: add to `JobStatus` enum

- **Liskov Substitution**: Not heavily used (no inheritance hierarchy)

- **Interface Segregation**: Small, focused interfaces
  - Each client class has minimal public API

- **Dependency Inversion**: Depend on abstractions
  - `CVMailer` depends on client classes, not implementations
  - Could swap SQLite for PostgreSQL easily

### 2. **DRY (Don't Repeat Yourself)**

- Configuration in one place (`config.py`)
- Database session creation centralized
- Email template logic separated

### 3. **KISS (Keep It Simple, Stupid)**

- SQLite for simplicity (not PostgreSQL)
- Class-based config (not complex YAML)
- Direct file paths (not complex routing)

### 4. **YAGNI (You Aren't Gonna Need It)**

- No complex caching (not needed yet)
- No message queue (simple sequential processing)
- No microservices (monolith is fine for this scale)

## Error Handling Strategy

1. **Configuration Errors**: Fail fast at startup
2. **API Errors**: Log and continue (don't crash on one failure)
3. **Database Errors**: Rollback transactions
4. **Rate Limit Errors**: Skip and log warning

## Security Considerations

1. **Credentials**: Never committed (`.gitignore`)
2. **Environment Variables**: Sensitive data in `.env`
3. **OAuth Tokens**: Stored locally, encrypted by Google
4. **Rate Limiting**: Prevents abuse detection

## Extensibility Points

### Easy to Extend

1. **New Email Types**: Add method to `EmailTemplate`
2. **New Data Sources**: Implement new client (e.g., `CSVClient`)
3. **New Statuses**: Add to `JobStatus` enum
4. **New Tracking Fields**: Add columns to models
5. **Web UI**: Add Flask/FastAPI layer using existing modules

### Would Require Refactoring

1. **Multi-account Support**: Need to refactor `GmailSender`
2. **Async Processing**: Need to add async/await
3. **Distributed System**: Need message queue

## Performance Considerations

1. **Database**: SQLite is fine for single-user, can upgrade later
2. **API Calls**: Sequential (rate limiting), could parallelize with care
3. **Memory**: Loads all rows into memory (fine for typical use)
4. **Rate Limiting**: Database queries on each email (acceptable overhead)

## Testing Strategy (Future)

- **Unit Tests**: Each module independently
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test full workflow with mock APIs

## Trade-offs Made

1. **SQLite vs PostgreSQL**: Chose SQLite for simplicity (can upgrade)
2. **Synchronous vs Async**: Chose sync for simplicity (can add async)
3. **CLI vs GUI**: Started with CLI (easier to add GUI later)
4. **Single Sheet vs Multi-Sheet**: Started with single (needs update - see below)

## Current Limitation: Multi-Sheet Support

The current implementation assumes a single worksheet. Your use case has multiple sheets (one per date). This needs to be addressed.

**Current Code**:

```python
self.sheets_client = GoogleSheetsClient(Config.SPREADSHEET_ID, Config.WORKSHEET_NAME)
rows = self.sheets_client.read_all_rows()  # Only reads one sheet
```

**Needed Change**:

- List all sheets
- Process each sheet
- Track which sheet each application came from

This is a straightforward extension that maintains the architecture.
