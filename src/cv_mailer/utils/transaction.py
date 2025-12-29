"""
Transaction management utilities for database operations.

Provides context managers and decorators for safe transaction handling
with automatic rollback on errors.
"""

import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@contextmanager
def transaction(session: Session) -> Generator[Session, None, None]:
    """
    Context manager for database transactions with automatic rollback on errors.

    Usage:
        with transaction(session) as tx_session:
            # Perform operations
            tx_session.add(object)
            # Commit happens automatically on success
            # Rollback happens automatically on exception
    """
    try:
        yield session
        session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction rolled back due to error: {e}", exc_info=True)
        raise


def safe_commit(session: Session, operation_name: str = "operation") -> bool:
    """
    Safely commit a session with error handling and logging.

    Args:
        session: SQLAlchemy session
        operation_name: Name of the operation for logging

    Returns:
        True if commit succeeded, False otherwise
    """
    try:
        session.commit()
        logger.debug(f"{operation_name} committed successfully")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"{operation_name} failed to commit: {e}", exc_info=True)
        return False
