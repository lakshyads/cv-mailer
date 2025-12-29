"""
Logging utilities for consistent logging across the application.
"""

import logging
import functools
from typing import Callable, Any


def log_function_call(logger: logging.Logger, level: int = logging.INFO):
    """
    Decorator to log function calls with parameters and results.
    
    Args:
        logger: Logger instance to use
        level: Logging level (default: INFO)
        
    Usage:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Log function entry
            logger.log(
                level,
                f"Calling {func.__name__} with args={args}, kwargs={kwargs}"
            )
            
            try:
                result = func(*args, **kwargs)
                logger.log(
                    level,
                    f"{func.__name__} completed successfully"
                )
                return result
            except Exception as e:
                logger.error(
                    f"{func.__name__} failed with error: {e}",
                    exc_info=True
                )
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
                    f"{func.__name__} executed in {execution_time:.3f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed after {execution_time:.3f}s: {e}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator

