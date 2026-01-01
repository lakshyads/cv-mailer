# Email Conversation Threading & Management

**Priority**: High  
**Status**: ✅ **COMPLETED** (2026-01-01)  
**Phase**: Phase 3 - Conversation Management (Q1 2026)  
**Implementation**: See [Email Threading Design](../../../design/email-threading-design.md) for complete implementation details

---

## Description

Maintain proper email conversation threads for each recruiter. Follow-ups should be replies to previous emails, creating a cohesive conversation trail. This feature enables complete conversation tracking and a better user experience for managing email communications with recruiters.

**Key Goals**:

- Follow-up emails are replies to the original or previous email in the thread
- Complete conversation history viewable per recruiter per application
- Selective follow-up triggering for specific recruiters
- Professional email communication trail

---

## Use Cases

1. **Maintain Email Context**: Recruiters see full conversation history in their email client
2. **Better Organization**: All emails related to an application are properly threaded
3. **Selective Communication**: Send follow-ups to specific recruiters, not all at once
4. **Conversation Tracking**: View complete email threads in the UI
5. **Professional Communication**: Maintain proper email etiquette with threaded conversations

---

## Implementation Details

### Email Threading (Reply-to-Previous)

#### Current State

- Follow-up emails are sent as standalone emails
- No thread linking between emails
- No conversation context maintained

#### Target State

- Follow-up emails are replies to the original or previous email in the thread
- Proper Gmail thread linking maintained
- Full conversation context preserved

#### Implementation Steps

1. **Database Changes**
   - Add `EmailRecord.thread_id` (String) - Gmail thread ID
   - Add `EmailRecord.in_reply_to` (String) - Message ID of parent email
   - Add `EmailRecord.references` (Text) - References header chain
   - Add index on `thread_id` for efficient conversation queries

2. **Backend Changes**
   - Modify `GmailSender.send_email()` to accept `thread_id` and `references` parameters
   - Update `EmailService.send_follow_up()` to fetch previous email's thread info
   - Store thread information when sending emails
   - Gmail API: Use `threadId` parameter when sending replies

3. **Migration Strategy**
   - For existing emails without thread_id, can be left null (new emails will have threads)
   - Optional: Backfill thread_ids for existing emails if Gmail API allows

### Conversation Tracking & UI

#### API Endpoints

- `GET /api/v1/applications/{id}/conversations` - Get all conversations grouped by recruiter
- `GET /api/v1/applications/{id}/conversations/{recruiter_id}` - Get conversation thread for specific recruiter
- `GET /api/v1/emails/{id}/thread` - Get all emails in a thread

#### Database Queries

- Group emails by `thread_id` or `recipient_email` + `job_application_id`
- Sort emails chronologically (oldest to newest) to show conversation flow
- Query conversation metadata (total messages, last activity, participants)

#### UI Components

1. **Conversation View Component**
   - Display threaded emails in conversation format
   - Reverse chronological display (newest first, with expandable thread view)
   - Visual thread indicator (lines connecting emails in conversation)

2. **Application Detail Page Integration**
   - Per-recruiter conversation tabs
   - Email thread viewer modal with full conversation history
   - Conversation summary cards (message count, last activity)

3. **Data Model Considerations**
   - Optional: Add `ConversationThread` model for metadata
   - Or query emails by `thread_id` directly (simpler approach)
   - Store conversation metadata (total messages, last activity, participants)

### Selective Follow-up Triggering

#### Current State

- `EmailService.send_follow_up()` already supports `recruiter_id` parameter
- UI doesn't expose this capability
- Follow-ups are triggered for all recruiters at once

#### Target State

- UI allows selecting specific recruiters for follow-up
- Per-recruiter follow-up buttons
- Bulk selection option available

#### Implementation Steps

1. **API Updates**
   - Update `POST /api/v1/applications/{id}/send-follow-up` to accept optional `recruiter_ids[]` array
   - Support both single recruiter and multiple recruiters
   - Default: Select all recruiters (maintain current behavior)

2. **Frontend Updates**
   - Add recruiter selection UI before triggering follow-up
   - Show recruiter list with checkboxes/multi-select
   - Display conversation status for each recruiter (e.g., "3 messages in thread")
   - Per-recruiter follow-up button in conversation view

3. **UI Enhancements**
   - Recruiter cards with "Send Follow-up" button (individual action)
   - Bulk selection for multiple recruiters
   - Visual indicator showing last email sent date per recruiter
   - Conversation status badges (e.g., "Active conversation", "No replies yet")

---

## Technical Considerations

### Gmail API Threading

- Gmail automatically groups emails into threads based on subject line and participants
- Using `threadId` parameter ensures emails are added to existing threads
- `In-Reply-To` and `References` headers provide additional threading context
- Thread IDs are persistent and can be retrieved from sent messages

### Performance Considerations

- Index on `thread_id` for efficient conversation queries
- Consider caching conversation metadata for frequently accessed applications
- Lazy load conversation content for better initial page load

### Backward Compatibility

- Existing emails without thread_id will still display correctly
- New emails will have proper threading
- Migration script can optionally backfill thread_ids for existing emails

---

## Dependencies

- Gmail API access with appropriate scopes
- EmailRecord model updates (database migration required)
- UI component updates for conversation display
- API endpoint additions for conversation queries

---

## Related Features

- [Email Response Parsing](../high-priority/02-email-response-parsing.md) - Responses will be linked to threads
- [Email Editing & Customization](../high-priority/03-email-editing-customization.md) - Editing emails in threads
- [Settings Page](../high-priority/04-settings-page.md) - May include conversation display preferences

---

## Benefits

- ✅ Maintains proper email conversation context
- ✅ Recruiters see full conversation history in their email client
- ✅ Better email management in Gmail
- ✅ Professional communication trail
- ✅ Improved user experience with conversation views
- ✅ Flexibility in follow-up targeting

---

## Success Criteria

- [ ] Follow-up emails are properly threaded in Gmail
- [ ] Conversation view displays complete email threads
- [ ] Selective follow-up triggering works from UI
- [ ] All emails in a conversation are linked via thread_id
- [ ] Performance is acceptable for applications with many emails
- [ ] Backward compatible with existing emails

---

**Last Updated**: January 2026
