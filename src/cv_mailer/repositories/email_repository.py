"""
Repository for email record data access.
"""

import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from cv_mailer.core import EmailRecord, EmailStatus
from cv_mailer.utils.logging_utils import log_function_call

logger = logging.getLogger(__name__)


class EmailRepository:
    """Repository for EmailRecord entities."""
    
    def __init__(self, session: Session):
        self.session = session
    
    @log_function_call(logger)
    def find_by_application(self, application_id: int) -> List[EmailRecord]:
        """
        Find all emails for an application.
        
        Args:
            application_id: Application ID
            
        Returns:
            List of emails
        """
        return (
            self.session.query(EmailRecord)
            .filter_by(job_application_id=application_id)
            .order_by(EmailRecord.created_at.desc())
            .all()
        )
    
    @log_function_call(logger)
    def find_all(
        self,
        status: Optional[EmailStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[EmailRecord], int]:
        """
        Find emails with optional filtering.
        
        Args:
            status: Optional status filter
            limit: Maximum results
            offset: Offset for pagination
            
        Returns:
            Tuple of (emails, total_count)
        """
        query = self.session.query(EmailRecord)
        
        if status:
            query = query.filter_by(status=status)
        
        total = query.count()
        emails = query.order_by(EmailRecord.created_at.desc()).offset(offset).limit(limit).all()
        
        return emails, total

