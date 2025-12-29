# Feature Suggestions & Future Enhancements

**Roadmap of planned features and enhancements for CV Mailer.**

> 📖 **Current Features**: See [Changelog](../CHANGELOG.md) for implemented features

**Last Updated**: December 2025  
**Status**: Post-refactoring with REST API

> 📖 **Related Docs**: [Architecture](ARCHITECTURE.md) | [API Guide](../API_GUIDE.md) | [Setup Guide](../SETUP_GUIDE.md)

## ✅ Fully Implemented Features

### Core Application Features

- ✅ **Google Sheets Integration**
  - Read applications from spreadsheets
  - Multi-sheet support with filtering
  - Flexible column name matching
  - Update sheet status after sending emails
  - Custom message support from sheet

- ✅ **Gmail Integration**
  - Send emails via Gmail API
  - Resume attachment (file path or Google Drive link)
  - Rate limiting (daily limit, delays between emails)
  - Email tracking with message IDs
  - Error handling and retry logic

- ✅ **Application Management**
  - 11 application statuses with validation
  - Status transition validation
  - Status history tracking
  - Notes on status changes
  - Timeline of events
  - Search and filter (status, date, company, position)
  - Sorting (created_at, updated_at, status)
  - Pagination support

- ✅ **Email Management**
  - First contact emails
  - Follow-up emails with numbering
  - Email templates (Jinja2-based HTML)
  - Custom message support
  - Email history tracking
  - Email status tracking (sent, failed, pending, bounced)
  - Follow-up timing validation
  - Max follow-ups limit

- ✅ **Recruiter Management**
  - Multi-recruiter support per application
  - Recruiter parsing from sheet cells
  - Recruiter contact information
  - Application count per recruiter
  - Individual email tracking per recruiter

- ✅ **Statistics & Analytics**
  - Total applications count
  - Applications by status
  - Total emails sent
  - Follow-up emails count
  - Applications reached interviews
  - Applications reached offers
  - Applications reached out
  - Interview breakdown
  - Response rate calculation

### REST API (FastAPI)

- ✅ **Complete API Endpoints**
  - Applications CRUD with filtering, searching, sorting, pagination
  - Email records management
  - Recruiter management
  - Statistics endpoints (comprehensive and summary)
  - Sync endpoints (Google Sheets sync, follow-ups)
  - Health check endpoint
  - Timeline endpoint

- ✅ **API Features**
  - Auto-generated OpenAPI documentation (`/docs`, `/redoc`)
  - CORS support for web frontends
  - Dependency injection pattern
  - Pydantic models for validation
  - Comprehensive error handling
  - Pagination support

**Documentation**: See `docs/API_GUIDE.md`

### Web Dashboard (React)

- ✅ **Status**: Completed (December 2025)
- **Tech Stack**:
  - Backend: FastAPI ✅
  - Frontend: React 18 + TypeScript + Vite ✅
  - Styling: Tailwind CSS with custom design system ✅
  - Data Fetching: TanStack Query ✅
  - Charts: Recharts ✅
  - UI: Dark mode support ✅

- ✅ **Implemented Features**:
  - **Dashboard Page**:
    - Statistics overview cards
    - Bar chart of applications by status
    - Status breakdown with detailed statistics
    - Recent applications list
    - Google Sheets sync controls
  - **Applications Page**:
    - Infinite scroll pagination
    - Search by company/position (debounced)
    - Multi-select status filtering
    - Date filtering (today, this week, this month)
    - Sorting (created_at, updated_at, status)
    - Progress tracker visualization (toggleable)
    - Expandable rows
    - Action menu per application
    - Clear all filters button
  - **Application Detail Page**:
    - Complete application information
    - Progress tracker visualization
    - Timeline of events
    - Email history with viewer modal
    - Recruiter information card
    - Status update with notes
    - Trigger reach-out and follow-up actions (✅ Email sending from UI is implemented)
  - **Recruiters Pages**:
    - Grid view of all recruiters
    - Recruiter detail view with applications
  - **UI/UX**:
    - Responsive design (mobile-friendly)
    - Dark mode support
    - Error handling and loading states
    - Toast notifications
    - Error boundary
    - Theme-aware chart labels

- **Documentation**: See `docs/WEB_DASHBOARD_GUIDE.md`
- **Location**: `frontend/` directory

