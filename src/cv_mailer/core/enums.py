"""
Enumeration types for CV Mailer application.
"""

from enum import Enum


class JobStatus(str, Enum):
    """
    Job application status.

    Status flow:
    1. APPLIED - Application added to sheet (already applied to company)
    2. REACHED_OUT - We've reached out to recruiter(s) about this application
    3. [Rest of the flow based on responses]
    """

    # Initial states
    APPLIED = "applied"  # Default: Application already submitted to company
    REACHED_OUT = "reached_out"  # We've contacted recruiter(s)

    # Interview process
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_IN_PROGRESS = "interview_in_progress"
    RESULT_AWAITED = "result_awaited"

    # Final states (positive)
    OFFER_RECEIVED = "offer_received"
    ACCEPTED = "accepted"

    # Final states (negative)
    REJECTED = "rejected"  # Rejected by company/interviewer
    GHOSTED = "ghosted"
    WITHDRAWN = "withdrawn"
    OFFER_REJECTED = "offer_rejected"  # Applicant rejected/declined the offer


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
