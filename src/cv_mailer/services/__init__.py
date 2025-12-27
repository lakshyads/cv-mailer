"""
Business logic services.
"""

from cv_mailer.services.tracker import ApplicationTracker
from cv_mailer.services.template_service import EmailTemplateService, EmailTemplate

__all__ = [
    "ApplicationTracker",
    "EmailTemplateService",
    "EmailTemplate",  # Backward compatibility alias
]
