"""
Application-related schemas.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, constr
from datetime import datetime

from cv_mailer.core import JobStatus


class RecruiterSummary(BaseModel):
    """Recruiter summary in application responses."""
    
    id: int
    name: Optional[str]
    email: str
    
    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    """Basic application response."""
    
    id: int
    company_name: str
    position: str
    status: JobStatus
    location: Optional[str] = None
    created_at: datetime
    applied_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApplicationListResponse(ApplicationResponse):
    """Application in list responses."""
    pass


class ApplicationDetailResponse(ApplicationResponse):
    """Detailed application response."""
    
    job_posting_url: Optional[str] = None
    expected_salary: Optional[str] = None
    custom_message: Optional[str] = None
    notes: Optional[str] = None
    updated_at: datetime
    closed_at: Optional[datetime] = None
    recruiters: List[RecruiterSummary] = []
    emails_count: int = 0


class UpdateStatusRequest(BaseModel):
    """Request to update application status."""
    
    status: JobStatus
    notes: Optional[constr(max_length=5000)] = Field(None, description="Optional notes")


class EmailActionResponse(BaseModel):
    """Response from email actions (reach-out, follow-up)."""
    
    message: str
    sent_count: int
    failed_count: int


class ApplicationSearchRequest(BaseModel):
    """Application search parameters."""
    
    query: constr(min_length=1) = Field(..., description="Search term")
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)

