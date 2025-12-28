"""
Repository for job application data access.
"""

from typing import List, Optional, Tuple, Literal
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, desc, asc

from cv_mailer.core import JobApplication, JobStatus, EmailRecord


class ApplicationRepository:
    """Repository for JobApplication entities."""

    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, application_id: int) -> Optional[JobApplication]:
        """
        Find application by ID with relationships loaded.

        Args:
            application_id: Application ID

        Returns:
            JobApplication or None
        """
        return (
            self.session.query(JobApplication)
            .options(joinedload(JobApplication.recruiters))
            .filter_by(id=application_id)
            .first()
        )

    def find_all(
        self,
        status: Optional[JobStatus] = None,
        statuses: Optional[List[JobStatus]] = None,
        search_term: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: Optional[Literal["created_at", "updated_at", "status"]] = None,
        order: Optional[Literal["asc", "desc"]] = None,
    ) -> Tuple[List[JobApplication], int]:
        """
        Find applications with optional filtering, searching, and sorting.

        Args:
            status: Optional single status filter (for backward compatibility)
            statuses: Optional list of statuses to filter by
            search_term: Optional search term for company name or position
            date_from: Optional start date for filtering by updated_at
            date_to: Optional end date for filtering by updated_at
            limit: Maximum results
            offset: Offset for pagination
            sort_by: Field to sort by (created_at, updated_at, status)
            order: Sort order (asc, desc). Defaults to desc for updated_at, asc otherwise.

        Returns:
            Tuple of (applications, total_count)
        """
        query = self.session.query(JobApplication)

        # Handle status filtering - prioritize statuses list over single status
        if statuses:
            query = query.filter(JobApplication.status.in_(statuses))
        elif status:
            query = query.filter_by(status=status)

        if search_term:
            pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    JobApplication.company_name.ilike(pattern),
                    JobApplication.position.ilike(pattern),
                )
            )

        if date_from:
            query = query.filter(JobApplication.updated_at >= date_from)
        if date_to:
            query = query.filter(JobApplication.updated_at <= date_to)

        # Apply sorting
        if sort_by:
            if sort_by == "created_at":
                column = JobApplication.created_at
            elif sort_by == "updated_at":
                column = JobApplication.updated_at
            elif sort_by == "status":
                column = JobApplication.status
            else:
                column = JobApplication.updated_at  # Default fallback

            # Default order: desc for updated_at, asc for others
            if order is None:
                order = "desc" if sort_by == "updated_at" else "asc"

            if order == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        else:
            # Default: sort by updated_at descending
            query = query.order_by(desc(JobApplication.updated_at))

        total = query.count()
        applications = query.offset(offset).limit(limit).all()

        return applications, total

    def search(
        self,
        search_term: str,
        limit: int = 50,
        offset: int = 0,
        sort_by: Optional[Literal["created_at", "updated_at", "status"]] = None,
        order: Optional[Literal["asc", "desc"]] = None,
    ) -> Tuple[List[JobApplication], int]:
        """
        Search applications by company name or position with optional sorting.

        Args:
            search_term: Search term
            limit: Maximum results
            offset: Offset for pagination
            sort_by: Field to sort by (created_at, updated_at, status)
            order: Sort order (asc, desc). Defaults to desc for updated_at, asc otherwise.

        Returns:
            Tuple of (applications, total_count)
        """
        pattern = f"%{search_term}%"
        query = self.session.query(JobApplication).filter(
            or_(JobApplication.company_name.ilike(pattern), JobApplication.position.ilike(pattern))
        )

        # Apply sorting
        if sort_by:
            if sort_by == "created_at":
                column = JobApplication.created_at
            elif sort_by == "updated_at":
                column = JobApplication.updated_at
            elif sort_by == "status":
                column = JobApplication.status
            else:
                column = JobApplication.updated_at  # Default fallback

            # Default order: desc for updated_at, asc for others
            if order is None:
                order = "desc" if sort_by == "updated_at" else "asc"

            if order == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        else:
            # Default: sort by updated_at descending
            query = query.order_by(desc(JobApplication.updated_at))

        total = query.count()
        applications = query.offset(offset).limit(limit).all()

        return applications, total

    def count_by_status(self, status: JobStatus) -> int:
        """
        Count applications by status.

        Args:
            status: Job status

        Returns:
            Count
        """
        return self.session.query(JobApplication).filter_by(status=status).count()

    def get_emails_count(self, application_id: int) -> int:
        """
        Get count of emails for an application (optimized).

        Args:
            application_id: Application ID

        Returns:
            Email count
        """
        return (
            self.session.query(func.count(EmailRecord.id))
            .filter_by(job_application_id=application_id)
            .scalar()
        )
