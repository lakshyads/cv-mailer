"""
Service for syncing job applications from Google Sheets.
This service contains the core business logic used by both CLI and API.
"""

import logging
from typing import Dict, Any

from cv_mailer.config import Config
from cv_mailer.integrations import GoogleSheetsClient
from cv_mailer.services.tracker import ApplicationTracker
from cv_mailer.services.email_service import EmailService
from cv_mailer.core import JobApplication, EmailRecord, EmailStatus, EmailType
from cv_mailer.parsers import RecruiterParser
from cv_mailer.utils.sheet_parser import extract_application_data
from cv_mailer.utils.logging_utils import log_function_call, log_execution_time

logger = logging.getLogger(__name__)


class SyncService:
    """Service for syncing applications from Google Sheets."""

    def __init__(self):
        """Initialize the sync service."""
        self.sheets_client = GoogleSheetsClient(Config.SPREADSHEET_ID, Config.WORKSHEET_NAME)
        self.tracker = ApplicationTracker()
        from cv_mailer.integrations import GmailSender

        self.email_service = EmailService(gmail_sender=GmailSender(), tracker=self.tracker)

    @log_function_call(logger)
    @log_execution_time(logger)
    def sync_applications(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Sync job applications from Google Sheets.

        When dry_run=False (Sync Applications & Reach Out):
        - Reads data from Google Sheets
        - Creates or updates job applications in the database
        - Sends first contact emails to recruiters

        When dry_run=True (Sync Applications):
        - Reads data from Google Sheets
        - Creates or updates job applications in the database
        - Does NOT send emails (dry run mode)

        This is the core business logic extracted from CLI for reuse by both
        CLI and API.

        Args:
            dry_run: If True, only sync applications without sending emails.
                     If False, sync and send first contact emails.

        Returns:
            Dictionary with sync results (sent_count, skipped_count,
            total_rows, message, errors)
        """
        try:
            # Read data from Google Sheets
            if Config.PROCESS_ALL_SHEETS:
                rows = self.sheets_client.read_all_sheets(sheet_filter=Config.SHEET_NAME_FILTER)
                filter_str = Config.SHEET_NAME_FILTER or "none"
                logger.info(f"Processing all sheets (filter: {filter_str})")
            else:
                sheet_name = Config.WORKSHEET_NAME
                rows = self.sheets_client.read_all_rows(worksheet_name=sheet_name)
                logger.info(f"Processing single sheet: {sheet_name}")

            if not rows:
                logger.warning("No data found in Google Sheets")
                return {
                    "sent_count": 0,
                    "skipped_count": 0,
                    "total_rows": 0,
                    "message": "No data found in Google Sheets",
                }

            logger.info(f"Found {len(rows)} total rows across all sheets")

            sent_count = 0
            skipped_count = 0
            errors = []

            for row in rows:
                try:
                    # Extract data from sheet using utility function
                    row_data = extract_application_data(row)
                    company_name = row_data["company_name"]
                    position = row_data["position"]
                    recruiter_cell = row_data["recruiter_cell"]
                    location = row_data["location"]
                    job_posting_url = row_data["job_posting_url"]
                    expected_salary = row_data["expected_salary"]
                    custom_message = row_data["custom_message"]

                    recruiters = RecruiterParser.parse_recruiters(recruiter_cell)

                    # Create application using tracker
                    sheet_name = row.get("_sheet_name", Config.WORKSHEET_NAME)
                    row_id = row.get("_row_number", 0)
                    unique_row_id = f"{sheet_name}_{row_id}"

                    # Skip if required fields missing
                    if not company_name or not position or not recruiters:
                        logger.warning(f"Skipping {sheet_name}:row {row_id}: " f"missing fields")
                        skipped_count += 1
                        continue

                    # Check if application already exists and has sent emails
                    existing_app = (
                        self.tracker.session.query(JobApplication)
                        .filter_by(spreadsheet_row_id=unique_row_id)
                        .first()
                    )

                    if existing_app:
                        # Check if emails have already been sent
                        sent_emails = (
                            self.tracker.session.query(EmailRecord)
                            .filter_by(
                                job_application_id=existing_app.id,
                                email_type=EmailType.FIRST_CONTACT,
                                status=EmailStatus.SENT,
                            )
                            .count()
                        )

                        if sent_emails > 0:
                            logger.info(
                                f"Skipping {sheet_name}:row {row_id}: "
                                f"application already processed "
                                f"({sent_emails} email(s) already sent)"
                            )
                            skipped_count += 1
                            continue

                        # Application exists but no emails sent - use existing
                        job_app = existing_app
                    else:
                        # Create new application
                        job_app = self.tracker.get_or_create_job_application(
                            spreadsheet_row_id=unique_row_id,
                            company_name=company_name,
                            position=position,
                            recruiters=recruiters,
                            location=location,
                            job_posting_url=job_posting_url,
                            expected_salary=expected_salary,
                            custom_message=custom_message,
                            sheet_name=sheet_name,
                        )

                    # Send emails using service
                    if dry_run:
                        logger.info(
                            f"DRY RUN: Would send to {len(recruiters)} "
                            f"recruiter(s) for {company_name} "
                            f"({sheet_name}:row {row_id})"
                        )
                        sent_count += len(recruiters)
                    else:
                        try:
                            result = self.email_service.send_first_contact(
                                job_app.id, dry_run=False
                            )
                            emails_sent = result["sent_count"]
                            if emails_sent > 0:
                                sent_count += emails_sent
                                logger.info(
                                    f"Sent {emails_sent} email(s) - "
                                    f"{position} - {company_name} "
                                    f"({sheet_name}:row {row_id})"
                                )

                                # Update sheet status
                                try:
                                    sheet_name_for_update, row_num_str = unique_row_id.rsplit(
                                        "_", 1
                                    )
                                    row_num = int(row_num_str)
                                    status_col = self.sheets_client.get_column_letter(
                                        "Status", worksheet_name=(sheet_name_for_update)
                                    )
                                    if status_col:
                                        self.sheets_client.update_cell(
                                            row_num,
                                            status_col,
                                            "Reached Out",
                                            worksheet_name=(sheet_name_for_update),
                                        )
                                except Exception as e:
                                    logger.warning(f"Could not update spreadsheet: {e}")
                            else:
                                skipped_count += 1
                        except ValueError as e:
                            logger.warning(
                                f"Skipping {company_name} " f"({sheet_name}:row {row_id}): {e}"
                            )
                            errors.append(f"{company_name}: {str(e)}")
                            skipped_count += 1

                except Exception as e:
                    logger.error(f"Error processing {sheet_name}:row {row_id}: {e}", exc_info=True)
                    errors.append(f"{sheet_name}:row {row_id}: {str(e)}")
                    skipped_count += 1

            message = f"Sync completed: {sent_count} sent, " f"{skipped_count} skipped"
            if errors:
                message += f", {len(errors)} errors"

            return {
                "sent_count": sent_count,
                "skipped_count": skipped_count,
                "total_rows": len(rows),
                "errors": errors[:10],  # Limit to first 10 errors
                "message": message,
            }

        except Exception as e:
            logger.error(f"Error syncing applications: {e}", exc_info=True)
            raise

    @log_function_call(logger)
    @log_execution_time(logger)
    def send_follow_ups(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Send follow-up emails for applications that need them.

        This is the core business logic extracted from CLI for reuse by both
        CLI and API.

        Args:
            dry_run: If True, don't actually send emails

        Returns:
            Dictionary with follow-up results (sent_count, skipped_count,
            total_needing, message, errors)
        """
        try:
            # Get applications needing follow-up
            applications = self.tracker.get_applications_needing_follow_up()

            if not applications:
                logger.info("No applications need follow-up at this time")
                return {
                    "sent_count": 0,
                    "skipped_count": 0,
                    "total_needing": 0,
                    "message": "No applications need follow-up at this time",
                }

            logger.info(f"Found {len(applications)} applications needing follow-up")

            sent_count = 0
            skipped_count = 0
            errors = []

            for app in applications:
                try:
                    if dry_run:
                        logger.info(f"DRY RUN: Would send follow-up for " f"{app.company_name}")
                        sent_count += len(app.recruiters)
                    else:
                        result = self.email_service.send_follow_up(app.id, dry_run=False)
                        emails_sent = result["sent_count"]
                        if emails_sent > 0:
                            sent_count += emails_sent
                            logger.info(
                                f"Follow-up sent ({emails_sent} email(s)) - " f"{app.company_name}"
                            )
                        else:
                            skipped_count += 1
                except ValueError as e:
                    logger.warning(f"Skipping {app.company_name}: {e}")
                    errors.append(f"{app.company_name}: {str(e)}")
                    skipped_count += 1
                except Exception as e:
                    logger.error(
                        f"Error sending follow-up for {app.company_name}: {e}", exc_info=True
                    )
                    errors.append(f"{app.company_name}: {str(e)}")
                    skipped_count += 1

            message = f"Follow-ups completed: {sent_count} sent, " f"{skipped_count} skipped"
            if errors:
                message += f", {len(errors)} errors"

            return {
                "sent_count": sent_count,
                "skipped_count": skipped_count,
                "total_needing": len(applications),
                "errors": errors[:10],  # Limit to first 10 errors
                "message": message,
            }

        except Exception as e:
            logger.error(f"Error sending follow-ups: {e}", exc_info=True)
            raise
