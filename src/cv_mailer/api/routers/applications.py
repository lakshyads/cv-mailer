"""
API endpoints for job applications.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from cv_mailer.services import ApplicationTracker
from cv_mailer.core import JobApplication, JobStatus
from cv_mailer.api.dependencies import get_tracker

router = APIRouter()


@router.get("/applications")
async def list_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tracker: ApplicationTracker = Depends(get_tracker),
):
    """
    List job applications with optional filtering.

    Args:
        status: Filter by job status
        limit: Maximum number of results
        offset: Number of results to skip
        tracker: Application tracker dependency

    Returns:
        List of job applications
    """
    query = tracker.session.query(JobApplication)

    if status:
        try:
            job_status = JobStatus(status.lower())
            query = query.filter_by(status=job_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    applications = query.offset(offset).limit(limit).all()

    return {
        "total": query.count(),
        "limit": limit,
        "offset": offset,
        "applications": [
            {
                "id": app.id,
                "company_name": app.company_name,
                "position": app.position,
                "status": app.status.value,
                "location": app.location,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "applied_at": app.applied_at.isoformat() if app.applied_at else None,
            }
            for app in applications
        ],
    }


@router.get("/applications/{application_id}")
async def get_application(application_id: int, tracker: ApplicationTracker = Depends(get_tracker)):
    """
    Get details of a specific job application.

    Args:
        application_id: Job application ID
        tracker: Application tracker dependency

    Returns:
        Job application details
    """
    app = tracker.session.query(JobApplication).get(application_id)

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    return {
        "id": app.id,
        "company_name": app.company_name,
        "position": app.position,
        "status": app.status.value,
        "location": app.location,
        "job_posting_url": app.job_posting_url,
        "expected_salary": app.expected_salary,
        "custom_message": app.custom_message,
        "notes": app.notes,
        "created_at": app.created_at.isoformat() if app.created_at else None,
        "updated_at": app.updated_at.isoformat() if app.updated_at else None,
        "applied_at": app.applied_at.isoformat() if app.applied_at else None,
        "closed_at": app.closed_at.isoformat() if app.closed_at else None,
        "recruiters": [{"id": r.id, "name": r.name, "email": r.email} for r in app.recruiters],
        "emails_count": len(app.emails),
    }


@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    status: str,
    notes: Optional[str] = None,
    tracker: ApplicationTracker = Depends(get_tracker),
):
    """
    Update job application status.

    Args:
        application_id: Job application ID
        status: New status
        notes: Optional notes
        tracker: Application tracker dependency

    Returns:
        Success message
    """
    try:
        job_status = JobStatus(status.lower())
        tracker.update_job_status(application_id, job_status, notes)
        return {"message": "Status updated successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications/search")
async def search_applications(
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tracker: ApplicationTracker = Depends(get_tracker),
):
    """
    Search job applications by company name or position.

    Args:
        q: Search query
        limit: Maximum number of results
        offset: Number of results to skip
        tracker: Application tracker dependency

    Returns:
        List of matching job applications
    """
    search_term = f"%{q}%"
    query = tracker.session.query(JobApplication).filter(
        (JobApplication.company_name.ilike(search_term))
        | (JobApplication.position.ilike(search_term))
    )

    applications = query.offset(offset).limit(limit).all()

    return {
        "total": query.count(),
        "limit": limit,
        "offset": offset,
        "query": q,
        "applications": [
            {
                "id": app.id,
                "company_name": app.company_name,
                "position": app.position,
                "status": app.status.value,
                "location": app.location,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "applied_at": app.applied_at.isoformat() if app.applied_at else None,
            }
            for app in applications
        ],
    }
