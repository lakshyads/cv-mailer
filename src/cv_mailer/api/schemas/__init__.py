"""
Pydantic schemas for API request/response validation.
"""

from cv_mailer.api.schemas.application import (
    ApplicationResponse,
    ApplicationListResponse,
    ApplicationDetailResponse,
    UpdateStatusRequest,
    EmailActionResponse,
)
from cv_mailer.api.schemas.email import EmailResponse, EmailDetailResponse
from cv_mailer.api.schemas.recruiter import RecruiterResponse, RecruiterDetailResponse
from cv_mailer.api.schemas.common import PaginatedResponse, TimelineEvent

__all__ = [
    # Application
    "ApplicationResponse",
    "ApplicationListResponse",
    "ApplicationDetailResponse",
    "UpdateStatusRequest",
    "EmailActionResponse",
    # Email
    "EmailResponse",
    "EmailDetailResponse",
    # Recruiter
    "RecruiterResponse",
    "RecruiterDetailResponse",
    # Common
    "PaginatedResponse",
    "TimelineEvent",
]

