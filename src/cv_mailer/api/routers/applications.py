"""
Application API endpoints - Thin controller layer.

NO BUSINESS LOGIC HERE - just request/response handling.
All business logic is in ApplicationService.
"""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query

from cv_mailer.services import ApplicationService, EmailService
from cv_mailer.core import JobStatus
from cv_mailer.core.status_constants import TERMINAL_STATUSES
from cv_mailer.api.dependencies import get_application_service, get_email_service
from cv_mailer.api.schemas import (
    ApplicationListResponse,
    ApplicationDetailResponse,
    UpdateStatusRequest,
    EmailActionResponse,
    PaginatedResponse,
    TimelineEvent,
)
from cv_mailer.api.schemas.email import (
    ConversationListResponse,
    ConversationThread,
    EmailResponse,
    EmailDetailResponse,
)
from cv_mailer.utils.date import parse_iso_datetime_optional
from cv_mailer.utils.exceptions import (
    NotFoundError,
    ValidationError,
    BusinessLogicError,
    format_error_response,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/applications", response_model=PaginatedResponse[ApplicationListResponse])
async def list_applications(
    status: Optional[str] = Query(
        None, description="Filter by single status (deprecated, use statuses)"
    ),
    statuses: Optional[List[str]] = Query(None, description="Filter by multiple statuses"),
    q: Optional[str] = Query(None, description="Search query for company name or position"),
    date_from: Optional[str] = Query(None, description="Start date for filtering (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date for filtering (ISO format)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: Optional[str] = Query(
        None, description="Sort by field (created_at, updated_at, status)"
    ),
    order: Optional[str] = Query(None, description="Sort order (asc, desc)"),
    service: ApplicationService = Depends(get_application_service),
):
    """List job applications with optional filtering, searching, and sorting."""
    # Parse status filters
    job_status = None
    job_statuses = None

    try:
        if statuses and len(statuses) > 0:
            # Multi-select: parse list of statuses
            job_statuses = [JobStatus(s.lower()) for s in statuses if s]
        elif status:
            # Single status (backward compatibility)
            job_status = JobStatus(status.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status: {str(e)}")

    # Validate sort_by
    if sort_by and sort_by not in ["created_at", "updated_at", "status"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by: {sort_by}. Must be one of: created_at, updated_at, status",
        )

    # Validate order
    if order and order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, detail=f"Invalid order: {order}. Must be one of: asc, desc"
        )

    # Parse date filters using utility function
    try:
        date_from_dt = parse_iso_datetime_optional(date_from)
        date_to_dt = parse_iso_datetime_optional(date_to)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    applications, total = service.list_applications(
        status=job_status,
        statuses=job_statuses,
        search=q,
        date_from=date_from_dt,
        date_to=date_to_dt,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order,
    )

    # Build response with last main flow status for terminal states
    items = []
    for app in applications:
        response = ApplicationListResponse.from_orm(app)
        # Get emails count
        response.emails_count = service.get_emails_count(app.id)
        # Get last main flow status for terminal states
        if app.status in TERMINAL_STATUSES:
            response.last_main_flow_status = service.get_last_main_flow_status(app.id)
        items.append(response)

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items,
        sort_by=sort_by,
        order=order,
    )


@router.get("/applications/{application_id}", response_model=ApplicationDetailResponse)
async def get_application(
    application_id: int,
    service: ApplicationService = Depends(get_application_service),
):
    """Get details of a specific job application."""
    try:
        app = service.get_application(application_id)
        emails_count = service.get_emails_count(application_id)

        response = ApplicationDetailResponse.from_orm(app)
        response.emails_count = emails_count
        # Get last main flow status for terminal states
        if app.status in [
            JobStatus.REJECTED,
            JobStatus.GHOSTED,
            JobStatus.WITHDRAWN,
            JobStatus.OFFER_REJECTED,
        ]:
            response.last_main_flow_status = service.get_last_main_flow_status(application_id)

        return response
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting application {application_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    request: UpdateStatusRequest,
    service: ApplicationService = Depends(get_application_service),
):
    """Update job application status."""
    try:
        service.update_status(application_id, request.status, request.notes)
        logger.info(f"API: Updated application {application_id} status to {request.status.value}")
        return {"message": "Status updated successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Error updating status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/applications/{application_id}/trigger-reach-out", response_model=EmailActionResponse)
