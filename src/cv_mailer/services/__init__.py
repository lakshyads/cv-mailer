"""
Service layer - Single source of truth for all business logic.

Both CLI and API use these services. No business logic should exist outside this layer.
"""

from cv_mailer.services.application_service import ApplicationService
from cv_mailer.services.email_service import EmailService
from cv_mailer.services.recruiter_service import RecruiterService
from cv_mailer.services.statistics_service import StatisticsService
from cv_mailer.services.template_service import EmailTemplate, EmailTemplateService
from cv_mailer.services.tracker import ApplicationTracker

__all__ = [
    "ApplicationService",
    "EmailService",
    "RecruiterService",
    "StatisticsService",
    "EmailTemplate",
    "EmailTemplateService",
    "ApplicationTracker",  # Legacy, being phased out
]
