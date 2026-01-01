"""
Database migration utilities for schema changes.

This module provides utilities to migrate existing databases when schema changes are made.
"""

import logging
from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError

from cv_mailer.utils.database import get_engine, get_session
from cv_mailer.core.models import Base

logger = logging.getLogger(__name__)


def migrate_add_email_threading_fields():
    """
    Add email threading fields to EmailRecord table if they don't exist.
    
    This migration adds:
    - thread_id (String)
    - in_reply_to (String)
    - references (Text)
    - Index on thread_id
    
    Safe to run multiple times (checks if columns exist first).
    """
    engine = get_engine()
    session = get_session()
    
    try:
        inspector = inspect(engine)
        columns = [col["name"] for col in inspector.get_columns("email_records")]
        
        with engine.connect() as conn:
            # Add thread_id column if it doesn't exist
            if "thread_id" not in columns:
                logger.info("Adding thread_id column to email_records table")
                conn.execute(text("ALTER TABLE email_records ADD COLUMN thread_id VARCHAR(255)"))
                conn.commit()
                logger.info("✓ Added thread_id column")
            else:
                logger.debug("thread_id column already exists")
            
            # Add in_reply_to column if it doesn't exist
            if "in_reply_to" not in columns:
                logger.info("Adding in_reply_to column to email_records table")
                conn.execute(text("ALTER TABLE email_records ADD COLUMN in_reply_to VARCHAR(255)"))
                conn.commit()
                logger.info("✓ Added in_reply_to column")
            else:
                logger.debug("in_reply_to column already exists")
            
            # Add references column if it doesn't exist
            # Note: "references" is a SQLite reserved keyword, but SQLAlchemy handles it
            if "references" not in columns:
                logger.info("Adding references column to email_records table")
                conn.execute(text('ALTER TABLE email_records ADD COLUMN "references" TEXT'))
                conn.commit()
                logger.info("✓ Added references column")
            else:
                logger.debug("references column already exists")
            
            # Add email_message_id column if it doesn't exist
            if "email_message_id" not in columns:
                logger.info("Adding email_message_id column to email_records table")
                conn.execute(text("ALTER TABLE email_records ADD COLUMN email_message_id VARCHAR(255)"))
                conn.commit()
                logger.info("✓ Added email_message_id column")
            else:
                logger.debug("email_message_id column already exists")
            
            # Check if index exists
            indexes = [idx["name"] for idx in inspector.get_indexes("email_records")]
            if "ix_email_thread_id" not in indexes:
                logger.info("Adding index on thread_id column")
                try:
                    conn.execute(text("CREATE INDEX ix_email_thread_id ON email_records(thread_id)"))
                    conn.commit()
                    logger.info("✓ Added thread_id index")
                except OperationalError as e:
                    # Index might already exist (race condition or manual creation)
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        logger.debug("thread_id index already exists")
                    else:
                        raise
            else:
                logger.debug("thread_id index already exists")
        
        logger.info("Migration completed successfully")
        return True
        
    except OperationalError as e:
        logger.error(f"Error during migration: {e}")
        session.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}", exc_info=True)
        session.rollback()
        return False
    finally:
        session.close()


def run_migrations():
    """Run all pending migrations."""
    logger.info("Running database migrations...")
    
    # Migration 1: Add email threading fields
    success = migrate_add_email_threading_fields()
    
    if success:
        logger.info("✓ All migrations completed successfully")
    else:
        logger.error("✗ Some migrations failed")
    
    return success

