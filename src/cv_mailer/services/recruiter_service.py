"""
Recruiter Service - Centralized business logic for recruiter operations.

This is the SINGLE source of truth for recruiter-related operations.
Both CLI and API use this service.
"""

import logging
from typing import List, Optional, Tuple

from cv_mailer.core import Recruiter
from cv_mailer.repositories import RecruiterRepository
from cv_mailer.utils import get_session, NotFoundError
from cv_mailer.utils.logging_utils import log_function_call

logger = logging.getLogger(__name__)


class RecruiterService:
    """Service for recruiter business logic."""

    def __init__(self, repository: Optional[RecruiterRepository] = None):
        """
        Initialize recruiter service.

        Args:
            repository: Recruiter repository (creates new if None)
        """
        if repository:
            self.repository = repository
        else:
            session = get_session()
            self.repository = RecruiterRepository(session)
            self._owns_session = True

    @log_function_call(logger)
    def get_recruiter(self, recruiter_id: int) -> Recruiter:
        """
        Get recruiter by ID.

        Args:
            recruiter_id: Recruiter ID

        Returns:
            Recruiter

        Raises:
            NotFoundError: If recruiter not found
        """
        recruiter = self.repository.find_by_id(recruiter_id)
        if not recruiter:
            raise NotFoundError(f"Recruiter {recruiter_id} not found")
        return recruiter

    @log_function_call(logger)
    def list_recruiters(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Tuple[Recruiter, int]], int]:
        """
        List recruiters with application counts.

        Args:
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Tuple of (list of (recruiter, app_count), total_count)
        """
        return self.repository.find_all(limit=limit, offset=offset)

    def __del__(self):
        """Cleanup session if owned."""
        if hasattr(self, "_owns_session") and self._owns_session:
            self.repository.session.close()
