"""
Tracking system for job applications and email communications.
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import (
    JobApplication, EmailRecord, ResponseRecord, JobStatus, 
    EmailType, EmailStatus, Recruiter, get_session
)
from config import Config

logger = logging.getLogger(__name__)


class ApplicationTracker:
    """Track job applications and email communications."""
    
    def __init__(self):
        self.session = get_session()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    def get_or_create_job_application(
        self,
        spreadsheet_row_id: str,  # Changed to str to support "sheet_name_row" format
        company_name: str,
        position: str,
        recruiters: List[Dict[str, str]],  # List of dicts with 'name' and 'email' keys
        location: Optional[str] = None,
        job_posting_url: Optional[str] = None,
        expected_salary: Optional[str] = None,
        custom_message: Optional[str] = None,
        sheet_name: Optional[str] = None
    ) -> JobApplication:
        """
        Get existing or create new job application.
        
        Args:
            recruiters: List of dictionaries with 'name' and 'email' keys
        """
        # Check if application already exists
        app = self.session.query(JobApplication).filter_by(
            spreadsheet_row_id=spreadsheet_row_id
        ).first()
        
        if app:
            # Update if needed
            app.company_name = company_name
            app.position = position
            app.location = location or app.location
            app.job_posting_url = job_posting_url or app.job_posting_url
            app.expected_salary = expected_salary or app.expected_salary
            app.custom_message = custom_message or app.custom_message
            app.updated_at = datetime.utcnow()
            
            # Update recruiters relationship
            self._link_recruiters_to_application(app, recruiters)
            return app
        
        # Create new application
        app = JobApplication(
            spreadsheet_row_id=spreadsheet_row_id,
            sheet_name=sheet_name,
            company_name=company_name,
            position=position,
            location=location,
            job_posting_url=job_posting_url,
            expected_salary=expected_salary,
            custom_message=custom_message,
            status=JobStatus.DRAFT
        )
        self.session.add(app)
        self.session.flush()  # Flush to get the ID
        
        # Link all recruiters to the application
        self._link_recruiters_to_application(app, recruiters)
        
        self.session.commit()
        logger.info(f"Created new job application: {company_name} - {position} with {len(recruiters)} recruiters")
        return app
    
    def _link_recruiters_to_application(self, app: JobApplication, recruiters: List[Dict[str, str]]):
        """Link recruiters to a job application, creating recruiter records if needed."""
        if not recruiters:
            return
        
        # Clear existing recruiters for this application
        app.recruiters.clear()
        
        for recruiter_data in recruiters:
            email = recruiter_data.get('email')
            name = recruiter_data.get('name')
            
            if not email:
                continue
            
            # Get or create recruiter
            recruiter = self.session.query(Recruiter).filter_by(email=email).first()
            if not recruiter:
                recruiter = Recruiter(
                    email=email,
                    name=name
                )
                self.session.add(recruiter)
                self.session.flush()
            
            # Link recruiter to application
            if recruiter not in app.recruiters:
                app.recruiters.append(recruiter)
    
    def record_email_sent(
        self,
        job_application_id: int,
        email_type: EmailType,
        subject: str,
        body: str,
        recipient_email: str,
        recipient_name: Optional[str] = None,
        gmail_message_id: Optional[str] = None,
        is_follow_up: bool = False,
        follow_up_number: int = 0
    ) -> EmailRecord:
        """Record that an email was sent."""
        job_app = self.session.query(JobApplication).get(job_application_id)
        if not job_app:
            raise ValueError(f"Job application {job_application_id} not found")
        
        email_record = EmailRecord(
            job_application_id=job_application_id,
            email_type=email_type,
            subject=subject,
            body=body,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            status=EmailStatus.SENT if gmail_message_id else EmailStatus.PENDING,
            gmail_message_id=gmail_message_id,
            is_follow_up=is_follow_up,
            follow_up_number=follow_up_number,
            sent_at=datetime.now(timezone.utc) if gmail_message_id else None
        )
        
        self.session.add(email_record)
        
        # Update job application status
        if job_app.status == JobStatus.DRAFT:
            job_app.status = JobStatus.REACHED_OUT
            job_app.applied_at = datetime.now(timezone.utc)
        
        self.session.commit()
        log = f"Recorded email sent for job application {job_application_id}"
        logger.info(log)
        return email_record
    
    def record_email_failed(
        self,
        job_application_id: int,
        email_type: EmailType,
        subject: str,
        body: str,
        recipient_email: str,
        recipient_name: Optional[str] = None,
        error_message: str = "Failed to send email"
    ):
        """Record that an email failed to send."""
        job_app = self.session.query(JobApplication).get(job_application_id)
        if not job_app:
            raise ValueError(f"Job application {job_application_id} not found")
        
        email_record = EmailRecord(
            job_application_id=job_application_id,
            email_type=email_type,
            subject=subject,
            body=body,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            status=EmailStatus.FAILED,
            error_message=error_message
        )
        
        self.session.add(email_record)
        self.session.commit()
        logger.warning(f"Recorded email failure for job application {job_application_id}: {error_message}")
    
    def get_applications_needing_follow_up(self) -> List[JobApplication]:
        """Get job applications that need follow-up emails."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=Config.FOLLOW_UP_DAYS)
        
        applications = self.session.query(JobApplication).filter(
            JobApplication.status.in_([
                JobStatus.REACHED_OUT,
                JobStatus.APPLIED
            ])
        ).all()
        
        needing_follow_up = []
        for app in applications:
            # Get last email sent
            last_email = self.session.query(EmailRecord).filter_by(
                job_application_id=app.id,
                status=EmailStatus.SENT
            ).order_by(EmailRecord.sent_at.desc()).first()
            
            if not last_email:
                continue
            
            # Check if enough time has passed
            # Normalize sent_at to timezone-aware (UTC) if it's naive
            if last_email.sent_at:
                sent_at = last_email.sent_at
                if sent_at.tzinfo is None:
                    # Assume naive datetime is UTC
                    sent_at = sent_at.replace(tzinfo=timezone.utc)
                
                if sent_at < cutoff_date:
                    # Count existing follow-ups
                    # IMPORTANT: EmailRecord is one row per recipient, so we must NOT count rows
                    # (multi-recruiter applications would inflate counts and skip numbers).
                    # Instead, treat follow-ups as the max follow_up_number we've successfully sent.
                    last_follow_up_number = self.session.query(func.max(EmailRecord.follow_up_number)).filter_by(
                        job_application_id=app.id,
                        is_follow_up=True,
                        status=EmailStatus.SENT
                    ).scalar() or 0
                    
                    if last_follow_up_number < Config.MAX_FOLLOW_UPS:
                        needing_follow_up.append(app)
        
        return needing_follow_up
    
    def get_next_follow_up_number(self, job_application_id: int) -> int:
        """Get the next follow-up number for a job application."""
        # EmailRecord is stored per-recipient, so counting rows breaks when an application
        # has multiple recruiters (e.g., 2 recipients => follow_up #1 creates 2 rows,
        # and the next computed number incorrectly becomes 3).
        last_follow_up_number = self.session.query(func.max(EmailRecord.follow_up_number)).filter_by(
            job_application_id=job_application_id,
            is_follow_up=True,
            status=EmailStatus.SENT
        ).scalar() or 0
        
        return int(last_follow_up_number) + 1

    def repair_follow_up_numbers(self, dry_run: bool = True) -> Dict[str, int]:
        """
        Repair follow-up numbering for multi-recruiter applications.

        Historical bug: follow-up numbers were computed using a row-count. Since we store
        one EmailRecord per recipient, apps with multiple recruiters could skip numbers
        (e.g. two recipients => follow_up #1 created two rows => next computed as #3).

        This repair renumbers follow-up "waves" per application so they become sequential
        again (1..N), preserving chronological order by sent_at.

        Args:
            dry_run: If True, do not write changes; just report what would change.

        Returns:
            Dict with counts: applications_scanned, applications_changed, rows_updated.
        """
        stats = {"applications_scanned": 0, "applications_changed": 0, "rows_updated": 0}

        app_ids = [
            row[0]
            for row in self.session.query(EmailRecord.job_application_id)
            .filter_by(is_follow_up=True, status=EmailStatus.SENT)
            .distinct()
            .all()
        ]

        for app_id in app_ids:
            stats["applications_scanned"] += 1

            # Distinct follow-up numbers ordered by the first time they were sent.
            waves = (
                self.session.query(
                    EmailRecord.follow_up_number,
                    func.min(EmailRecord.sent_at).label("first_sent_at"),
                )
                .filter_by(job_application_id=app_id, is_follow_up=True, status=EmailStatus.SENT)
                .filter(EmailRecord.follow_up_number > 0)
                .group_by(EmailRecord.follow_up_number)
                .order_by(func.min(EmailRecord.sent_at).asc())
                .all()
            )

            existing_numbers = [w.follow_up_number for w in waves]
            if not existing_numbers:
                continue

            desired_numbers = list(range(1, len(existing_numbers) + 1))
            if existing_numbers == desired_numbers:
                continue

            mapping = {old: new for old, new in zip(existing_numbers, desired_numbers)}
            logger.warning(
                f"Repairing follow-up numbers for job_application_id={app_id}: {mapping} (dry_run={dry_run})"
            )
            stats["applications_changed"] += 1

            for old_num, new_num in mapping.items():
                if old_num == new_num:
                    continue
                q = (
                    self.session.query(EmailRecord)
                    .filter_by(job_application_id=app_id, is_follow_up=True, status=EmailStatus.SENT)
                    .filter(EmailRecord.follow_up_number == old_num)
                )
                if dry_run:
                    stats["rows_updated"] += q.count()
                else:
                    stats["rows_updated"] += q.update(
                        {EmailRecord.follow_up_number: new_num},
                        synchronize_session=False,
                    )

        if not dry_run:
            self.session.commit()

        return stats
    
    def update_job_status(
        self,
        job_application_id: int,
        status: JobStatus,
        notes: Optional[str] = None
    ):
        """Update job application status."""
        app = self.session.query(JobApplication).get(job_application_id)
        if not app:
            raise ValueError(f"Job application {job_application_id} not found")
        
        app.status = status
        app.updated_at = datetime.now(timezone.utc)
        
        if notes:
            app.notes = notes
        
        if status == JobStatus.CLOSED:
            app.closed_at = datetime.now(timezone.utc)
        elif status == JobStatus.INTERVIEW_SCHEDULED:
            app.status = JobStatus.INTERVIEW_SCHEDULED
        
        self.session.commit()
        logger.info(f"Updated job application {job_application_id} status to {status}")
    
    def record_response(
        self,
        job_application_id: int,
        response_type: str,
        response_text: Optional[str] = None,
        email_record_id: Optional[int] = None
    ):
        """Record a response from a recruiter."""
        response = ResponseRecord(
            job_application_id=job_application_id,
            email_record_id=email_record_id,
            response_type=response_type,
            response_text=response_text,
            responded_at=datetime.now(timezone.utc)
        )
        
        self.session.add(response)
        
        # Update job status based on response type
        if response_type == 'positive' or response_type == 'interview_request':
            self.update_job_status(job_application_id, JobStatus.INTERVIEW_SCHEDULED)
        elif response_type == 'negative':
            self.update_job_status(job_application_id, JobStatus.REJECTED)
        
        self.session.commit()
        logger.info(f"Recorded response for job application {job_application_id}: {response_type}")
    
    def get_statistics(self) -> dict:
        """Get application statistics."""
        total_apps = self.session.query(JobApplication).count()
        by_status = {}
        for status in JobStatus:
            count = self.session.query(JobApplication).filter_by(status=status).count()
            by_status[status.value] = count
        
        total_emails = self.session.query(EmailRecord).filter_by(status=EmailStatus.SENT).count()
        follow_ups = self.session.query(EmailRecord).filter_by(
            is_follow_up=True,
            status=EmailStatus.SENT
        ).count()
        
        return {
            'total_applications': total_apps,
            'by_status': by_status,
            'total_emails_sent': total_emails,
            'follow_ups_sent': follow_ups
        }

