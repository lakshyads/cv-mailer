"""
Email service for sending first contact and follow-up emails.
Provides a consistent interface for both CLI and API.
"""

import logging
from typing import Optional, Dict

from cv_mailer.integrations import GmailSender
from cv_mailer.services.template_service import EmailTemplate
from cv_mailer.services.tracker import ApplicationTracker
from cv_mailer.core import JobApplication, EmailType, EmailStatus, JobStatus
from cv_mailer.utils.exceptions import (
    NotFoundError,
    BusinessLogicError,
)
from cv_mailer.utils.logging_utils import log_function_call, log_execution_time

logger = logging.getLogger(__name__)


class EmailService:
    """Service for handling email operations."""

    def __init__(
        self,
        gmail_sender: Optional[GmailSender] = None,
        tracker: Optional[ApplicationTracker] = None,
    ):
        """
        Initialize email service.

        Args:
            gmail_sender: Gmail sender instance (creates new if None)
            tracker: Application tracker instance (creates new if None)
        """
        self.gmail_sender = gmail_sender or GmailSender()
        self.tracker = tracker or ApplicationTracker()

    @log_function_call(logger)
    def send_first_contact(
        self, application_id: int, recruiter_id: Optional[int] = None, dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Send first contact email for an application.

        Args:
            application_id: Job application ID
            recruiter_id: Optional specific recruiter ID (sends to all if None)
            dry_run: If True, don't actually send emails

        Returns:
            Dictionary with sent_count and failed_count

        Raises:
            NotFoundError: If application not found or no recruiters
            ExternalServiceError: If email sending fails
        """
        app = self.tracker.session.query(JobApplication).get(application_id)
        if not app:
            raise NotFoundError(f"Application {application_id} not found")

        if not app.recruiters:
            raise NotFoundError(f"No recruiters found for application {application_id}")

        logger.info(f"Sending first contact for application {application_id}")

        sent_count = 0
        failed_count = 0

        recruiters_to_email = app.recruiters
        if recruiter_id:
            recruiters_to_email = [r for r in app.recruiters if r.id == recruiter_id]
            if not recruiters_to_email:
                raise NotFoundError(
                    f"Recruiter {recruiter_id} not found for application {application_id}"
                )

        for recruiter in recruiters_to_email:
            # Check if already sent
            from cv_mailer.core import EmailRecord

            existing_email = (
                self.tracker.session.query(EmailRecord)
                .filter_by(
                    job_application_id=app.id,
                    recipient_email=recruiter.email,
                    email_type=EmailType.FIRST_CONTACT,
                    status=EmailStatus.SENT,
                )
                .first()
            )

            if existing_email:
                logger.debug(
                    f"Already sent first contact to {recruiter.email} for app {application_id}"
                )
                continue

            # Generate email
            subject, body = EmailTemplate.render_first_contact(
                recruiter_name=recruiter.name,
                company_name=app.company_name,
                position=app.position,
                location=app.location,
                job_posting_url=app.job_posting_url,
                custom_message=app.custom_message,
            )

            if dry_run:
                logger.debug(f"[DRY RUN] Would send first contact to {recruiter.email}")
                sent_count += 1
                continue

            # Send email
            message_id = self.gmail_sender.send_email(
                to=recruiter.email, subject=subject, body=body
            )

            if message_id:
                # Record email first (before status update)
                self.tracker.record_email_sent(
                    job_application_id=app.id,
                    email_type=EmailType.FIRST_CONTACT,
                    subject=subject,
                    body=body,
                    recipient_email=recruiter.email,
                    recipient_name=recruiter.name,
                    gmail_message_id=message_id,
                    is_follow_up=False,
                    follow_up_number=0,
                )
                sent_count += 1
                logger.info(
                    f"Email sent: first contact to {recruiter.email} for application {application_id}, "
                    f"message_id={message_id}"
                )
            else:
                self.tracker.record_email_failed(
                    job_application_id=app.id,
                    email_type=EmailType.FIRST_CONTACT,
                    subject=subject,
                    body=body,
                    recipient_email=recruiter.email,
                    recipient_name=recruiter.name,
                    error_message="Failed to send email",
                )
                failed_count += 1
                logger.error(f"✗ Failed to send first contact to {recruiter.email}")

        # Update status AFTER all emails are sent (not during the loop)
        if sent_count > 0 and app.status == JobStatus.APPLIED:
            self.tracker.update_job_status(app.id, JobStatus.REACHED_OUT, None)
            logger.info(
                f"Updated application {application_id} status to REACHED_OUT after sending {sent_count} email(s)"
            )

        return {"sent_count": sent_count, "failed_count": failed_count}

    @log_function_call(logger)
    def send_follow_up(
        self, application_id: int, recruiter_id: Optional[int] = None, dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Send follow-up email for an application.

        Args:
            application_id: Job application ID
            recruiter_id: Optional specific recruiter ID (sends to all if None)
            dry_run: If True, don't actually send emails

        Returns:
            Dictionary with sent_count and failed_count

        Raises:
            NotFoundError: If application not found or no recruiters
            BusinessLogicError: If timing check fails
            ExternalServiceError: If email sending fails
        """
        app = self.tracker.session.query(JobApplication).get(application_id)
        if not app:
            raise NotFoundError(f"Application {application_id} not found")

        if not app.recruiters:
            raise NotFoundError(f"No recruiters found for application {application_id}")

        # Check if follow-up is allowed (timing and status checks)
        can_send, reason = self.tracker.can_send_follow_up(application_id)
        if not can_send:
            raise BusinessLogicError(f"Cannot send follow-up: {reason}")

        logger.info(f"Sending follow-up for application {application_id}")

        sent_count = 0
        failed_count = 0

        recruiters_to_email = app.recruiters
        if recruiter_id:
            recruiters_to_email = [r for r in app.recruiters if r.id == recruiter_id]
            if not recruiters_to_email:
                raise NotFoundError(
                    f"Recruiter {recruiter_id} not found for application {application_id}"
                )

        # Get follow-up number ONCE for all recruiters (same wave)
        follow_up_number = self.tracker.get_next_follow_up_number(app.id)
        logger.info(f"Follow-up wave #{follow_up_number} for application {application_id}")

        for recruiter in recruiters_to_email:

            # Check if already sent this follow-up
            from cv_mailer.core import EmailRecord

            existing_follow_up = (
                self.tracker.session.query(EmailRecord)
                .filter_by(
                    job_application_id=app.id,
                    recipient_email=recruiter.email,
                    is_follow_up=True,
                    follow_up_number=follow_up_number,
                    status=EmailStatus.SENT,
                )
                .first()
            )

            if existing_follow_up:
                logger.debug(
                    f"Already sent follow-up #{follow_up_number} to {recruiter.email} "
                    f"for app {application_id}"
                )
                continue

            # Generate email
            subject, body = EmailTemplate.render_follow_up(
                recruiter_name=recruiter.name,
                company_name=app.company_name,
                position=app.position,
                location=app.location,
                follow_up_number=follow_up_number,
            )

            if dry_run:
                logger.debug(
                    f"[DRY RUN] Would send follow-up #{follow_up_number} to {recruiter.email}"
                )
                sent_count += 1
                continue

            # Send email
            message_id = self.gmail_sender.send_email(
                to=recruiter.email, subject=subject, body=body
            )

            if message_id:
                self.tracker.record_email_sent(
                    job_application_id=app.id,
                    email_type=EmailType.FOLLOW_UP,
                    subject=subject,
                    body=body,
                    recipient_email=recruiter.email,
                    recipient_name=recruiter.name,
                    gmail_message_id=message_id,
                    is_follow_up=True,
                    follow_up_number=follow_up_number,
                )
                sent_count += 1
                logger.info(
                    f"Email sent: follow-up #{follow_up_number} to {recruiter.email} "
                    f"for application {application_id}, message_id={message_id}"
                )
            else:
                self.tracker.record_email_failed(
                    job_application_id=app.id,
                    email_type=EmailType.FOLLOW_UP,
                    subject=subject,
                    body=body,
                    recipient_email=recruiter.email,
                    recipient_name=recruiter.name,
                    error_message="Failed to send email",
                )
                failed_count += 1
                logger.error(f"✗ Failed to send follow-up to {recruiter.email}")

        return {"sent_count": sent_count, "failed_count": failed_count}

    @log_function_call(logger)
    def get_emails_for_application(self, application_id: int):
        """Get all emails for an application."""
        from cv_mailer.core import EmailRecord

        return (
            self.tracker.session.query(EmailRecord)
            .filter_by(job_application_id=application_id)
            .order_by(EmailRecord.created_at.desc())
            .all()
        )

    @log_function_call(logger)
    def list_emails(self, status=None, limit=50, offset=0):
        """List emails with filtering."""
        from cv_mailer.core import EmailRecord

        query = self.tracker.session.query(EmailRecord)
        if status:
            query = query.filter_by(status=status)

        total = query.count()
        emails = query.order_by(EmailRecord.created_at.desc()).offset(offset).limit(limit).all()
        return emails, total
