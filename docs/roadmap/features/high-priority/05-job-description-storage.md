# Job Description Storage

**Priority**: High  
**Status**: Not Started  
**Phase**: Phase 3 - Conversation Management (Q1 2026)  
**Estimated Timeline**: Q1 2026

---

## Description

Store job description for each application to enable AI-powered personalized email generation, interview preparation, and job matching analysis. This feature provides the foundation for intelligent email personalization based on job requirements.

**Key Goals**:
- Store full job description text for each application
- Support multiple input methods (sheet import, manual entry, URL fetch)
- Enable AI-powered email personalization
- Support interview preparation
- Enable job matching analysis

---

## Use Cases

1. **AI-Powered Email Personalization**: Analyze job description to match skills and generate personalized emails
2. **Interview Preparation**: Reference job description when preparing for interviews
3. **Job Matching**: Analyze job requirements against your skills/experience
4. **Email Content Suggestions**: Generate email content suggestions based on job requirements
5. **Historical Reference**: Keep job descriptions for reference after application is closed

---

## Implementation Details

### Database Changes

#### New Fields in JobApplication Model

- `job_description` (Text) - Full job description text
  - Type: Text (supports long descriptions, 10,000+ characters)
  - Nullable: True (optional field for backward compatibility)
  - Index: Not needed (full-text search can use FTS if needed)

- `job_description_source` (String, optional) - URL or source of job description
  - Type: String(500)
  - Nullable: True
  - Purpose: Track where job description came from (sheet, manual entry, URL)
  - Examples: "Google Sheets", "https://jobs.example.com/post/123", "Manual entry"

#### Migration Strategy

- Add fields as nullable for backward compatibility
- Existing applications will have null job_description (OK)
- New applications will have job_description populated
- Optional: Backfill job descriptions for existing applications

### Sheet Parser Integration

#### Google Sheets Template

- Add `job_description` column mapping in Google Sheets template
- Column name variations:
  - `job_description`
  - `job_description_text`
  - `job_description_full`
  - Case-insensitive matching

#### Parser Updates

- Update `src/cv_mailer/utils/sheet_parser.py`
- Add job_description to parsed row data
- Handle long text fields (job descriptions can be lengthy)
- Store job_description_source as "Google Sheets"

#### Sheet Row Processing

- Parse job_description from sheet row
- Store in database when creating/updating applications
- Handle empty/missing job_description gracefully
- Preserve formatting (line breaks, bullet points, etc.)

### Manual Entry

#### Application Creation Form

- Add job description field in application creation form
- Text area component (multi-line input)
- Character limit: 10,000 characters (reasonable limit)
- Character counter display
- Optional field (not required)

#### Application Edit Form

- Add job description field in application edit form
- Same text area component
- Pre-populated with existing job description
- Allow editing/updating

#### Input Methods

- **Paste from job posting**: Allow users to paste job description text
- **Manual typing**: Allow users to type job description
- **"Fetch from URL" button**: Future enhancement to fetch job description from URL

#### UI Components

- Large text area (10+ rows)
- Character counter (X/10,000 characters)
- Formatting hints (supports line breaks, bullet points)
- Clear/reset button
- Auto-save draft (optional, future enhancement)

### API Changes

#### Schema Updates

**ApplicationCreate Schema**:
- Add `job_description: Optional[str]` field
- Add `job_description_source: Optional[str]` field

**ApplicationUpdate Schema**:
- Add `job_description: Optional[str]` field
- Add `job_description_source: Optional[str]` field

**ApplicationResponse Schema**:
- Include `job_description` in application detail responses
- Include `job_description_source` in application detail responses

#### API Endpoints

**No new endpoints required** - existing endpoints will support job_description:

- `POST /api/v1/applications` - Accept job_description in request body
- `PUT /api/v1/applications/{id}` - Accept job_description in request body
- `GET /api/v1/applications/{id}` - Return job_description in response
- `GET /api/v1/applications` - Include job_description in list responses (optional, may be large)

#### Response Considerations

- Job descriptions can be large (5-10KB+)
- Consider omitting from list endpoints (performance)
- Include in detail endpoint responses
- Optional: Add `?include_description=true` query parameter

### UI Components

#### Application Detail Page

**Job Description Display**:
- Expandable/collapsible job description section
- Full job description text
- Preserve formatting (line breaks, paragraphs)
- Copy to clipboard button
- "Edit" button (if user has edit permissions)

**Layout**:
- Collapsed by default (show first 500 characters + "Show more")
- Expandable to show full description
- Scrollable if description is very long
- Read-only view (separate from edit form)

#### Application Form (Create/Edit)

**Job Description Editor**:
- Large text area (10-15 rows)
- Character counter
- Placeholder text with instructions
- Formatting hints
- Auto-resize or scrollable

**Integration**:
- Part of application creation/edit form
- Optional field (not required)
- Save with other application data

#### Future Enhancements

- **"Fetch from URL" button**: Fetch job description from job posting URL
- **Job description analyzer**: Highlight key skills/requirements
- **Job matching score**: Match job requirements with your skills
- **AI summary**: Generate summary of job requirements

---

## Technical Considerations

### Text Storage

- Use TEXT type in database (supports large text, 65KB+)
- Consider character encoding (UTF-8)
- Preserve formatting (line breaks, special characters)
- Handle HTML/rich text (if fetched from URL, strip HTML or store as-is)

### Performance

- Job descriptions can be large (5-10KB+)
- Don't include in list endpoint responses (performance)
- Include in detail endpoint only
- Consider pagination for applications with very long descriptions

### Search Considerations

- Full-text search on job descriptions (future enhancement)
- Index for search performance (FTS index)
- Search job descriptions by keywords
- Match applications by job description content

### Data Validation

- Validate character limit (10,000 characters)
- Sanitize input (prevent XSS if displaying in UI)
- Validate job_description_source URL format (if provided)
- Handle special characters and encoding

---

## Dependencies

- Database migration for new fields
- Sheet parser updates
- API schema updates (Pydantic models)
- Frontend form components
- Application detail page updates

---

## Related Features

- [Email Response Parsing](../high-priority/02-email-response-parsing.md) - Job description can inform response analysis
- [AI-Powered Email Generation](../nice-to-have/17-ai-powered-email-generation.md) - Job description is input for AI email generation
- [Email Editing & Customization](../high-priority/03-email-editing-customization.md) - Job description can inform email personalization
- [Interview Preparation Assistant](../nice-to-have/20-interview-preparation-assistant.md) - Job description is key input for interview prep

---

## Benefits

- ✅ Foundation for AI-powered email personalization
- ✅ Better interview preparation with job requirements
- ✅ Job matching analysis capabilities
- ✅ Historical reference for closed applications
- ✅ Enables future intelligent features

---

## Success Criteria

- [ ] Job descriptions can be stored in database
- [ ] Job descriptions can be imported from Google Sheets
- [ ] Job descriptions can be entered manually via UI
- [ ] Job descriptions display correctly on application detail page
- [ ] Job descriptions are included in API responses
- [ ] Character limit validation works correctly
- [ ] Performance is acceptable (descriptions don't slow down queries)
- [ ] Backward compatible (existing applications work without job descriptions)

---

## Future Enhancements

- **URL Fetching**: Automatically fetch job description from job posting URL
- **Job Description Analysis**: Extract key skills, requirements, salary range
- **Job Matching**: Score how well job matches your skills
- **AI Summary**: Generate summary of job requirements
- **Full-Text Search**: Search applications by job description content

---

**Last Updated**: January 2026