### CLI Interface

- ✅ **Commands**:
  - Process new applications (`cv-mailer`)
  - Send follow-ups (`cv-mailer --follow-ups`)
  - View statistics (`cv-mailer --stats`)
  - Dry-run mode (`cv-mailer --dry-run`)
  - Repair follow-up numbering (`cv-mailer --repair-followups`)

- ✅ **Features**:
  - Rich terminal UI with progress bars
  - Color-coded output
  - Error handling
  - Configuration validation

### Code Quality & Architecture

- ✅ **Modern Package Structure**
  - Proper Python packaging (`src/` layout)
  - CLI entry points (`cv-mailer`, `cv-mailer-api`)
  - Organized directories (`data/`, `logs/`, `assets/`)
  - Pip installable (`pip install -e .`)

- ✅ **Production Readiness**
  - Comprehensive logging (65+ functions)
  - Custom exception system
  - Status constants (DRY principle)
  - Input validation utilities
  - Transaction management
  - Database indexes for performance
  - Repository pattern
  - Service layer pattern
  - Dependency injection

**Quick Start**:

```bash
# Start API
cv-mailer-api

# Start Dashboard (in new terminal)
cd frontend && npm install && npm run dev
# Open http://localhost:3000
```

---

## 🔮 Planned Features

The following features are **not yet implemented** and are planned for future releases:

## 🔥 High Priority Features

### 2. Authentication & Authorization

- **Status**: Needed for Multi-User
- **Description**: Secure API access for production deployment
- **Implementation**:
  - OAuth2 with JWT tokens
  - User registration/login
  - Role-based access control (RBAC)
  - API key management
- **Tech Stack**:
  - `python-jose` for JWT
  - `passlib` for password hashing
  - FastAPI Security utilities
- **Priority**: High if deploying publicly

### 3. Email Response Parsing

- **Status**: Not Started
- **Description**: Automatically detect and parse responses from recruiters
- **Implementation**:
  - Gmail API to read incoming emails (read scope needed)
  - NLP to detect positive/negative responses
  - Auto-update application status
  - Extract interview dates/times
  - Link responses to applications (by subject/message-id)
- **Tech Stack**:
  - Gmail API (watch/push notifications)
  - spaCy or transformers for NLP
  - OpenAI API for response classification (optional)
- **Database Changes**:
  - Add `ResponseRecord.sentiment` field
  - Add `ResponseRecord.entities` (JSON field for dates, contacts)

### 3. Calendar Integration

- **Status**: Not Started
- **Description**: Sync interview dates to Google Calendar
- **Features**:
  - Auto-create calendar events from email responses
  - Reminders before interviews
  - Link interviews to job applications
  - Two-way sync (calendar → application status)
- **Implementation**:
  - Google Calendar API
  - Event parsing from email responses
  - `JobApplication.interview_datetime` field

## 🎯 Medium Priority Features

### 4. Advanced Analytics & Reporting

- **Status**: Basic statistics available ✅ | Advanced Pending
- **Current**: Application counts by status, email counts
- **Future**:
  - Response rate by company/industry
  - Time to response (average days)
  - Follow-up effectiveness (which number works best)
  - Application funnel visualization
  - Success rate by job type
  - Best time to send emails (day/hour analysis)
- **API Endpoints**: Extend `/api/v1/statistics/*`
- **Visualization**: Chart.js, Recharts, or D3.js in web UI

### 5. Multi-Resume Support

- **Status**: Not Started
- **Description**: Use different resumes for different job types
- **Implementation**:
  - `JobApplication.resume_version` field
  - `assets/resumes/` directory structure
  - Resume selection based on:
    - Job category (manual tagging)
    - Keywords in job description
    - Company type (startup vs. enterprise)
  - A/B testing different resumes
- **Configuration**:

  ```env
  RESUME_GENERAL=./assets/resumes/general.pdf
  RESUME_BACKEND=./assets/resumes/backend.pdf
  RESUME_FULLSTACK=./assets/resumes/fullstack.pdf
  ```

### 6. Email Template Management

- **Status**: Templates in code | UI Management Pending
- **Current**: Templates in `src/cv_mailer/services/template_service.py`
- **Future**:
  - Database-stored templates
  - Template library (per job type, per company)
  - Visual template editor
  - Variable substitution preview
  - A/B testing templates
  - Template versioning
