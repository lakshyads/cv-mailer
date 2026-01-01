# Email Scheduling

**Priority**: Medium  
**Status**: Not Started  
**Phase**: Phase 5 - Scalability (Q3 2026)  
**Estimated Timeline**: Q3 2026

---

## Description

Schedule emails to be sent at specific times. Includes business hours scheduling, timezone support, queue management, and batch scheduling. Enables better email delivery timing and rate limit management.

**Key Goals**:
- Schedule emails for optimal delivery times
- Business hours-only sending
- Timezone-aware scheduling
- Queue management (pause/resume)
- Batch scheduling over multiple days

---

## Use Cases

1. **Business Hours**: Send emails only during business hours (9am-5pm)
2. **Timezone Support**: Schedule emails based on recruiter's timezone
3. **Rate Limit Management**: Spread emails over time to avoid rate limits
4. **Batch Scheduling**: Schedule multiple emails over days/weeks
5. **Queue Management**: Pause/resume email queue as needed

---

## Implementation Details

### Scheduling Features

#### Business Hours Scheduling

- Send emails only during business hours (configurable, default 9am-5pm)
- Skip weekends (optional)
- Skip holidays (optional)
- Queue emails outside business hours for next business day

#### Timezone Support

- Detect recruiter's timezone (if available)
- Schedule emails based on recipient's local time
- Handle timezone conversion correctly
- Support multiple timezones

#### Queue Management

- Pause email queue (stop sending scheduled emails)
- Resume email queue
- Clear email queue
- Queue status monitoring

#### Batch Scheduling

- Schedule multiple emails over days/weeks
- Spread emails evenly over time period
- Avoid rate limits through scheduling
- Respect daily email limits

### Implementation

#### Task Queue System

**Options**:
- **Celery**: Full-featured task queue with Redis/RabbitMQ backend
- **APScheduler**: Lightweight Python scheduler
- **Custom Queue**: Simple in-memory or database-backed queue

**Recommendation**: Start with APScheduler for simplicity, migrate to Celery if needed

#### Database Changes

- Add `EmailRecord.scheduled_at` field (DateTime, nullable)
- Add `EmailRecord.queue_status` field (Enum: pending, scheduled, sent, failed, cancelled)
- Add `EmailRecord.sent_at` field (DateTime, nullable) - Actual send time

#### Scheduling Logic

1. Check if email should be sent now (business hours, timezone)
2. If yes, send immediately
3. If no, schedule for next appropriate time
4. Update queue status
5. Process scheduled emails periodically

### Configuration

#### Business Hours

```env
EMAIL_BUSINESS_HOURS_START=09:00
EMAIL_BUSINESS_HOURS_END=17:00
EMAIL_SKIP_WEEKENDS=true
EMAIL_TIMEZONE=America/New_York
```

#### Scheduling Options

- Per-email scheduling
- Default scheduling behavior
- Timezone detection rules
- Queue processing interval

### API Endpoints

- `POST /api/v1/applications/{id}/send-outreach/schedule` - Schedule outreach email
- `POST /api/v1/applications/{id}/send-follow-up/schedule` - Schedule follow-up email
- `GET /api/v1/emails/scheduled` - List scheduled emails
- `PUT /api/v1/emails/{id}/schedule` - Update scheduled time
- `DELETE /api/v1/emails/{id}/schedule` - Cancel scheduled email
- `POST /api/v1/emails/queue/pause` - Pause email queue
- `POST /api/v1/emails/queue/resume` - Resume email queue

---

## Technical Considerations

### Task Queue Backend

**Celery with Redis**:
- Production-ready
- Scalable
- Requires Redis/RabbitMQ
- More complex setup

**APScheduler**:
- Lightweight
- No external dependencies
- Simpler setup
- Less scalable for high volume

### Timezone Handling

- Use `pytz` or `zoneinfo` for timezone handling
- Store times in UTC, convert for display
- Handle DST transitions correctly
- Support recruiter timezone detection (if available)

### Queue Processing

- Periodic task to process scheduled emails
- Handle failures and retries
- Monitor queue status
- Alert on queue issues

### Rate Limiting Integration

- Respect existing rate limits
- Spread emails to avoid rate limits
- Queue emails when rate limit reached
- Resume when rate limit resets

---

## Dependencies

- Task queue system (Celery or APScheduler)
- Redis (if using Celery)
- Timezone library (pytz or zoneinfo)
- Database schema updates
- Queue monitoring tools

---

## Related Features

- Email sending (already implemented) - Core email functionality
- Rate limiting (already implemented) - Integration with scheduling
- [Calendar Integration](../high-priority/06-calendar-integration.md) - Timezone-aware scheduling

---

## Benefits

- ✅ Optimal email delivery timing
- ✅ Business hours compliance
- ✅ Better rate limit management
- ✅ Timezone-aware scheduling
- ✅ Queue management flexibility

---

## Success Criteria

- [ ] Emails can be scheduled for future delivery
- [ ] Business hours scheduling works correctly
- [ ] Timezone handling is accurate
- [ ] Queue management functions properly
- [ ] Batch scheduling works
- [ ] Integration with rate limiting works
- [ ] Performance is acceptable

---

**Last Updated**: January 2026

