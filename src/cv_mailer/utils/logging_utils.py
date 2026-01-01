"""
Logging utilities for consistent logging across the application.
"""

import logging
import functools
import gzip
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Optional

from cv_mailer.config import Config


def log_function_call(logger: logging.Logger, level: Optional[int] = None):
    """
    Decorator to log function calls with parameters and results.

    Args:
        logger: Logger instance to use
        level: Logging level (default: DEBUG if VERBOSE_LOGGING,
               else no logging)

    Usage:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            ...
    """
    if level is None:
        level = logging.DEBUG if Config.VERBOSE_LOGGING else logging.NOTSET

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Only log if level is set (not NOTSET)
            if level != logging.NOTSET:
                # Log function entry (simplified - don't log full args)
                logger.log(level, f"Calling {func.__name__}")

            try:
                result = func(*args, **kwargs)
                if level != logging.NOTSET:
                    logger.log(level, f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed with error: {e}", exc_info=True)
                raise

        return wrapper

    return decorator


def log_execution_time(logger: logging.Logger, level: int = logging.DEBUG):
    """
    Decorator to log function execution time.

    Args:
        logger: Logger instance to use
        level: Logging level (default: DEBUG)

    Usage:
        @log_execution_time(logger)
        def my_function():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.log(
                    level,
                    f"{func.__name__} executed in {execution_time:.3f}s",
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed after " f"{execution_time:.3f}s: {e}",
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


def _get_date_based_log_filename(base_log_file: str, date: Optional[datetime] = None) -> str:
    """
    Generate date-based log filename.

    Args:
        base_log_file: Base log file path (e.g., 'logs/cv_mailer.log')
        date: Date to use (default: today)

    Returns:
        Date-based filename (e.g., 'logs/cv_mailer_2026-01-01.log')
    """
    if date is None:
        date = datetime.now()

    log_path = Path(base_log_file)
    directory = log_path.parent
    base_name = log_path.stem  # 'cv_mailer' (without extension)
    date_str = date.strftime("%Y-%m-%d")
    return str(directory / f"{base_name}_{date_str}.log")


def _compress_log_file(source: Path, dest: Path) -> bool:
    """
    Compress a log file using gzip.

    Args:
        source: Source log file path
        dest: Destination compressed file path

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(source, "rb") as f_in:
            with gzip.open(dest, "wb") as f_out:
                f_out.writelines(f_in)
        os.remove(source)
        return True
    except Exception as e:
        print(
            f"Error compressing log file {source} to {dest}: {e}",
            file=sys.stderr,
        )
        return False


class DateBasedRotatingFileHandler(logging.FileHandler):
    """
    Custom file handler that rotates logs based on date changes.

    Supports both:
    - Startup rotation (for start/stop usage patterns)
    - Midnight rotation (for continuously running applications)

    Creates date-based log files: cv_mailer_YYYY-MM-DD.log
    """

    def __init__(
        self,
        base_log_file: str,
        retention_days: int = 30,
        compress: bool = True,
        encoding: str = "utf-8",
    ):
        """
        Initialize the date-based rotating file handler.

        Args:
            base_log_file: Base log file path (e.g., 'logs/cv_mailer.log')
            retention_days: Number of days to keep log files
            compress: Whether to compress rotated files
            encoding: File encoding (default: utf-8)
        """
        self.base_log_file = base_log_file
        self.retention_days = retention_days
        self.compress = compress
        self.current_date = datetime.now().date()
        self.current_log_file = _get_date_based_log_filename(base_log_file, datetime.now())

        # Ensure log directory exists
        log_path = Path(self.current_log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize with today's log file
        super().__init__(self.current_log_file, encoding=encoding)

    def emit(self, record):
        """
        Emit a log record, checking for date change and rotating if needed.
        """
        # Check if date has changed (midnight rotation)
        today = datetime.now().date()
        if today != self.current_date:
            self._rotate_to_new_date(today)

        # Emit the log record
        super().emit(record)

    def _rotate_to_new_date(self, new_date: date):
        """
        Rotate to a new date's log file.

        Args:
            new_date: The new date to rotate to
        """
        old_log_file = self.current_log_file

        # Close the current file
        self.close()

        # Compress the old log file if needed
        if self.compress and Path(old_log_file).exists():
            compressed_file = f"{old_log_file}.gz"
            if _compress_log_file(Path(old_log_file), Path(compressed_file)):
                print(f"Rotated and compressed log: {old_log_file} -> " f"{compressed_file}")

        # Update to new date
        self.current_date = new_date
        self.current_log_file = _get_date_based_log_filename(
            self.base_log_file,
            datetime.combine(new_date, datetime.min.time()),
        )

        # Open new log file
        self.baseFilename = self.current_log_file
        self.stream = self._open()

        # Clean up old files beyond retention period
        self._cleanup_old_files()

    def _cleanup_old_files(self):
        """Clean up log files older than retention period."""
        log_path = Path(self.base_log_file)
        directory = log_path.parent
        base_name = log_path.stem
        cutoff_date = datetime.now().date() - timedelta(days=self.retention_days)

        pattern = f"{base_name}_*.log*"
        for log_file in directory.glob(pattern):
            try:
                # Extract date from filename
                filename = log_file.stem
                if filename.endswith(".log"):
                    filename = filename[:-4]

                if "_" not in filename:
                    continue

                # Extract date part: filename is like "cv_mailer_2025-12-28"
                # Split by "_" and take the last part (the date)
                parts = filename.split("_")
                if len(parts) < 2:
                    continue

                # Date is the last part after the last underscore
                date_part = parts[-1]
                file_date = datetime.strptime(date_part, "%Y-%m-%d").date()

                if file_date < cutoff_date:
                    log_file.unlink()
                    print(f"Deleted old log (beyond retention): " f"{log_file.name}")
            except (ValueError, IndexError):
                continue
            except Exception as cleanup_error:
                print(
                    f"Error cleaning up {log_file.name}: {cleanup_error}",
                    file=sys.stderr,
                )


def _rotate_old_log_files(base_log_file: str, retention_days: int, compress: bool):
    """
    Rotate old log files on startup.

    Checks for log files from previous days and rotates/compresses them.
    Also cleans up log files older than retention period.
    Handles migration of old non-dated log files.

    Args:
        base_log_file: Base log file path (e.g., 'logs/cv_mailer.log')
        retention_days: Number of days to keep log files
        compress: Whether to compress rotated files
    """
    log_path = Path(base_log_file)
    directory = log_path.parent
    base_name = log_path.stem  # 'cv_mailer'

    today = datetime.now().date()
    cutoff_date = today - timedelta(days=retention_days)

    # Handle migration of old non-dated log file (if exists)
    if log_path.exists():
        # Get file modification date to determine which date to use
        file_mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
        file_date = file_mtime.date()

        # Create dated filename for the old log file
        old_dated_file = _get_date_based_log_filename(base_log_file, file_mtime)
        old_dated_path = Path(old_dated_file)

        # If dated file doesn't exist, rename the old file
        if not old_dated_path.exists():
            try:
                log_path.rename(old_dated_path)
                print(f"Migrated old log file: {log_path.name} -> " f"{old_dated_path.name}")
            except Exception as migrate_error:
                print(
                    f"Error migrating old log file: {migrate_error}",
                    file=sys.stderr,
                )
        else:
            # If dated file exists, append old file content and remove it
            try:
                with open(log_path, "rb") as old_file:
                    with open(old_dated_path, "ab") as dated_file:
                        dated_file.write(b"\n--- Appended from old log file ---\n")
                        dated_file.write(old_file.read())
                log_path.unlink()
                print(f"Merged old log file into: {old_dated_path.name}")
            except Exception as merge_error:
                print(
                    f"Error merging old log file: {merge_error}",
                    file=sys.stderr,
                )

    # Find all log files matching the pattern
    pattern = f"{base_name}_*.log*"
    for log_file in directory.glob(pattern):
        try:
            # Extract date from filename
            # Format: cv_mailer_YYYY-MM-DD.log or
            # cv_mailer_YYYY-MM-DD.log.gz
            filename = log_file.stem  # Remove .gz if present
            if filename.endswith(".log"):
                filename = filename[:-4]  # Remove .log

            if "_" not in filename:
                continue

            # Extract date part: filename is like "cv_mailer_2025-12-28"
            # Split by "_" and take the last part (the date)
            parts = filename.split("_")
            if len(parts) < 2:
                continue

            # Date is the last part after the last underscore
            date_part = parts[-1]
            file_date = datetime.strptime(date_part, "%Y-%m-%d").date()

            # If file is from a previous day (not today), rotate it
            if file_date < today:
                if not log_file.name.endswith(".gz"):
                    # Compress if not already compressed
                    if compress:
                        compressed_name = f"{log_file.name}.gz"
                        compressed_path = directory / compressed_name
                        if _compress_log_file(log_file, compressed_path):
                            print(f"Compressed old log: {log_file.name} -> " f"{compressed_name}")
                        else:
                            # If compression fails, keep the file
                            continue
                    else:
                        # Just rename to indicate it's old (optional)
                        pass

            # Clean up files older than retention period
            if file_date < cutoff_date:
                try:
                    log_file.unlink()
                    print(f"Deleted old log file (beyond retention): " f"{log_file.name}")
                except Exception as delete_error:
                    print(
                        f"Error deleting old log file {log_file.name}: " f"{delete_error}",
                        file=sys.stderr,
                    )

        except (ValueError, IndexError):
            # Skip files that don't match the expected pattern
            continue
        except Exception as process_error:
            print(
                f"Error processing log file {log_file.name}: " f"{process_error}",
                file=sys.stderr,
            )


def setup_logging():
    """
    Setup logging with date-based files and startup rotation.

    This function should be called once at application startup.
    - Creates log files with today's date: cv_mailer_YYYY-MM-DD.log
    - Rotates/compresses old log files from previous days on startup
    - Cleans up log files older than retention period
    - Works for start/stop usage patterns (not just continuous running)
    """
    base_log_file = Config.LOG_FILE
    log_path = Path(base_log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Rotate old log files on startup (before creating new logger)
    _rotate_old_log_files(base_log_file, Config.LOG_RETENTION_DAYS, Config.LOG_COMPRESS)

    # Get log level
    log_level = getattr(logging, Config.LOG_LEVEL, logging.INFO)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Setup file handler with date-based rotation
    # This handler supports both startup rotation and midnight rotation
    file_handler = DateBasedRotatingFileHandler(
        base_log_file=base_log_file,
        retention_days=Config.LOG_RETENTION_DAYS,
        compress=Config.LOG_COMPRESS,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # Clear any existing handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate logs
    root_logger.propagate = False
