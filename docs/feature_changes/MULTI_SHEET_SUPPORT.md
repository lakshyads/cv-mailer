# Multi-Sheet Support

The application now supports processing multiple sheets in your Google Spreadsheet. This is perfect for your use case where each sheet represents a different date.

## How It Works

### Configuration

In your `.env` file, you can now configure:

```env
# Process all sheets (default: true)
PROCESS_ALL_SHEETS=true

# Optional: Filter sheets by name pattern (regex)
# Example: Only process sheets from 2024
SHEET_NAME_FILTER=2024

# If PROCESS_ALL_SHEETS=false, uses this single sheet
WORKSHEET_NAME=Sheet1
```

### Behavior

1. **When `PROCESS_ALL_SHEETS=true`** (default):
   - Lists all sheets in your spreadsheet
   - Reads data from each sheet
   - Combines all rows into a single list
   - Each row includes `_sheet_name` field indicating which sheet it came from

2. **When `PROCESS_ALL_SHEETS=false`**:
   - Only processes the sheet specified in `WORKSHEET_NAME`
   - Works like the original single-sheet mode

### Sheet Name Filtering

You can use regex patterns to filter which sheets to process:

```env
# Only process sheets from 2024
SHEET_NAME_FILTER=2024

# Only process sheets matching date pattern YYYY-MM-DD
SHEET_NAME_FILTER=\d{4}-\d{2}-\d{2}

# Process all sheets (no filter)
SHEET_NAME_FILTER=
```

### Unique Row Identification

To handle duplicate row numbers across sheets, the system now uses:

- Format: `{sheet_name}_{row_number}`
- Example: `2024-01-15_5` means row 5 in sheet "2024-01-15"

This ensures each application is uniquely tracked even if row numbers overlap.

### Database Changes

The `JobApplication` model now includes:

- `spreadsheet_row_id`: Changed from Integer to String (supports "sheet_row" format)
- `sheet_name`: New field storing the sheet name

### Example Workflow

1. Your spreadsheet has sheets: "2024-01-15", "2024-01-16", "2024-01-17"
2. Application reads all three sheets
3. Finds 10 rows in "2024-01-15", 5 in "2024-01-16", 8 in "2024-01-17"
4. Processes all 23 rows
5. Updates status in the correct sheet for each row

### Status Updates

When updating the "Status" column:

- The system automatically detects which sheet the row came from
- Updates the correct cell in the correct sheet
- Handles column name variations ("Status", "status", etc.)

## Migration Notes

If you have an existing database:

- The `spreadsheet_row_id` column type changed from Integer to String
- You may need to migrate existing data
- New applications will use the new format automatically

## Best Practices

1. **Consistent Sheet Names**: Use a consistent naming pattern (e.g., YYYY-MM-DD)
2. **Same Column Structure**: All sheets should have the same column headers
3. **Filter When Needed**: Use `SHEET_NAME_FILTER` to process only recent sheets
4. **Backup First**: Always backup your spreadsheet before first run
