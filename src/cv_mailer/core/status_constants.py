"""
Status constants for job applications.

Centralizes status categorization to eliminate duplication and ensure consistency.
"""

from cv_mailer.core.enums import JobStatus

# Main flow statuses (progressive states in the application process)
MAIN_FLOW_STATUSES = {
    JobStatus.APPLIED,
    JobStatus.REACHED_OUT,
    JobStatus.INTERVIEW_SCHEDULED,
    JobStatus.INTERVIEW_IN_PROGRESS,
    JobStatus.RESULT_AWAITED,
    JobStatus.OFFER_RECEIVED,
    JobStatus.ACCEPTED,
}

# Terminal states (final states that cannot transition further)
TERMINAL_STATUSES = {
    JobStatus.REJECTED,
    JobStatus.GHOSTED,
    JobStatus.WITHDRAWN,
    JobStatus.OFFER_REJECTED,
    JobStatus.ACCEPTED,  # Also terminal (positive outcome)
}

# Statuses that should set closed_at when reached
STATUSES_THAT_CLOSE_APPLICATION = {
    JobStatus.REJECTED,
    JobStatus.GHOSTED,
    JobStatus.ACCEPTED,
    JobStatus.WITHDRAWN,
    JobStatus.OFFER_REJECTED,
}

# Interview stage statuses (for statistics)
INTERVIEW_STAGE_STATUSES = {
    JobStatus.INTERVIEW_SCHEDULED,
    JobStatus.INTERVIEW_IN_PROGRESS,
    JobStatus.RESULT_AWAITED,
    JobStatus.OFFER_RECEIVED,
    JobStatus.ACCEPTED,
}

# Offer stage statuses (for statistics)
OFFER_STAGE_STATUSES = {
    JobStatus.OFFER_RECEIVED,
    JobStatus.ACCEPTED,
}

# Statuses that indicate we've reached out (for statistics)
REACHED_OUT_STATUSES = {
    JobStatus.REACHED_OUT,
    JobStatus.INTERVIEW_SCHEDULED,
    JobStatus.INTERVIEW_IN_PROGRESS,
    JobStatus.RESULT_AWAITED,
    JobStatus.OFFER_RECEIVED,
    JobStatus.ACCEPTED,
    JobStatus.REJECTED,
    JobStatus.GHOSTED,
    JobStatus.WITHDRAWN,
    JobStatus.OFFER_REJECTED,
}
