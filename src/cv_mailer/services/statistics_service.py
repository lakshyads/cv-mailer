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
        # Also include offer_rejected since they definitely had interviews (got an offer)
        apps_in_interview_stages = sum(
            by_status.get(status.value, 0) for status in interview_stage_statuses
        ) + by_status.get(JobStatus.OFFER_REJECTED.value, 0)

        # Count rejected/ghosted/withdrawn applications that reached interviews (check status_history)
        terminal_with_interviews = (
            self.session.query(StatusHistory.job_application_id)
            .join(JobApplication, StatusHistory.job_application_id == JobApplication.id)
            .filter(
                JobApplication.status.in_(
                    [
                        JobStatus.REJECTED,
                        JobStatus.GHOSTED,
                        JobStatus.WITHDRAWN,
                        JobStatus.OFFER_REJECTED,
                    ]
                )
            )
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

        total_reached_interviews = apps_in_interview_stages + terminal_with_interviews

        # Applications that reached out (reached_out or beyond)
        # This counts all applications that have progressed beyond "applied" status
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
            JobStatus.OFFER_REJECTED,
        ]
        total_reached_out = sum(by_status.get(status.value, 0) for status in reached_out_statuses)

        # Total applications applied = all applications (since all are imported as "applied")
        total_applications_applied = total_apps

        # Applications currently at "applied" status
        applications_currently_applied = by_status.get(JobStatus.APPLIED.value, 0)

        # Applications currently at "reached_out" status
        applications_currently_reached_out = by_status.get(JobStatus.REACHED_OUT.value, 0)

        # Detailed breakdown of interview stages for tooltip
        # Count rejected/ghosted/withdrawn separately for breakdown
        rejected_after_interview = (
            self.session.query(StatusHistory.job_application_id)
            .join(JobApplication, StatusHistory.job_application_id == JobApplication.id)
            .filter(JobApplication.status == JobStatus.REJECTED)
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

        ghosted_after_interview = (
            self.session.query(StatusHistory.job_application_id)
            .join(JobApplication, StatusHistory.job_application_id == JobApplication.id)
            .filter(JobApplication.status == JobStatus.GHOSTED)
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

        withdrawn_after_interview = (
            self.session.query(StatusHistory.job_application_id)
            .join(JobApplication, StatusHistory.job_application_id == JobApplication.id)
            .filter(JobApplication.status == JobStatus.WITHDRAWN)
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

        interview_breakdown = {
            "interview_scheduled": by_status.get(JobStatus.INTERVIEW_SCHEDULED.value, 0),
            "interview_in_progress": by_status.get(JobStatus.INTERVIEW_IN_PROGRESS.value, 0),
            "result_awaited": by_status.get(JobStatus.RESULT_AWAITED.value, 0),
            "offer_received": by_status.get(JobStatus.OFFER_RECEIVED.value, 0),
            "accepted": by_status.get(JobStatus.ACCEPTED.value, 0),
            "offer_rejected": by_status.get(JobStatus.OFFER_REJECTED.value, 0),
            "rejected_after_interview": rejected_after_interview,
            "ghosted_after_interview": ghosted_after_interview,
            "withdrawn_after_interview": withdrawn_after_interview,
        }

        # Calculate applications that reached offer stage
        # This includes:
        # 1. Applications currently in offer_received or accepted
        # 2. Applications that are offer_rejected (they definitely got an offer)
        # 3. Applications that are rejected/ghosted/withdrawn BUT have history showing they reached offer_received
        offer_stage_statuses = [
            JobStatus.OFFER_RECEIVED,
            JobStatus.ACCEPTED,
        ]

        apps_in_offer_stages = sum(
            by_status.get(status.value, 0) for status in offer_stage_statuses
        ) + by_status.get(JobStatus.OFFER_REJECTED.value, 0)

        # Count terminal applications that reached offer_received (check status_history)
        terminal_with_offer = (
            self.session.query(StatusHistory.job_application_id)
            .join(JobApplication, StatusHistory.job_application_id == JobApplication.id)
            .filter(
                JobApplication.status.in_(
                    [
                        JobStatus.REJECTED,
                        JobStatus.GHOSTED,
                        JobStatus.WITHDRAWN,
                    ]
                )
            )
            .filter(StatusHistory.to_status == JobStatus.OFFER_RECEIVED)
            .distinct()
            .count()
        )

        total_reached_offers = apps_in_offer_stages + terminal_with_offer

        return {
            "total_applications": total_apps,
            "by_status": by_status,
            "total_emails_sent": total_emails,
            "follow_ups_sent": follow_ups,
            "applications_reached_interviews": total_reached_interviews,
            "applications_reached_out": total_reached_out,
            "applications_reached_offers": total_reached_offers,
            "total_applications_applied": total_applications_applied,
            "applications_currently_applied": applications_currently_applied,
            "applications_currently_reached_out": applications_currently_reached_out,
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
