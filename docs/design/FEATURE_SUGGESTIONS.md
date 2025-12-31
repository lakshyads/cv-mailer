# Feature Suggestions & Future Enhancements

**Roadmap of planned features and enhancements for CV Mailer.**

> 📖 **Current Features**: See [Changelog](../CHANGELOG.md) for implemented features

**Last Updated**: January 2026  
**Status**: Post-refactoring with REST API, focusing on conversation management features

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

### 1. Email Conversation Threading & Management

- **Status**: Not Started
- **Description**: Maintain proper email conversation threads for each recruiter. Follow-ups should be replies to previous emails, creating a cohesive conversation trail.

#### 1.1 Email Threading (Reply-to-Previous)

- **Current**: Follow-up emails are sent as standalone emails
- **Future**: Follow-up emails should be replies to the original or previous email in the thread
- **Implementation**:
  - Store Gmail thread ID (`thread_id`) in `EmailRecord` model
  - Store `In-Reply-To` and `References` headers for proper threading
  - Link emails by `thread_id` and `gmail_message_id`
  - Modify `GmailSender.send_email()` to accept `thread_id` and `references` parameters
  - Update `EmailService.send_follow_up()` to fetch previous email's thread info
  - Gmail API: Use `threadId` parameter when sending replies
- **Database Changes**:
  - Add `EmailRecord.thread_id` (String) - Gmail thread ID
  - Add `EmailRecord.in_reply_to` (String) - Message ID of parent email
  - Add `EmailRecord.references` (Text) - References header chain
  - Add index on `thread_id` for efficient conversation queries
- **Benefits**:
  - Maintains proper email conversation context
  - Recruiters see full conversation history
  - Better email management in Gmail
  - Professional communication trail

#### 1.2 Conversation Tracking & UI

- **Status**: Not Started
- **Description**: Track and display complete email conversations for each recruiter per application
- **Implementation**:
  - New API endpoint: `GET /api/v1/applications/{id}/conversations` - Get all conversations grouped by recruiter
  - New API endpoint: `GET /api/v1/applications/{id}/conversations/{recruiter_id}` - Get conversation thread for specific recruiter
  - New API endpoint: `GET /api/v1/emails/{id}/thread` - Get all emails in a thread
  - Database query: Group emails by `thread_id` or `recipient_email` + `job_application_id`
  - Sort emails chronologically (oldest to newest) to show conversation flow
- **UI Components**:
  - Conversation view component showing threaded emails
  - Reverse chronological display (newest first, with expandable thread view)
  - Visual thread indicator (lines connecting emails in conversation)
  - Per-recruiter conversation tabs on application detail page
  - Email thread viewer modal with full conversation history
- **Data Model**:
  - Add `ConversationThread` model (optional) or query emails by `thread_id`
  - Store conversation metadata (total messages, last activity, participants)

#### 1.3 Selective Follow-up Triggering