async def trigger_reach_out(
    application_id: int,
    recruiter_id: Optional[int] = Query(None, description="Optional recruiter ID"),
    email_service: EmailService = Depends(get_email_service),
):
    """Trigger first contact email for an application."""
    try:
        logger.info(f"API: Triggering reach-out for application {application_id}")
        result = email_service.send_first_contact(application_id, recruiter_id)

        message = (
            f"Reach-out triggered: {result['sent_count']} sent, {result['failed_count']} failed"
        )
        logger.info(f"API: {message}")

        return EmailActionResponse(
            message=message,
            sent_count=result["sent_count"],
            failed_count=result["failed_count"],
        )
    except NotFoundError as e:
        logger.warning(f"API: Invalid request for reach-out: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        logger.warning(f"API: Business logic error for reach-out: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Error triggering reach-out: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/applications/{application_id}/trigger-follow-up", response_model=EmailActionResponse)
async def trigger_follow_up(
    application_id: int,
    recruiter_id: Optional[int] = Query(
        None, description="Optional recruiter ID (deprecated, use recruiter_ids)"
    ),
    recruiter_ids: Optional[List[int]] = Query(None, description="Optional list of recruiter IDs"),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Trigger follow-up email for an application.
    Respects FOLLOW_UP_DAYS configuration.
    Supports selective follow-ups by specifying recruiter_ids.
    """
    try:
        logger.info(f"API: Triggering follow-up for application {application_id}")

        result = email_service.send_follow_up(application_id, recruiter_id, recruiter_ids)

        message = (
            f"Follow-up triggered: {result['sent_count']} sent, {result['failed_count']} failed"
        )
        logger.info(f"API: {message}")

        return EmailActionResponse(
            message=message,
            sent_count=result["sent_count"],
            failed_count=result["failed_count"],
        )
    except NotFoundError as e:
        logger.warning(f"API: Invalid request for follow-up: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        logger.warning(f"API: Business logic error for follow-up: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Error triggering follow-up: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/applications/{application_id}/timeline")
async def get_application_timeline(
    application_id: int,
    service: ApplicationService = Depends(get_application_service),
):
    """Get timeline of events for an application."""
    try:
        logger.info(f"API: Fetching timeline for application {application_id}")
        events = service.get_application_timeline(application_id)

        timeline_events = [TimelineEvent(**event) for event in events]

        return {"application_id": application_id, "events": timeline_events}
    except NotFoundError as e:
        logger.warning(f"API: Invalid request for timeline: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"API: Error getting timeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/applications/{application_id}/conversations", response_model=ConversationListResponse)
async def get_application_conversations(
    application_id: int,
    email_service: EmailService = Depends(get_email_service),
):
    """Get all email conversations for an application, grouped by recruiter."""
    try:
        logger.info(f"API: Fetching conversations for application {application_id}")

        # Get conversations from service layer (business logic)
        conversation_data = email_service.get_conversations_for_application(application_id)

        # Convert to response models
        conversations = [
            ConversationThread(
                thread_id=conv["thread_id"],
                recipient_email=conv["recipient_email"],
                recipient_name=conv["recipient_name"],
                recipient_id=conv["recipient_id"],
                emails=[EmailDetailResponse.from_orm(e) for e in conv["emails"]],
                message_count=conv["message_count"],
                last_activity=conv["last_activity"],
            )
            for conv in conversation_data
        ]

        return ConversationListResponse(
            application_id=application_id,
            conversations=conversations,
            total_conversations=len(conversations),
        )
    except NotFoundError as e:
        logger.warning(f"API: Invalid request for conversations: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"API: Error getting conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/applications/{application_id}/conversations/{recruiter_id}", response_model=ConversationThread
)
async def get_recruiter_conversation(
    application_id: int,
    recruiter_id: int,
    service: ApplicationService = Depends(get_application_service),
    email_service: EmailService = Depends(get_email_service),
):
    """Get email conversation thread for a specific recruiter."""
    try:
        logger.info(
            f"API: Fetching conversation for application {application_id}, recruiter {recruiter_id}"
        )

        # Get application to verify it exists and find recruiter
        app = service.get_application(application_id)

        recruiter = None
        for r in app.recruiters:
            if r.id == recruiter_id:
                recruiter = r
                break

        if not recruiter:
            raise NotFoundError(
                f"Recruiter {recruiter_id} not found for application {application_id}"
            )

        # Get all emails for this application and recruiter
        all_emails = email_service.get_emails_for_application(application_id)
        emails = [e for e in all_emails if e.recipient_email == recruiter.email]

        # Sort emails chronologically (oldest first for conversation flow)
        emails.sort(key=lambda e: e.sent_at or e.created_at or datetime.min)

        # Get thread_id and last activity
        thread_id = None
        last_activity = None
        if emails:
            thread_id = emails[0].thread_id
            last_email = emails[-1]
            last_activity = last_email.sent_at or last_email.created_at

        return ConversationThread(
            thread_id=thread_id,
            recipient_email=recruiter.email,
            recipient_name=recruiter.name,
            recipient_id=recruiter.id,
            emails=[EmailDetailResponse.from_orm(e) for e in emails],
            message_count=len(emails),
            last_activity=last_activity,
        )
    except NotFoundError as e:
        logger.warning(f"API: Invalid request for recruiter conversation: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"API: Error getting recruiter conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
