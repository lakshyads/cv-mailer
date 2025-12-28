"""
Recruiter API endpoints - Thin controller layer.

NO BUSINESS LOGIC HERE - just request/response handling.
All business logic is in RecruiterService.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from cv_mailer.services import RecruiterService
from cv_mailer.api.dependencies import get_recruiter_service
from cv_mailer.api.schemas import RecruiterResponse, RecruiterDetailResponse, PaginatedResponse

router = APIRouter()


@router.get("/recruiters", response_model=PaginatedResponse[RecruiterResponse])
async def list_recruiters(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: RecruiterService = Depends(get_recruiter_service),
):
    """List all recruiters with application counts."""
    results, total = service.list_recruiters(limit=limit, offset=offset)

    items = [
        RecruiterResponse(
            id=recruiter.id,
            name=recruiter.name,
            email=recruiter.email,
            applications_count=app_count,
        )
        for recruiter, app_count in results
    ]

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items,
    )


@router.get("/recruiters/{recruiter_id}", response_model=RecruiterDetailResponse)
async def get_recruiter(
    recruiter_id: int,
    service: RecruiterService = Depends(get_recruiter_service),
):
    """Get details of a specific recruiter."""
    try:
        recruiter = service.get_recruiter(recruiter_id)
        
        # Manually serialize applications since Pydantic might not handle relationship properly
        applications = [
            {
                "id": app.id,
                "company_name": app.company_name,
                "position": app.position,
                "status": app.status.value,
            }
            for app in recruiter.job_applications
        ]
        
        return RecruiterDetailResponse(
            id=recruiter.id,
            name=recruiter.name,
            email=recruiter.email,
            created_at=recruiter.created_at,
            applications=applications,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
