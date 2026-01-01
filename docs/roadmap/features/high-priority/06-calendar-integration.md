# Google Calendar Integration & Dashboard Widget

**Priority**: High  
**Status**: Not Started  
**Phase**: Phase 3 - Conversation Management (Q1 2026)  
**Estimated Timeline**: Q1 2026

---

## Description

Two-way sync with Google Calendar and calendar widget on dashboard. Automatically create calendar events from email responses (interview invitations), display upcoming interviews on the dashboard, and enable manual calendar event creation.

**Key Goals**:

- Auto-create calendar events from email responses
- Display upcoming interviews on dashboard
- Manual calendar event creation
- Two-way sync between calendar and application status
- Interview reminders and notifications

---

## Use Cases

1. **Automatic Event Creation**: Interview invitations in emails automatically create calendar events
2. **Dashboard Visibility**: See upcoming interviews at a glance on dashboard
3. **Manual Event Creation**: Create calendar events manually for interviews
4. **Calendar Management**: Manage interview schedule alongside application tracking
5. **Reminders**: Get reminders before interviews

---

## Implementation Details

### Calendar Integration

#### Features

1. **Auto-create Calendar Events**
   - Extract interview dates/times from email responses
   - Create Google Calendar events automatically
   - Link events to job applications
   - Include application context (company, position, recruiter)

2. **Reminders**
   - Set reminders before interviews (e.g., 1 day, 1 hour before)
   - Configurable reminder times
   - Email or notification reminders

3. **Link to Applications**
   - Link calendar events to job applications
   - Navigate from calendar event to application detail
   - Display application status in calendar event description

4. **Two-way Sync**
   - Calendar → Application status: Update application when event is created/updated
   - Application → Calendar: Update/delete event when application status changes
   - Handle conflicts gracefully

5. **Manual Event Creation**
   - Create calendar events from application detail page
   - Pre-fill event details from application data
   - Allow user to customize event details

#### Implementation

**Google Calendar API Integration**:

- OAuth2 authentication for Google Calendar API
- Scope: `https://www.googleapis.com/auth/calendar`
- Create, read, update, delete calendar events
- Handle API rate limits

**Event Parsing from Email Responses**:

- Extract dates/times from email responses (via NLP, see Email Response Parsing feature)
- Parse date formats (various formats)
- Handle timezone information
- Extract meeting links (Zoom, Teams, Google Meet, etc.)

**Database Field**:

- `JobApplication.interview_datetime` field (check if already exists, add if needed)
  - Type: DateTime
  - Nullable: True
  - Timezone-aware (store as UTC)
  - Index for querying upcoming interviews

**Calendar Event Creation Service**:

- Service class: `CalendarService` or `GoogleCalendarService`
- Methods:
  - `create_event(application_id, datetime, title, description, location)`
  - `update_event(event_id, **updates)`
  - `delete_event(event_id)`
  - `get_events(application_id)`
  - `sync_from_email_response(email_response_id)`

**Event Update/Delete Logic**:

- When application status changes to `REJECTED` or `CLOSED`, optionally delete calendar event
- When interview_datetime changes, update calendar event
- Handle event deletion gracefully (event may have been deleted in calendar)

### Calendar Widget on Dashboard

#### Description

Display upcoming interviews and events on dashboard. Provides at-a-glance view of interview schedule.

#### Implementation

**Dashboard Widget Display**:

- Upcoming interviews (next 7-30 days, configurable)
- Today's interviews (highlighted/special styling)
- Calendar view options: month/week/day toggle
- Click to navigate to application detail page

**Data Source**:

- Primary: `JobApplication.interview_datetime` field
- Optional: Sync from Google Calendar API (more complex, future enhancement)

**UI Components**:

1. **Calendar Widget Component**
   - Use calendar library: `react-big-calendar`, `@fullcalendar/react`, or custom component
   - Month view (default)
   - Week view (optional)
   - Day view (optional)
   - Event cards with application info

2. **Event Cards**
   - Display application info: company, position, time
   - Show interview type (phone, video, in-person) if available
   - Show meeting link if available
   - Click to navigate to application detail

3. **"Add to Calendar" Button**
   - Manual event creation
   - Opens modal/drawer with event creation form
   - Pre-fills with application data
   - Creates calendar event via API

4. **Integration Status Indicator**
   - Show connection status (connected/disconnected)
   - "Connect Calendar" button if not connected
   - Error messages if connection fails

