"""
Email-related schemas.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from cv_mailer.core import EmailType, EmailStatus


class EmailResponse(BaseModel):
    """Email record response."""
    
    id: int
    job_application_id: Optional[int] = None
    email_type: EmailType
    subject: str
    recipient_email: str
    recipient_name: Optional[str] = None
    status: EmailStatus
    is_follow_up: bool = False
    follow_up_number: int = 0
    sent_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailDetailResponse(EmailResponse):
    """Detailed email response including body."""
    
    body: str

