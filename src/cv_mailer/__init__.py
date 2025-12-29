"""
CV Mailer - Automated Resume Email System

A professional system for automating resume submissions with comprehensive tracking,
follow-up management, and multi-recruiter support.
"""

__version__ = "1.0.0"
__author__ = "Lakshya Dev Singh"

# Public API
from cv_mailer.core import (
    JobStatus,
    EmailType,
    EmailStatus,
    JobApplication,
    EmailRecord,
    Recruiter,
)
from cv_mailer.config import Config
from cv_mailer.services import ApplicationTracker, EmailTemplate
from cv_mailer.integrations import GmailSender, GoogleSheetsClient
from cv_mailer.utils import init_database, get_session

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Core
    "JobStatus",
    "EmailType",
    "EmailStatus",
    "JobApplication",
    "EmailRecord",
    "Recruiter",
    # Config
    "Config",
    # Services
    "ApplicationTracker",
    "EmailTemplate",
    # Integrations
    "GmailSender",
    "GoogleSheetsClient",
    # Utils
    "init_database",
    "get_session",
]
