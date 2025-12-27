# Google Sheets Template Guide

Reference guide for setting up your Google Sheet with job applications.

> 📖 **Setup**: See [Quick Start](QUICK_START.md) or [Complete Setup Guide](SETUP_GUIDE.md)

## Required Columns

Your Google Sheet should have the following columns (column names are case-insensitive and flexible):

### Essential Columns

1. **Company Name** (or `company_name`)
   - The name of the company you're applying to
   - Example: "Google", "Microsoft", "Amazon"

2. **Position** (or `position`)
   - The job title/position you're applying for
   - Example: "Software Engineer", "Data Scientist", "Product Manager"

3. **Recruiter Email** (or `recruiter_email`)
   - Email address of the recruiter or hiring manager
   - Example: "<recruiter@company.com>"

### Optional Columns

1. **Recruiter Name** (or `recruiter_name`)
   - Name of the recruiter (for personalization)
   - Example: "John Doe", "Jane Smith"

2. **Location** (or `location`)
   - Job location
   - Example: "San Francisco, CA", "Remote", "New York, NY"

3. **Job Posting URL** (or `job_posting_url`)
   - Link to the job posting
   - Example: "<https://careers.company.com/job/12345>"

4. **Expected salary** (or `expected_salary`, `Salary`)
   - Your expected salary for this position
   - Example: "$120,000", "150k", "Negotiable"
   - Stored in database for tracking (not included in email by default)

5. **Message** (or `message`, `Custom Message`)
   - Custom message to include in the email
   - If provided, replaces the default email body text
   - Example: "I'm particularly interested in this role because..."
   - Leave empty to use default email template

6. **Status** (or `status`)
   - Application status (auto-updated by the application)
   - Values: "Draft", "Reached Out", "Applied", "Interview Scheduled", etc.
   - Leave empty for new applications

## Example Sheet Structure

| Company Name | Position | Recruiter Name | Recruiter Email | Location | Job Posting URL | Expected salary | Message | Status |
|-------------|----------|----------------|-----------------|----------|-----------------|-----------------|---------|--------|
| Google | Software Engineer | John Doe | <john@google.com> | Mountain View, CA | <https://careers.google.com/jobs/123> | $150,000 | | |
| Microsoft | Data Scientist | Jane Smith | <jane@microsoft.com> | Seattle, WA | <https://careers.microsoft.com/jobs/456> | $140k | I'm excited about AI opportunities | |
| Amazon | Product Manager | | <hiring@amazon.com> | Remote | <https://amazon.jobs/en/jobs/789> | Negotiable | | |

## Column Name Flexibility

The application is flexible with column names. It will try to match multiple variations:

### Company Column

- `Company Name` (preferred)
- `company_name`
- `Company` (also supported)
- `company`

### Position Column

- `Position` (preferred)
- `position`

### Recruiter Column

- `Recruiter Names` (preferred, supports multiple recruiters)
- `recruiter_names`
- `Recruiter Name` (also supported)
- `recruiter_name`
- `Recruiter Email` (fallback)
- `recruiter_email`

### Location Column

- `Location` (preferred)
- `location`

### Job Posting Column

- `Job Posting URL` (preferred)
- `job_posting_url`
- `Job Posting` (also supported)
- `job_posting`

### Expected Salary Column

- `Expected salary` (preferred)
- `expected_salary`
- `Expected Salary`
- `Salary`
- `salary`

### Message Column

- `Message` (preferred)
- `message`
- `Custom Message`
- `custom_message`

### Status Column

- `Status` (preferred)
- `status`

The application will automatically try these variations in order, so your sheet will work with any of these column names.

## Status Values

The application will automatically update the `Status` column with:

- **Reached Out**: After sending the first email
- **Applied**: When you manually mark as applied
- **Interview Scheduled**: When a response indicates an interview
- **In Progress**: Application is being processed
- **Closed**: Application is closed
- **Rejected**: Application was rejected
- **Accepted**: Application was accepted

## Tips

1. **Keep it organized**: Use one row per job application
2. **Update regularly**: Manually update status as your applications progress
3. **Add notes**: You can add additional columns for your own tracking (they'll be ignored by the app)
4. **Backup**: Keep a backup of your sheet before running the application for the first time

## Multi-Sheet Support

The application supports processing multiple sheets in a single spreadsheet:

**Enable Multi-Sheet Mode** (`.env`):
```env
PROCESS_ALL_SHEETS=true
SHEET_NAME_FILTER=2024  # Optional: filter by sheet name pattern
```

**Benefits**:
- Organize applications by date (e.g., "2024-01-15", "2024-01-20")
- Keep historical data separated
- Each row uniquely tracked as `{sheet_name}_{row_number}`

**Example Spreadsheet Structure**:
```
My Job Applications
├── 2024-01-15 (sheet)
├── 2024-01-20 (sheet)
└── 2024-02-01 (sheet)
```

All sheets must use the same column structure.

## Multi-Recruiter Support

Contact multiple recruiters for the same job:

**Format** (in Recruiter Names column):
```
Alice Johnson - alice@company.com, Bob Smith - bob@company.com
```

**Features**:
- Send personalized emails to each recruiter
- Track each separately in database
- Automatic duplicate prevention
- Individual follow-up tracking

## Customizing Column Names

If your sheet uses different column names, you can modify the column mapping in `src/cv_mailer/cli/app.py` in the `process_new_applications` method.

Example modification:

```python
company_name = row.get('Company', row.get('company_name', ''))
position = row.get('Job Title', row.get('position', ''))
```

**Note**: With the new package structure, the file is now located at:
`src/cv_mailer/cli/app.py` (instead of `main.py` at root)
