# Logging Strategy for CV Mailer

## Overview

This document defines the logging strategy for production observability. Logs are structured to enable monitoring dashboards, alerting, and debugging.

## Log Level Guidelines

### INFO Level - Critical for Observability

**Purpose:** Track application health, business metrics, and key operations for production monitoring.

**What to log:**

1. **External Service Authentication**
   - ✅ Authentication success/failure for Google Sheets API
   - ✅ Authentication success/failure for Gmail API
   - **Why:** Critical health indicators - if auth fails, nothing works

2. **Sync Operations**
   - ✅ Sync start: Total rows found, sheets processed, dry_run status
   - ✅ Sync completion: Summary (sent_count, skipped_count, total_rows, error_count)
   - ✅ Follow-up start: Count of applications needing follow-up
   - ✅ Follow-up completion: Summary (sent_count, skipped_count, total_needing, error_count)
   - **Why:** Core business metrics - need to track sync volume and success rates

3. **Email Operations**
   - ✅ Email sent successfully: recipient, application_id, email_type, message_id
   - ✅ Email sending started: For tracking email operations
   - ✅ Daily rate limit status: When approaching or at limit
   - **Why:** Track email delivery, identify issues, monitor rate limits

4. **API Endpoints**
   - ✅ Endpoint calls: Which endpoint, key parameters (dry_run, application_id, etc.)
   - ✅ Status updates: Application status changes
   - ✅ Email triggers: Reach out, follow up actions
   - **Why:** Track API usage patterns and user actions

5. **Application Lifecycle**
   - ✅ Database initialization
   - ✅ Application startup/shutdown
   - ✅ WAL checkpointing
   - **Why:** Track application health and lifecycle events

### WARNING Level - Non-Critical Issues

**Purpose:** Alert on issues that don't stop operation but should be monitored.

**What to log:**

1. **Skipped Operations**
   - ⚠️ Records skipped: Missing fields, already processed (with context)
   - ⚠️ Applications skipped: No recruiters, validation errors
   - **Why:** Track data quality issues and processing efficiency

2. **Partial Failures**
   - ⚠️ Spreadsheet update failures (non-critical)
   - ⚠️ Some emails sent, some failed
   - ⚠️ Retry attempts
   - **Why:** Track partial failures that don't stop overall operation

3. **Rate Limiting**
   - ⚠️ Approaching rate limit (not at limit yet)
   - **Why:** Early warning before hitting limits

4. **Configuration Issues**
   - ⚠️ Missing optional configs
   - ⚠️ Invalid filter patterns
   - **Why:** Track configuration problems

### ERROR Level - Critical Failures

**Purpose:** Alert on failures that stop operations or cause data loss.

**What to log:**

1. **Authentication Failures**
   - ❌ External service auth failures
   - ❌ Token refresh failures
   - **Why:** Critical - application cannot function

2. **API Errors**
   - ❌ External API call failures
   - ❌ Network timeouts
   - ❌ Rate limit exceeded
   - **Why:** Critical - operations cannot complete

3. **Processing Errors**
   - ❌ Individual record processing failures
   - ❌ Database errors
   - ❌ Validation errors
   - **Why:** Track failures that prevent data processing

### DEBUG Level - Detailed Diagnostics

**Purpose:** Detailed information for debugging, only enabled with VERBOSE_LOGGING=true.

**What to log:**

1. **Function Calls** (only if VERBOSE_LOGGING=true)
   - 🔍 Function entry/exit
   - 🔍 Execution times
   - **Why:** Performance profiling and detailed debugging

2. **Detailed Processing**
   - 🔍 Row-by-row processing details
   - 🔍 Individual field parsing
   - 🔍 Internal state changes
   - **Why:** Deep debugging of processing logic

3. **Low-level Details**
   - 🔍 HTTP request/response details
   - 🔍 Detailed parsing logs
   - 🔍 Sheet-by-sheet processing
   - **Why:** Debug external service interactions

## Key Metrics to Track

### Sync Metrics

- Total rows processed per sync
- Sheets processed per sync
- Emails sent per sync
- Records skipped per sync
- Errors per sync
- Sync duration

### Email Metrics

- Emails sent per day/hour
- Email success rate
- Rate limit usage
- Email types (first contact vs follow-up)

### Application Health

- Authentication success rate
- API error rate
- Database operation success rate
- Application uptime

## Implementation Notes

1. **Structured Logging:** Use consistent log message formats for easy parsing
2. **Context:** Include relevant IDs (application_id, message_id, etc.) in logs
3. **Performance:** Don't log in tight loops - aggregate and log summaries
4. **Sensitive Data:** Never log passwords, tokens, or full email content
5. **VERBOSE_LOGGING:** Use config switch to enable detailed DEBUG logs only when needed
