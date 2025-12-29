"""
Gmail API authentication utilities.
"""

import logging
import pickle
import os
import httplib2
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth_httplib2 import AuthorizedHttp

from cv_mailer.config import Config
from cv_mailer.utils.logging_utils import log_function_call

logger = logging.getLogger(__name__)


class GmailAuthenticator:
    """Handle Gmail API authentication."""

    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    TOKEN_FILE = "gmail_token.pickle"

    @classmethod
    @log_function_call(logger)
    def authenticate(cls):
        """
        Authenticate with Gmail API and return service object.

        Returns:
            Gmail API service object
        """
        creds = None

        # Try to load existing token
        if os.path.exists(cls.TOKEN_FILE):
            with open(cls.TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    # Don't log here - token refresh errors will bubble up to API layer
                    raise
            else:
                if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
                    logger.error(
                        f"Google credentials file not found: {Config.GOOGLE_CREDENTIALS_FILE}"
                    )
                    raise FileNotFoundError(
                        f"Google credentials file not found: {Config.GOOGLE_CREDENTIALS_FILE}"
                    )
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        Config.GOOGLE_CREDENTIALS_FILE, cls.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    # Don't log here - authentication errors will bubble up to API layer
                    raise

            # Save credentials for next run
            with open(cls.TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)

        # Configure HTTP client with timeouts to prevent hanging
        # The timeout ensures fast failure (30s) instead of hanging
        # Authorize the HTTP client with credentials, then pass only http
        http_client = httplib2.Http(timeout=30)  # 30 second timeout
        authorized_http = AuthorizedHttp(creds, http=http_client)
        service = build(
            "gmail",
            "v1",
            http=authorized_http,
            # cache_discovery defaults to True, which caches discovery doc
        )
        logger.info("Successfully authenticated with Gmail API")
        return service
