"""
FastAPI dependencies for dependency injection.

Provides service layer instances to API endpoints.
NO business logic here - just dependency injection.
"""

from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from cv_mailer.services import (
    ApplicationService,
    EmailService,
    RecruiterService,
    StatisticsService,
    SyncService,
)
from cv_mailer.repositories import (
    ApplicationRepository,
    EmailRepository,
    RecruiterRepository,
)
from cv_mailer.integrations import GmailSender
from cv_mailer.services.tracker import ApplicationTracker
from cv_mailer.utils import get_session


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Yields:
        SQLAlchemy session
    """
    session = get_session()
    try:
        yield session
    finally:
        session.close()


# Service Layer Dependencies - What API endpoints should use


def get_application_service(
    session: Session = Depends(get_db_session),
) -> ApplicationService:
    """
    Get application service.

    This is what API endpoints should use for application operations.
    """
    repository = ApplicationRepository(session)
    return ApplicationService(repository=repository)


def get_email_service(
    session: Session = Depends(get_db_session),
) -> EmailService:
    """
    Get email service.

    This is what API endpoints should use for email operations.
    """
    tracker = ApplicationTracker()  # Uses its own session internally
    gmail_sender = GmailSender()
    return EmailService(gmail_sender=gmail_sender, tracker=tracker)


def get_recruiter_service(
    session: Session = Depends(get_db_session),
) -> RecruiterService:
    """
    Get recruiter service.

    This is what API endpoints should use for recruiter operations.
    """
    repository = RecruiterRepository(session)
    return RecruiterService(repository=repository)


def get_statistics_service(
    session: Session = Depends(get_db_session),
) -> StatisticsService:
    """
    Get statistics service.

    This is what API endpoints should use for statistics.
    """
    return StatisticsService(session=session)


def get_sync_service() -> SyncService:
    """
    Get sync service.

    This is what API endpoints should use for Google Sheets sync operations.
    """
    return SyncService()


# Legacy dependencies (for backward compatibility during migration)


def get_tracker() -> Generator[ApplicationTracker, None, None]:
    """
    LEGACY: Get ApplicationTracker instance.

    TODO: Phase out in favor of ApplicationService.
    """
    tracker = ApplicationTracker()
    try:
        yield tracker
    finally:
        tracker.session.close()


def get_application_repository(session: Session = Depends(get_db_session)) -> ApplicationRepository:
    """
    INTERNAL USE ONLY: Direct repository access.

    API endpoints should use ApplicationService instead.
    """
    return ApplicationRepository(session)


def get_email_repository(session: Session = Depends(get_db_session)) -> EmailRepository:
    """
    INTERNAL USE ONLY: Direct repository access.

    API endpoints should use EmailService instead.
    """
    return EmailRepository(session)


def get_recruiter_repository(session: Session = Depends(get_db_session)) -> RecruiterRepository:
    """
    INTERNAL USE ONLY: Direct repository access.

    API endpoints should use RecruiterService instead.
    """
    return RecruiterRepository(session)
