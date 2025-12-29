"""
Custom SQLAlchemy types for handling UTC datetimes with SQLite.

SQLite doesn't preserve timezone information, so we need to ensure
all datetimes are stored and retrieved as UTC.
"""

from datetime import datetime, timezone
from sqlalchemy import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator):
    """
    Custom DateTime type that ensures all datetimes are stored and retrieved
    as UTC.

    SQLite doesn't preserve timezone information, so:
    - When storing: Converts timezone-aware datetimes to UTC, then to naive
    - When reading: Assumes naive datetimes are UTC and makes them
      timezone-aware
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert datetime to UTC before storing."""
        if value is None:
            return None
        if isinstance(value, datetime):
            # If timezone-aware, convert to UTC
            if value.tzinfo is not None:
                value = value.astimezone(timezone.utc)
            # Convert to naive UTC datetime for SQLite storage
            # SQLite will store as ISO format string
            return value.replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        """Convert naive datetime from DB to UTC-aware datetime."""
        if value is None:
            return None
        if isinstance(value, datetime):
            # SQLite returns naive datetimes - assume they are UTC
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            # If somehow timezone-aware, convert to UTC
            return value.astimezone(timezone.utc)
        return value
