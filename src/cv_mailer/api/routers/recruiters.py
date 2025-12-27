"""
API endpoints for recruiters.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from cv_mailer.services import ApplicationTracker
from cv_mailer.core import Recruiter
from cv_mailer.api.dependencies import get_tracker

router = APIRouter()


@router.get("/recruiters")
async def list_recruiters(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    tracker: ApplicationTracker = Depends(get_tracker),
):
    """
    List all recruiters.

    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        tracker: Application tracker dependency

    Returns:
        List of recruiters
    """
    query = tracker.session.query(Recruiter)
    recruiters = query.offset(offset).limit(limit).all()

    return {
        "total": query.count(),
        "limit": limit,
        "offset": offset,
        "recruiters": [
            {
                "id": recruiter.id,
                "name": recruiter.name,
                "email": recruiter.email,
                "applications_count": len(recruiter.job_applications),
            }
            for recruiter in recruiters
        ],
    }


@router.get("/recruiters/{recruiter_id}")
async def get_recruiter(recruiter_id: int, tracker: ApplicationTracker = Depends(get_tracker)):
    """
    Get details of a specific recruiter.

    Args:
        recruiter_id: Recruiter ID
        tracker: Application tracker dependency

    Returns:
        Recruiter details
    """
    recruiter = tracker.session.query(Recruiter).get(recruiter_id)

    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    return {
        "id": recruiter.id,
        "name": recruiter.name,
        "email": recruiter.email,
        "created_at": recruiter.created_at.isoformat() if recruiter.created_at else None,
        "applications": [
            {
                "id": app.id,
                "company_name": app.company_name,
                "position": app.position,
                "status": app.status.value,
            }
            for app in recruiter.job_applications
        ],
    }
