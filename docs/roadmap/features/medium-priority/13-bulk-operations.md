# Bulk Operations & CSV Import/Export

**Priority**: Medium  
**Status**: Not Started  
**Phase**: Phase 4 - Calendar & Intelligence (Q2 2026)  
**Estimated Timeline**: Q2 2026

---

## Description

Bulk operations for managing applications efficiently. Includes CSV import/export, bulk status updates, bulk email sending, and selective processing. Enables efficient management of large numbers of applications.

**Key Goals**:
- Import applications from CSV
- Export applications to CSV/Excel
- Bulk status updates
- Bulk email sending with delays
- Selective processing by filters

---

## Use Cases

1. **Initial Setup**: Import existing applications from CSV
2. **Data Migration**: Migrate data from other systems
3. **Bulk Updates**: Update status for multiple applications at once
4. **Backup/Export**: Export applications for backup or analysis
5. **Bulk Actions**: Perform actions on filtered application sets

---

## Implementation Details

### CSV Import

#### Import Features

- Import applications from CSV file
- Map CSV columns to application fields
- Validate imported data
- Handle errors gracefully
- Preview before importing
- Import status reporting

#### CSV Format

**Required Columns**:
- Company name
- Position
- (Optional) Location, salary, job posting URL, recruiter info, etc.

**Column Mapping**:
- Flexible column name matching (case-insensitive)
- Map CSV columns to application fields
- Support custom column names
- Handle missing columns

#### Import Process

1. Upload CSV file
2. Preview and validate data
3. Map columns to fields
4. Review import preview
5. Confirm and import
6. Report import results (success/failures)

#### API Endpoint

- `POST /api/v1/applications/import` - Import applications from CSV
  - Request: Multipart file upload (CSV file)
  - Response: Import results (success count, failures, errors)

### CSV Export

#### Export Features

- Export applications to CSV
- Export filtered applications
- Export selected fields
- Support Excel format (.xlsx)
- Include related data (recruiters, emails, etc.)

#### Export Options

- All applications or filtered set
- Selected fields or all fields
- Include related data (emails, recruiters)
- Date range filtering
- Format selection (CSV, Excel)

#### API Endpoint

- `GET /api/v1/applications/export?format=csv` - Export applications
  - Query params: `format` (csv, xlsx), `fields[]`, `filters`, `date_range`
  - Response: CSV/Excel file download

### Bulk Status Updates

#### Update Features

- Update status for multiple applications
- Selective update by filters
- Batch update with validation
- Update status with notes
- Rollback capability (optional)

#### API Endpoint

- `PUT /api/v1/applications/bulk-update` - Bulk update applications
  - Request body: `{ "ids": [1, 2, 3], "status": "rejected", "notes": "..." }`
  - Or: `{ "filters": {...}, "status": "rejected" }`

### Bulk Email Sending

#### Sending Features

- Send emails to multiple applications
- Respect rate limits (automatic delays)
- Selective sending by filters
- Progress tracking
- Error handling per email

#### Implementation

- Queue emails for sending
- Respect rate limits (delay between emails)
- Track progress
- Report results (success/failures)

#### API Endpoint

- `POST /api/v1/applications/bulk-send-outreach` - Bulk send outreach emails
- `POST /api/v1/applications/bulk-send-followup` - Bulk send follow-up emails

### Selective Processing

#### Filter-Based Operations

- Apply operations to filtered application sets
- Filter by status, date, company, etc.
- Preview filtered set before operation
- Confirm before executing bulk operation

---

## Technical Considerations

### CSV Parsing

- Use `pandas` or `csv` module for parsing
- Handle encoding issues (UTF-8, etc.)
- Handle large CSV files (chunked processing)
- Validate data types and formats
- Error handling for malformed CSV

### File Upload

- Support large file uploads
- Validate file type and size
- Secure file handling
- Clean up temporary files
- Progress tracking for large imports

### Performance

- Process large imports in chunks/batches
- Async processing for large operations
- Progress tracking and status updates
- Timeout handling
- Resource management

### Data Validation

- Validate imported data
- Check required fields
- Validate data formats
- Handle duplicates
- Report validation errors

---

## Dependencies

- CSV parsing library (pandas or csv module)
- File upload handling
- Excel export library (openpyxl, if supporting Excel)
- Bulk operation service
- Background job processing (for large operations)

---

## Related Features

- Application Management (already implemented) - Core application CRUD
- [Email Scheduling](../medium-priority/12-email-scheduling.md) - Integration with bulk email sending
- Rate limiting (already implemented) - Integration with bulk sending

---

## Benefits

- ✅ Efficient data management
- ✅ Easy data migration
- ✅ Bulk operations save time
- ✅ Data backup and export
- ✅ Flexible data import/export

---

## Success Criteria

- [ ] CSV import works correctly
- [ ] CSV export works correctly
- [ ] Bulk status updates work
- [ ] Bulk email sending respects rate limits
- [ ] Selective processing works
- [ ] Performance is acceptable for large datasets
- [ ] Error handling is robust
- [ ] Data validation prevents errors

---

**Last Updated**: January 2026

