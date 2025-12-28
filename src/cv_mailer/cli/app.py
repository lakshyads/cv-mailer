"""
Main CLI application - Thin layer that calls services.
"""

import logging
import sys
from typing import Optional

from cv_mailer.config import Config
from cv_mailer.integrations import GoogleSheetsClient
from cv_mailer.services import ApplicationService, EmailService, StatisticsService
from cv_mailer.services.tracker import ApplicationTracker
from cv_mailer.core import JobStatus
from cv_mailer.utils import init_database
from cv_mailer.parsers import RecruiterParser
from cv_mailer.cli.display import console, show_progress, show_statistics

logger = logging.getLogger(__name__)


class CVMailer:
    """Main CV Mailer application - uses service layer."""

    def __init__(self):
        """Initialize the application."""
        errors = Config.validate()
        if errors:
            console.print("[red]Configuration errors:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            sys.exit(1)

        init_database()

        # Initialize services (not direct integrations)
        self.sheets_client = GoogleSheetsClient(Config.SPREADSHEET_ID, Config.WORKSHEET_NAME)
        self.tracker = ApplicationTracker()  # Legacy, TODO: phase out
        self.email_service = EmailService()
        self.app_service = ApplicationService()
        self.stats_service = StatisticsService()

        if Config.PROCESS_ALL_SHEETS:
            sheets = self.sheets_client.list_all_sheets()
            console.print(f"[cyan]Found {len(sheets)} sheets in spreadsheet[/cyan]")
            if len(sheets) <= 10:
                sheet_names = [s["title"] for s in sheets]
                console.print(f"[dim]Sheets: {', '.join(sheet_names)}[/dim]")

        console.print("[green]✓[/green] CV Mailer initialized successfully")

    def process_new_applications(self, dry_run: bool = False) -> int:
        """Process new job applications from Google Sheets."""
        console.print("\n[bold]Processing new job applications...[/bold]")
        logger.info("Process new job applications")

        try:
            # Read data from Google Sheets
            if Config.PROCESS_ALL_SHEETS:
                rows = self.sheets_client.read_all_sheets(sheet_filter=Config.SHEET_NAME_FILTER)
                console.print(
                    f"[cyan]Processing all sheets (filter: {Config.SHEET_NAME_FILTER or 'none'})[/cyan]"
                )
            else:
                rows = self.sheets_client.read_all_rows()
                console.print(f"[cyan]Processing single sheet: {Config.WORKSHEET_NAME}[/cyan]")

            if not rows:
                console.print("[yellow]No data found in Google Sheets[/yellow]")
                return 0

            console.print(f"[cyan]Found {len(rows)} total rows across all sheets[/cyan]")

            sent_count = 0
            skipped_count = 0

            with show_progress(len(rows), "Processing applications...") as progress:
                for row in rows:
                    progress.advance(1)

                    # Extract data from sheet
                    company_name = (
                        row.get("Company Name")
                        or row.get("company_name")
                        or row.get("Company")
                        or row.get("company")
                        or ""
                    )
                    position = row.get("Position") or row.get("position") or ""
                    recruiter_cell = (
                        row.get("Recruiter Names")
                        or row.get("recruiter_names")
                        or row.get("Recruiter Name")
                        or row.get("recruiter_name")
                        or row.get("Recruiter Email")
                        or row.get("recruiter_email")
                        or ""
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

                    recruiters = RecruiterParser.parse_recruiters(recruiter_cell)

                    # Skip if required fields missing
                    if not company_name or not position or not recruiters:
                        logger.warning(f"Skipping row {row.get('_row_number')}: missing fields")
                        skipped_count += 1
                        continue

                    # Create application using tracker (legacy)
                    sheet_name = row.get("_sheet_name", Config.WORKSHEET_NAME)
                    row_id = row.get("_row_number", 0)
                    unique_row_id = f"{sheet_name}_{row_id}"

                    # Check if application already exists and has sent emails
                    from cv_mailer.core import JobApplication, EmailRecord, EmailStatus, EmailType

                    existing_app = (
                        self.tracker.session.query(JobApplication)
                        .filter_by(spreadsheet_row_id=unique_row_id)
                        .first()
                    )

                    if existing_app:
                        # Check if emails have already been sent for this application
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
                                f"Skipping row {row.get('_row_number')}: application already processed "
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
                    try:
                        if dry_run:
                            console.print(
                                f"\n[dim]DRY RUN: Would send to {len(recruiters)} recruiter(s) for {company_name}[/dim]"
                            )
                            sent_count += len(recruiters)
                        else:
                            result = self.email_service.send_first_contact(
                                job_app.id, dry_run=False
                            )
                            emails_sent = result["sent_count"]
                            if emails_sent > 0:
                                sent_count += emails_sent
                                console.print(
                                    f"[green]✓[/green] Sent {emails_sent} email(s) - {position} - {company_name}"
                                )

                                # Update sheet status
                                try:
                                    sheet_name_for_update, row_num_str = unique_row_id.rsplit(
                                        "_", 1
                                    )
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
                                except Exception as e:
                                    logger.warning(f"Could not update spreadsheet: {e}")
                            else:
                                skipped_count += 1
                    except ValueError as e:
                        logger.warning(f"Skipping {company_name}: {e}")
                        skipped_count += 1

            console.print(f"\n[bold]Summary:[/bold] {sent_count} sent, {skipped_count} skipped\n")
            return sent_count

        except Exception as e:
            logger.error(f"Error processing applications: {e}", exc_info=True)
            console.print(f"[red]Error: {e}[/red]\n")
            return 0

    def send_follow_ups(self, dry_run: bool = False) -> int:
        """Send follow-up emails - uses service layer."""
        console.print("[bold]Sending follow-up emails...[/bold]")
        logger.info("Send follow-up emails")

        try:
            # Get applications needing follow-up
            applications = self.tracker.get_applications_needing_follow_up()

            if not applications:
                console.print("[yellow]No applications need follow-up at this time[/yellow]\n")
                return 0

            console.print(f"[cyan]Found {len(applications)} applications needing follow-up[/cyan]")

            sent_count = 0

            for app in applications:
                try:
                    # Use service to send follow-ups
                    if dry_run:
                        console.print(
                            f"\n[dim]DRY RUN: Would send follow-up for {app.company_name}[/dim]"
                        )
                        sent_count += len(app.recruiters)
                    else:
                        result = self.email_service.send_follow_up(app.id, dry_run=False)
                        emails_sent = result["sent_count"]
                        if emails_sent > 0:
                            sent_count += emails_sent
                            console.print(
                                f"[green]✓[/green] Follow-up sent ({emails_sent} email(s)) - {app.company_name}"
                            )
                except ValueError as e:
                    logger.warning(f"Skipping {app.company_name}: {e}")
                    continue

            console.print(f"\n[bold]Summary:[/bold] {sent_count} follow-ups sent\n")
            return sent_count

        except Exception as e:
            logger.error(f"Error sending follow-ups: {e}", exc_info=True)
            console.print(f"[red]Error: {e}[/red]\n")
            return 0

    def show_statistics(self):
        """Display application statistics - uses service layer."""
        stats = self.stats_service.get_statistics()
        show_statistics(stats)

    def update_status(self, job_id: int, status: str, notes: Optional[str] = None):
        """Update job application status - uses service layer."""
        try:
            job_status = JobStatus(status.lower())
            self.app_service.update_status(job_id, job_status, notes)
            console.print(f"[green]✓[/green] Updated job {job_id} status to {status}")
        except ValueError as e:
            console.print(f"[red]Invalid: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
