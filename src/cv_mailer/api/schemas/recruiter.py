"""
Recruiter-related schemas.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime


class RecruiterResponse(BaseModel):
    """Basic recruiter response."""

    id: int
    name: Optional[str]
    email: str
    applications_count: int = 0

    class Config:
        from_attributes = True


class ApplicationSummary(BaseModel):
    """Application summary in recruiter detail."""

    id: int
    company_name: str
    position: str
    status: str

    class Config:
        from_attributes = True


class RecruiterDetailResponse(BaseModel):
    """Detailed recruiter response."""

    id: int
    name: Optional[str]
    email: str
    created_at: datetime
    applications: List[ApplicationSummary] = []

    class Config:
        from_attributes = True
