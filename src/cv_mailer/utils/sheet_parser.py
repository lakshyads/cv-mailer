"""
Utilities for parsing Google Sheets row data with flexible column name matching.
"""

from typing import Optional, Dict, Any, List


def get_row_value(row: Dict[str, Any], column_names: List[str], default: Any = None) -> Any:
    """
    Get value from row dictionary using multiple possible column names.

    Tries each column name in order and returns the first non-empty value found.
    If all are empty or missing, returns the default value.

    Args:
        row: Dictionary representing a row from Google Sheets
        column_names: List of possible column names to try (in order of preference)
        default: Default value to return if no match is found

    Returns:
        Value from row, or default if not found

    Example:
        company_name = get_row_value(row, ["Company Name", "company_name", "Company", "company"], "")
    """
    for column_name in column_names:
        value = row.get(column_name)
        if value is not None and value != "":
            return value
    return default


def extract_application_data(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract application data from Google Sheets row with flexible column name matching.

    This function handles various column name formats (e.g., "Company Name", "company_name", "Company")
    to make the system more resilient to different spreadsheet formats.

    Args:
        row: Dictionary representing a row from Google Sheets

    Returns:
        Dictionary with extracted application data:
        - company_name: str
        - position: str
        - recruiter_cell: str
        - location: Optional[str]
        - job_posting_url: Optional[str]
        - expected_salary: Optional[str]
        - custom_message: Optional[str]
    """
    return {
        "company_name": get_row_value(
            row, ["Company Name", "company_name", "Company", "company"], ""
        ),
        "position": get_row_value(row, ["Position", "position"], ""),
        "recruiter_cell": get_row_value(
            row,
            [
                "Recruiter Names",
                "recruiter_names",
                "Recruiter Name",
                "recruiter_name",
                "Recruiter Email",
                "recruiter_email",
            ],
            "",
        ),
        "location": get_row_value(row, ["Location", "location"], None),
        "job_posting_url": get_row_value(
            row,
            [
                "Job Posting URL",
                "job_posting_url",
                "Job Posting",
                "job_posting",
            ],
            None,
        ),
        "expected_salary": get_row_value(
            row,
            [
                "Expected salary",
                "expected_salary",
                "Expected Salary",
                "Salary",
                "salary",
            ],
            None,
        ),
        "custom_message": get_row_value(
            row,
            [
                "Message",
                "message",
                "Custom Message",
                "custom_message",
            ],
            None,
        ),
    }
