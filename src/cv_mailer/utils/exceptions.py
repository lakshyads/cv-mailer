"""
Centralized exception classes and error handling utilities.

This module provides custom exceptions and utilities for consistent
error handling across the application.
"""

from typing import Optional, Dict, Any


class CVMailerException(Exception):
    """Base exception for CV Mailer application."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(CVMailerException):
    """Raised when a resource is not found."""

    pass


class ValidationError(CVMailerException):
    """Raised when validation fails."""

    pass


class BusinessLogicError(CVMailerException):
    """Raised when business logic rules are violated."""

    pass


class ExternalServiceError(CVMailerException):
    """Raised when external service calls fail."""

    pass


def format_error_response(
    error: Exception, status_code: int = 500, include_details: bool = False
) -> Dict[str, Any]:
    """
    Format error response for API.

    Args:
        error: Exception instance
        status_code: HTTP status code
        include_details: Whether to include detailed error information

    Returns:
        Formatted error response dictionary
    """
    response = {
        "error": error.__class__.__name__,
        "message": str(error),
    }

    if include_details and isinstance(error, CVMailerException) and error.details:
        response["details"] = error.details

    return response
