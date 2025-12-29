"""
Main CLI application - Thin layer that calls services.
"""

import logging
import sys
from typing import Optional

from cv_mailer.config import Config
from cv_mailer.integrations import GoogleSheetsClient
from cv_mailer.services import ApplicationService, EmailService, StatisticsService, SyncService
from cv_mailer.services.tracker import ApplicationTracker
from cv_mailer.core import JobStatus
from cv_mailer.utils import init_database
from cv_mailer.utils.exceptions import NotFoundError, BusinessLogicError, ExternalServiceError
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
        self.sync_service = SyncService()  # Use sync service for Google Sheets operations

        if Config.PROCESS_ALL_SHEETS:
            sheets = self.sheets_client.list_all_sheets()
            console.print(f"[cyan]Found {len(sheets)} sheets in spreadsheet[/cyan]")
            if len(sheets) <= 10:
                sheet_names = [s["title"] for s in sheets]
                console.print(f"[dim]Sheets: {', '.join(sheet_names)}[/dim]")

        console.print("[green]✓[/green] CV Mailer initialized successfully")

    def process_new_applications(self, dry_run: bool = False) -> int:
        """Process new job applications from Google Sheets - uses SyncService."""
        console.print("\n[bold]Processing new job applications...[/bold]")
        logger.info("Process new job applications")

        try:
            # Use sync service for the actual work
            result = self.sync_service.sync_applications(dry_run=dry_run)

            # Display results in CLI-friendly format
            console.print(
                f"\n[bold]Summary:[/bold] {result['sent_count']} sent, {result['skipped_count']} skipped"
            )
            if result.get("errors"):
                console.print(f"[yellow]Errors: {len(result['errors'])}[/yellow]")
            console.print()

            return result["sent_count"]
        except (NotFoundError, BusinessLogicError, ExternalServiceError) as e:
            logger.error(f"Error processing applications: {e}", exc_info=True)
            console.print(f"[red]Error: {e}[/red]\n")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error processing applications: {e}", exc_info=True)
            console.print(f"[red]Unexpected error: {e}[/red]\n")
            return 0

    def send_follow_ups(self, dry_run: bool = False) -> int:
        """Send follow-up emails - uses SyncService."""
        console.print("[bold]Sending follow-up emails...[/bold]")
        logger.info("Send follow-up emails")

        try:
            # Use sync service for the actual work
            result = self.sync_service.send_follow_ups(dry_run=dry_run)

            # Display results in CLI-friendly format
            if result["total_needing"] == 0:
                console.print("[yellow]No applications need follow-up at this time[/yellow]\n")
            else:
                console.print(
                    f"[cyan]Found {result['total_needing']} applications needing follow-up[/cyan]"
                )
                console.print(
                    f"\n[bold]Summary:[/bold] {result['sent_count']} follow-ups sent, {result['skipped_count']} skipped"
                )
                if result.get("errors"):
                    console.print(f"[yellow]Errors: {len(result['errors'])}[/yellow]")
            console.print()

            return result["sent_count"]
        except (NotFoundError, BusinessLogicError, ExternalServiceError) as e:
            logger.error(f"Error sending follow-ups: {e}", exc_info=True)
            console.print(f"[red]Error: {e}[/red]\n")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error sending follow-ups: {e}", exc_info=True)
            console.print(f"[red]Unexpected error: {e}[/red]\n")
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
        except (NotFoundError, BusinessLogicError) as e:
            logger.error(f"Error updating status: {e}")
            console.print(f"[red]Error: {e}[/red]")
        except ValueError as e:
            logger.error(f"Invalid status: {e}")
            console.print(f"[red]Invalid status: {e}[/red]")
        except Exception as e:
            logger.error(f"Unexpected error updating status: {e}", exc_info=True)
            console.print(f"[red]Unexpected error: {e}[/red]")
