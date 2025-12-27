"""
Date and time utility functions.
"""

from typing import Optional
from datetime import datetime


def format_date(dt: Optional[datetime]) -> str:
    """Format datetime for display."""
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")
