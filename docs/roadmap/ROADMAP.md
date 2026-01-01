# CV Mailer Roadmap

**Roadmap of planned features and enhancements for CV Mailer.**

> 📖 **Current Features**: See [Changelog](../CHANGELOG.md) for complete feature history and implementation details.

**Last Updated**: January 2026  
**Status**: Post-refactoring with REST API, focusing on conversation management features

> 📖 **Related Docs**: [Architecture](../design/ARCHITECTURE.md) | [API Guide](../API_GUIDE.md) | [Setup Guide](../SETUP_GUIDE.md) | [Contributing](CONTRIBUTING.md)

---

## Overview

CV Mailer is a production-ready application for managing job applications with email automation, comprehensive tracking, and a modern web dashboard. This roadmap outlines planned enhancements organized by priority.

**Current Focus**: Phase 3 - Conversation Management (Q1 2026)

---

## ✅ Implemented Features Summary

### Core Capabilities

- ✅ Google Sheets Integration (multi-sheet support, flexible column matching)
- ✅ Gmail Integration (rate limiting, email tracking, error handling)
- ✅ Application Management (11 statuses, timeline, search/filter/sort, pagination)
- ✅ Email Management (first contact, follow-ups, templates, history tracking)
- ✅ Recruiter Management (multi-recruiter support, individual tracking)
- ✅ Statistics & Analytics (comprehensive metrics and charts)
- ✅ REST API (FastAPI with OpenAPI docs, CORS, dependency injection)
- ✅ Web Dashboard (React + TypeScript, responsive, dark mode)
- ✅ CLI Interface (rich terminal UI with progress bars)
- ✅ Production Readiness (comprehensive logging, custom exceptions, repository pattern)

**See [Changelog](../CHANGELOG.md) for complete feature history and detailed implementation notes.**

---

## Current Focus: Phase 3 - Conversation Management (Q1 2026)

We're currently focused on building comprehensive conversation management capabilities:

- **Email Threading** - Follow-ups as replies to maintain conversation context
- **Conversation Tracking** - Complete email thread views per recruiter
- **Response Parsing** - Automatic email response analysis and action items
- **Email Editing** - Customize emails before sending
- **Settings Page** - Manage templates, resumes, and configuration via UI
- **Job Description Storage** - Store job descriptions for AI-powered personalization
- **Calendar Integration** - Google Calendar sync with dashboard widget
- **Rolling Logs** - Daily log rotation for better log management

[See detailed feature specs →](features/high-priority/)

---

## 🔥 High Priority Features

Core features for conversation management and email workflow improvements.

| # | Feature | Status | Description |
|---|---------|--------|-------------|
| 1 | [Email Conversation Threading & Management](features/high-priority/01-email-conversation-threading.md) | Not Started | Reply-to-previous threading, conversation tracking, selective follow-ups |
| 2 | [Email Response Parsing & Analysis](features/high-priority/02-email-response-parsing.md) | Not Started | Auto-detect responses, NLP analysis, action items generation |
| 3 | [Email Editing & Customization](features/high-priority/03-email-editing-customization.md) | Not Started | Edit subject/content, resume selection before sending |
| 4 | [Settings Page & Configuration](features/high-priority/04-settings-page.md) | Not Started | Manage templates, resumes, and app config via UI |
| 5 | [Job Description Storage](features/high-priority/05-job-description-storage.md) | Not Started | Store job descriptions for AI-powered email generation |
| 6 | [Calendar Integration & Widget](features/high-priority/06-calendar-integration.md) | Not Started | Google Calendar sync with dashboard calendar widget |
| 7 | [Rolling Logs by Date](features/high-priority/07-rolling-logs.md) | Not Started | Daily log rotation with configurable retention |

---

## 🎯 Medium Priority Features

Important enhancements for production deployment and advanced functionality.

