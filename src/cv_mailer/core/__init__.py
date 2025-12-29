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
    StatusHistory,
    job_application_recruiter,
)
from cv_mailer.core.status_constants import (
    MAIN_FLOW_STATUSES,
    TERMINAL_STATUSES,
    STATUSES_THAT_CLOSE_APPLICATION,
    INTERVIEW_STAGE_STATUSES,
    OFFER_STAGE_STATUSES,
    REACHED_OUT_STATUSES,
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
    "StatusHistory",
    "job_application_recruiter",
    # Status constants
    "MAIN_FLOW_STATUSES",
    "TERMINAL_STATUSES",
    "STATUSES_THAT_CLOSE_APPLICATION",
    "INTERVIEW_STAGE_STATUSES",
    "OFFER_STAGE_STATUSES",
    "REACHED_OUT_STATUSES",
]