**Calendar Widget Layout**:

- Full-width widget on dashboard
- Or sidebar widget (compact view)
- Responsive design (stack on mobile)
- Configurable date range (default: next 30 days)

#### API Endpoints

- `GET /api/v1/calendar/upcoming` - Get upcoming interviews
  - Query params: `days` (default: 30), `start_date`, `end_date`
  - Returns: List of applications with interview_datetime in range
  - Include: application_id, company, position, interview_datetime, recruiter info

- `GET /api/v1/calendar/events` - Get calendar events (if syncing from Google)
  - Optional endpoint for full calendar sync
  - Returns: Calendar events linked to applications

- `POST /api/v1/applications/{id}/calendar-event` - Create calendar event
  - Request body: `datetime`, `title` (optional), `description` (optional), `location` (optional), `reminders` (optional)
  - Creates Google Calendar event
  - Updates application.interview_datetime
  - Returns: calendar_event_id

- `PUT /api/v1/applications/{id}/calendar-event` - Update calendar event (optional)
- `DELETE /api/v1/applications/{id}/calendar-event` - Delete calendar event (optional)

---

## Technical Considerations

### Google Calendar API

**Authentication**:

- OAuth2 flow for Google Calendar API
- Store refresh token securely
- Handle token refresh automatically
- Support multiple Google accounts (future)

**API Limits**:

- Rate limits: 1,000,000 queries per day per project
- Quota limits: 600 requests per minute per user
- Implement rate limiting and retry logic

**Event Structure**:

- Event title: "{Company} - {Position} Interview"
- Event description: Application details, recruiter info, meeting links
- Event location: Meeting link or physical location
- Event attendees: Recruiter email (optional)
- Event reminders: Configurable (1 day, 1 hour before)

### Date/Time Handling

**Timezone**:

- Store interview_datetime as UTC in database
- Display in user's local timezone in UI
- Handle timezone conversion correctly
- Support timezone selection per event

**Date Parsing**:

- Parse dates from email responses (various formats)
- Handle relative dates ("next Monday", "in 2 days")
- Validate date/time values
- Handle invalid/ambiguous dates gracefully

### Calendar Sync

**Sync Strategy**:

- One-way sync: Application → Calendar (simpler, recommended initially)
- Two-way sync: Application ↔ Calendar (more complex, future)
- Handle sync conflicts (event modified in both places)
- Last-write-wins or user resolution for conflicts

**Event Linking**:

- Store calendar_event_id in database (new field in JobApplication or separate table)
- Link events to applications
- Handle event deletion in calendar (clean up links)
- Handle application deletion (optionally delete events)

### Performance

**Dashboard Widget**:

- Cache upcoming interviews (refresh every 5-10 minutes)
- Limit number of events displayed (pagination or date range)
- Lazy load calendar widget (load on dashboard view)
- Optimize queries (index on interview_datetime)

**Calendar API Calls**:

- Batch API calls when possible
- Cache calendar events
- Async processing for event creation/updates
- Don't block API responses waiting for calendar API

---

## Dependencies

- Google Calendar API access
- OAuth2 authentication setup
- Email Response Parsing feature (for extracting dates from emails)
- Database field: `JobApplication.interview_datetime`
- Calendar widget component library
- Calendar service implementation

---

## Related Features

- [Email Response Parsing](../high-priority/02-email-response-parsing.md) - Extracts interview dates from email responses
- [Application Management](../high-priority/01-email-conversation-threading.md) - Links calendar events to applications
- [Notification System](../medium-priority/14-notification-system.md) - Interview reminders and notifications

---

## Benefits

- ✅ Automatic interview scheduling
- ✅ Dashboard visibility of upcoming interviews
- ✅ Better interview preparation and management
- ✅ Integration with existing calendar workflow
- ✅ Reminders prevent missed interviews
- ✅ Centralized interview management

---

## Success Criteria

- [ ] Calendar events are automatically created from email responses
- [ ] Calendar widget displays upcoming interviews correctly
- [ ] Manual event creation works from application detail page
- [ ] Calendar events are linked to applications
- [ ] Two-way sync works correctly (if implemented)
- [ ] Timezone handling is correct
- [ ] Performance is acceptable (calendar widget loads quickly)
- [ ] Error handling works (API failures, invalid dates, etc.)

---

**Last Updated**: January 2026
