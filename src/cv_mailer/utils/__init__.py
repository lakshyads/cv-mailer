"""
Utility functions and helpers.
"""

from cv_mailer.utils.database import (
    get_engine,
    get_session,
    init_database,
    checkpoint_wal,
    close_database,
)
from cv_mailer.utils.date import format_date, parse_iso_datetime, parse_iso_datetime_optional
from cv_mailer.utils.exceptions import (
    CVMailerException,
    NotFoundError,
    ValidationError,
    BusinessLogicError,
    ExternalServiceError,
    format_error_response,
)
from cv_mailer.utils.query_builder import QueryBuilder
from cv_mailer.utils.validators import validate_email
from cv_mailer.utils.logging_utils import (
    log_function_call,
    log_execution_time,
    setup_logging,
)
from cv_mailer.utils.sheet_parser import get_row_value, extract_application_data
from cv_mailer.utils.transaction import transaction, safe_commit
from cv_mailer.utils.validation import (
    validate_positive_integer,
    validate_non_negative_integer,
    validate_string_not_empty,
    validate_limit_offset,
    validate_application_id,
)

__all__ = [
    # Database
    "get_engine",
    "get_session",
    "init_database",
    "checkpoint_wal",
    "close_database",
    # Date utilities
    "format_date",
    "parse_iso_datetime",
    "parse_iso_datetime_optional",
    # Exceptions
    "CVMailerException",
    "NotFoundError",
    "ValidationError",
    "BusinessLogicError",
    "ExternalServiceError",
    "format_error_response",
    # Query builder
    "QueryBuilder",
    # Validators
    "validate_email",
    # Logging
    "log_function_call",
    "log_execution_time",
    "setup_logging",
    # Sheet parsing
    "get_row_value",
    "extract_application_data",
    # Transaction management
    "transaction",
    "safe_commit",
    # Validation
    "validate_positive_integer",
    "validate_non_negative_integer",
    "validate_string_not_empty",
    "validate_limit_offset",
    "validate_application_id",
]
