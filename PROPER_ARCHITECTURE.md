# Proper Architecture - Single Source of Truth

## ✅ Correct Architecture (After Final Refactoring)

```
┌─────────────────────────────────────────────────────────────┐
│                   Presentation Layer                         │
│  (Request/Response handling ONLY - NO business logic)       │
├──────────────────────┬──────────────────────────────────────┤
│   CLI Application    │   API Application                    │
│                      │                                       │
│   - Parse arguments  │   - Parse HTTP requests              │
│   - Display output   │   - Return HTTP responses            │
│   - User interaction │   - Handle errors → HTTP codes       │
└──────────┬───────────┴───────────┬──────────────────────────┘
           │                       │
           │  Both call the same   │
           │  service methods      │
           │                       │
┌──────────▼───────────────────────▼──────────────────────────┐
│                     SERVICE LAYER                            │
│         ⭐ SINGLE SOURCE OF TRUTH FOR BUSINESS LOGIC ⭐       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ApplicationService           EmailService                  │
│  ├─ get_application()         ├─ send_first_contact()       │
│  ├─ list_applications()       ├─ send_follow_up()           │
│  ├─ search_applications()     └─ [respects FOLLOW_UP_DAYS]  │
│  ├─ update_status()                                          │
│  └─ get_application_timeline()                              │
│                                                              │
│  RecruiterService             StatisticsService             │
│  ├─ get_recruiter()           ├─ get_statistics()           │
│  └─ list_recruiters()         └─ get_summary()              │
│                                                              │
│  ⚠️  ALL business rules, validations, and logic HERE        │
│  ⚠️  Any feature change ONLY touches this layer             │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                  REPOSITORY LAYER                            │
│       (Data access ONLY - NO business logic)                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ApplicationRepository                                       │
│  ├─ find_by_id()              ← Pure data access            │
│  ├─ find_all()                ← Database queries only       │
│  ├─ search()                  ← No validation/rules         │
│  └─ get_emails_count()                                       │
│                                                              │
│  EmailRepository              RecruiterRepository           │
│  ├─ find_by_application()     ├─ find_by_id()               │
│  └─ find_all()                └─ find_all()                 │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                   DATABASE                                   │
│  (SQLite with indexes)                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Golden Rules

### 1. **Service Layer is the ONLY place for business logic**

✅ **CORRECT** - Business logic in service:
```python
# services/application_service.py
def update_status(self, app_id: int, status: JobStatus, notes: str):
    """Business logic for updating status."""
    app = self.repository.find_by_id(app_id)
    
    # ✅ Business rule: Set closed_at for terminal states
    if status in [JobStatus.REJECTED, JobStatus.ACCEPTED, ...]:
        app.closed_at = datetime.now(timezone.utc)
    
    # ✅ Business rule: Reopen if moving from terminal state
    elif app.closed_at:
        app.closed_at = None
    
    app.status = status
    self.repository.session.commit()
```

❌ **WRONG** - Business logic in API/CLI:
```python
# ❌ NEVER do this in API router:
@router.put("/applications/{id}/status")
async def update_status(...):
    app = repo.find_by_id(id)
    if status in [JobStatus.REJECTED, ...]:  # ❌ Business logic!
        app.closed_at = datetime.now()
```

### 2. **API routers are thin controllers**

✅ **CORRECT** - Router calls service:
```python
@router.get("/applications")
async def list_applications(
    service: ApplicationService = Depends(get_application_service)
):
    # ✅ Just call service, handle response
    applications, total = service.list_applications(...)
    return PaginatedResponse(items=applications, total=total)
```

❌ **WRONG** - Router has business logic:
```python
@router.get("/applications")
async def list_applications(repo: Repo = Depends(...)):
    # ❌ Direct repository access
    query = repo.session.query(Application)
    # ❌ Business logic in router
    if status:
        query = query.filter_by(status=status)
    applications = query.all()
