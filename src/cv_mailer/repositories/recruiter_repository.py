"""
Repository for recruiter data access.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from cv_mailer.core import Recruiter, JobApplication
from cv_mailer.core.models import job_application_recruiter


class RecruiterRepository:
    """Repository for Recruiter entities."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def find_by_id(self, recruiter_id: int) -> Optional[Recruiter]:
        """
        Find recruiter by ID with applications loaded.
        
        Args:
            recruiter_id: Recruiter ID
            
        Returns:
            Recruiter or None
        """
        return (
            self.session.query(Recruiter)
            .options(joinedload(Recruiter.job_applications))
            .filter_by(id=recruiter_id)
            .first()
        )
    
    def find_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Tuple[Recruiter, int]], int]:
        """
        Find recruiters with application counts (optimized).
        
        Args:
            limit: Maximum results
            offset: Offset for pagination
            
        Returns:
            Tuple of (list of (recruiter, app_count), total_count)
        """
        # Query with application count using join
        query = (
            self.session.query(
                Recruiter,
                func.count(job_application_recruiter.c.job_application_id).label('app_count')
            )
            .outerjoin(job_application_recruiter)
            .group_by(Recruiter.id)
        )
        
        total = self.session.query(Recruiter).count()
        results = query.offset(offset).limit(limit).all()
        
        return results, total

