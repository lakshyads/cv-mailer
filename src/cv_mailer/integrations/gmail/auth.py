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
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GOOGLE_CREDENTIALS_FILE, cls.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(cls.TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)

        # Configure HTTP client with timeouts to prevent hanging
        # The timeout ensures fast failure (30s) instead of hanging
        # Discovery document is cached by default, so it only downloads once
        http = httplib2.Http(timeout=30)  # 30 second timeout
        service = build(
            "gmail",
            "v1",
            credentials=creds,
            http=http,
            # cache_discovery defaults to True, which caches discovery doc
        )
        logger.info("Successfully authenticated with Gmail API")
        return service
