# Multi-Resume Support

**Priority**: Medium  
**Status**: Partially Covered by Settings Page  
**Phase**: Phase 4 - Calendar & Intelligence (Q2 2026)  
**Estimated Timeline**: Q2 2026

---

## Description

Smart resume selection based on job category, keywords, and company type. Extends basic resume file management (available in Settings) with intelligent auto-selection, A/B testing, and resume versioning per application.

**Note**: Basic resume file management is now in Settings (High Priority #4.2). This feature adds intelligent selection and A/B testing capabilities.

**Key Goals**:
- Auto-select resume based on job description keywords
- Resume selection based on job category and company type
- A/B testing different resumes
- Resume versioning per application
- Track resume performance metrics

---

## Use Cases

1. **Job-Specific Resumes**: Use different resumes for backend, frontend, fullstack positions
2. **A/B Testing**: Test which resume versions get better response rates
3. **Company-Specific**: Use startup-focused resume for startups, enterprise-focused for large companies
4. **Keyword Matching**: Auto-select resume based on keywords in job description
5. **Performance Tracking**: Track which resumes perform best

---

## Implementation Details

### Smart Resume Selection

#### Selection Criteria

**Job Category** (manual tagging or auto-detect):
- Backend Developer
- Frontend Developer
- Full Stack Developer
- DevOps Engineer
- Data Engineer
- etc.

**Job Description Keywords**:
- Extract keywords from job description
- Match keywords to resume categories
- Score resumes based on keyword match
- Select best-matching resume

**Company Type**:
- Startup vs. Enterprise
- Industry-based selection
- Company size-based selection

#### Auto-Selection Logic

1. Extract job description keywords
2. Match keywords to resume categories
3. Score available resumes based on match
4. Select highest-scoring resume
5. Fallback to default resume if no match

### Resume Versioning

#### Database Changes

- Add `JobApplication.resume_version` field (String, nullable)
- Store which resume version was used for each application
- Link to resume file/category used

#### Version Tracking

- Track resume version per application
- Historical tracking of which resume was used
- Performance metrics per resume version

### A/B Testing

#### Testing Framework

- Define resume variants for A/B testing
- Random assignment of resumes to applications
- Track response rates per resume variant
- Statistical analysis of results

#### Metrics Tracking

- Response rate per resume
- Interview rate per resume
- Offer rate per resume
- Time-to-response per resume

### Implementation

#### Resume Categories

- Define resume categories (backend, frontend, fullstack, etc.)
- Map resumes to categories
- Keyword matching rules per category
- Scoring algorithm for resume selection

#### Configuration

**Resume Category Mapping**:
```python
RESUME_CATEGORIES = {
    "backend": ["backend", "server", "api", "python", "java"],
    "frontend": ["frontend", "react", "ui", "javascript"],
    "fullstack": ["fullstack", "full-stack", "full stack"],
    # ...
}
```

**Resume Selection Rules**:
- Keyword-based selection
- Category-based selection
- Company type-based selection
- Manual override option

---

## Dependencies

- [Settings Page - Resume File Management](../high-priority/04-settings-page.md) - Foundation for resume management
- [Job Description Storage](../high-priority/05-job-description-storage.md) - For keyword extraction
- Resume category configuration
- A/B testing framework (optional)

---

## Related Features

- [Settings Page](../high-priority/04-settings-page.md) - Resume file management
- [Email Editing & Customization](../high-priority/03-email-editing-customization.md) - Manual resume selection
- [Advanced Analytics](../medium-priority/09-advanced-analytics.md) - Resume performance metrics

---

## Benefits

- ✅ Better job-resume matching
- ✅ A/B testing capabilities
- ✅ Data-driven resume selection
- ✅ Improved response rates
- ✅ Resume performance insights

---

## Success Criteria

- [ ] Resume auto-selection works based on job description
- [ ] A/B testing framework functions correctly
- [ ] Resume versioning tracks correctly
- [ ] Performance metrics are accurate
- [ ] Selection logic is configurable
- [ ] Manual override option works

---

**Last Updated**: January 2026

