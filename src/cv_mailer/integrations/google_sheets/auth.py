"""
Google Sheets API authentication utilities.
"""

import logging
import pickle
import os
import httplib2
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_httplib2 import AuthorizedHttp

from cv_mailer.config import Config
from cv_mailer.utils.logging_utils import log_function_call

logger = logging.getLogger(__name__)


class SheetsAuthenticator:
    """Handle Google Sheets API authentication."""

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    TOKEN_FILE = "token.pickle"

    @classmethod
    @log_function_call(logger)
    def authenticate(cls):
        """
        Authenticate with Google Sheets API and return service object.

        Returns:
            Google Sheets API service object
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
                # Try service account first, then OAuth
                if os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
                    try:
                        # Check if it's a service account JSON
                        creds = service_account.Credentials.from_service_account_file(
                            Config.GOOGLE_CREDENTIALS_FILE,
                            scopes=cls.SCOPES,
                        )
                    except Exception:
                        # If not service account, use OAuth flow
                        flow = InstalledAppFlow.from_client_secrets_file(
                            Config.GOOGLE_CREDENTIALS_FILE, cls.SCOPES
                        )
                        creds = flow.run_local_server(port=0)

                # Save credentials for next run (only for OAuth)
                if not isinstance(creds, service_account.Credentials):
                    with open(cls.TOKEN_FILE, "wb") as token:
                        pickle.dump(creds, token)

        # Configure HTTP client with timeouts to prevent hanging
        # The timeout ensures fast failure (30s) instead of hanging
        # Authorize the HTTP client with credentials, then pass only http
        http_client = httplib2.Http(timeout=30)  # 30 second timeout
        authorized_http = AuthorizedHttp(creds, http=http_client)
        service = build(
            "sheets",
            "v4",
            http=authorized_http,
            # cache_discovery defaults to True, which caches the discovery doc
        )
        logger.info("Successfully authenticated with Google Sheets API")
        return service
