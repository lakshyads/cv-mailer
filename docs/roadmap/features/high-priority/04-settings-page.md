# Settings Page & Configuration Management

**Priority**: High  
**Status**: Not Started  
**Phase**: Phase 3 - Conversation Management (Q1 2026)  
**Estimated Timeline**: Q1 2026

---

## Description

Comprehensive settings page in UI for managing email templates, resume files, and application configuration. This feature provides a centralized interface for managing all application settings without requiring direct file edits or environment variable changes.

**Key Goals**:
- Edit email templates via UI
- Manage resume files
- Configure application settings (rate limits, follow-up timing, etc.)
- Centralized settings management
- User-friendly interface for all configurations

---

## Use Cases

1. **Template Management**: Update email templates without code changes
2. **Resume Management**: Upload, organize, and set default resumes
3. **Configuration**: Adjust rate limits, timing, and other settings
4. **Quick Setup**: Configure application settings during initial setup
5. **Ongoing Maintenance**: Update settings as needs change

---

## Implementation Details

### Settings Page UI

#### Location
- New route: `/settings` in frontend
- Accessible from main navigation menu
- Protected route (future: with authentication)

#### Layout Options

**Option 1: Tabbed Interface**
- Tabs for each settings category
- Clean separation of concerns
- Easy navigation

**Option 2: Accordion Sections**
- Expandable sections for each category
- Single page view of all settings
- Good for mobile/responsive design

**Recommended**: Start with tabbed interface, consider accordion for mobile

#### Sections

1. **Email Templates** (Section 4.1)
2. **Resume Files** (Section 4.2)
3. **Application Settings** (Section 4.3)
4. **Future Sections**:
   - Notifications
   - Integrations
   - Advanced options

#### UI Features

- Save/Cancel buttons per section
- Success/error toast notifications
- Validation error display inline
- Loading states during save
- Confirmation dialogs for destructive actions

### Email Template Management

#### Description

Edit default email subjects and content/templates for outreach and follow-ups. Allows users to customize email templates without modifying code.

#### Implementation

**Template Types**:
- First contact email (subject + body)
- Follow-up email (subject + body, with follow-up number variable)

**Template Editor Features**:
- Text editor for subject line
- Rich text editor for email body
- Template variable documentation/preview
- Live preview with sample data
- Save templates to database or config file
- Reset to default templates

**Template Variables**:
- `{{ recruiter_name }}` - Recruiter's name
- `{{ company_name }}` - Company name
- `{{ position }}` - Job position
- `{{ location }}` - Job location
- `{{ job_posting_url }}` - URL to job posting
- `{{ follow_up_number }}` - Follow-up number (follow-up emails only)

**Live Preview**:
- Show template rendered with sample data
- Update preview in real-time as user types
- Display how email will appear to recipients

#### Database Changes (Optional)

**Option 1: Database Storage**
- New model: `EmailTemplate`
  - `id` (Integer, primary key)
  - `template_type` (Enum: first_contact, follow_up)
  - `subject` (Text)
  - `body` (Text)
  - `is_default` (Boolean)
  - `created_at` (DateTime)
  - `updated_at` (DateTime)

**Option 2: Config File Storage**
- Store templates in configuration file
- Update file via API
- Requires file system access

**Recommendation**: Start with database storage for flexibility

#### API Endpoints

- `GET /api/v1/settings/templates` - Get all templates
- `GET /api/v1/settings/templates/{type}` - Get specific template (first_contact or follow_up)
- `PUT /api/v1/settings/templates/{type}` - Update template
- `POST /api/v1/settings/templates/{type}/reset` - Reset to default template

### Resume File Management

#### Description

Select and manage default/custom resume files. Allows users to upload, organize, and set default resumes via the UI.

#### Implementation

**Resume File List**:
- Default resume (from `RESUME_PATH` config)
- Additional resume files (from `assets/resumes/` or configurable directory)
- Display metadata: file name, size, upload date, usage count

**Actions**:
- Set default resume
- Upload new resume file
- Delete resume file (with confirmation)
- Edit resume Google Drive link
- View resume usage statistics

**Resume Metadata**:
- File name
- File size
- Upload date
- Usage count (how many emails sent with this resume)
- File path or Google Drive link

#### API Endpoints