```

### 3. **CLI uses same services as API**

✅ **CORRECT** - CLI calls service:
```python
# cli/app.py
class CVMailer:
    def __init__(self):
        self.app_service = ApplicationService()
        self.email_service = EmailService()
    
    def show_statistics(self):
        # ✅ Uses same service as API
        stats = StatisticsService().get_statistics()
        display.show_statistics(stats)
```

❌ **WRONG** - CLI has duplicate logic:
```python
# cli/app.py
def show_statistics(self):
    # ❌ Duplicates what StatisticsService does
    total = self.session.query(Application).count()
    by_status = {...}  # Same logic as service
```

### 4. **Repository layer is pure data access**

✅ **CORRECT** - Repository returns data:
```python
class ApplicationRepository:
    def find_all(self, status, limit, offset):
        """Pure data access - no business rules."""
        query = self.session.query(JobApplication)
        if status:
            query = query.filter_by(status=status)
        return query.offset(offset).limit(limit).all()
```

❌ **WRONG** - Repository has business logic:
```python
class ApplicationRepository:
    def find_all(self, status):
        query = self.session.query(JobApplication)
        # ❌ Business rule in repository
        if status == JobStatus.REACHED_OUT:
            # Check follow-up timing...  ❌ This belongs in service!
```

---

## 📁 File Organization

### Service Layer (`src/cv_mailer/services/`)

**Purpose:** ALL business logic resides here

```
services/
├── __init__.py                    # Export all services
├── application_service.py         # ⭐ Application business logic
├── email_service.py               # ⭐ Email sending business logic
├── recruiter_service.py           # ⭐ Recruiter business logic
├── statistics_service.py          # ⭐ Statistics business logic
├── template_service.py            # Email template rendering
└── tracker.py                     # Legacy (being phased out)
```

**Each service:**
- ✅ Contains all business rules for its domain
- ✅ Validates input
- ✅ Enforces constraints (e.g., follow-up timing)
- ✅ Orchestrates operations (e.g., send email + update status)
- ✅ Used by BOTH CLI and API

### API Layer (`src/cv_mailer/api/`)

**Purpose:** HTTP request/response handling ONLY

```
api/
├── app.py                         # FastAPI setup (NO business logic)
├── dependencies.py                # Dependency injection
├── schemas/                       # Pydantic models for validation
│   ├── application.py
│   ├── email.py
│   └── recruiter.py
└── routers/                       # Thin controllers
    ├── applications.py            # ✅ Calls ApplicationService
    ├── emails.py                  # ✅ Calls EmailService
    ├── recruiters.py              # ✅ Calls RecruiterService
    └── stats.py                   # ✅ Calls StatisticsService
```

**Each router:**
- ✅ Parses request parameters
- ✅ Calls service method
- ✅ Returns response
- ❌ NO business logic
- ❌ NO direct repository access
- ❌ NO database queries

### CLI Layer (`src/cv_mailer/cli/`)

**Purpose:** User interaction and display ONLY

```
cli/
├── app.py                         # ✅ Calls services (same as API)
├── commands.py                    # Argument parsing
└── display.py                     # Terminal output formatting
```

### Repository Layer (`src/cv_mailer/repositories/`)

**Purpose:** Database queries ONLY

```
repositories/
├── application_repository.py      # Application data access
├── email_repository.py            # Email data access
└── recruiter_repository.py        # Recruiter data access
```

---

## 🔄 Data Flow Examples

### Example 1: Triggering Follow-up (API)

```
1. User clicks "Send Follow-up" in UI
   ↓
2. Frontend: POST /api/v1/applications/1/trigger-follow-up
   ↓
3. API Router (applications.py):
   - Parse request
   - Call: email_service.send_follow_up(1)
   - Return response
   ↓
4. EmailService (email_service.py):
   - ✅ Check timing: tracker.can_send_follow_up()
   - ✅ Validate status must be REACHED_OUT
   - ✅ Check max follow-ups
   - ✅ If valid: send emails
   - ✅ Update application status
   - Return result
   ↓
