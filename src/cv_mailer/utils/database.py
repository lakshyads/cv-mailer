"""
Database connection and session management utilities.
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from cv_mailer.config.settings import Config
from cv_mailer.core.models import Base

logger = logging.getLogger(__name__)

# Database setup
_engine = None
_Session = None


def get_engine():
    """Create or get database engine with proper SQLite configuration."""
    global _engine
    if _engine is None:
        # Configure SQLite for better concurrency:
        # - connect_args with timeout allows waiting for locks (default 5s)
        # - pool_pre_ping checks connections before using them
        _engine = create_engine(
            f"sqlite:///{Config.DATABASE_PATH}",
            echo=False,
            connect_args={
                "timeout": 30,  # Wait up to 30 seconds for locks
                "check_same_thread": False,  # Allow multi-threaded access
            },
            pool_pre_ping=True,  # Verify connections before using
        )
        Base.metadata.create_all(_engine)

        # Enable WAL (Write-Ahead Logging) mode for better concurrency
        # This allows multiple readers and a single writer simultaneously
        with _engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.commit()

    return _engine


def get_session():
    """Get database session."""
    global _Session
    engine = get_engine()
    if _Session is None:
        _Session = sessionmaker(bind=engine)
    return _Session()


def init_database():
    """Initialize database tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def checkpoint_wal():
    """
    Checkpoint the WAL file, merging pending changes into main database.

    This is useful to call on application shutdown to ensure all changes
    are persisted and the WAL file is cleaned up.

    Returns:
        tuple: (pages_moved, pages_written, pages_in_wal) or None on error
    """
    global _engine
    if _engine is None:
        logger.debug("No database engine to checkpoint")
        return None

    try:
        with _engine.connect() as conn:
            result = conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
            row = result.fetchone()
            if row:
                pages_moved, pages_written, pages_in_wal = row
                logger.info(
                    f"WAL checkpoint: {pages_moved} moved, "
                    f"{pages_written} written, {pages_in_wal} remaining"
                )
                return (pages_moved, pages_written, pages_in_wal)
    except Exception as e:
        logger.warning(f"Error during WAL checkpoint: {e}")
        return None


def close_database():
    """
    Close database connections and checkpoint WAL file.

    Call this on application shutdown to ensure proper cleanup.
    """
    global _engine, _Session

    # Checkpoint WAL before closing
    checkpoint_wal()

    # Close engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("Database engine closed")

    _Session = None
