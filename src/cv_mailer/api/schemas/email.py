"""
Email-related schemas.
"""

from typing import Optional, List
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
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EmailDetailResponse(EmailResponse):
    """Detailed email response including body."""

    body: str


class ConversationThread(BaseModel):
    """Email conversation thread response."""

    thread_id: Optional[str] = None
    recipient_email: str
    recipient_name: Optional[str] = None
    recipient_id: Optional[int] = None
    emails: List[EmailDetailResponse] = []  # Use EmailDetailResponse to include body
    message_count: int = 0
    last_activity: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """List of conversations for an application."""

    application_id: int
    conversations: List[ConversationThread] = []
    total_conversations: int = 0
