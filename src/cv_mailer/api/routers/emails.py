"""
Email API endpoints - Thin controller layer.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from cv_mailer.core import EmailStatus
from cv_mailer.services import EmailService
from cv_mailer.api.dependencies import get_email_service
from cv_mailer.api.schemas import EmailResponse, EmailDetailResponse, PaginatedResponse

router = APIRouter()


@router.get("/applications/{application_id}/emails")
async def get_application_emails(
    application_id: int,
    service: EmailService = Depends(get_email_service),
):
    """Get all emails for a specific job application."""
    emails = service.get_emails_for_application(application_id)

    return {
        "application_id": application_id,
        "emails": [EmailDetailResponse.from_orm(email) for email in emails],
    }


@router.get("/emails", response_model=PaginatedResponse[EmailResponse])
async def list_emails(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: EmailService = Depends(get_email_service),
):
    """List all email records with optional filtering."""
    try:
        email_status = EmailStatus(status.lower()) if status else None
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    emails, total = service.list_emails(status=email_status, limit=limit, offset=offset)

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[EmailResponse.from_orm(email) for email in emails],
    )
