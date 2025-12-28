"""
Statistics Service - Centralized business logic for statistics and analytics.

This is the SINGLE source of truth for statistics operations.
Both CLI and API use this service.
"""

import logging
from typing import Dict

from cv_mailer.core import JobApplication, EmailRecord, JobStatus, EmailStatus, StatusHistory
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

        # Calculate applications that reached interview stages
        # This includes:
        # 1. Applications currently in interview stages (interview_scheduled, interview_in_progress, result_awaited)
        # 2. Applications that reached offer_received or accepted (they definitely had interviews)
        # 3. Applications that are rejected/ghosted BUT have history showing they reached interview_scheduled or beyond
        interview_stage_statuses = [
            JobStatus.INTERVIEW_SCHEDULED,
            JobStatus.INTERVIEW_IN_PROGRESS,
            JobStatus.RESULT_AWAITED,
            JobStatus.OFFER_RECEIVED,
            JobStatus.ACCEPTED,
        ]

        # Count applications currently in interview stages or beyond
        apps_in_interview_stages = sum(
            by_status.get(status.value, 0) for status in interview_stage_statuses
        )

        # Count rejected/ghosted applications that reached interviews (check status_history)
        rejected_ghosted_with_interviews = (
            self.session.query(StatusHistory.job_application_id)
            .join(JobApplication, StatusHistory.job_application_id == JobApplication.id)
            .filter(JobApplication.status.in_([JobStatus.REJECTED, JobStatus.GHOSTED]))
            .filter(
                StatusHistory.to_status.in_(
                    [
                        JobStatus.INTERVIEW_SCHEDULED,
                        JobStatus.INTERVIEW_IN_PROGRESS,
                        JobStatus.RESULT_AWAITED,
                        JobStatus.OFFER_RECEIVED,
                    ]
                )
            )
            .distinct()
            .count()
        )

        total_reached_interviews = apps_in_interview_stages + rejected_ghosted_with_interviews

        # Applications that reached out (reached_out or beyond)
        reached_out_statuses = [
            JobStatus.REACHED_OUT,
            JobStatus.INTERVIEW_SCHEDULED,
            JobStatus.INTERVIEW_IN_PROGRESS,
            JobStatus.RESULT_AWAITED,
            JobStatus.OFFER_RECEIVED,
            JobStatus.ACCEPTED,
            JobStatus.REJECTED,
            JobStatus.GHOSTED,
            JobStatus.WITHDRAWN,
        ]
        total_reached_out = sum(by_status.get(status.value, 0) for status in reached_out_statuses)

        # Detailed breakdown of interview stages for tooltip
        interview_breakdown = {
            "interview_scheduled": by_status.get(JobStatus.INTERVIEW_SCHEDULED.value, 0),
            "interview_in_progress": by_status.get(JobStatus.INTERVIEW_IN_PROGRESS.value, 0),
            "result_awaited": by_status.get(JobStatus.RESULT_AWAITED.value, 0),
            "offer_received": by_status.get(JobStatus.OFFER_RECEIVED.value, 0),
            "accepted": by_status.get(JobStatus.ACCEPTED.value, 0),
            "rejected_after_interview": rejected_ghosted_with_interviews,
        }

        return {
            "total_applications": total_apps,
            "by_status": by_status,
            "total_emails_sent": total_emails,
            "follow_ups_sent": follow_ups,
            "applications_reached_interviews": total_reached_interviews,
            "applications_reached_out": total_reached_out,
            "interview_breakdown": interview_breakdown,
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
        if hasattr(self, "_owns_session") and self._owns_session:
            self.session.close()
