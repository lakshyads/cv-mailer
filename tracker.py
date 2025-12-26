"""
Tracking system for job applications and email communications.
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta
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
            sent_at=datetime.utcnow() if gmail_message_id else None
        )
        
        self.session.add(email_record)
        
        # Update job application status
        if job_app.status == JobStatus.DRAFT:
            job_app.status = JobStatus.REACHED_OUT
            job_app.applied_at = datetime.utcnow()
        
        self.session.commit()
        logger.info(f"Recorded email sent for job application {job_application_id}")
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
        cutoff_date = datetime.utcnow() - timedelta(days=Config.FOLLOW_UP_DAYS)
        
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
            if last_email.sent_at and last_email.sent_at < cutoff_date:
                # Count existing follow-ups
                follow_up_count = self.session.query(EmailRecord).filter_by(
                    job_application_id=app.id,
                    is_follow_up=True,
                    status=EmailStatus.SENT
                ).count()
                
                if follow_up_count < Config.MAX_FOLLOW_UPS:
                    needing_follow_up.append(app)
        
        return needing_follow_up
    
    def get_next_follow_up_number(self, job_application_id: int) -> int:
        """Get the next follow-up number for a job application."""
        count = self.session.query(EmailRecord).filter_by(
            job_application_id=job_application_id,
            is_follow_up=True,
            status=EmailStatus.SENT
        ).count()
        
        return count + 1
    
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
        app.updated_at = datetime.utcnow()
        
        if notes:
            app.notes = notes
        
        if status == JobStatus.CLOSED:
            app.closed_at = datetime.utcnow()
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
            responded_at=datetime.utcnow()
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

