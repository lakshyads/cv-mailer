# Email Response Parsing & Analysis

**Priority**: High  
**Status**: Not Started  
**Phase**: Phase 3 - Conversation Management (Q1 2026)  
**Estimated Timeline**: Q1 2026

---

## Description

Automatically detect, parse, and analyze email responses from recruiters. Integrate seamlessly with conversation tracking and generate actionable insights. This feature enables intelligent email response handling with automatic status updates and action item generation.

**Key Goals**:
- Automatically detect incoming email responses
- Parse and analyze response content using NLP
- Generate actionable insights and next steps
- Integrate with conversation tracking
- Auto-update application status based on response intent

---

## Use Cases

1. **Automatic Response Detection**: Know immediately when a recruiter responds
2. **Sentiment Analysis**: Understand if the response is positive, negative, or neutral
3. **Intent Classification**: Identify if it's an interview invitation, rejection, or information request
4. **Action Item Generation**: Automatically create tasks based on response content
5. **Status Updates**: Auto-update application status based on response type
6. **Entity Extraction**: Extract dates, contact info, meeting links from responses

---

## Implementation Details

### Response Detection & Parsing

#### Gmail API Integration

- Gmail API to read incoming emails (requires `gmail.readonly` scope)
- Watch/push notifications for new emails (Gmail API push notifications)
- Polling alternative if push notifications are not available

#### Email Linking

Link responses to applications via multiple methods (in priority order):

1. **Thread ID matching** (primary method) - Most reliable
2. **Subject line matching** (fallback) - Match application-related subjects
3. **Recipient email matching** (fallback) - Match recruiter emails

#### Email Parsing

- Parse email content (HTML/text extraction)
- Extract metadata: sender, timestamp, attachments
- Handle email encoding and formatting
- Extract quoted/replied content separately

#### Database Changes

- New model: `EmailResponse` or extend `EmailRecord` with `is_response` flag
- Add `EmailRecord.is_response` (Boolean) - True for incoming emails
- Add `EmailRecord.parent_email_id` (ForeignKey) - Link to original sent email
- Store original email content and parsed text
- Store email headers for threading

### Response Analysis & Deductions

#### NLP Analysis

**Options**:
- spaCy for local NLP processing
- Transformers (BERT, etc.) for advanced analysis
- OpenAI API for response classification (optional, paid)
- Hybrid approach: spaCy for basic, OpenAI for complex cases

#### Sentiment Analysis

Classify sentiment as:
- Positive
- Negative
- Neutral
- Interested
- Not interested

#### Intent Classification

Classify intent as:
- Interview invitation
- Rejection
- Request for more information
- Scheduling request
- Offer discussion
- No response needed (acknowledgment)

#### Entity Extraction

Extract entities from responses:
- Interview dates/times
- Phone numbers
- Meeting links (Zoom, Teams, Google Meet, etc.)
- Additional contact information
- Salary/compensation mentions
- Company/position references

#### Database Changes

- Add `EmailResponse.analysis` (JSON) - Store analysis results
- Add `EmailResponse.sentiment` (Enum: positive, negative, neutral)
- Add `EmailResponse.intent` (Enum: interview, rejection, info_request, scheduling, offer, acknowledgment)
- Add `EmailResponse.extracted_entities` (JSON) - Dates, contacts, links, etc.
- Add `EmailResponse.confidence_score` (Float) - Analysis confidence (0.0-1.0)

### Action Items Generation

#### Automatic Status Updates

Based on response intent, automatically update application status:

- Interview invitation → Update status to `INTERVIEW_SCHEDULED`
- Rejection → Update status to `REJECTED`
- Offer discussion → Update status to `OFFER_RECEIVED`
- Request for info → Keep current status, create action item

#### Action Item Types

Create action items based on response analysis:

- **Schedule interview on [date]** → Calendar integration
- **Respond with availability** → Quick reply template
- **Send additional information** → Mark for follow-up
- **Update application status** → Status change action
- **No action needed** → Archive conversation

#### Manual Review Queue

- Responses with low confidence scores go to manual review
- User can approve/reject auto-generated actions
- Learning mechanism to improve classification over time

#### Database Changes

New model: `ActionItem`

```python
class ActionItem(Base):
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    email_response_id = Column(Integer, ForeignKey("email_records.id"))
    action_type = Column(Enum(ActionType))  # schedule_interview, send_reply, update_status, etc.
    description = Column(Text)
    due_date = Column(DateTime, nullable=True)
    status = Column(Enum(ActionStatus))  # pending, completed, cancelled
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

#### UI Components

1. **Action Items Panel** on application detail page
   - List of pending action items
   - Quick actions (complete, cancel, edit)
   - Due date indicators

2. **Action Items Dashboard** (all pending items)
   - Cross-application view of all action items
   - Filter by type, due date, status
   - Bulk actions

3. **Quick Actions** from response analysis
   - One-click buttons for common actions
   - "Schedule in Calendar", "Send Reply", etc.

4. **Manual Action Item Creation**
   - User can create action items manually
   - Link to specific email responses

5. **Action Item Completion Workflow**
   - Mark as completed
   - Add completion notes
   - Auto-update related application status if needed

### Integration with Conversation View

- Display parsed responses in conversation thread
- Show analysis badges (sentiment, intent) on each response email
- Inline action suggestions below analyzed responses
- Highlight important information (dates, contacts) in response content
- Visual indicators for responses that need attention

---

## Technical Considerations

### Gmail API Scopes

- Required: `gmail.readonly` scope for reading emails
- Consider: `gmail.modify` if we need to mark emails as read/archived

### NLP Service Selection

- **spaCy**: Free, fast, good for entity extraction, runs locally
- **OpenAI API**: More accurate, but costs money, requires API key
- **Hybrid**: Use spaCy for simple cases, OpenAI for complex/important responses

### Performance

- Batch process incoming emails (don't process one-by-one)
- Cache NLP models to avoid repeated loading
- Async processing for email analysis (don't block API responses)
- Queue system for processing large volumes

### Privacy & Security

- Only process emails that match application threads
- Don't store full email content unnecessarily
- Encrypt sensitive extracted information
- User consent for automatic status updates

### Error Handling

- Handle API rate limits gracefully
- Retry failed email fetches
- Handle malformed email content
- Graceful degradation if NLP service unavailable

---

## Dependencies

- Gmail API access with `gmail.readonly` scope
- NLP library (spaCy or OpenAI API)
- EmailRecord model updates (database migration required)
- ActionItem model (new database model)
- UI components for action items and analysis display
- Calendar integration (for scheduling actions)

---

## Related Features

- [Email Conversation Threading](../high-priority/01-email-conversation-threading.md) - Responses linked to threads
- [Calendar Integration](../high-priority/06-calendar-integration.md) - Schedule interviews from action items
- [Email Editing & Customization](../high-priority/03-email-editing-customization.md) - Quick reply templates

---

## Benefits

- ✅ Automatic response detection and processing
- ✅ Intelligent analysis saves time
- ✅ Actionable insights from every response
- ✅ Automatic status updates reduce manual work
- ✅ Never miss important information (dates, contacts)
- ✅ Better follow-up management

---

## Success Criteria

- [ ] Incoming emails are automatically detected and parsed
- [ ] Sentiment and intent classification accuracy > 80%
- [ ] Action items are automatically created for important responses
- [ ] Application status updates work correctly based on response type
- [ ] Entity extraction successfully finds dates, contacts, links
- [ ] Manual review queue handles uncertain responses
- [ ] Integration with conversation view works seamlessly
- [ ] Performance is acceptable for real-time processing

---

**Last Updated**: January 2026