- **Status**: Partially Supported (recruiter_id parameter exists but UI doesn't expose it)
- **Description**: Allow triggering follow-ups for specific recruiters, not all at once
- **Current**: `EmailService.send_follow_up()` already supports `recruiter_id` parameter
- **Implementation**:
  - Update API endpoint: `POST /api/v1/applications/{id}/send-follow-up` to accept optional `recruiter_ids[]` array
  - Frontend: Add recruiter selection UI before triggering follow-up
  - Show recruiter list with checkboxes/multi-select
  - Display conversation status for each recruiter (e.g., "3 messages in thread")
  - Default: Select all recruiters (maintain current behavior)
  - Per-recruiter follow-up button in conversation view
- **UI Enhancements**:
  - Recruiter cards with "Send Follow-up" button (individual action)
  - Bulk selection for multiple recruiters
  - Visual indicator showing last email sent date per recruiter

### 2. Email Response Parsing & Analysis (Enhanced)

- **Status**: Not Started
- **Description**: Automatically detect, parse, and analyze email responses from recruiters. Integrate seamlessly with conversation tracking and generate actionable insights.

#### 2.1 Response Detection & Parsing

- **Implementation**:
  - Gmail API to read incoming emails (requires `gmail.readonly` scope)
  - Watch/push notifications for new emails (Gmail API push notifications)
  - Link responses to applications via:
    - Thread ID matching (primary method)
    - Subject line matching (fallback)
    - Recipient email matching
  - Parse email content (HTML/text extraction)
  - Extract metadata: sender, timestamp, attachments
- **Database Changes**:
  - New model: `EmailResponse` or extend `EmailRecord` with `is_response` flag
  - Add `EmailRecord.is_response` (Boolean) - True for incoming emails
  - Add `EmailRecord.parent_email_id` (ForeignKey) - Link to original sent email
  - Store original email content and parsed text

#### 2.2 Response Analysis & Deductions

- **Implementation**:
  - NLP analysis using spaCy, transformers, or OpenAI API
  - Sentiment analysis (positive, negative, neutral, interested, not interested)
  - Intent classification:
    - Interview invitation
    - Rejection
    - Request for more information
    - Scheduling request
    - Offer discussion
    - No response needed (acknowledgment)
  - Entity extraction:
    - Interview dates/times
    - Phone numbers
    - Meeting links (Zoom, Teams, etc.)
    - Additional contact information
    - Salary/compensation mentions
- **Database Changes**:
  - Add `EmailResponse.analysis` (JSON) - Store analysis results
  - Add `EmailResponse.sentiment` (Enum: positive, negative, neutral)
  - Add `EmailResponse.intent` (Enum: interview, rejection, info_request, etc.)
  - Add `EmailResponse.extracted_entities` (JSON) - Dates, contacts, links
  - Add `EmailResponse.confidence_score` (Float) - Analysis confidence

#### 2.3 Action Items Generation

- **Description**: Generate actionable next steps based on response analysis
- **Implementation**:
  - Automatic status updates based on intent:
    - Interview invitation → Update status to `INTERVIEW_SCHEDULED`
    - Rejection → Update status to `REJECTED`
    - Offer discussion → Update status to `OFFER_RECEIVED`
  - Create action items:
    - "Schedule interview on [date]" → Calendar integration
    - "Respond with availability" → Quick reply template
    - "Send additional information" → Mark for follow-up
    - "No action needed" → Archive conversation
  - Manual review queue for uncertain responses
- **Database Changes**:
  - New model: `ActionItem`
    - `id`, `application_id`, `email_response_id`
    - `action_type` (Enum: schedule_interview, send_reply, update_status, etc.)
    - `description` (Text)
    - `due_date` (DateTime, optional)
    - `status` (Enum: pending, completed, cancelled)
    - `created_at`, `updated_at`
- **UI Components**:
  - Action items panel on application detail page
  - Action items dashboard (all pending items)
  - Quick actions from response analysis (one-click buttons)
  - Manual action item creation
  - Action item completion workflow

#### 2.4 Integration with Conversation View

- Display parsed responses in conversation thread
- Show analysis badges (sentiment, intent) on each response email
- Inline action suggestions below analyzed responses
- Highlight important information (dates, contacts) in response content

### 3. Email Editing & Customization Before Sending

- **Status**: Not Started
- **Description**: Allow users to edit email subject, content, and resume attachments before sending outreach or follow-up emails.

#### 3.1 Email Content Editing

- **Implementation**:
  - New API endpoint: `POST /api/v1/applications/{id}/send-outreach/preview` - Generate email preview with editable fields
  - New API endpoint: `POST /api/v1/applications/{id}/send-outreach` - Send with custom subject/content
  - New API endpoint: `POST /api/v1/applications/{id}/send-follow-up/preview` - Preview follow-up email
  - New API endpoint: `POST /api/v1/applications/{id}/send-follow-up` - Send follow-up with custom content
  - Request body includes:
    - `subject` (optional, uses template default if not provided)
    - `body` (optional, uses template default if not provided)
    - `recruiter_ids[]` (optional, for selective sending)
- **UI Components**:
  - Email composer modal/drawer
  - Rich text editor for email body (or markdown editor)
  - Subject line input
  - Live preview of rendered email
  - Template variable substitution preview
  - "Use default template" button to reset to template

#### 3.2 Resume File Selection & Editing

- **Description**: Select custom resume file or edit resume Google Drive link per email
- **Implementation**:
  - New API endpoints accept:
    - `resume_file_path` (optional) - Path to local resume file
    - `resume_drive_link` (optional) - Google Drive link to resume
    - If both provided, `resume_file_path` takes precedence
  - Resume selection dropdown in email composer:
    - "Default resume" (from config)
    - "Custom file..." (file picker)
    - "Google Drive link..." (text input)
    - Recent resumes (cached list)
  - Validate resume file exists (for local files)
  - Validate Google Drive link format
- **Database Changes**:
  - Add `EmailRecord.resume_file_path` (String, optional)
  - Add `EmailRecord.resume_drive_link` (Text, optional)
  - Store per-email resume info for historical tracking
- **UI Components**:
  - Resume selector component in email composer
  - File upload button (if using local files)
  - Google Drive link input with validation
  - Resume preview/icon display

### 4. Settings Page & Configuration Management

- **Status**: Not Started
- **Description**: Comprehensive settings page in UI for managing email templates, resume files, and application configuration.

#### 4.1 Email Template Management

- **Description**: Edit default email subjects and content/templates for outreach and follow-ups
- **Implementation**:
  - Settings page section: "Email Templates"
  - Template editor for:
    - First contact email (subject + body)
    - Follow-up email (subject + body, with follow-up number variable)
  - Template variables preview/documentation:
    - `{{ recruiter_name }}`, `{{ company_name }}`, `{{ position }}`, `{{ location }}`, `{{ job_posting_url }}`, `{{ follow_up_number }}`
  - Live preview with sample data
  - Save templates to database or config file
  - Reset to default templates
- **Database Changes** (Optional):
  - New model: `EmailTemplate`
    - `id`, `template_type` (Enum: first_contact, follow_up)
    - `subject` (Text), `body` (Text)
    - `is_default` (Boolean)
    - `created_at`, `updated_at`
  - Or store in config file/database config table
- **API Endpoints**:
  - `GET /api/v1/settings/templates` - Get all templates
  - `GET /api/v1/settings/templates/{type}` - Get specific template
  - `PUT /api/v1/settings/templates/{type}` - Update template
  - `POST /api/v1/settings/templates/{type}/reset` - Reset to default

#### 4.2 Resume File Management

- **Description**: Select and manage default/custom resume files
- **Implementation**:
  - Settings page section: "Resume Files"
  - Resume file list:
    - Default resume (from `RESUME_PATH` config)
    - Additional resume files (from `assets/resumes/` or configurable directory)
  - Actions:
    - Set default resume
    - Upload new resume file
    - Delete resume file (with confirmation)
    - Edit resume Google Drive link
  - Resume file metadata:
    - File name, size, upload date
    - Usage count (how many emails sent with this resume)
- **API Endpoints**:
  - `GET /api/v1/settings/resumes` - List all resume files
  - `POST /api/v1/settings/resumes` - Upload new resume
  - `PUT /api/v1/settings/resumes/default` - Set default resume
  - `DELETE /api/v1/settings/resumes/{id}` - Delete resume file

#### 4.3 Application Configuration

- **Description**: Edit default config values for `DAILY_EMAIL_LIMIT`, `FOLLOW_UP_DAYS`, `MAX_FOLLOW_UPS`
- **Implementation**:
  - Settings page section: "Application Settings"
  - Configuration form with:
    - Daily Email Limit (integer input with min/max validation)
    - Follow-up Days (integer input, days to wait before follow-up)
    - Max Follow-ups (integer input, maximum follow-ups per application)
    - Email Delay Min/Max (optional, delay between emails)
  - Input validation (positive integers, reasonable ranges)
  - Save to `.env` file or database config table
  - Apply changes immediately or require restart (based on implementation)
  - Show current values and allow reset to defaults
- **API Endpoints**:
  - `GET /api/v1/settings/config` - Get current configuration
  - `PUT /api/v1/settings/config` - Update configuration
  - `POST /api/v1/settings/config/reset` - Reset to defaults
- **Database Changes** (Optional):
  - Config table to store runtime configuration
  - Or update `.env` file (requires file system access)

#### 4.4 Settings Page UI

- **Location**: New route `/settings` in frontend
- **Layout**:
  - Tabbed interface or accordion sections:
    - Email Templates
    - Resume Files
    - Application Settings
    - (Future: Notifications, Integrations, etc.)
  - Save/Cancel buttons per section
  - Success/error toast notifications
  - Validation error display

### 5. Job Description Storage

- **Status**: Not Started
- **Description**: Store job description for each application to enable AI-powered personalized email generation.
- **Implementation**:
  - Database Changes:
    - Add `JobApplication.job_description` (Text) - Full job description text
    - Add `JobApplication.job_description_source` (String, optional) - URL or source of job description
  - Sheet Parser:
    - Add `job_description` column mapping in Google Sheets template
    - Parse and store job description from sheet row
  - Manual Entry:
    - Add job description field in application creation/edit forms
    - Allow paste from job posting URL
    - Text area with character limit (e.g., 10,000 chars)
  - API Changes:
    - Update `ApplicationCreate` schema to include `job_description`
    - Update `ApplicationUpdate` schema to include `job_description`
    - Include `job_description` in application detail responses
  - UI Components:
    - Job description display on application detail page (expandable/collapsible)
    - Job description editor in application form
    - "Fetch from URL" button (optional, future enhancement)
- **Use Cases**:
  - AI-powered email personalization (analyze job description, match skills)
  - Email content suggestions based on job requirements
  - Interview preparation (reference job description)
  - Job matching analysis

### 6. Google Calendar Integration & Dashboard Widget

- **Status**: Not Started
- **Description**: Two-way sync with Google Calendar and calendar widget on dashboard.

#### 6.1 Calendar Integration

- **Features**:
  - Auto-create calendar events from email responses (interview invitations)
  - Reminders before interviews
  - Link interviews to job applications
  - Two-way sync (calendar → application status)
  - Manual calendar event creation from application detail page
- **Implementation**:
  - Google Calendar API integration
  - Event parsing from email responses (dates extracted via NLP)
  - `JobApplication.interview_datetime` field (already exists or needs addition)
  - Calendar event creation service
  - Calendar event update/delete when application status changes

#### 6.2 Calendar Widget on Dashboard

- **Description**: Display upcoming interviews and events on dashboard
- **Implementation**:
  - Dashboard widget showing:
    - Upcoming interviews (next 7-30 days)
    - Today's interviews (highlighted)
    - Calendar view (month/week/day toggle)
    - Click to navigate to application detail
  - Data source:
    - `JobApplication.interview_datetime` field
    - Or sync from Google Calendar API
  - UI Components:
    - Calendar widget component (use a calendar library like `react-big-calendar` or `@fullcalendar/react`)
    - Event cards with application info (company, position, time)
    - "Add to Calendar" button for manual events
    - Integration status indicator (connected/disconnected)
- **API Endpoints**:
  - `GET /api/v1/calendar/upcoming` - Get upcoming interviews
  - `GET /api/v1/calendar/events` - Get calendar events (if syncing from Google)
  - `POST /api/v1/applications/{id}/calendar-event` - Create calendar event

### 7. Rolling Logs by Date

- **Status**: Not Started
- **Description**: Implement log rotation by date to manage log file sizes and improve log management.
- **Implementation**:
  - Use Python's `logging.handlers.TimedRotatingFileHandler`
  - Rotate logs daily at midnight
  - Log file naming: `cv_mailer_YYYY-MM-DD.log`
  - Keep logs for configurable retention period (e.g., 30 days, 90 days)
  - Compress old log files (optional, gzip)
  - Archive old logs to `logs/archive/` directory
- **Configuration**:
  - Add `LOG_RETENTION_DAYS` environment variable (default: 30)
  - Add `LOG_COMPRESS` boolean (default: true)
- **Code Changes**:
  - Update `src/cv_mailer/utils/logging_utils.py` or logging configuration
  - Initialize `TimedRotatingFileHandler` with `when='midnight'`, `interval=1`, `backupCount=LOG_RETENTION_DAYS`
- **Benefits**:
  - Easier log file management
  - Prevents log files from growing too large
  - Better organization for troubleshooting
  - Easier log archival and cleanup

## 🎯 Medium Priority Features

### 8. Authentication & Authorization (Reprioritized)

- **Status**: Reprioritized to Medium (was High Priority)
- **Description**: Secure API access for production deployment
- **Priority**: Medium - Defer until conversation features are complete
- **Implementation**:
  - OAuth2 with JWT tokens
  - User registration/login
  - Role-based access control (RBAC)
  - API key management
- **Tech Stack**:
  - `python-jose` for JWT
  - `passlib` for password hashing
  - FastAPI Security utilities
- **Priority**: High only if deploying publicly before conversation features are complete

### 9. Advanced Analytics & Reporting

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

### 10. Multi-Resume Support

- **Status**: Partially Covered by Settings Page (Resume File Management)
- **Description**: Use different resumes for different job types
- **Note**: Basic resume file management is now in Settings (High Priority #4.2). This feature extends it with:
  - Smart resume selection based on job category/keywords
  - A/B testing different resumes
  - Resume versioning per application
- **Implementation**:
  - `JobApplication.resume_version` field
  - Auto-select resume based on job description keywords
  - Resume selection based on:
    - Job category (manual tagging)
    - Keywords in job description
    - Company type (startup vs. enterprise)
  - A/B testing different resumes (track response rates per resume)

### 11. Email Template Management (Advanced)

- **Status**: Basic Template Management in Settings (High Priority #4.1)
- **Description**: Advanced template features beyond basic editing
- **Note**: Basic template editing is now in Settings. This feature adds:
  - Template library (per job type, per company)
  - Template versioning
  - A/B testing templates
  - Template performance analytics
- **Current**: Templates in `src/cv_mailer/services/template_service.py`
- **Future Enhancements**:
  - Multiple template variants per type
  - Template performance tracking (open rates, response rates)
  - Template cloning and branching
  - Template import/export
- **Database Changes**:
  - `EmailTemplate.version` field
  - `template_id` foreign key in `EmailRecord`
  - Template analytics table

### 12. Email Scheduling

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

### 13. Bulk Operations & CSV Import/Export

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

### 14. Notification System

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

### 15. LinkedIn Integration

- **Status**: Not Started
- **Description**: Auto-extract recruiter info from LinkedIn
- **Features**:
  - Find recruiter emails from LinkedIn profiles
  - Company information lookup
  - Profile matching (find best contact)
  - Auto-populate application data
- **Challenges**: LinkedIn doesn't have public API for this
- **Alternative**: Browser extension or manual paste

### 16. Job Board Integration

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

### 17. AI-Powered Email Generation

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

### 18. Multi-Account Support

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

### 19. Email Tracking & Analytics

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

### 20. Interview Preparation Assistant

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

### 21. Database Migrations (Alembic)

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

### 22. Comprehensive Testing Suite

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

### 23. Docker Support

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

### 24. CI/CD Pipeline

- **Status**: Not Started
- **Description**: Automated testing and deployment
- **Platform**: GitHub Actions / GitLab CI
- **Pipeline**:
  - Lint (black, isort, flake8, mypy)
  - Test (pytest)
  - Build (Docker image)
  - Deploy (optional)
- **File**: `.github/workflows/ci.yml`

### 25. Database Performance Optimization

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

### 26. Caching Layer

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

### 27. Rate Limiting for API

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

### 28. Monitoring & Logging (Advanced)

- **Status**: Basic Logging ✅ | Rolling Logs by Date (High Priority #7) | Advanced Pending
- **Current**: Log to `logs/cv_mailer.log` (basic logging implemented)
- **Future** (beyond rolling logs):
  - Structured logging (JSON format)
  - Log aggregation (ELK stack, Datadog)
  - Error tracking (Sentry)
  - Performance monitoring (APM)
  - Metrics (Prometheus + Grafana)

## 🔒 Security Enhancements

### 29. Secrets Management

- **Status**: `.env` File | Vault Pending
- **Current**: Secrets in `.env` (good for local)
- **Future**:
  - AWS Secrets Manager
  - HashiCorp Vault
  - Azure Key Vault
  - Google Secret Manager
- **Priority**: High for production deployment

### 30. Database Encryption

- **Status**: Not Started
- **Description**: Encrypt sensitive data at rest
- **Fields to Encrypt**:
  - Recruiter emails
  - Personal notes
  - Resume content (if stored)
- **Implementation**: SQLAlchemy hybrid properties with encryption

### 31. API Authentication

- **Status**: Not Started | Required for Multi-User
- **Note**: Related to Authentication & Authorization (Medium Priority #8)
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

### 32. Audit Logging

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

### 33. Interactive CLI Improvements

- **Status**: Rich Console ✅ | Interactive Pending
- **Current**: Rich progress bars, tables, colors
- **Future**:
  - Interactive prompts (`questionary`)
  - Command completion (shell completion)
  - Fuzzy search for applications
  - TUI (Terminal UI) with `textual`
- **Example**: `cv-mailer tui` for full-screen terminal UI

### 34. Email Preview Mode

- **Status**: Partially Covered by Email Editing (High Priority #3)
- **Description**: Preview emails before sending
- **Note**: Basic preview is now part of Email Editing feature. This adds CLI preview mode.
- **Features**:
  - HTML preview in browser
  - Test variable substitution
  - Preview with different data
  - Send test email to self
- **Implementation**: `cv-mailer preview --application-id 1`

### 35. Configuration Validation & Testing

- **Status**: Basic Validation ✅ | Testing Pending
- **Current**: `Config.validate()` checks required fields
- **Future**:
  - Test Gmail connection
  - Test Sheets connection
  - Verify resume file exists
  - Check API quotas
  - Validate email templates
- **Command**: `cv-mailer test-config`

### 36. Onboarding Wizard

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

### Phase 3: Conversation Management (Q1 2026) - CURRENT FOCUS

- [ ] Email threading (reply-to-previous)
- [ ] Conversation tracking & UI
- [ ] Selective follow-up triggering
- [ ] Email response parsing & analysis
- [ ] Action items generation
- [ ] Email editing before sending
- [ ] Resume file selection per email
- [ ] Settings page (templates, resumes, config)
- [ ] Job description storage
- [ ] Rolling logs by date

### Phase 4: Calendar & Intelligence (Q2 2026)

- [ ] Google Calendar integration
- [ ] Calendar widget on dashboard
- [ ] Advanced analytics
- [ ] AI-powered email generation

### Phase 5: Scalability (Q3 2026)

- [ ] Database migrations (Alembic)
- [ ] Caching layer (Redis)
- [ ] Email scheduling (Celery)
- [ ] Docker deployment

### Phase 6: Enterprise (Q4 2026)

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

**Last Updated**: January 2026
