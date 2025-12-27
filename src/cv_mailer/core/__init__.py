"""
Core domain models and business entities.
"""

from cv_mailer.core.enums import JobStatus, EmailType, EmailStatus
from cv_mailer.core.models import (
    Base,
    JobApplication,
    EmailRecord,
    Recruiter,
    ResponseRecord,
    DailyEmailStats,
    job_application_recruiter,
)

__all__ = [
    "JobStatus",
    "EmailType",
    "EmailStatus",
    "Base",
    "JobApplication",
    "EmailRecord",
    "Recruiter",
    "ResponseRecord",
    "DailyEmailStats",
    "job_application_recruiter",
]