- `GET /api/v1/settings/resumes` - List all resume files
- `POST /api/v1/settings/resumes` - Upload new resume file
- `PUT /api/v1/settings/resumes/default` - Set default resume
- `DELETE /api/v1/settings/resumes/{id}` - Delete resume file
- `GET /api/v1/settings/resumes/{id}/stats` - Get usage statistics (optional)

#### File Storage

- Local files: Store in `assets/resumes/` directory
- Google Drive links: Store link in database
- Validate file types (PDF recommended)
- Handle file size limits

### Application Configuration

#### Description

Edit default config values for `DAILY_EMAIL_LIMIT`, `FOLLOW_UP_DAYS`, `MAX_FOLLOW_UPS`, and other application settings.

#### Configuration Options

- **Daily Email Limit**: Maximum emails to send per day (integer)
- **Follow-up Days**: Days to wait before sending follow-up (integer)
- **Max Follow-ups**: Maximum follow-ups per application (integer)
- **Email Delay Min/Max**: Delay between emails in seconds (optional)

#### Implementation

**Configuration Form**:
- Integer inputs with min/max validation
- Input validation (positive integers, reasonable ranges)
- Show current values
- Allow reset to defaults
- Real-time validation feedback

**Storage Options**:

**Option 1: Database Config Table**
- New model: `ApplicationConfig`
- Store key-value pairs
- Runtime updates (no restart required)
- More flexible

**Option 2: .env File**
- Update `.env` file via API
- Requires file system access
- May require application restart
- Simpler for existing setup

**Recommendation**: Start with database storage for runtime updates

#### API Endpoints

- `GET /api/v1/settings/config` - Get current configuration
- `PUT /api/v1/settings/config` - Update configuration
- `POST /api/v1/settings/config/reset` - Reset to defaults
- `GET /api/v1/settings/config/validation` - Validate configuration values (optional)

#### Configuration Validation

- Validate positive integers
- Set reasonable ranges (e.g., daily limit: 1-1000)
- Validate logical relationships (e.g., max follow-ups >= 1)
- Show validation errors inline
- Prevent saving invalid configurations

---

## Technical Considerations

### Settings Persistence

- Ensure settings persist across application restarts
- Handle concurrent updates (last write wins or optimistic locking)
- Backup settings before major changes
- Audit log for settings changes (optional)

### Template Rendering

- Templates use Jinja2 syntax (match existing template service)
- Validate template syntax before saving
- Test template rendering with sample data
- Handle template errors gracefully

### File Upload

- Support common resume formats (PDF, DOC, DOCX)
- Validate file size (e.g., max 10MB)
- Scan uploaded files for viruses (optional, future)
- Handle upload errors gracefully
- Show upload progress

### Configuration Updates

- Runtime configuration updates (if using database storage)
- Notify services of configuration changes (if needed)
- Validate configuration before applying
- Rollback mechanism for invalid configurations

### Security

- Validate user input (prevent XSS, injection)
- Sanitize template content
- Secure file upload handling
- Restrict file access (don't expose file system)
- Authentication/authorization for settings access (future)

---

## Dependencies

- Database models for EmailTemplate and ApplicationConfig (if using database storage)
- File upload handling for resume files
- Template rendering service (existing)
- Configuration management service
- Frontend settings page components

---

## Related Features

- [Email Editing & Customization](../high-priority/03-email-editing-customization.md) - Uses templates from settings
- [Email Conversation Threading](../high-priority/01-email-conversation-threading.md) - Templates used in threaded emails
- Authentication (future) - Settings page access control

---

## Benefits

- ✅ User-friendly settings management
- ✅ No code changes required for template/config updates
- ✅ Centralized configuration management
- ✅ Easy resume file management
- ✅ Quick setup and ongoing maintenance
- ✅ Reduces support requests for configuration changes

---

## Success Criteria

- [ ] Users can edit email templates via UI
- [ ] Templates are saved and loaded correctly
- [ ] Resume files can be uploaded and managed
- [ ] Application configuration can be updated via UI
- [ ] Settings persist across application restarts
- [ ] Validation prevents invalid configurations
- [ ] UI is intuitive and user-friendly
- [ ] Settings page is responsive and accessible

---

**Last Updated**: January 2026