5. API Router: Return EmailActionResponse
```

### Example 2: Triggering Follow-up (CLI)

```
1. User runs: cv-mailer --follow-ups
   ↓
2. CLI App (cli/app.py):
   - Parse arguments
   - Call: self.send_follow_ups()
   ↓
3. CVMailer.send_follow_ups():
   - Get apps: tracker.get_applications_needing_follow_up()
   - For each app: email_service.send_follow_up(app.id)
   - Display results
   ↓
4. EmailService (email_service.py):
   - ✅ SAME business logic as API path
   - Check timing, send emails, update status
   ↓
5. CLI: Display Rich console output
```

**🎯 Notice:** Steps 4 is IDENTICAL for both API and CLI!

---

## ✅ Verification Checklist

Use this to verify architecture is correct:

### Service Layer Checklist

- [ ] All business logic is in services
- [ ] Services contain validation rules
- [ ] Services enforce constraints (timing, limits, etc.)
- [ ] Services orchestrate operations
- [ ] No business logic in routers/controllers
- [ ] No business logic in repositories
- [ ] CLI and API use same service methods

### API Router Checklist

- [ ] Routers are < 50 lines per endpoint
- [ ] Routers only parse requests
- [ ] Routers only call service methods
- [ ] Routers only format responses
- [ ] No database queries in routers
- [ ] No business rules in routers
- [ ] No direct repository access

### Repository Checklist

- [ ] Repositories only do database queries
- [ ] No validation in repositories
- [ ] No business rules in repositories
- [ ] Repositories return raw data
- [ ] Repositories are reusable

### CLI Checklist

- [ ] CLI calls service methods (same as API)
- [ ] CLI only handles user interaction
- [ ] CLI only formats output
- [ ] No duplicate business logic
- [ ] No direct database queries

---

## 🚀 Benefits of This Architecture

### 1. **Single Source of Truth**
- ✅ Feature change in ONE place (service)
- ✅ Bug fix in ONE place
- ✅ CLI and API automatically consistent

### 2. **Easy to Test**
- ✅ Test service layer independently
- ✅ Mock repositories for unit tests
- ✅ Test API routers with mocked services

### 3. **Scalable**
- ✅ Add new endpoints easily (just call service)
- ✅ Add new features (extend service)
- ✅ Add new interfaces (mobile app, webhooks)

### 4. **Maintainable**
- ✅ Clear separation of concerns
- ✅ Easy to understand (each layer has one job)
- ✅ Easy to debug (trace through layers)

### 5. **Ready for Millions of Users**
- ✅ Can add caching at service layer
- ✅ Can add async/await throughout
- ✅ Can add message queues
- ✅ Can add load balancing
- ✅ Can scale horizontally

---

## 📝 Quick Reference

### Where to Put Code

| Type of Code | Layer | Example |
|-------------|-------|---------|
| HTTP parsing | API Router | Parse query params |
| Argument parsing | CLI Commands | argparse logic |
| Business rules | Service | Follow-up timing check |
| Validation | Service | Check status transitions |
| Database query | Repository | `session.query(...)` |
| Email sending | Service | Send + log + update status |
| Display output | CLI Display | Rich console formatting |
| Response formatting | API Router | Return Pydantic model |

### What NOT to Do

❌ **NEVER** put business logic in:
- API routers
- CLI command handlers
- Repositories
- Database models

✅ **ALWAYS** put business logic in:
- Service layer ONLY

---

## 🎉 Result

**Your architecture is now:**
- ✅ Industry-standard (Service + Repository pattern)
- ✅ Scalable to millions of users
- ✅ Single source of truth for all features
- ✅ Easy to maintain (change in ONE place)
- ✅ Easy to test (mock services/repositories)
- ✅ Ready for any interface (API, CLI, mobile, webhooks)

**Any feature change touches ONLY the service layer.**
**CLI and API automatically stay in sync.**

This is production-ready, enterprise-grade architecture. 🚀