- **Database Changes**:
  - `EmailTemplate` model (not to confuse with the service)
  - `template_id` foreign key in `EmailRecord`

### 7. Email Scheduling

- **Status**: Not Started
- **Description**: Schedule emails to be sent at specific times
- **Features**:
  - Send during business hours only (9am-5pm)
  - Timezone support (recruiter's timezone)
  - Queue management (pause/resume)
  - Batch scheduling (spread over days)
- **Implementation**:
  - Celery or APScheduler
  - Redis for job queue
  - `EmailRecord.scheduled_at` field

### 8. Bulk Operations & CSV Import/Export

- **Status**: Not Started
- **Features**:
  - Import applications from CSV
  - Export applications to CSV/Excel
  - Bulk status updates
  - Bulk email sending with delays
  - Selective processing (by filter)
- **API Endpoints**:
  - `POST /api/v1/applications/import` (CSV upload)
  - `GET /api/v1/applications/export?format=csv`
  - `PUT /api/v1/applications/bulk-update`

### 9. Notification System

- **Status**: Not Started
- **Description**: Get notified of important events
- **Channels**:
  - Email notifications (sent to your email)
  - Slack integration (webhooks)
  - Discord integration
  - Desktop notifications (web UI)
  - SMS alerts (Twilio)
- **Events**:
  - New response received
  - Follow-up needed
  - Interview scheduled
  - Daily summary
- **Implementation**: Event-driven architecture with webhooks

## 💡 Nice-to-Have Features

### 10. LinkedIn Integration

- **Status**: Not Started
- **Description**: Auto-extract recruiter info from LinkedIn
- **Features**:
  - Find recruiter emails from LinkedIn profiles
  - Company information lookup
  - Profile matching (find best contact)
  - Auto-populate application data
- **Challenges**: LinkedIn doesn't have public API for this
- **Alternative**: Browser extension or manual paste

### 11. Job Board Integration

- **Status**: Not Started
- **Description**: Auto-import jobs from job boards
- **Sources**:
  - LinkedIn Jobs (no official API)
  - Indeed (no public API anymore)
  - Glassdoor (limited API)
  - Custom RSS feeds
  - Company career pages (web scraping)
- **Implementation**: Web scraping with `playwright` or `selenium`
- **Legal**: Check ToS before scraping

### 12. AI-Powered Email Generation

- **Status**: Not Started
- **Description**: Generate personalized emails using AI
- **Features**:
  - Analyze job description
  - Match with your resume
  - Generate personalized email
  - Tone adjustment (formal/casual)
  - Highlight relevant skills
- **Tech Stack**:
  - OpenAI API (GPT-4)
  - Anthropic API (Claude)
  - Or local LLM (Llama 3)
- **API Endpoint**: `POST /api/v1/emails/generate-draft`

### 13. Multi-Account Support

- **Status**: Not Started
- **Description**: Manage multiple Gmail accounts
- **Use Cases**:
  - Different emails for different job types
  - A/B testing from addresses
  - Regional accounts
- **Implementation**:
  - Multiple OAuth tokens
  - Account selection per application
  - Per-account rate limits
  - Unified dashboard

### 14. Email Tracking & Analytics

- **Status**: Not Started
- **Description**: Track email opens and link clicks
- **Features**:
  - Pixel tracking (1x1 image)
  - Link tracking (redirect through API)
  - Read receipts
  - Click-through rate
- **Implementation**:
  - Tracking pixel in email HTML
  - Short links with tracking
  - Database: `EmailEngagement` table
- **Privacy**: Inform recipients about tracking

### 15. Interview Preparation Assistant

- **Status**: Not Started (Future)
- **Description**: Help prepare for interviews
- **Features**:
  - Company research summary
  - Common interview questions
  - Your relevant experience mapping
  - Mock interview questions
  - Notes and reminders
- **Integration**: Link with job applications

## 🛠️ Technical Improvements

### 16. Database Migrations (Alembic)

- **Status**: Not Started | Needed for Schema Changes
- **Description**: Proper migration system for database schema changes
- **Implementation**:

  ```bash
  pip install alembic
  alembic init alembic
  alembic revision --autogenerate -m "Initial migration"
  alembic upgrade head
  ```

- **Benefits**: Safe schema updates without data loss

### 17. Comprehensive Testing Suite

- **Status**: Structure Ready | Tests Pending
- **Types**:
  - Unit tests (services, parsers, utils)
  - Integration tests (database, Gmail API, Sheets API)
  - API tests (FastAPI TestClient)
  - E2E tests (full workflow)
- **Structure**:

  ```
  tests/
  ├── unit/
  ├── integration/
  └── e2e/
  ```

- **Tools**: pytest, pytest-cov, pytest-mock

### 18. Docker Support

- **Status**: Not Started
- **Description**: Containerize the application
- **Files Needed**:
  - `Dockerfile` (Python app)
  - `docker-compose.yml` (app + database + cache)
  - `.dockerignore`
- **Benefits**:
  - Easy deployment
  - Consistent environment
  - Production-ready
- **Configuration**: Mount `.env` and credentials

### 19. CI/CD Pipeline

- **Status**: Not Started
- **Description**: Automated testing and deployment
- **Platform**: GitHub Actions / GitLab CI
- **Pipeline**:
  - Lint (black, isort, flake8, mypy)
  - Test (pytest)
  - Build (Docker image)
  - Deploy (optional)
- **File**: `.github/workflows/ci.yml`

### 20. Database Performance Optimization

- **Status**: SQLite Sufficient | PostgreSQL Optional
- **Improvements**:
  - Add database indexes on frequently queried fields
  - Connection pooling for API
  - Query optimization (eager loading)
  - Caching (Redis) for expensive queries
- **Migration**: SQLite → PostgreSQL for production

  ```python
  # config/settings.py
  DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/cv_mailer.db")
  # Set to: postgresql://user:pass@host:5432/cv_mailer
  ```

### 21. Caching Layer

- **Status**: Not Started
- **Description**: Cache expensive operations
- **Use Cases**:
  - Statistics (cache for 60 seconds)
  - Application lists (cache per filter)
  - Sheets data (cache per sheet)
- **Tech**: Redis + `fastapi-cache2`
- **Implementation**:

  ```python
  @cache(expire=60)
  async def get_statistics():
      ...
  ```

### 22. Rate Limiting for API

- **Status**: Not Started | Needed for Production
- **Description**: Protect API from abuse
- **Implementation**:
  - `slowapi` for FastAPI
  - Rate limit per IP: 100 requests/minute
  - Rate limit per endpoint
- **Example**:

  ```python
  @limiter.limit("100/minute")
  @router.get("/applications")
  async def list_applications():
      ...
  ```

### 23. Monitoring & Logging

- **Status**: Basic Logging ✅ | Advanced Pending
- **Current**: Log to `logs/cv_mailer.log`
- **Future**:
  - Structured logging (JSON format)
  - Log aggregation (ELK stack, Datadog)
  - Error tracking (Sentry)
  - Performance monitoring (APM)
  - Metrics (Prometheus + Grafana)

## 🔒 Security Enhancements

### 24. Secrets Management

- **Status**: `.env` File | Vault Pending
- **Current**: Secrets in `.env` (good for local)
- **Future**:
  - AWS Secrets Manager
  - HashiCorp Vault
  - Azure Key Vault
  - Google Secret Manager
- **Priority**: High for production deployment

### 25. Database Encryption

- **Status**: Not Started
- **Description**: Encrypt sensitive data at rest
- **Fields to Encrypt**:
  - Recruiter emails
  - Personal notes
  - Resume content (if stored)
- **Implementation**: SQLAlchemy hybrid properties with encryption

### 26. API Authentication

- **Status**: Not Started | Required for Multi-User
- **Implementation**:
  - JWT tokens
  - OAuth2 password flow
  - Refresh tokens
  - API keys for integrations
- **Endpoints**:
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/refresh`
  - `POST /api/v1/auth/logout`

### 27. Audit Logging

- **Status**: Email Records ✅ | Comprehensive Pending
- **Current**: `EmailRecord` tracks all sent emails
- **Future**:
  - Comprehensive audit trail
  - Log all status changes
  - Log all configuration changes
  - Log all API access
  - Tamper-proof logs
- **Table**: `AuditLog(id, user_id, action, resource, timestamp)`

## 🎨 User Experience Enhancements

### 28. Interactive CLI Improvements

- **Status**: Rich Console ✅ | Interactive Pending
- **Current**: Rich progress bars, tables, colors
- **Future**:
  - Interactive prompts (`questionary`)
  - Command completion (shell completion)
  - Fuzzy search for applications
  - TUI (Terminal UI) with `textual`
- **Example**: `cv-mailer tui` for full-screen terminal UI

### 29. Email Preview Mode

- **Status**: Not Started
- **Description**: Preview emails before sending
- **Features**:
  - HTML preview in browser
  - Test variable substitution
  - Preview with different data
  - Send test email to self
- **Implementation**: `cv-mailer preview --application-id 1`

### 30. Configuration Validation & Testing

- **Status**: Basic Validation ✅ | Testing Pending
- **Current**: `Config.validate()` checks required fields
- **Future**:
  - Test Gmail connection
  - Test Sheets connection
  - Verify resume file exists
  - Check API quotas
  - Validate email templates
- **Command**: `cv-mailer test-config`

### 31. Onboarding Wizard

- **Status**: Not Started
- **Description**: Interactive setup wizard for first-time users
- **Steps**:
  1. Welcome message
  2. Check Python version
  3. Create virtual environment
  4. Install dependencies
  5. Configure `.env` (interactive prompts)
  6. Set up Google Cloud credentials
  7. Test connections
  8. Create first application
  9. Send test email
- **Command**: `cv-mailer setup`

## 📊 Implementation Roadmap

### Phase 1: Foundation Complete ✅ (December 2025)

- ✅ REST API with FastAPI
- ✅ Modern package structure
- ✅ Multi-sheet support
- ✅ Multi-recruiter support
- ✅ Comprehensive documentation
- ✅ Web Dashboard (React + TypeScript)

### Phase 2: Web UI (Completed ✅ - December 2025)

- ✅ Frontend application (React + TypeScript + Vite)
- ✅ Dashboard with charts and statistics
- ✅ Application management interface (search, filter, sort, pagination)
- ✅ Application detail page (timeline, email history, progress tracker)
- ✅ Recruiter management pages
- ✅ Google Sheets sync from UI
- ✅ Status updates from UI
- ✅ Trigger reach-out and follow-up from UI
- ✅ Dark mode support
- ✅ Responsive design
- [ ] Authentication system (Future)
- [ ] Real-time updates via WebSockets (Future)

### Phase 3: Intelligence (Q2 2026)

- [ ] Email response parsing
- [ ] Calendar integration
- [ ] Advanced analytics
- [ ] AI-powered email generation

### Phase 4: Scalability (Q3 2026)

- [ ] Database migrations (Alembic)
- [ ] Caching layer (Redis)
- [ ] Email scheduling (Celery)
- [ ] Docker deployment

### Phase 5: Enterprise (Q4 2026)

- [ ] Multi-account support
- [ ] Advanced security (secrets vault)
- [ ] Comprehensive testing
- [ ] Production monitoring

## 🤝 Contributing

Want to implement any of these features?

**Process**:

1. Open an issue to discuss the feature
2. Create a feature branch from `main`
3. Follow existing code style (Black, isort, mypy)
4. Add tests for new functionality
5. Update relevant documentation
6. Submit a pull request

**Development Setup**:

```bash
git clone https://github.com/lakshyads/cv-mailer.git
cd cv-mailer
pip install -e ".[dev]"
```

**Code Quality**:

```bash
black src/ tests/      # Format code
isort src/ tests/      # Sort imports
mypy src/              # Type checking
flake8 src/            # Linting
pytest                 # Run tests
```

## 📝 Feature Request Template

To request a new feature, open an issue with:

**Title**: `[Feature Request] <Brief Description>`

**Content**:

```markdown
## Description
What feature would you like to see?

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How would you implement this?

## Alternatives
What alternatives have you considered?

## Additional Context
Any other information, mockups, or examples?
```

## 📧 Contact

- **Issues**: <https://github.com/lakshyads/cv-mailer/issues>
- **Email**: <lakshyads.96@gmail.com>
- **LinkedIn**: <https://www.linkedin.com/in/lakshya-dev-singh>

---

**Note**: This is a living document. Features are added and prioritized based on user feedback and practical utility.

**Last Updated**: December 2025
