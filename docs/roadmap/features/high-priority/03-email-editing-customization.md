# Email Editing & Customization Before Sending

**Priority**: High  
**Status**: Not Started  
**Phase**: Phase 3 - Conversation Management (Q1 2026)  
**Estimated Timeline**: Q1 2026

---

## Description

Allow users to edit email subject, content, and resume attachments before sending outreach or follow-up emails. This feature provides flexibility to customize emails on a per-application basis while maintaining the convenience of templates.

**Key Goals**:
- Edit email subject and body before sending
- Select custom resume files per email
- Edit resume Google Drive links
- Preview emails before sending
- Maintain template defaults as fallback

---

## Use Cases

1. **Personalization**: Customize email content for specific applications
2. **Resume Selection**: Use different resumes for different job types
3. **Quick Edits**: Make minor adjustments to template-generated emails
4. **Preview**: Review email before sending to ensure quality
5. **Selective Sending**: Customize emails for specific recruiters

---

## Implementation Details

### Email Content Editing

#### API Endpoints

1. **Preview Endpoints** (Generate email preview with editable fields):
   - `POST /api/v1/applications/{id}/send-outreach/preview` - Preview first contact email
   - `POST /api/v1/applications/{id}/send-follow-up/preview` - Preview follow-up email

2. **Send Endpoints** (Send with custom subject/content):
   - `POST /api/v1/applications/{id}/send-outreach` - Send outreach with custom content
   - `POST /api/v1/applications/{id}/send-follow-up` - Send follow-up with custom content

#### Request Body Structure

```json
{
  "subject": "string (optional)",      // Uses template default if not provided
  "body": "string (optional)",         // Uses template default if not provided
  "recruiter_ids": [1, 2],             // Optional, for selective sending
  "resume_file_path": "string (optional)",
  "resume_drive_link": "string (optional)"
}
```

#### Backend Implementation

- Load default template if subject/body not provided
- Render template with application data
- Allow override of subject/body
- Support template variable substitution
- Validate email content before sending

#### UI Components

1. **Email Composer Modal/Drawer**
   - Full-screen or drawer-style email editor
   - Accessible from "Send Outreach" or "Send Follow-up" buttons
   - Pre-populated with template-generated content

2. **Rich Text Editor**
   - HTML editor for email body (or markdown editor)
   - Toolbar with formatting options
   - Syntax highlighting for template variables
   - HTML preview toggle

3. **Subject Line Input**
   - Text input field
   - Character counter
   - Template variable support

4. **Live Preview**
   - Rendered email preview panel
   - Show how email will appear to recipient
   - Update in real-time as user types

5. **Template Variable Preview**
   - Show available template variables
   - Preview variable values for current application
   - Copy variable syntax to clipboard

6. **Actions**
   - "Use default template" button to reset to template
   - "Save as draft" (future enhancement)
   - "Send" button with confirmation

### Resume File Selection & Editing

#### Implementation Details

**Resume Selection Options**:
- Default resume (from `RESUME_PATH` config)
- Custom file (file picker for local files)
- Google Drive link (text input with validation)
- Recent resumes (cached list of recently used)

**Priority Logic**:
- If both `resume_file_path` and `resume_drive_link` provided, `resume_file_path` takes precedence
- If neither provided, use default resume from config

#### Validation

- **Local Files**: Validate file exists and is readable
- **Google Drive Links**: Validate URL format (must be valid Google Drive share link)
- **File Type**: Ensure file is PDF (or other supported format)

#### Database Changes

- Add `EmailRecord.resume_file_path` (String, optional) - Path to local resume file
- Add `EmailRecord.resume_drive_link` (Text, optional) - Google Drive link to resume
- Store per-email resume info for historical tracking
- Allows tracking which resume was used for each email

#### UI Components

1. **Resume Selector Component**
   - Dropdown/select component in email composer
   - Shows current selection
   - Lists available options

2. **File Upload Button** (if using local files)
   - File picker dialog
   - Supports PDF files
   - Shows file name after selection

3. **Google Drive Link Input**
   - Text input with validation
   - URL format validation
   - Extract file ID from Google Drive URL if needed

4. **Resume Preview/Icon Display**
   - Show selected resume name/icon
   - Preview thumbnail (if available)
   - Remove/reset option

---

## Technical Considerations

### Template Variable Handling

- Support existing template variables: `{{ recruiter_name }}`, `{{ company_name }}`, `{{ position }}`, `{{ location }}`, `{{ job_posting_url }}`, `{{ follow_up_number }}`
- Allow users to add custom variables in edited content
- Validate variable syntax in user-edited content

### Email Formatting

- Preserve HTML formatting from templates
- Allow users to add HTML formatting in editor
- Sanitize user input to prevent XSS
- Ensure email renders correctly across email clients

### Resume Handling

- Store resume selection per email for historical tracking
- Support both local files and Google Drive links
- Handle file access errors gracefully
- Cache recent resume selections for quick access

### Performance

- Lazy load email preview (don't render until requested)
- Cache template renders for performance
- Optimize file upload/preview for large resume files

---

## Dependencies

- Email template service (for default templates)
- File system access (for local resume files)
- Google Drive API (for Drive link validation, if needed)
- Rich text editor component for frontend
- Email preview rendering capability

---

## Related Features

- [Settings Page](../high-priority/04-settings-page.md) - Manage default templates and resume files
- [Email Conversation Threading](../high-priority/01-email-conversation-threading.md) - Edited emails will be part of threads
- [Email Response Parsing](../high-priority/02-email-response-parsing.md) - Responses to edited emails

---

## Benefits

- ✅ Flexibility to customize emails per application
- ✅ Professional email personalization
- ✅ Easy resume selection for different job types
- ✅ Preview before sending reduces errors
- ✅ Maintains template convenience while allowing customization
- ✅ Historical tracking of resume usage per email

---

## Success Criteria

- [ ] Users can edit email subject and body before sending
- [ ] Email preview shows accurate rendering
- [ ] Resume selection works for both local files and Google Drive links
- [ ] Template variables are properly substituted
- [ ] Edited emails are stored with resume information
- [ ] UI is intuitive and user-friendly
- [ ] Performance is acceptable (preview loads quickly)

---

**Last Updated**: January 2026

