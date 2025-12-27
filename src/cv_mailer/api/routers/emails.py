"""
API endpoints for email records.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from cv_mailer.services import ApplicationTracker
from cv_mailer.core import EmailRecord, EmailStatus
from cv_mailer.api.dependencies import get_tracker

router = APIRouter()


@router.get("/applications/{application_id}/emails")
async def get_application_emails(
    application_id: int, tracker: ApplicationTracker = Depends(get_tracker)
):
    """
    Get all emails for a specific job application.

    Args:
        application_id: Job application ID
        tracker: Application tracker dependency

    Returns:
        List of email records
    """
    emails = (
        tracker.session.query(EmailRecord)
        .filter_by(job_application_id=application_id)
        .order_by(EmailRecord.created_at.desc())
        .all()
    )

    return {
        "application_id": application_id,
        "emails": [
            {
                "id": email.id,
                "email_type": email.email_type.value,
                "subject": email.subject,
                "recipient_email": email.recipient_email,
                "recipient_name": email.recipient_name,
                "status": email.status.value,
                "is_follow_up": email.is_follow_up,
                "follow_up_number": email.follow_up_number,
                "sent_at": email.sent_at.isoformat() if email.sent_at else None,
                "created_at": email.created_at.isoformat() if email.created_at else None,
            }
            for email in emails
        ],
    }


@router.get("/emails")
async def list_emails(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tracker: ApplicationTracker = Depends(get_tracker),
):
    """
    List all email records with optional filtering.

    Args:
        status: Filter by email status
        limit: Maximum number of results
        offset: Number of results to skip
        tracker: Application tracker dependency

    Returns:
        List of email records
    """
    query = tracker.session.query(EmailRecord)

    if status:
        try:
            email_status = EmailStatus(status.lower())
            query = query.filter_by(status=email_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    emails = query.order_by(EmailRecord.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": query.count(),
        "limit": limit,
        "offset": offset,
        "emails": [
            {
                "id": email.id,
                "job_application_id": email.job_application_id,
                "email_type": email.email_type.value,
                "subject": email.subject,
                "recipient_email": email.recipient_email,
                "recipient_name": email.recipient_name,
                "status": email.status.value,
                "is_follow_up": email.is_follow_up,
                "follow_up_number": email.follow_up_number,
                "sent_at": email.sent_at.isoformat() if email.sent_at else None,
            }
            for email in emails
        ],
    }
