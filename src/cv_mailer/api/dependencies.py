"""
FastAPI dependencies for dependency injection.
"""

from typing import Generator
from cv_mailer.services import ApplicationTracker
from cv_mailer.utils import get_session


def get_tracker() -> Generator[ApplicationTracker, None, None]:
    """
    Dependency to get ApplicationTracker instance.

    Yields:
        ApplicationTracker instance with database session
    """
    tracker = ApplicationTracker()
    try:
        yield tracker
    finally:
        tracker.session.close()


def get_db_session():
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