| # | Feature | Status | Description |
|---|---------|--------|-------------|
| 8 | [Authentication & Authorization](features/medium-priority/08-authentication.md) | Not Started | OAuth2/JWT for secure API access |
| 9 | [Advanced Analytics & Reporting](features/medium-priority/09-advanced-analytics.md) | Not Started | Response rates, time-to-response, funnel analysis |
| 10 | [Multi-Resume Support](features/medium-priority/10-multi-resume-support.md) | Not Started | Smart resume selection based on job type |
| 11 | [Email Template Management (Advanced)](features/medium-priority/11-email-template-management-advanced.md) | Not Started | Template library, versioning, A/B testing |
| 12 | [Email Scheduling](features/medium-priority/12-email-scheduling.md) | Not Started | Business hours scheduling, timezone support |
| 13 | [Bulk Operations & CSV](features/medium-priority/13-bulk-operations.md) | Not Started | CSV import/export, bulk updates |
| 14 | [Notification System](features/medium-priority/14-notification-system.md) | Not Started | Email, Slack, Discord notifications |

---

## 💡 Nice-to-Have Features

Enhancements that would add value but aren't critical.

- [15. LinkedIn Integration](features/nice-to-have/15-linkedin-integration.md) - Auto-extract recruiter info
- [16. Job Board Integration](features/nice-to-have/16-job-board-integration.md) - Auto-import from job boards
- [17. AI-Powered Email Generation](features/nice-to-have/17-ai-powered-email-generation.md) - Generate personalized emails
- [18. Multi-Account Support](features/nice-to-have/18-multi-account-support.md) - Manage multiple Gmail accounts
- [19. Email Tracking & Analytics](features/nice-to-have/19-email-tracking-analytics.md) - Track opens and clicks
- [20. Interview Preparation Assistant](features/nice-to-have/20-interview-preparation-assistant.md) - Interview prep tools

---

## 🛠️ Technical Improvements

Infrastructure and developer experience enhancements.

- [21. Database Migrations (Alembic)](features/technical-improvements/21-database-migrations.md)
- [22. Comprehensive Testing Suite](features/technical-improvements/22-testing-suite.md)
- [23. Docker Support](features/technical-improvements/23-docker-support.md)
- [24. CI/CD Pipeline](features/technical-improvements/24-cicd-pipeline.md)
- [25. Database Performance](features/technical-improvements/25-database-performance.md)
- [26. Caching Layer](features/technical-improvements/26-caching-layer.md)
- [27. Rate Limiting for API](features/technical-improvements/27-rate-limiting.md)
- [28. Advanced Monitoring & Logging](features/technical-improvements/28-monitoring-logging-advanced.md)

---

## 🔒 Security Enhancements

Security improvements for production deployments.

- [29. Secrets Management](features/security/29-secrets-management.md)
- [30. Database Encryption](features/security/30-database-encryption.md)
- [31. API Authentication](features/security/31-api-authentication.md)
- [32. Audit Logging](features/security/32-audit-logging.md)

---

## 🎨 User Experience Enhancements

UX improvements for better user interaction.

- [33. Interactive CLI Improvements](features/ux-enhancements/33-interactive-cli-improvements.md)
- [34. Email Preview Mode](features/ux-enhancements/34-email-preview-mode.md)
- [35. Configuration Validation & Testing](features/ux-enhancements/35-configuration-validation.md)
- [36. Onboarding Wizard](features/ux-enhancements/36-onboarding-wizard.md)

---

## 📊 Implementation Roadmap

### Phase 1: Foundation ✅ (December 2025)

- ✅ REST API with FastAPI
- ✅ Modern package structure
- ✅ Multi-sheet support
- ✅ Multi-recruiter support
- ✅ Comprehensive documentation
- ✅ Web Dashboard (React + TypeScript)

### Phase 2: Web UI ✅ (December 2025)

- ✅ Frontend application (React + TypeScript + Vite)
- ✅ Dashboard with charts and statistics
- ✅ Application management interface
- ✅ Application detail page (timeline, email history, progress tracker)
- ✅ Recruiter management pages
- ✅ Google Sheets sync from UI
- ✅ Status updates from UI
- ✅ Trigger reach-out and follow-up from UI
- ✅ Dark mode support
- ✅ Responsive design

### Phase 3: Conversation Management (Q1 2026) - **CURRENT FOCUS**

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

---

## Quick Links

- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute and feature request template
- **[Changelog](../CHANGELOG.md)** - Complete feature history and changes
- **[Architecture Guide](../design/ARCHITECTURE.md)** - System architecture and design
- **[API Guide](../API_GUIDE.md)** - REST API documentation

---

**Note**: This is a living document. Features are added and prioritized based on user feedback and practical utility.

**Last Updated**: January 2026
