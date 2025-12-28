"""
Application API endpoints - Thin controller layer.

NO BUSINESS LOGIC HERE - just request/response handling.
All business logic is in ApplicationService.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from cv_mailer.services import ApplicationService, EmailService
from cv_mailer.core import JobStatus
from cv_mailer.api.dependencies import get_application_service, get_email_service
from cv_mailer.api.schemas import (
    ApplicationListResponse,
    ApplicationDetailResponse,
    UpdateStatusRequest,
    EmailActionResponse,
    PaginatedResponse,
    TimelineEvent,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/applications", response_model=PaginatedResponse[ApplicationListResponse])
async def list_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ApplicationService = Depends(get_application_service),
):
    """List job applications with optional filtering."""
    try:
        job_status = JobStatus(status.lower()) if status else None
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    applications, total = service.list_applications(status=job_status, limit=limit, offset=offset)

    # Build response with last main flow status for terminal states
    items = []
    for app in applications:
        response = ApplicationListResponse.from_orm(app)
        # Get last main flow status for terminal states
        if app.status in [
            JobStatus.REJECTED,
            JobStatus.GHOSTED,
            JobStatus.WITHDRAWN,
            JobStatus.OFFER_REJECTED,
        ]:
            response.last_main_flow_status = service.get_last_main_flow_status(app.id)
        items.append(response)

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items,
    )


@router.get("/applications/search", response_model=PaginatedResponse[ApplicationListResponse])
async def search_applications(
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ApplicationService = Depends(get_application_service),
):
    """Search job applications by company name or position."""
    applications, total = service.search_applications(query=q, limit=limit, offset=offset)

    # Build response with last main flow status for terminal states
    items = []
    for app in applications:
        response = ApplicationListResponse.from_orm(app)
        # Get last main flow status for terminal states
        if app.status in [
            JobStatus.REJECTED,
            JobStatus.GHOSTED,
            JobStatus.WITHDRAWN,
            JobStatus.OFFER_REJECTED,
        ]:
            response.last_main_flow_status = service.get_last_main_flow_status(app.id)
        items.append(response)

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items,
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
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
    except ValueError as e:
        # ValueError can be from validation (400) or not found (404)
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            # Status transition validation error
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"API: Error updating status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
    except ValueError as e:
        logger.warning(f"API: Invalid request for reach-out: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Error triggering reach-out: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{application_id}/trigger-follow-up", response_model=EmailActionResponse)
async def trigger_follow_up(
    application_id: int,
    recruiter_id: Optional[int] = Query(None, description="Optional recruiter ID"),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Trigger follow-up email for an application.
    Respects FOLLOW_UP_DAYS configuration.
    """
    try:
        logger.info(f"API: Triggering follow-up for application {application_id}")

        result = email_service.send_follow_up(application_id, recruiter_id)

        message = (
            f"Follow-up triggered: {result['sent_count']} sent, {result['failed_count']} failed"
        )
        logger.info(f"API: {message}")

        return EmailActionResponse(
            message=message,
            sent_count=result["sent_count"],
            failed_count=result["failed_count"],
        )
    except ValueError as e:
        logger.warning(f"API: Invalid request for follow-up: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Error triggering follow-up: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
    except ValueError as e:
        logger.warning(f"API: Invalid request for timeline: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"API: Error getting timeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
