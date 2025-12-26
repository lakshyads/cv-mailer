"""
Main application orchestrator for CV Mailer.
"""
import logging
import sys
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from config import Config
from google_sheets import GoogleSheetsClient
from gmail_sender import GmailSender
from email_templates import EmailTemplate
from tracker import ApplicationTracker
from models import JobStatus, EmailType, EmailStatus, init_database
from recruiter_parser import RecruiterParser

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
console = Console()


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
                sheet_names = [s['title'] for s in sheets]
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
        
        try:
            # Read data from Google Sheets
            if Config.PROCESS_ALL_SHEETS:
                rows = self.sheets_client.read_all_sheets(sheet_filter=Config.SHEET_NAME_FILTER)
                console.print(f"[cyan]Processing all sheets (filter: {Config.SHEET_NAME_FILTER or 'none'})[/cyan]")
            else:
                rows = self.sheets_client.read_all_rows()
                console.print(f"[cyan]Processing single sheet: {Config.WORKSHEET_NAME}[/cyan]")
            
            if not rows:
                console.print("[yellow]No data found in Google Sheets[/yellow]")
                return 0
            
            console.print(f"[cyan]Found {len(rows)} total rows across all sheets[/cyan]")
            
            sent_count = 0
            skipped_count = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processing applications...", total=len(rows))
                
                for row in rows:
                    progress.update(task, advance=1)
                    
                    # Extract data (adjust column names based on your sheet)
                    # Support multiple column name variations
                    company_name = (
                        row.get('Company Name') or 
                        row.get('company_name') or 
                        row.get('Company') or 
                        row.get('company') or 
                        ''
                    )
                    position = (
                        row.get('Position') or 
                        row.get('position') or 
                        ''
                    )
                    
                    # Handle recruiter information - can be in "Recruiter Name", "Recruiter Names", or "Recruiter Email" column
                    # Support format: "Name - email@domain.com, Name2 - email2@domain.com"
                    recruiter_cell = (
                        row.get('Recruiter Names') or 
                        row.get('recruiter_names') or 
                        row.get('Recruiter Name') or 
                        row.get('recruiter_name') or 
                        ''
                    )
                    if not recruiter_cell:
                        # Fallback to Recruiter Email column if Recruiter Name is empty
                        recruiter_cell = (
                            row.get('Recruiter Email') or 
                            row.get('recruiter_email') or 
                            ''
                        )
                    
                    location = (
                        row.get('Location') or 
                        row.get('location') or 
                        None
                    )
                    job_posting_url = (
                        row.get('Job Posting URL') or 
                        row.get('job_posting_url') or 
                        row.get('Job Posting') or 
                        row.get('job_posting') or 
                        None
                    )
                    status = (
                        row.get('Status') or 
                        row.get('status') or 
                        ''
                    )
                    
                    # Read optional fields: Expected salary and Message
                    expected_salary = (
                        row.get('Expected salary') or 
                        row.get('expected_salary') or 
                        row.get('Expected Salary') or 
                        row.get('Salary') or 
                        row.get('salary') or 
                        None
                    )
                    custom_message = (
                        row.get('Message') or 
                        row.get('message') or 
                        row.get('Custom Message') or 
                        row.get('custom_message') or 
                        None
                    )
                    
                    # Parse recruiters from the cell (handles multiple recruiters)
                    recruiters = RecruiterParser.parse_recruiters(recruiter_cell)
                    
                    # Skip if required fields are missing
                    if not company_name or not position or not recruiters:
                        logger.warning(f"Skipping row {row.get('_row_number')}: missing required fields (company: {company_name}, position: {position}, recruiters: {len(recruiters)})")
                        skipped_count += 1
                        continue
                    
                    # Skip if already processed (status indicates sent)
                    if status and status.lower() in ['sent', 'reached_out', 'applied']:
                        logger.info(f"Skipping row {row.get('_row_number')}: already processed")
                        skipped_count += 1
                        continue
                    
                    # Get or create job application (one per row, shared across all recruiters)
                    # Use sheet name + row number as unique identifier for multi-sheet support
                    sheet_name = row.get('_sheet_name', Config.WORKSHEET_NAME)
                    row_id = row.get('_row_number', 0)
                    # Create unique ID: sheet_name + row_number (e.g., "2024-01-15_5")
                    unique_row_id = f"{sheet_name}_{row_id}"
                    
                    # Create job application with all recruiters
                    job_app = self.tracker.get_or_create_job_application(
                        spreadsheet_row_id=unique_row_id,
                        company_name=company_name,
                        position=position,
                        recruiters=recruiters,  # Pass all recruiters
                        location=location,
                        job_posting_url=job_posting_url,
                        expected_salary=expected_salary,
                        custom_message=custom_message,
                        sheet_name=sheet_name
                    )
                    
                    # Process each recruiter separately
                    emails_sent_for_row = 0
                    emails_skipped_for_row = 0
                    
                    for recruiter in recruiters:
                        recruiter_email = recruiter['email']
                        recruiter_name = recruiter['name']
                        
                        if not recruiter_email:
                            logger.warning(f"Skipping recruiter {recruiter_name}: no email address")
                            emails_skipped_for_row += 1
                            continue
                        
                        # Check if we've already sent an email to this specific recruiter for this job
                        from models import EmailRecord
                        existing_email = self.tracker.session.query(EmailRecord).filter_by(
                            job_application_id=job_app.id,
                            recipient_email=recruiter_email,
                            status=EmailStatus.SENT
                        ).first()
                        
                        if existing_email:
                            logger.info(f"Already sent email to {recruiter_email} for {company_name} - {position}")
                            emails_skipped_for_row += 1
                            continue
                        
                        # Generate email (personalized for each recruiter)
                        subject, body = EmailTemplate.render_first_contact(
                            recruiter_name=recruiter_name,
                            company_name=company_name,
                            position=position,
                            location=location,
                            job_posting_url=job_posting_url,
                            custom_message=job_app.custom_message
                        )
                        
                        if dry_run:
                            console.print(f"\n[dim]DRY RUN: Would send email to {recruiter_name or 'N/A'} ({recruiter_email})[/dim]")
                            console.print(f"[dim]Subject: {subject}[/dim]")
                            emails_sent_for_row += 1
                            sent_count += 1
                        else:
                            # Send email
                            message_id = self.gmail_sender.send_email(
                                to=recruiter_email,
                                subject=subject,
                                body=body
                            )
                            
                            if message_id:
                                # Record email (one record per recruiter)
                                self.tracker.record_email_sent(
                                    job_application_id=job_app.id,
                                    email_type=EmailType.FIRST_CONTACT,
                                    subject=subject,
                                    body=body,
                                    recipient_email=recruiter_email,
                                    recipient_name=recruiter_name,
                                    gmail_message_id=message_id,
                                    is_follow_up=False,
                                    follow_up_number=0
                                )
                                
                                emails_sent_for_row += 1
                                sent_count += 1
                                console.print(f"[green]✓[/green] Sent to {recruiter_name or 'N/A'} ({recruiter_email}) - {company_name}")
                            else:
                                # Record failure
                                self.tracker.record_email_failed(
                                    job_application_id=job_app.id,
                                    email_type=EmailType.FIRST_CONTACT,
                                    subject=subject,
                                    body=body,
                                    recipient_email=recruiter_email,
                                    recipient_name=recruiter_name,
                                    error_message="Failed to send email"
                                )
                                emails_skipped_for_row += 1
                                console.print(f"[red]✗[/red] Failed to send to {recruiter_email}")
                    
                    # Update spreadsheet status only once per row (after processing all recruiters)
                    if emails_sent_for_row > 0 and not dry_run:
                        try:
                            # Extract sheet name and row number from unique_row_id
                            if '_' in unique_row_id:
                                sheet_name_for_update, row_num_str = unique_row_id.rsplit('_', 1)
                                row_num = int(row_num_str)
                                # Find Status column and update
                                status_col = self.sheets_client.get_column_letter('Status', worksheet_name=sheet_name_for_update)
                                if status_col:
                                    self.sheets_client.update_cell(
                                        row_num,
                                        status_col,
                                        'Reached Out',
                                        worksheet_name=sheet_name_for_update
                                    )
                                else:
                                    # Try updating by column name using update_row
                                    self.sheets_client.update_row(
                                        row_num,
                                        {'Status': 'Reached Out'},
                                        worksheet_name=sheet_name_for_update
                                    )
                            else:
                                # Fallback for single sheet mode
                                status_col = self.sheets_client.get_column_letter('Status')
                                if status_col:
                                    self.sheets_client.update_cell(
                                        row_id,
                                        status_col,
                                        'Reached Out'
                                    )
                                else:
                                    self.sheets_client.update_row(
                                        row_id,
                                        {'Status': 'Reached Out'}
                                    )
                        except Exception as e:
                            logger.warning(f"Could not update spreadsheet: {e}")
                    
                    if emails_skipped_for_row == len(recruiters):
                        # All recruiters were skipped (already sent or failed)
                        skipped_count += 1
            
            console.print(f"\n[bold]Summary:[/bold] {sent_count} sent, {skipped_count} skipped")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error processing applications: {e}", exc_info=True)
            console.print(f"[red]Error: {e}[/red]")
            return 0
    
    def send_follow_ups(self, dry_run: bool = False) -> int:
        """
        Send follow-up emails for applications that need them.
        
        Args:
            dry_run: If True, don't actually send emails
        
        Returns:
            Number of follow-up emails sent
        """
        console.print("\n[bold]Sending follow-up emails...[/bold]")
        
        try:
            applications = self.tracker.get_applications_needing_follow_up()
            
            if not applications:
                console.print("[yellow]No applications need follow-up at this time[/yellow]")
                return 0
            
            console.print(f"[cyan]Found {len(applications)} applications needing follow-up[/cyan]")
            
            sent_count = 0
            
            for app in applications:
                follow_up_number = self.tracker.get_next_follow_up_number(app.id)
                
                # Get all recruiters who received the first email for this application
                from models import EmailRecord
                first_contact_emails = self.tracker.session.query(EmailRecord).filter_by(
                    job_application_id=app.id,
                    email_type=EmailType.FIRST_CONTACT,
                    status=EmailStatus.SENT
                ).all()
                
                if not first_contact_emails:
                    # Fallback to recruiters from job application if no first contact emails found
                    if app.recruiters:
                        recruiters_to_follow_up = [{
                            'email': r.email,
                            'name': r.name
                        } for r in app.recruiters]
                    else:
                        # No recruiters found, skip this application
                        logger.warning(f"No recruiters found for job application {app.id}, skipping follow-up")
                        continue
                else:
                    # Get unique recruiters from first contact emails
                    recruiters_to_follow_up = []
                    seen_emails = set()
                    for email_record in first_contact_emails:
                        if email_record.recipient_email and email_record.recipient_email not in seen_emails:
                            seen_emails.add(email_record.recipient_email)
                            recruiters_to_follow_up.append({
                                'email': email_record.recipient_email,
                                'name': email_record.recipient_name
                            })
                
                # Send follow-up to each recruiter who received the first email
                for recruiter in recruiters_to_follow_up:
                    # Check if we've already sent this follow-up number to this recruiter
                    existing_follow_up = self.tracker.session.query(EmailRecord).filter_by(
                        job_application_id=app.id,
                        recipient_email=recruiter['email'],
                        is_follow_up=True,
                        follow_up_number=follow_up_number,
                        status=EmailStatus.SENT
                    ).first()
                    
                    if existing_follow_up:
                        logger.info(f"Already sent follow-up #{follow_up_number} to {recruiter['email']}")
                        continue
                    
                    # Generate follow-up email (personalized for each recruiter)
                    subject, body = EmailTemplate.render_follow_up(
                        recruiter_name=recruiter['name'],
                        company_name=app.company_name,
                        position=app.position,
                        location=app.location,
                        follow_up_number=follow_up_number
                    )
                    
                    if dry_run:
                        console.print(f"\n[dim]DRY RUN: Would send follow-up #{follow_up_number} to {recruiter['name'] or 'N/A'} ({recruiter['email']})[/dim]")
                        sent_count += 1
                    else:
                        # Send email
                        message_id = self.gmail_sender.send_email(
                            to=recruiter['email'],
                            subject=subject,
                            body=body
                        )
                        
                        if message_id:
                            self.tracker.record_email_sent(
                                job_application_id=app.id,
                                email_type=EmailType.FOLLOW_UP,
                                subject=subject,
                                body=body,
                                recipient_email=recruiter['email'],
                                recipient_name=recruiter['name'],
                                gmail_message_id=message_id,
                                is_follow_up=True,
                                follow_up_number=follow_up_number
                            )
                            sent_count += 1
                            console.print(f"[green]✓[/green] Follow-up #{follow_up_number} sent to {recruiter['name'] or 'N/A'} ({recruiter['email']})")
                        else:
                            console.print(f"[red]✗[/red] Failed to send follow-up to {recruiter['email']}")
            
            console.print(f"\n[bold]Summary:[/bold] {sent_count} follow-ups sent")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending follow-ups: {e}", exc_info=True)
            console.print(f"[red]Error: {e}[/red]")
            return 0
    
    def show_statistics(self):
        """Display application statistics."""
        stats = self.tracker.get_statistics()
        
        table = Table(title="Application Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Applications", str(stats['total_applications']))
        table.add_row("Total Emails Sent", str(stats['total_emails_sent']))
        table.add_row("Follow-ups Sent", str(stats['follow_ups_sent']))
        
        console.print("\n")
        console.print(table)
        
        # Status breakdown
        status_table = Table(title="Status Breakdown")
        status_table.add_column("Status", style="cyan")
        status_table.add_column("Count", style="magenta")
        
        for status, count in stats['by_status'].items():
            status_table.add_row(status.replace('_', ' ').title(), str(count))
        
        console.print("\n")
        console.print(status_table)
    
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


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CV Mailer - Automate resume emailing to recruiters")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without actually sending emails'
    )
    parser.add_argument(
        '--follow-ups',
        action='store_true',
        help='Send follow-up emails only'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics'
    )
    parser.add_argument(
        '--repair-followups',
        action='store_true',
        help='Repair historical follow-up numbering issues in the local DB (use --dry-run to preview)'
    )
    parser.add_argument(
        '--new',
        action='store_true',
        help='Process new applications only (default)'
    )
    
    args = parser.parse_args()
    
    # Show banner
    console.print(Panel.fit(
        "[bold cyan]CV Mailer[/bold cyan]\nAutomated Resume Email System",
        border_style="cyan"
    ))
    
    try:
        mailer = CVMailer()
        
        if args.stats:
            mailer.show_statistics()
        elif args.repair_followups:
            console.print("\n[bold]Repairing follow-up numbering...[/bold]")
            stats = mailer.tracker.repair_follow_up_numbers(dry_run=args.dry_run)
            if args.dry_run:
                console.print(
                    f"[yellow]DRY RUN:[/yellow] scanned={stats['applications_scanned']}, "
                    f"would_change={stats['applications_changed']}, "
                    f"would_update_rows={stats['rows_updated']}"
                )
            else:
                console.print(
                    f"[green]✓[/green] Repair complete: scanned={stats['applications_scanned']}, "
                    f"changed={stats['applications_changed']}, "
                    f"updated_rows={stats['rows_updated']}"
                )
        elif args.follow_ups:
            mailer.send_follow_ups(dry_run=args.dry_run)
        else:
            # Default: process new applications
            mailer.process_new_applications(dry_run=args.dry_run)
            if not args.dry_run:
                # Also check for follow-ups
                mailer.send_follow_ups(dry_run=False)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

