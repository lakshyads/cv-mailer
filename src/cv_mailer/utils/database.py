"""
Database connection and session management utilities.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from cv_mailer.config.settings import Config
from cv_mailer.core.models import Base

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
