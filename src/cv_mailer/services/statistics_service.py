"""
Statistics Service - Centralized business logic for statistics and analytics.

This is the SINGLE source of truth for statistics operations.
Both CLI and API use this service.
"""

import logging
from typing import Dict

from cv_mailer.core import JobApplication, EmailRecord, JobStatus, EmailStatus
from cv_mailer.utils import get_session

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for statistics and analytics."""

    def __init__(self, session=None):
        """
        Initialize statistics service.
        
        Args:
            session: Database session (creates new if None)
        """
        self.session = session or get_session()
        self._owns_session = session is None

    def get_statistics(self) -> Dict:
        """
        Get comprehensive application statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_apps = self.session.query(JobApplication).count()
        
        # Count by status
        by_status = {}
        for status in JobStatus:
            count = self.session.query(JobApplication).filter_by(status=status).count()
            by_status[status.value] = count
        
        # Email statistics
        total_emails = self.session.query(EmailRecord).filter_by(status=EmailStatus.SENT).count()
        follow_ups = (
            self.session.query(EmailRecord)
            .filter_by(is_follow_up=True, status=EmailStatus.SENT)
            .count()
        )
        
        return {
            "total_applications": total_apps,
            "by_status": by_status,
            "total_emails_sent": total_emails,
            "follow_ups_sent": follow_ups,
        }

    def get_summary(self) -> Dict:
        """
        Get summary statistics.
        
        Returns:
            Dictionary with summary stats
        """
        stats = self.get_statistics()
        
        return {
            "total_applications": stats["total_applications"],
            "total_emails_sent": stats["total_emails_sent"],
            "follow_ups_sent": stats["follow_ups_sent"],
            "by_status": stats["by_status"],
        }

    def __del__(self):
        """Cleanup session if owned."""
        if hasattr(self, '_owns_session') and self._owns_session:
            self.session.close()

