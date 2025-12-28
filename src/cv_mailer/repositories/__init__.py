"""
Repository layer for data access.
"""

from cv_mailer.repositories.application_repository import ApplicationRepository
from cv_mailer.repositories.email_repository import EmailRepository
from cv_mailer.repositories.recruiter_repository import RecruiterRepository

__all__ = [
    "ApplicationRepository",
    "EmailRepository",
    "RecruiterRepository",
]

