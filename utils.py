"""
Utility functions for CV Mailer.
"""
import logging
from typing import Optional
from datetime import datetime
from models import get_session, JobApplication, EmailRecord, JobStatus

logger = logging.getLogger(__name__)


def get_job_application_by_id(job_id: int) -> Optional[JobApplication]:
    """Get job application by ID."""
    session = get_session()
    try:
        return session.query(JobApplication).get(job_id)
    finally:
        session.close()


def list_job_applications(status: Optional[JobStatus] = None, limit: int = 50):
    """List job applications, optionally filtered by status."""
    session = get_session()
    try:
        query = session.query(JobApplication)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(JobApplication.created_at.desc()).limit(limit).all()
    finally:
        session.close()


def get_email_history(job_application_id: int):
    """Get email history for a job application."""
    session = get_session()
    try:
        return session.query(EmailRecord).filter_by(
            job_application_id=job_application_id
        ).order_by(EmailRecord.created_at.desc()).all()
    finally:
        session.close()


def format_date(dt: Optional[datetime]) -> str:
    """Format datetime for display."""
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")

