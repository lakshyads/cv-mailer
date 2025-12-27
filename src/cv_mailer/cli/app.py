"""
Main CLI application orchestrator for CV Mailer.
"""

import logging
import sys
from typing import List, Dict, Optional

from cv_mailer.config import Config
from cv_mailer.integrations import GoogleSheetsClient, GmailSender
from cv_mailer.services import EmailTemplate, ApplicationTracker
from cv_mailer.core import JobStatus, EmailType, EmailStatus
from cv_mailer.utils import init_database
from cv_mailer.parsers import RecruiterParser
from cv_mailer.cli.display import console, show_progress, show_statistics

logger = logging.getLogger(__name__)


class CVMailer:
    """Main CV Mailer application."""

    def __init__(self):
        """Initialize the application."""
        # Validate configuration
        errors = Config.validate()
        if errors:
            console.print("[red]Configuration errors:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            sys.exit(1)

        # Initialize database
        init_database()

        # Initialize clients
        self.sheets_client = GoogleSheetsClient(Config.SPREADSHEET_ID, Config.WORKSHEET_NAME)
        self.gmail_sender = GmailSender()
        self.tracker = ApplicationTracker()

        # Show sheet information
        if Config.PROCESS_ALL_SHEETS:
            sheets = self.sheets_client.list_all_sheets()
            console.print(f"[cyan]Found {len(sheets)} sheets in spreadsheet[/cyan]")
            if len(sheets) <= 10:
                sheet_names = [s["title"] for s in sheets]
                console.print(f"[dim]Sheets: {', '.join(sheet_names)}[/dim]")

        console.print("[green]✓[/green] CV Mailer initialized successfully")

    def process_new_applications(self, dry_run: bool = False) -> int:
        """
        Process new job applications from Google Sheets.

        Args:
            dry_run: If True, don't actually send emails

        Returns:
            Number of emails sent
        """
        console.print("\n[bold]Processing new job applications...[/bold]")
        logger.info("============================")
        logger.info("Process new job applications")
        logger.info("============================")

        try:
            # Read data from Google Sheets
            if Config.PROCESS_ALL_SHEETS:
                rows = self.sheets_client.read_all_sheets(sheet_filter=Config.SHEET_NAME_FILTER)
                logger.info(f"Processing all sheets (filter: {Config.SHEET_NAME_FILTER or 'none'})")
                console.print(
                    f"[cyan]Processing all sheets (filter: {Config.SHEET_NAME_FILTER or 'none'})[/cyan]"
                )
            else:
                rows = self.sheets_client.read_all_rows()
                logger.info(f"Processing single sheet: {Config.WORKSHEET_NAME}")
                console.print(f"[cyan]Processing single sheet: {Config.WORKSHEET_NAME}[/cyan]")

            if not rows:
                logger.info("No data found in Google Sheets")
                console.print("[yellow]No data found in Google Sheets[/yellow]")
                return 0

            logger.info(f"Found {len(rows)} total rows across all sheets")
            console.print(f"[cyan]Found {len(rows)} total rows across all sheets[/cyan]")

            sent_count = 0
            skipped_count = 0

            with show_progress(len(rows), "Processing applications...") as progress:
                for row in rows:
                    progress.advance(1)

                    # Extract data (adjust column names based on your sheet)
                    company_name = (
                        row.get("Company Name")
                        or row.get("company_name")
                        or row.get("Company")
                        or row.get("company")
                        or ""
                    )
                    position = row.get("Position") or row.get("position") or ""

                    # Handle recruiter information
                    recruiter_cell = (
                        row.get("Recruiter Names")
                        or row.get("recruiter_names")
                        or row.get("Recruiter Name")
                        or row.get("recruiter_name")
                        or ""
                    )
                    if not recruiter_cell:
                        recruiter_cell = (
                            row.get("Recruiter Email") or row.get("recruiter_email") or ""
                        )

                    location = row.get("Location") or row.get("location") or None
                    job_posting_url = (
                        row.get("Job Posting URL")
                        or row.get("job_posting_url")
                        or row.get("Job Posting")
                        or row.get("job_posting")
                        or None
                    )
                    status = row.get("Status") or row.get("status") or ""

                    expected_salary = (
                        row.get("Expected salary")
                        or row.get("expected_salary")
                        or row.get("Expected Salary")
                        or row.get("Salary")
                        or row.get("salary")
                        or None
                    )
                    custom_message = (
                        row.get("Message")
                        or row.get("message")
                        or row.get("Custom Message")
                        or row.get("custom_message")
                        or None
                    )

                    # Parse recruiters
                    recruiters = RecruiterParser.parse_recruiters(recruiter_cell)

                    # Skip if required fields are missing
                    if not company_name or not position or not recruiters:
                        logger.warning(
                            f"Skipping row {row.get('_row_number')}: missing required fields"
                        )
                        skipped_count += 1
                        continue

                    # Skip if already processed
                    if status and status.lower() in ["sent", "reached_out", "applied"]:
                        logger.info(f"Skipping row {row.get('_row_number')}: already processed")
                        skipped_count += 1
                        continue

                    # Get or create job application
                    sheet_name = row.get("_sheet_name", Config.WORKSHEET_NAME)
                    row_id = row.get("_row_number", 0)
                    unique_row_id = f"{sheet_name}_{row_id}"

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

                    # Process each recruiter
                    emails_sent_for_row = 0
                    emails_skipped_for_row = 0

                    for recruiter in recruiters:
                        recruiter_email = recruiter["email"]
                        recruiter_name = recruiter["name"]

                        if not recruiter_email:
                            logger.warning(f"Skipping recruiter {recruiter_name}: no email address")
                            emails_skipped_for_row += 1
                            continue

                        # Check if already sent to this recruiter
                        from cv_mailer.core import EmailRecord

                        existing_email = (
                            self.tracker.session.query(EmailRecord)
                            .filter_by(
                                job_application_id=job_app.id,
                                recipient_email=recruiter_email,
                                status=EmailStatus.SENT,
                            )
                            .first()
                        )

                        if existing_email:
                            logger.info(f"Already sent email to {recruiter_email}")
                            emails_skipped_for_row += 1
                            continue

                        # Generate email
                        subject, body = EmailTemplate.render_first_contact(
                            recruiter_name=recruiter_name,
                            company_name=company_name,
                            position=position,
                            location=location,
                            job_posting_url=job_posting_url,
                            custom_message=job_app.custom_message,
                        )

                        if dry_run:
                            console.print(
                                f"\n[dim]DRY RUN: Would send email to {recruiter_name or 'N/A'} ({recruiter_email})[/dim]"
                            )
                            console.print(f"[dim]Subject: {subject}[/dim]")
                            emails_sent_for_row += 1
                            sent_count += 1
                        else:
                            # Send email
                            message_id = self.gmail_sender.send_email(
                                to=recruiter_email, subject=subject, body=body
                            )

                            if message_id:
                                self.tracker.record_email_sent(
                                    job_application_id=job_app.id,
                                    email_type=EmailType.FIRST_CONTACT,
                                    subject=subject,
                                    body=body,
                                    recipient_email=recruiter_email,
                                    recipient_name=recruiter_name,
                                    gmail_message_id=message_id,
                                    is_follow_up=False,
                                    follow_up_number=0,
                                )

                                emails_sent_for_row += 1
                                sent_count += 1
                                logger.info(
                                    f"✓ Sent to {recruiter_name or 'N/A'} ({recruiter_email})"
                                )
                                console.print(
                                    f"[green]✓[/green] Sent to {recruiter_name or 'N/A'} ({recruiter_email}) - {position} - {company_name}"
                                )
                            else:
                                self.tracker.record_email_failed(
                                    job_application_id=job_app.id,
                                    email_type=EmailType.FIRST_CONTACT,
                                    subject=subject,
                                    body=body,
                                    recipient_email=recruiter_email,
                                    recipient_name=recruiter_name,
                                    error_message="Failed to send email",
                                )
                                emails_skipped_for_row += 1
                                logger.info(f"✗ Failed to send to {recruiter_email}")
                                console.print(f"[red]✗[/red] Failed to send to {recruiter_email}")

                    # Update spreadsheet status
                    if emails_sent_for_row > 0 and not dry_run:
                        try:
                            if "_" in unique_row_id:
                                sheet_name_for_update, row_num_str = unique_row_id.rsplit("_", 1)
                                row_num = int(row_num_str)
                                status_col = self.sheets_client.get_column_letter(
                                    "Status", worksheet_name=sheet_name_for_update
                                )
                                if status_col:
                                    self.sheets_client.update_cell(
                                        row_num,
                                        status_col,
                                        "Reached Out",
                                        worksheet_name=sheet_name_for_update,
                                    )
                                else:
                                    self.sheets_client.update_row(
                                        row_num,
                                        {"Status": "Reached Out"},
                                        worksheet_name=sheet_name_for_update,
                                    )
                        except Exception as e:
                            logger.warning(f"Could not update spreadsheet: {e}")

                    if emails_skipped_for_row == len(recruiters):
                        skipped_count += 1

            logger.info(f"Summary: {sent_count} sent, {skipped_count} skipped")
            console.print(f"\n[bold]Summary:[/bold] {sent_count} sent, {skipped_count} skipped\n")
            return sent_count

        except Exception as e:
            logger.error(f"Error processing applications: {e}", exc_info=True)
            console.print(f"[red]Error: {e}[/red]\n")
            return 0

    def send_follow_ups(self, dry_run: bool = False) -> int:
        """
        Send follow-up emails for applications that need them.

        Args:
            dry_run: If True, don't actually send emails

        Returns:
            Number of follow-up emails sent
        """
        console.print("[bold]Sending follow-up emails...[/bold]")
        logger.info("=====================")
        logger.info("Send follow-up emails")
        logger.info("=====================")

        try:
            applications = self.tracker.get_applications_needing_follow_up()

            if not applications:
                logger.info("No applications need follow-up at this time")
                console.print("[yellow]No applications need follow-up at this time[/yellow]\n")
                return 0

            logger.info(f"Found {len(applications)} applications needing follow-up")
            console.print(f"[cyan]Found {len(applications)} applications needing follow-up[/cyan]")

            sent_count = 0

            for app in applications:
                follow_up_number = self.tracker.get_next_follow_up_number(app.id)

                # Get recruiters who received first email
                from cv_mailer.core import EmailRecord

                first_contact_emails = (
                    self.tracker.session.query(EmailRecord)
                    .filter_by(
                        job_application_id=app.id,
                        email_type=EmailType.FIRST_CONTACT,
                        status=EmailStatus.SENT,
                    )
                    .all()
                )

                if not first_contact_emails:
                    if app.recruiters:
                        recruiters_to_follow_up = [
                            {"email": r.email, "name": r.name} for r in app.recruiters
                        ]
                    else:
                        logger.warning(f"No recruiters found for job application {app.id}")
                        continue
                else:
                    recruiters_to_follow_up = []
                    seen_emails = set()
                    for email_record in first_contact_emails:
                        if (
                            email_record.recipient_email
                            and email_record.recipient_email not in seen_emails
                        ):
                            seen_emails.add(email_record.recipient_email)
                            recruiters_to_follow_up.append(
                                {
                                    "email": email_record.recipient_email,
                                    "name": email_record.recipient_name,
                                }
                            )

                # Send follow-up to each recruiter
                for recruiter in recruiters_to_follow_up:
                    # Check if already sent this follow-up
                    existing_follow_up = (
                        self.tracker.session.query(EmailRecord)
                        .filter_by(
                            job_application_id=app.id,
                            recipient_email=recruiter["email"],
                            is_follow_up=True,
                            follow_up_number=follow_up_number,
                            status=EmailStatus.SENT,
                        )
                        .first()
                    )

                    if existing_follow_up:
                        logger.info(
                            f"Already sent follow-up #{follow_up_number} to {recruiter['email']}"
                        )
                        continue

                    # Generate follow-up email
                    subject, body = EmailTemplate.render_follow_up(
                        recruiter_name=recruiter["name"],
                        company_name=app.company_name,
                        position=app.position,
                        location=app.location,
                        follow_up_number=follow_up_number,
                    )

                    if dry_run:
                        console.print(
                            f"\n[dim]DRY RUN: Would send follow-up #{follow_up_number} to {recruiter['name'] or 'N/A'} ({recruiter['email']})[/dim]"
                        )
                        sent_count += 1
                    else:
                        message_id = self.gmail_sender.send_email(
                            to=recruiter["email"], subject=subject, body=body
                        )

                        if message_id:
                            self.tracker.record_email_sent(
                                job_application_id=app.id,
                                email_type=EmailType.FOLLOW_UP,
                                subject=subject,
                                body=body,
                                recipient_email=recruiter["email"],
                                recipient_name=recruiter["name"],
                                gmail_message_id=message_id,
                                is_follow_up=True,
                                follow_up_number=follow_up_number,
                            )
                            sent_count += 1
                            logger.info(
                                f"✓ Follow-up #{follow_up_number} sent to {recruiter['name'] or 'N/A'} ({recruiter['email']})"
                            )
                            console.print(
                                f"[green]✓[/green] Follow-up #{follow_up_number} sent to {recruiter['name'] or 'N/A'} ({recruiter['email']}) - {app.company_name}"
                            )
                        else:
                            logger.info(f"✗ Failed to send follow-up to {recruiter['email']}")
                            console.print(
                                f"[red]✗[/red] Failed to send follow-up to {recruiter['email']}"
                            )

            logger.info(f"Summary: {sent_count} follow-ups sent")
            console.print(f"\n[bold]Summary:[/bold] {sent_count} follow-ups sent\n")
            return sent_count

        except Exception as e:
            logger.error(f"Error sending follow-ups: {e}", exc_info=True)
            console.print(f"[red]Error: {e}[/red]\n")
            return 0

    def show_statistics(self):
        """Display application statistics."""
        stats = self.tracker.get_statistics()
        show_statistics(stats)

    def update_status(self, job_id: int, status: str, notes: Optional[str] = None):
        """Update job application status."""
        try:
            job_status = JobStatus(status.lower())
            self.tracker.update_job_status(job_id, job_status, notes)
            console.print(f"[green]✓[/green] Updated job {job_id} status to {status}")
        except ValueError:
            console.print(f"[red]Invalid status: {status}[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
