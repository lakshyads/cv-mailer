"""
Repository for job application data access.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_

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
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[JobApplication], int]:
        """
        Find applications with optional filtering.
        
        Args:
            status: Optional status filter
            limit: Maximum results
            offset: Offset for pagination
            
        Returns:
            Tuple of (applications, total_count)
        """
        query = self.session.query(JobApplication)
        
        if status:
            query = query.filter_by(status=status)
        
        total = query.count()
        applications = query.offset(offset).limit(limit).all()
        
        return applications, total
    
    def search(
        self,
        search_term: str,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[JobApplication], int]:
        """
        Search applications by company name or position.
        
        Args:
            search_term: Search term
            limit: Maximum results
            offset: Offset for pagination
            
        Returns:
            Tuple of (applications, total_count)
        """
        pattern = f"%{search_term}%"
        query = self.session.query(JobApplication).filter(
            or_(
                JobApplication.company_name.ilike(pattern),
                JobApplication.position.ilike(pattern)
            )
        )
        
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

