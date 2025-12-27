# Multi-Recruiter Support

The application now supports multiple recruiters in a single cell, which is perfect for your use case where you list multiple recruiters for the same job opportunity.

## Format Support

The application can parse recruiters from a cell in the following formats:

### Format 1: Multiple Recruiters (Your Format)

```
Salman Khan - salman.khan@presight.ai, Alia Alkatheeri - alia.alkatheeri@presight.ai, Hamda Alkhamisi - hamda.alkhamisi@presight.ai, Max Baillon - max.baillon@presight.ai
```

### Format 2: Single Recruiter

```
John Doe - john.doe@company.com
```

### Format 3: Just Email

```
recruiter@company.com
```

### Format 4: Name Only (will skip if no email)

```
John Doe
```

## How It Works

### Parsing

1. **Splits by comma** to separate multiple recruiters
2. **Extracts name and email** from each part using pattern matching
3. **Removes duplicates** (same email address)
4. **Validates emails** before processing

### Processing

For each row in your Google Sheet:

1. **Parses all recruiters** from the "Recruiter Name" or "Recruiter Email" column
2. **Creates one JobApplication record** (shared across all recruiters for that job)
3. **Sends separate emails** to each recruiter:
   - Each email is personalized with the recruiter's name
   - Each email is tracked separately in the database
   - Prevents duplicate emails (checks if already sent to that recruiter)
4. **Updates spreadsheet status** once after processing all recruiters

### Database Tracking

- **One JobApplication** per row (represents the job opportunity)
- **Multiple EmailRecords** per JobApplication (one per recruiter)
- Each email is tracked individually, so you can see:
  - Which recruiters you've contacted
  - When you contacted each recruiter
  - Follow-up status per recruiter

## Example Workflow

### Input (Google Sheet Row)

```
Company: Presight
Position: Software Engineer
Recruiter Name: Salman Khan - salman.khan@presight.ai, Alia Alkatheeri - alia.alkatheeri@presight.ai
```

### Processing

1. Parser extracts 2 recruiters:
   - Salman Khan (<salman.khan@presight.ai>)
   - Alia Alkatheeri (<alia.alkatheeri@presight.ai>)

2. Creates JobApplication:
   - Company: Presight
   - Position: Software Engineer
   - Primary Recruiter: Salman Khan (first in list)

3. Sends emails:
   - Email 1: To Salman Khan (personalized)
   - Email 2: To Alia Alkatheeri (personalized)

4. Records in database:
   - 1 JobApplication record
   - 2 EmailRecord records (linked to the JobApplication)

5. Updates spreadsheet:
   - Status: "Reached Out"

## Column Detection

The application looks for recruiter information in this order:

1. **"Recruiter Name"** column (or `recruiter_name`)
2. **"Recruiter Email"** column (or `recruiter_email`) - if Recruiter Name is empty

You can use either column, but "Recruiter Name" is preferred since it can contain both names and emails.

## Duplicate Prevention

The system prevents sending duplicate emails by:

1. **Checking database** before sending: Has an email already been sent to this recruiter for this job?
2. **Removing duplicate emails** during parsing: If the same email appears twice in the cell, only one email is sent
3. **Tracking per recruiter**: Each recruiter's email is tracked separately

## Follow-up Emails

Follow-up emails also support multiple recruiters:

- The system checks when the last email was sent to each recruiter
- Follow-ups are sent individually to each recruiter who needs one
- Each follow-up is tracked separately

## Benefits

1. **Efficiency**: Reach out to multiple recruiters at once
2. **Tracking**: See exactly who you've contacted and when
3. **Flexibility**: Mix and match formats in your sheet
4. **Safety**: Prevents duplicate emails automatically

## Tips

1. **Consistent Format**: Use "Name - <email@domain.com>" format for best results
2. **Separate by Comma**: Use commas to separate multiple recruiters
3. **Check Before Sending**: Use `--dry-run` to see which recruiters will receive emails
4. **Review Logs**: Check the logs to see how many recruiters were parsed from each row

## Example Sheet Structure

| Company Name | Position | Recruiter Name | Status |
|-------------|----------|----------------|--------|
| Presight | Software Engineer | Salman Khan - <salman.khan@presight.ai>, Alia Alkatheeri - <alia.alkatheeri@presight.ai> | |
| Google | Data Scientist | John Doe - <john@google.com> | |

The application will:

- Parse 2 recruiters from Presight row → send 2 emails
- Parse 1 recruiter from Google row → send 1 email
