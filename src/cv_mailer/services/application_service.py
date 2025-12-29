"""
Application Service - Centralized business logic for job applications.

This is the SINGLE source of truth for application-related operations.
Both CLI and API use this service.
"""

import logging
from typing import List, Optional, Tuple, Literal
from datetime import datetime, timezone

from cv_mailer.core import JobApplication, JobStatus, StatusHistory
from cv_mailer.core.status_constants import (
    MAIN_FLOW_STATUSES,
    TERMINAL_STATUSES,
    STATUSES_THAT_CLOSE_APPLICATION,
)
from cv_mailer.repositories import ApplicationRepository
from cv_mailer.utils import (
    get_session,
    NotFoundError,
    BusinessLogicError,
)
from cv_mailer.utils.logging_utils import log_function_call, log_execution_time

logger = logging.getLogger(__name__)


class ApplicationService:
    """Service for job application business logic."""

    def __init__(self, repository: Optional[ApplicationRepository] = None):
        """
        Initialize application service.

        Args:
            repository: Application repository (creates new if None)
        """
        if repository:
            self.repository = repository
        else:
            session = get_session()
            self.repository = ApplicationRepository(session)
            self._owns_session = True

    @log_function_call(logger)
    def get_application(self, application_id: int) -> Optional[JobApplication]:
        """
        Get application by ID.

        Args:
            application_id: Application ID

        Returns:
            JobApplication or None

        Raises:
            NotFoundError: If application not found
        """
        app = self.repository.find_by_id(application_id)
        if not app:
            raise NotFoundError(f"Application {application_id} not found")
        return app

    @log_function_call(logger)
    @log_execution_time(logger)
    def list_applications(
        self,
        status: Optional[JobStatus] = None,
        statuses: Optional[List[JobStatus]] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: Optional[Literal["created_at", "updated_at", "status"]] = None,
        order: Optional[Literal["asc", "desc"]] = None,
    ) -> Tuple[List[JobApplication], int]:
        """
        List applications with filtering, searching, pagination, and sorting.

        Args:
            status: Optional single status filter (for backward compatibility)
            statuses: Optional list of statuses to filter by
            search: Optional search term for company name or position
            date_from: Optional start date for filtering by updated_at
            date_to: Optional end date for filtering by updated_at
            limit: Maximum results
            offset: Pagination offset
            sort_by: Field to sort by (created_at, updated_at, status)
            order: Sort order (asc, desc)

        Returns:
            Tuple of (applications, total_count)
        """
        return self.repository.find_all(
            status=status,
            statuses=statuses,
            search_term=search,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order,
        )

    @log_function_call(logger)
    def search_applications(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0,
        sort_by: Optional[Literal["created_at", "updated_at", "status"]] = None,
        order: Optional[Literal["asc", "desc"]] = None,
    ) -> Tuple[List[JobApplication], int]:
        """
        Search applications by company name or position with optional sorting.

        Args:
            query: Search term
            limit: Maximum results
            offset: Pagination offset
            sort_by: Field to sort by (created_at, updated_at, status)
            order: Sort order (asc, desc)

        Returns:
            Tuple of (applications, total_count)
        """
        return self.repository.search(
            search_term=query, limit=limit, offset=offset, sort_by=sort_by, order=order
        )

    @log_function_call(logger)
    def update_status(
        self,
        application_id: int,
        status: JobStatus,
        notes: Optional[str] = None,
    ) -> JobApplication:
        """
        Update application status with validation.

        Args:
            application_id: Application ID
            status: New status
            notes: Optional notes

        Returns:
            Updated application

        Raises:
            NotFoundError: If application not found
            BusinessLogicError: If transition is invalid
        """
        app = self.get_application(application_id)
        # get_application already raises NotFoundError if not found

        # Refresh to ensure we have latest status from database
        self.repository.session.refresh(app)

        # Validate status transition (one-directional flow)
        from cv_mailer.services.status_validator import StatusValidator
        from cv_mailer.core import StatusHistory

        logger.info(f"Validating status transition: {app.status.value} -> {status.value}")
        try:
            StatusValidator.validate_transition(app.status, status)
            logger.info("Status transition validated successfully")
        except BusinessLogicError:
            # Re-raise BusinessLogicError from StatusValidator
            raise

        # Record status change in history before updating
        from_status = app.status
        status_history = StatusHistory(
            job_application_id=application_id,
            from_status=from_status,
            to_status=status,
            notes=notes,
            changed_at=datetime.now(timezone.utc),
        )
        self.repository.session.add(status_history)

        app.status = status
        app.updated_at = datetime.now(timezone.utc)

        if notes:
            app.notes = notes

        # Set closed_at for terminal states
        if status in STATUSES_THAT_CLOSE_APPLICATION:
            app.closed_at = datetime.now(timezone.utc)
        elif app.closed_at:
            # Reopen if moving from terminal to non-terminal
            app.closed_at = None

        self.repository.session.commit()
        logger.info(f"Updated application {application_id} status to {status.value}")

        return app

    def get_last_main_flow_status(self, application_id: int) -> Optional[JobStatus]:
        """
        Get the last main flow status before terminal state.

        For terminal states (rejected, ghosted, withdrawn), this returns
        the highest main flow status that was reached before the terminal state.

        Args:
            application_id: Application ID

        Returns:
            Last main flow status, or None if not found
        """

        # Get all status changes for this application
        status_changes = (
            self.repository.session.query(StatusHistory)
            .filter_by(job_application_id=application_id)
            .order_by(StatusHistory.changed_at.asc())
            .all()
        )

        # Find the last main flow status before terminal state
        last_main_flow: Optional[JobStatus] = None
        for status_change in status_changes:
            if status_change.to_status in MAIN_FLOW_STATUSES:
                last_main_flow = status_change.to_status
            elif status_change.to_status in TERMINAL_STATUSES:
                # Found terminal state, return the last main flow status
                return last_main_flow

        # If no terminal state found in history, check current status
        app = self.get_application(application_id)
        if app.status in TERMINAL_STATUSES:
            return last_main_flow

        # If current status is in main flow, return it
        if app.status in MAIN_FLOW_STATUSES:
            return app.status

        return None

    @log_function_call(logger)
    @log_execution_time(logger)
    def get_application_timeline(self, application_id: int) -> List[dict]:
        """
        Get timeline of events for an application.

        Args:
            application_id: Application ID

        Returns:
            List of timeline events

        Raises:
            NotFoundError: If application not found
        """
        app = self.get_application(application_id)

        # Refresh app to get latest updated_at from database
        self.repository.session.refresh(app)

        events = []

        # Application created event (oldest)
        if app.created_at:
            events.append(
                {
                    "id": f"created_{app.id}",
                    "type": "status_change",
                    "title": "Application Submitted",
                    "description": f"Application for {app.position} at {app.company_name} was submitted",
                    "timestamp": app.created_at.isoformat(),
                    "metadata": {"status": "applied"},
                }
            )

        # Email events - sort by sent_at (or created_at if sent_at is None)
        from cv_mailer.core import EmailType

        # Separate first contacts and follow-ups
        first_contacts = []
        follow_ups = []

        for email in app.emails:
            email_time = email.sent_at or email.created_at
            if not email_time:
                continue

            if email.email_type == EmailType.FIRST_CONTACT:
                first_contacts.append((email_time, email))
            elif email.email_type == EmailType.FOLLOW_UP:
                follow_ups.append((email_time, email))

        # Sort by time (oldest first)
        first_contacts.sort(key=lambda x: x[0])
        follow_ups.sort(key=lambda x: x[0])

        # Add first contact emails
        for email_time, email in first_contacts:
            events.append(
                {
                    "id": f"email_{email.id}",
                    "type": "first_contact",
                    "title": "First Contact Sent",
                    "description": f"Email sent to {email.recipient_name or email.recipient_email}",
                    "timestamp": email_time.isoformat(),
                    "metadata": {
                        "email_id": email.id,
                        "recipient_email": email.recipient_email,
                        "recipient_name": email.recipient_name,
                    },
                }
            )

        # Add follow-up emails
        for email_time, email in follow_ups:
            events.append(
                {
                    "id": f"email_{email.id}",
                    "type": "follow_up",
                    "title": f"Follow-up #{email.follow_up_number} Sent",
                    "description": f"Follow-up email sent to {email.recipient_name or email.recipient_email}",
                    "timestamp": email_time.isoformat(),
                    "metadata": {
                        "email_id": email.id,
                        "recipient_email": email.recipient_email,
                        "recipient_name": email.recipient_name,
                        "follow_up_number": email.follow_up_number,
                    },
                }
            )

        # Add all status changes from history (sorted by time)
        from cv_mailer.core import StatusHistory

        status_changes = (
            self.repository.session.query(StatusHistory)
            .filter_by(job_application_id=application_id)
            .order_by(StatusHistory.changed_at.asc())
            .all()
        )

        for status_change in status_changes:
            status_timestamp_str = (
                status_change.changed_at.isoformat().replace(":", "-").replace(".", "-")
            )
            events.append(
                {
                    "id": f"status_{status_change.to_status.value}_{app.id}_{status_timestamp_str}",
                    "type": "status_change",
                    "title": f"Status: {status_change.to_status.value.replace('_', ' ').title()}",
                    "description": f"Application status updated to {status_change.to_status.value.replace('_', ' ').title()}",
                    "timestamp": status_change.changed_at.isoformat(),
                    "metadata": {
                        "status": status_change.to_status.value,
                        "from_status": (
                            status_change.from_status.value if status_change.from_status else None
                        ),
                        "notes": status_change.notes,
                    },
                }
            )

        # Closed event
        if app.closed_at:
            events.append(
                {
                    "id": f"closed_{app.id}",
                    "type": "status_change",
                    "title": "Application Closed",
                    "description": "Application was closed",
                    "timestamp": app.closed_at.isoformat(),
                    "metadata": {"status": app.status.value},
                }
            )

        # Sort by timestamp (most recent first)
        # Timestamps are ISO format strings, which sort correctly lexicographically
        events.sort(key=lambda e: e["timestamp"] or "", reverse=True)

        return events

    def get_emails_count(self, application_id: int) -> int:
        """
        Get count of emails sent for an application.

        Args:
            application_id: Application ID

        Returns:
            Email count
        """
        return self.repository.get_emails_count(application_id)

    def __del__(self):
        """Cleanup session if owned."""
        if hasattr(self, "_owns_session") and self._owns_session:
            self.repository.session.close()
