"""
FastAPI-based REST API for CV Mailer.
"""

from cv_mailer.api.app import app, run_server

__all__ = ["app", "run_server"]
