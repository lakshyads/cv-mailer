"""
Email service for sending first contact and follow-up emails.
Provides a consistent interface for both CLI and API.
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone

from cv_mailer.integrations import GmailSender
from cv_mailer.services.template_service import EmailTemplate
from cv_mailer.services.tracker import ApplicationTracker
from cv_mailer.core import (
    JobApplication,
    EmailRecord,
    EmailType,
    EmailStatus,
    JobStatus,
)
from cv_mailer.utils.exceptions import (
    NotFoundError,
    BusinessLogicError,
)
from cv_mailer.utils.logging_utils import log_function_call
from cv_mailer.utils.email_utils import (
    extract_message_id_from_payload,
    format_message_id_for_header,
    build_references_chain,
    clean_subject_for_reply,
)

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
            result = self.gmail_sender.send_email(to=recruiter.email, subject=subject, body=body)

            if result and result.get("message_id"):
                message_id = result["message_id"]
                thread_id = result.get("thread_id")
                email_message_id = result.get("email_message_id")

                # Record email first (before status update)
                self.tracker.record_email_sent(
                    job_application_id=app.id,
                    email_type=EmailType.FIRST_CONTACT,
                    subject=subject,
                    body=body,
                    recipient_email=recruiter.email,
                    recipient_name=recruiter.name,
                    gmail_message_id=message_id,
                    email_message_id=email_message_id,
                    thread_id=thread_id,
                    is_follow_up=False,
                    follow_up_number=0,
                )
                sent_count += 1
                logger.info(
                    f"Email sent: first contact to {recruiter.email} for application {application_id}, "
                    f"message_id={message_id}, thread_id={thread_id}"
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
        self,
        application_id: int,
        recruiter_id: Optional[int] = None,
        recruiter_ids: Optional[List[int]] = None,
        dry_run: bool = False,
    ) -> Dict[str, int]:
        """
        Send follow-up email for an application.

        Args:
            application_id: Job application ID
            recruiter_id: Optional specific recruiter ID (deprecated, use recruiter_ids)
            recruiter_ids: Optional list of recruiter IDs (sends to all if None)
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

        # Check if follow-up is allowed (status check only - timing and max checks are per-recruiter)
        # We don't check max follow-ups here because different recruiters may have different counts
        can_send, reason = self.tracker.can_send_follow_up(
            application_id, check_max_follow_ups=False
        )
        if not can_send:
            raise BusinessLogicError(f"Cannot send follow-up: {reason}")

        logger.info(f"Sending follow-up for application {application_id}")

        sent_count = 0
        failed_count = 0

        # Determine which recruiters to email
        recruiters_to_email = app.recruiters
        if recruiter_ids:
            # Use recruiter_ids list (new preferred method)
            recruiters_to_email = [r for r in app.recruiters if r.id in recruiter_ids]
            if not recruiters_to_email:
                raise NotFoundError(
                    f"None of the specified recruiters found for application {application_id}"
                )
        elif recruiter_id:
            # Use single recruiter_id (backward compatibility)
            recruiters_to_email = [r for r in app.recruiters if r.id == recruiter_id]
            if not recruiters_to_email:
                raise NotFoundError(
                    f"Recruiter {recruiter_id} not found for application {application_id}"
                )

        # Pre-check all requested recruiters to see if any can receive follow-ups
        # If ALL have exhausted, return an error immediately
        recruiter_statuses = []
        for recruiter in recruiters_to_email:
            can_send_for_recruiter, reason = self.tracker.can_send_follow_up_for_recruiter(
                app.id, recruiter.email
            )
            recruiter_statuses.append(
                {
                    "recruiter": recruiter,
                    "can_send": can_send_for_recruiter,
                    "reason": reason,
                }
            )

        # Check if ALL recruiters have exhausted their follow-ups
        all_exhausted = all(not status["can_send"] for status in recruiter_statuses)
        if all_exhausted:
            # Collect all reasons for the error message
            reasons = [f"{s['recruiter'].email}: {s['reason']}" for s in recruiter_statuses]
            error_message = (
                f"Cannot send follow-up: All requested recruiters have exhausted their follow-ups. "
                f"Details: {'; '.join(reasons)}"
            )
            raise BusinessLogicError(error_message)

        # Filter to only recruiters who can receive follow-ups
        recruiters_to_email = [
            status["recruiter"] for status in recruiter_statuses if status["can_send"]
        ]

        # Log which recruiters are being skipped
        skipped_recruiters = [
            status["recruiter"] for status in recruiter_statuses if not status["can_send"]
        ]
        if skipped_recruiters:
            logger.info(
                f"Skipping {len(skipped_recruiters)} recruiter(s) who have exhausted follow-ups: "
                f"{[r.email for r in skipped_recruiters]}"
            )

        # Get follow-up number ONCE for all recruiters (same wave)
        # Calculate follow-up number per recruiter, not globally
        # This ensures each recruiter gets the correct sequential follow-up number
        logger.info(f"Calculating follow-up numbers per recruiter for application {application_id}")

        for recruiter in recruiters_to_email:

            # Calculate follow-up number for THIS specific recruiter
            # This ensures each recruiter gets sequential follow-up numbers (1, 2, 3...)
            # regardless of when other recruiters received their follow-ups
            follow_up_number = self.tracker.get_next_follow_up_number_for_recruiter(
                app.id, recruiter.email
            )
            logger.info(
                f"Follow-up #{follow_up_number} for recruiter {recruiter.email} "
                f"in application {application_id}"
            )

            # Check if already sent this follow-up
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

            # Get previous email in thread for this recruiter (for threading)
            previous_email = (
                self.tracker.session.query(EmailRecord)
                .filter_by(
                    job_application_id=app.id,
                    recipient_email=recruiter.email,
                    status=EmailStatus.SENT,
                )
                .order_by(EmailRecord.sent_at.desc())
                .first()
            )

            # Prepare threading parameters
            thread_id = None
            in_reply_to = None
            references = None
            original_subject = None

            if previous_email:
                thread_id = previous_email.thread_id
                original_subject = previous_email.subject

                # Get the ACTUAL Message-ID header that Gmail used
                # This is CRITICAL - must be the real Message-ID from Gmail, not a constructed one
                email_message_id = previous_email.email_message_id

                if not email_message_id:
                    # If missing, try to fetch it from Gmail (for old emails)
                    if previous_email.gmail_message_id:
                        try:
                            logger.info(
                                f"Fetching Message-ID for previous email "
                                f"{previous_email.gmail_message_id}"
                            )
                            full_message = (
                                self.gmail_sender.service.users()
                                .messages()
                                .get(
                                    userId="me",
                                    id=previous_email.gmail_message_id,
                                    format="full",
                                )
                                .execute()
                            )

                            email_message_id = extract_message_id_from_payload(
                                full_message.get("payload", {})
                            )

                            if email_message_id:
                                # Update database with the actual Message-ID
                                previous_email.email_message_id = email_message_id
                                self.tracker.session.commit()
                                logger.info(f"Retrieved and stored Message-ID: {email_message_id}")
                            else:
                                logger.error(
                                    f"Could not find Message-ID in Gmail message "
                                    f"{previous_email.gmail_message_id}. "
                                    f"Threading will fail!"
                                )
                        except Exception as e:
                            logger.error(
                                f"Error fetching Message-ID for previous email: {e}. "
                                f"Threading will fail!",
                                exc_info=True,
                            )

                if not email_message_id:
                    raise BusinessLogicError(
                        f"Cannot send follow-up: Missing Message-ID for previous email. "
                        f"Gmail message ID: {previous_email.gmail_message_id}"
                    )

                # Build References chain: ALL previous Message-IDs in the conversation
                # The References header should contain the full chain of Message-IDs
                # Format: <msg-id-1> <msg-id-2> <msg-id-3> ... <msg-id-n>
                references = build_references_chain(previous_email.references, email_message_id)

                # In-Reply-To should be the immediate parent's Message-ID
                in_reply_to = format_message_id_for_header(email_message_id)

                logger.info(
                    f"Threading follow-up to {recruiter.email}: "
                    f"thread_id={thread_id}, "
                    f"in_reply_to={in_reply_to}, "
                    f"references={references}, "
                    f"original_subject={original_subject}"
                )

            # Generate email
            subject, body = EmailTemplate.render_follow_up(
                recruiter_name=recruiter.name,
                company_name=app.company_name,
                position=app.position,
                location=app.location,
                follow_up_number=follow_up_number,
            )

            # Log body length for debugging
            logger.debug(
                f"Generated follow-up email body (length: {len(body)} chars) "
                f"for follow-up #{follow_up_number}"
            )

            # Ensure body is not empty
            if not body or len(body.strip()) == 0:
                logger.error(
                    f"Generated email body is empty for follow-up #{follow_up_number}! "
                    f"This will result in an empty email."
                )
                raise BusinessLogicError(f"Email body is empty for follow-up #{follow_up_number}")

            # Use "Re: " prefix with original subject for proper threading
            # Gmail threads based on subject line matching, so we need to match the original
            if original_subject:
                subject = clean_subject_for_reply(original_subject)
                logger.info(f"Using threaded subject: {subject}")

            if dry_run:
                logger.debug(
                    f"[DRY RUN] Would send follow-up #{follow_up_number} to {recruiter.email}"
                )
                sent_count += 1
                continue

            # Send email with threading
            result = self.gmail_sender.send_email(
                to=recruiter.email,
                subject=subject,
                body=body,
                thread_id=thread_id,
                in_reply_to=in_reply_to,
                references=references,
            )

            if result and result.get("message_id"):
                message_id = result["message_id"]
                # Use thread_id from response (Gmail may create new thread or use existing)
                response_thread_id = result.get("thread_id") or thread_id
                email_message_id = result.get("email_message_id")

                self.tracker.record_email_sent(
                    job_application_id=app.id,
                    email_type=EmailType.FOLLOW_UP,
                    subject=subject,
                    body=body,
                    recipient_email=recruiter.email,
                    recipient_name=recruiter.name,
                    gmail_message_id=message_id,
                    email_message_id=email_message_id,
                    thread_id=response_thread_id,
                    in_reply_to=in_reply_to,
                    references=references,
                    is_follow_up=True,
                    follow_up_number=follow_up_number,
                )
                sent_count += 1
                logger.info(
                    f"Email sent: follow-up #{follow_up_number} to {recruiter.email} "
                    f"for application {application_id}, message_id={message_id}, "
                    f"thread_id={response_thread_id}"
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

    @log_function_call(logger)
    def get_conversations_for_application(self, application_id: int) -> List[Dict[str, Any]]:
        """
        Get all email conversations for an application, grouped by recruiter.

        This method groups emails by recipient_email and builds conversation threads
        with proper metadata (thread_id, message_count, last_activity).

        Args:
            application_id: The job application ID

        Returns:
            List of conversation dictionaries with the following structure:
            {
                "thread_id": Optional[str],
                "recipient_email": str,
                "recipient_name": Optional[str],
                "recipient_id": Optional[int],
                "emails": List[EmailRecord],
                "message_count": int,
                "last_activity": Optional[datetime],
            }
        """
        # Get application to access recruiters
        app = self.tracker.session.query(JobApplication).get(application_id)
        if not app:
            raise NotFoundError(f"Application {application_id} not found")

        # Get all emails for this application
        emails = self.get_emails_for_application(application_id)

        # Group emails by recruiter (using recipient_email as key)
        conversations_by_recruiter = {}

        for email in emails:
            key = email.recipient_email
            if key not in conversations_by_recruiter:
                # Find recruiter ID and name if possible
                recruiter_id = None
                recruiter_name = email.recipient_name
                for recruiter in app.recruiters:
                    if recruiter.email == email.recipient_email:
                        recruiter_id = recruiter.id
                        recruiter_name = recruiter.name or recruiter_name
                        break

                conversations_by_recruiter[key] = {
                    "thread_id": email.thread_id,
                    "recipient_email": email.recipient_email,
                    "recipient_name": recruiter_name,
                    "recipient_id": recruiter_id,
                    "emails": [],
                }

            conversations_by_recruiter[key]["emails"].append(email)

        # Build conversation threads
        conversations = []
        for key, conv_data in conversations_by_recruiter.items():
            # Sort emails chronologically (oldest first for conversation flow)
            conv_data["emails"].sort(
                key=lambda e: e.sent_at or e.created_at or datetime.min.replace(tzinfo=timezone.utc)
            )

            # Get last activity
            last_activity = None
            if conv_data["emails"]:
                last_email = conv_data["emails"][-1]
                last_activity = last_email.sent_at or last_email.created_at

            # Use thread_id from first email if available
            thread_id = conv_data["thread_id"]
            if not thread_id and conv_data["emails"]:
                thread_id = conv_data["emails"][0].thread_id

            conversations.append(
                {
                    "thread_id": thread_id,
                    "recipient_email": conv_data["recipient_email"],
                    "recipient_name": conv_data["recipient_name"],
                    "recipient_id": conv_data["recipient_id"],
                    "emails": conv_data["emails"],
                    "message_count": len(conv_data["emails"]),
                    "last_activity": last_activity,
                }
            )

        # Sort conversations by last activity (most recent first)
        conversations.sort(
            key=lambda c: c["last_activity"] or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )

        return conversations

    @log_function_call(logger)
    def get_recruiter_conversation(self, application_id: int, recruiter_id: int) -> Dict[str, Any]:
        """
        Get conversation thread for a specific recruiter in an application.

        Args:
            application_id: The job application ID
            recruiter_id: The recruiter ID

        Returns:
            Conversation dictionary with the following structure:
            {
                "thread_id": Optional[str],
                "recipient_email": str,
                "recipient_name": Optional[str],
                "recipient_id": int,
                "emails": List[EmailRecord],
                "message_count": int,
                "last_activity": Optional[datetime],
            }

        Raises:
            NotFoundError: If application or recruiter not found
        """
        from cv_mailer.core import Recruiter

        # Get application
        app = self.tracker.session.query(JobApplication).get(application_id)
        if not app:
            raise NotFoundError(f"Application {application_id} not found")

        # Find recruiter
        recruiter = self.tracker.session.query(Recruiter).get(recruiter_id)
        if not recruiter:
            raise NotFoundError(f"Recruiter {recruiter_id} not found")

        # Verify recruiter belongs to this application
        if recruiter not in app.recruiters:
            raise NotFoundError(
                f"Recruiter {recruiter_id} not found in application {application_id}"
            )

        # Get all emails for this recruiter in this application
        emails = (
            self.tracker.session.query(EmailRecord)
            .filter_by(job_application_id=application_id, recipient_email=recruiter.email)
            .order_by(EmailRecord.sent_at.asc(), EmailRecord.created_at.asc())
            .all()
        )

        # Get thread_id from first email if available
        thread_id = None
        if emails:
            thread_id = emails[0].thread_id

        # Get last activity
        last_activity = None
        if emails:
            last_email = emails[-1]
            last_activity = last_email.sent_at or last_email.created_at

        return {
            "thread_id": thread_id,
            "recipient_email": recruiter.email,
            "recipient_name": recruiter.name,
            "recipient_id": recruiter.id,
            "emails": emails,
            "message_count": len(emails),
            "last_activity": last_activity,
        }
