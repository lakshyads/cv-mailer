"""
Date and time utility functions.
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import HTTPException

from cv_mailer.utils.exceptions import ValidationError


def format_date(dt: Optional[datetime]) -> str:
    """Format datetime for display."""
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_iso_datetime(date_string: str) -> datetime:
    """
    Parse ISO format datetime string and normalize to UTC.

    Args:
        date_string: ISO format datetime string (e.g., "2024-01-01T00:00:00Z")

    Returns:
        datetime object normalized to UTC

    Raises:
        ValidationError: If date string is invalid
    """
    try:
        # Replace Z with +00:00 for consistent parsing
        normalized = date_string.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)

        # Normalize to UTC if timezone-aware, otherwise assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

        return dt
    except (ValueError, AttributeError) as e:
        raise ValidationError(
            f"Invalid date format: {date_string}. Expected ISO format (e.g., '2024-01-01T00:00:00Z')"
        )


def parse_iso_datetime_optional(date_string: Optional[str]) -> Optional[datetime]:
    """
    Parse optional ISO format datetime string.

    Args:
        date_string: Optional ISO format datetime string

    Returns:
        datetime object normalized to UTC, or None if input is None
    """
    if date_string is None:
        return None
    return parse_iso_datetime(date_string)
