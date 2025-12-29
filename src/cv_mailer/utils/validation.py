"""
Input validation utilities for consistent validation across the application.
"""

from typing import Optional, List
from cv_mailer.utils.exceptions import ValidationError


def validate_positive_integer(value: int, field_name: str = "value") -> None:
    """
    Validate that an integer is positive.

    Args:
        value: Integer value to validate
        field_name: Name of the field for error messages

    Raises:
        ValidationError: If value is not positive
    """
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive integer, got: {value}")


def validate_non_negative_integer(value: int, field_name: str = "value") -> None:
    """
    Validate that an integer is non-negative.

    Args:
        value: Integer value to validate
        field_name: Name of the field for error messages

    Raises:
        ValidationError: If value is negative
    """
    if not isinstance(value, int) or value < 0:
        raise ValidationError(f"{field_name} must be a non-negative integer, got: {value}")


def validate_string_not_empty(value: Optional[str], field_name: str = "value") -> None:
    """
    Validate that a string is not empty.

    Args:
        value: String value to validate
        field_name: Name of the field for error messages

    Raises:
        ValidationError: If value is None or empty
    """
    if not value or not value.strip():
        raise ValidationError(f"{field_name} cannot be empty")


def validate_limit_offset(limit: int, offset: int) -> None:
    """
    Validate pagination parameters.

    Args:
        limit: Maximum number of results
        offset: Number of results to skip

    Raises:
        ValidationError: If parameters are invalid
    """
    validate_positive_integer(limit, "limit")
    validate_non_negative_integer(offset, "offset")


def validate_application_id(application_id: int) -> None:
    """
    Validate application ID.

    Args:
        application_id: Application ID to validate

    Raises:
        ValidationError: If ID is invalid
    """
    validate_positive_integer(application_id, "application_id")
