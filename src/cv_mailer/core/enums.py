"""
Enumeration types for CV Mailer application.
"""

from enum import Enum


class JobStatus(str, Enum):
    """Job application status."""

    DRAFT = "draft"
    REACHED_OUT = "reached_out"
    APPLIED = "applied"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class EmailType(str, Enum):
    """Type of email sent."""

    FIRST_CONTACT = "first_contact"
    FOLLOW_UP = "follow_up"


class EmailStatus(str, Enum):
    """Email delivery status."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
