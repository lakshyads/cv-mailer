"""
Status transition validation - ensures one-directional status flow.
"""

import logging

from cv_mailer.core import JobStatus
from cv_mailer.utils.exceptions import BusinessLogicError
from cv_mailer.utils.logging_utils import log_function_call

logger = logging.getLogger(__name__)


class StatusValidator:
    """Validates status transitions according to business rules."""

    # Define valid transitions from each status
    VALID_TRANSITIONS = {
        JobStatus.APPLIED: {
            JobStatus.REACHED_OUT,  # Can only move forward
        },
        JobStatus.REACHED_OUT: {
            JobStatus.INTERVIEW_SCHEDULED,
            JobStatus.REJECTED,
            JobStatus.GHOSTED,
            JobStatus.WITHDRAWN,
        },
        JobStatus.INTERVIEW_SCHEDULED: {
            JobStatus.INTERVIEW_IN_PROGRESS,
            JobStatus.REJECTED,
            JobStatus.GHOSTED,
            JobStatus.WITHDRAWN,
        },
        JobStatus.INTERVIEW_IN_PROGRESS: {
            JobStatus.RESULT_AWAITED,
            JobStatus.REJECTED,
            JobStatus.GHOSTED,
            JobStatus.WITHDRAWN,
        },
        JobStatus.RESULT_AWAITED: {
            JobStatus.OFFER_RECEIVED,
            JobStatus.REJECTED,
            JobStatus.GHOSTED,
            # WITHDRAWN not allowed here - too close to offer stage
        },
        JobStatus.OFFER_RECEIVED: {
            JobStatus.ACCEPTED,
            JobStatus.OFFER_REJECTED,  # Applicant rejects/declines the offer
            # WITHDRAWN not allowed - use OFFER_REJECTED instead
        },
        # Terminal states - cannot transition from these
        JobStatus.ACCEPTED: set(),
        JobStatus.REJECTED: set(),
        JobStatus.GHOSTED: set(),
        JobStatus.WITHDRAWN: set(),
        JobStatus.OFFER_REJECTED: set(),
    }

    @classmethod
    @log_function_call(logger)
    def can_transition(cls, from_status: JobStatus, to_status: JobStatus) -> tuple[bool, str]:
        """
        Check if a status transition is valid.

        Args:
            from_status: Current status
            to_status: Desired new status

        Returns:
            Tuple of (is_valid: bool, reason: str)
        """
        # Same status is always valid (no-op)
        if from_status == to_status:
            return True, "OK"

        # Check if transition is allowed
        allowed_transitions = cls.VALID_TRANSITIONS.get(from_status, set())

        if to_status not in allowed_transitions:
            # Build consistent error message format
            if not allowed_transitions:
                reason = (
                    f"Cannot change status from '{from_status.value}' to '{to_status.value}'. "
                    f"'{from_status.value}' is a terminal state and cannot be changed."
                )
            else:
                # Sort transitions for consistent ordering
                allowed = sorted([s.value for s in allowed_transitions])
                allowed_str = ", ".join(allowed)
                reason = (
                    f"Cannot change status from '{from_status.value}' to '{to_status.value}'. "
                    f"Valid transitions from '{from_status.value}': {allowed_str}"
                )
            return False, reason

        return True, "OK"

    @classmethod
    @log_function_call(logger)
    def validate_transition(cls, from_status: JobStatus, to_status: JobStatus):
        """
        Validate status transition, raising BusinessLogicError if invalid.

        Args:
            from_status: Current status
            to_status: Desired new status

        Raises:
            BusinessLogicError: If transition is not allowed
        """
        is_valid, reason = cls.can_transition(from_status, to_status)
        if not is_valid:
            raise BusinessLogicError(reason)
