"""
Gmail client for sending emails with rate limiting and resume attachments.
"""

import logging
import base64
import time
import random
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import make_msgid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from googleapiclient.errors import HttpError
from sqlalchemy.exc import OperationalError

from cv_mailer.config import Config
from cv_mailer.core import DailyEmailStats
from cv_mailer.utils import get_session, ExternalServiceError
from cv_mailer.utils.logging_utils import log_function_call, log_execution_time
from cv_mailer.utils.email_utils import extract_message_id_from_payload
from cv_mailer.integrations.gmail.auth import GmailAuthenticator

logger = logging.getLogger(__name__)


class GmailSender:
    """Gmail client for sending emails with rate limiting."""

    def __init__(self):
        self.service = None
        self._authenticate()

    @log_function_call(logger)
    def _authenticate(self):
        """Authenticate with Gmail API."""
        self.service = GmailAuthenticator.authenticate()

    @log_function_call(logger)
    def _check_rate_limit(self, max_retries: int = 3) -> bool:
        """
        Check if we can send an email based on daily email limits.
        Returns True if we can send, False if daily limit reached.
        """
        for attempt in range(max_retries):
            session = get_session()
            try:
                today = datetime.now(timezone.utc).date()
                today_start = datetime.combine(today, datetime.min.time()).replace(
                    tzinfo=timezone.utc
                )

                # Get today's stats
                stats = (
                    session.query(DailyEmailStats)
                    .filter(DailyEmailStats.date >= today_start)
                    .first()
                )

                if stats:
                    if stats.emails_sent >= Config.DAILY_EMAIL_LIMIT:
                        logger.warning(
                            f"Daily email limit reached: {stats.emails_sent}/{Config.DAILY_EMAIL_LIMIT}"
                        )
                        return False
                    # Log when approaching limit (80% threshold)
                    elif stats.emails_sent >= int(Config.DAILY_EMAIL_LIMIT * 0.8):
                        logger.info(
                            f"Approaching daily email limit: {stats.emails_sent}/{Config.DAILY_EMAIL_LIMIT} "
                            f"({int((stats.emails_sent / Config.DAILY_EMAIL_LIMIT) * 100)}%)"
                        )
                else:
                    # Create new stats record (don't commit yet, just prepare)
                    # Set date to start of today in UTC
                    today_start_utc = datetime.combine(today, datetime.min.time()).replace(
                        tzinfo=timezone.utc
                    )
                    stats = DailyEmailStats(date=today_start_utc, emails_sent=0)
                    session.add(stats)
                    session.flush()  # Flush to get ID but don't commit yet

                return True

            except OperationalError as e:
                error_str = str(e).lower()
                if "locked" in error_str and attempt < max_retries - 1:
                    wait_time = 0.05 * (2**attempt)
                    logger.warning(
                        f"Database locked while checking rate limit (attempt {attempt + 1}/{max_retries}). Retrying..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Error checking rate limit: {e}")
                    return True  # Allow sending if check fails
            except Exception as e:
                logger.error(f"Error checking rate limit: {e}")
                return True  # Allow sending if check fails
            finally:
                session.close()

        # If all retries failed, allow sending to avoid blocking
        return True

    @log_function_call(logger)
    def _update_rate_limit_stats(self, max_retries: int = 5):
        """Update daily email statistics after sending with retry logic."""
        for attempt in range(max_retries):
            session = get_session()
            try:
                today = datetime.now(timezone.utc).date()
                today_start = datetime.combine(today, datetime.min.time()).replace(
                    tzinfo=timezone.utc
                )

                stats = (
                    session.query(DailyEmailStats)
                    .filter(DailyEmailStats.date >= today_start)
                    .first()
                )

                if not stats:
                    # Set date to start of today in UTC
                    today_start_utc = datetime.combine(today, datetime.min.time()).replace(
                        tzinfo=timezone.utc
                    )
                    stats = DailyEmailStats(date=today_start_utc, emails_sent=0)
                    session.add(stats)

                stats.emails_sent += 1
                stats.last_email_sent_at = datetime.now(timezone.utc)
                session.commit()
                return  # Success, exit the retry loop

            except OperationalError as e:
                session.rollback()
                # Check if it's a database locked error
                error_str = str(e).lower()
                if "locked" in error_str or "database is locked" in error_str:
                    if attempt < max_retries - 1:
                        # Exponential backoff: wait 0.1s, 0.2s, 0.4s, 0.8s, 1.6s
                        wait_time = 0.1 * (2**attempt)
                        logger.warning(
                            f"Database locked while updating rate limit stats (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {wait_time:.2f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"Error updating rate limit stats after {max_retries} attempts: {e}"
                        )
                else:
                    # Other operational error, log and exit
                    logger.error(f"Database operational error updating rate limit stats: {e}")
                    break
            except Exception as e:
                session.rollback()
                logger.error(f"Unexpected error updating rate limit stats: {e}")
                break
            finally:
                session.close()

    @log_function_call(logger)
    def _create_message(
        self,
        to: str,
        subject: str,
        body: str,
        resume_path: Optional[str] = None,
        resume_drive_link: Optional[str] = None,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
    ) -> dict:
        """Create email message with optional resume attachment."""
        # Validate body is not empty
        if not body or len(body.strip()) == 0:
            logger.error("Email body is empty! Cannot send email without content.")
            raise ValueError("Email body cannot be empty")

        body_with_link = body
        if resume_drive_link and resume_drive_link not in body_with_link:
            drive_link_html = (
                f'<p style="margin-top: 16px;">'
                f"<strong>Resume (Google Drive):</strong> "
                f'<a href="{resume_drive_link}">Lakshya_Dev_Singh_Resume.pdf</a>'
                f"</p>"
            )
            # Prefer injecting before closing tags to keep HTML valid-ish.
            if "</div>" in body_with_link:
                body_with_link = body_with_link.replace("</div>", f"{drive_link_html}</div>", 1)
            elif "</body>" in body_with_link:
                body_with_link = body_with_link.replace("</body>", f"{drive_link_html}</body>", 1)
            else:
                body_with_link = body_with_link + drive_link_html
            logger.info("Added resume drive link to email")

        # Create multipart message (always "mixed" since we may have attachments)
        message = MIMEMultipart("mixed")
        message["to"] = to
        message["from"] = f"{Config.SENDER_NAME} <{Config.GMAIL_USER}>"
        message["subject"] = subject

        # Generate Message-ID header (required for email threading)
        # Python's email library will auto-generate one if not set, but we want control
        # Format: <unique-id@domain> - Gmail will accept this format
        if not message.get("Message-ID"):
            # Generate a Message-ID in the standard format
            # Use domain from sender email or a default
            domain = Config.GMAIL_USER.split("@")[1] if "@" in Config.GMAIL_USER else "gmail.com"
            message_id = make_msgid(domain=domain)
            message["Message-ID"] = message_id
            logger.debug(f"Generated Message-ID header: {message_id}")

        # Add threading headers for replies (required for Gmail threading)
        # The in_reply_to should be the Message-ID header from the previous email
        # Message-ID headers from Gmail are already in format: <message-id@domain>
        if in_reply_to:
            # In-Reply-To should be in angle brackets format: <message-id>
            # Message-ID headers from Gmail are already formatted, but ensure format
            in_reply_to_formatted = (
                in_reply_to if in_reply_to.startswith("<") else f"<{in_reply_to}>"
            )
            message["In-Reply-To"] = in_reply_to_formatted
            logger.info(f"Setting In-Reply-To header: {in_reply_to_formatted}")
        if references:
            # References should be space-separated message IDs in angle brackets
            # Format: <msg-id-1> <msg-id-2> <msg-id-3>
            refs_list = references.split() if isinstance(references, str) else references
            formatted_refs = []
            for ref in refs_list:
                # Remove angle brackets if present, then add them
                # This ensures consistent formatting
                clean_ref = ref.strip("<>").strip()
                if clean_ref:
                    formatted_refs.append(f"<{clean_ref}>")
            if formatted_refs:
                message["References"] = " ".join(formatted_refs)
                logger.info(f"Setting References header: {message['References']}")

        # Attach email body as HTML
        # CRITICAL: For replies, use simpler HTML structure to avoid Gmail collapsing content
        # Gmail collapses content that looks like quoted/previous messages
        if not body_with_link or len(body_with_link.strip()) == 0:
            logger.error("Email body (with link) is empty after processing!")
            raise ValueError("Email body cannot be empty after processing")

        # For replies (when in_reply_to is set), wrap body in minimal HTML structure
        # This helps Gmail recognize it as new content, not quoted content
        if in_reply_to:
            # If body doesn't already have HTML wrapper, add minimal one
            # But keep it simple - no DOCTYPE, html, head tags
            if not body_with_link.strip().startswith("<"):
                # Plain text - wrap in div
                body_with_link = f'<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">{body_with_link}</div>'
            elif "<!DOCTYPE" in body_with_link or "<html>" in body_with_link.lower():
                # Full HTML document - extract just the body content
                # This prevents Gmail from thinking it's quoted content
                import re

                # Try to extract content between <body> tags, or just use as-is if extraction fails
                body_match = re.search(
                    r"<body[^>]*>(.*?)</body>", body_with_link, re.DOTALL | re.IGNORECASE
                )
                if body_match:
                    body_with_link = body_match.group(1).strip()
                    logger.debug("Extracted body content from full HTML document for reply")

        # Log body info for debugging
        body_preview = body_with_link[:200] if len(body_with_link) > 200 else body_with_link
        logger.info(
            f"Attaching email body: length={len(body_with_link)} chars, "
            f"is_reply={bool(in_reply_to)}, "
            f"preview: {body_preview[:100]}..."
        )

        # Attach body as HTML text part with explicit charset
        # This ensures Gmail properly displays the content
        body_part = MIMEText(body_with_link, "html", "utf-8")
        body_part.set_charset("utf-8")
        message.attach(body_part)

        # Add resume attachment if available
        if resume_path and Path(resume_path).exists():
            filename = Path(resume_path).name
            content_type, _ = mimetypes.guess_type(filename)
            if content_type:
                maintype, subtype = content_type.split("/", 1)
            else:
                maintype, subtype = "application", "octet-stream"

            with open(resume_path, "rb") as attachment:
                part = MIMEBase(maintype, subtype)
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=filename)
            message.attach(part)
            logger.info(f"Attached resume file: {resume_path}")

        # Extract Message-ID from the message before encoding
        # This is the Message-ID header we'll use for threading
        email_message_id = message.get("Message-ID", "")

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return {
            "raw": raw_message,
            "thread_id": thread_id,
            "email_message_id": email_message_id,
        }

    @log_function_call(logger)
    @log_execution_time(logger)
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        resume_path: Optional[str] = None,
        resume_drive_link: Optional[str] = None,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
    ) -> Optional[Dict[str, str]]:
        """
        Send an email via Gmail.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (HTML)
            resume_path: Path to resume file to attach
            resume_drive_link: Google Drive link to resume
            thread_id: Gmail thread ID to add email to existing thread
            in_reply_to: Message ID of parent email (for threading)
            references: References header chain (for threading)

        Returns:
            Dictionary with "message_id" and "thread_id" if successful, None otherwise
        """
        # Check daily email limits
        if not self._check_rate_limit():
            logger.warning("Cannot send email: daily rate limit reached")
            return None

        try:
            # Add random delay between emails (100-500ms to avoid detection)
            delay = random.uniform(Config.EMAIL_DELAY_MIN, Config.EMAIL_DELAY_MAX)
            if delay > 0:
                time.sleep(delay)

            # Create message
            message_dict = self._create_message(
                to=to,
                subject=subject,
                body=body,
                resume_path=resume_path or Config.RESUME_FILE_PATH,
                resume_drive_link=resume_drive_link or Config.RESUME_DRIVE_LINK,
                thread_id=thread_id,
                in_reply_to=in_reply_to,
                references=references,
            )

            # Extract Message-ID from the message dict (set in _create_message)
            email_message_id_from_message = message_dict.get("email_message_id", "")

            # Send message with optional thread_id
            # Gmail API: threadId should be in the request body
            request_body: Dict[str, Any] = {"raw": message_dict["raw"]}
            # Use thread_id from message dict if available, otherwise use parameter
            if message_dict.get("thread_id"):
                request_body["threadId"] = str(message_dict["thread_id"])
            elif thread_id:
                request_body["threadId"] = str(thread_id)

            sent_message = (
                self.service.users().messages().send(userId="me", body=request_body).execute()
            )

            message_id = sent_message.get("id")
            response_thread_id = sent_message.get("threadId")

            # CRITICAL: Fetch the ACTUAL Message-ID that Gmail used/assigned
            # Gmail may rewrite our Message-ID header, so we MUST fetch it back
            # This is the only way to get the real Message-ID for threading
            email_message_id_header = None
            if message_id:
                try:
                    # Small delay to ensure Gmail has processed the message
                    time.sleep(0.5)

                    # Fetch the full message to get the actual headers Gmail used
                    full_message = (
                        self.service.users()
                        .messages()
                        .get(userId="me", id=message_id, format="full")
                        .execute()
                    )

                    # Extract Message-ID from headers (recursively for multipart)
                    email_message_id_header = extract_message_id_from_payload(
                        full_message.get("payload", {})
                    )

                    if email_message_id_header:
                        logger.info(
                            f"Retrieved ACTUAL Message-ID from Gmail: {email_message_id_header} "
                            f"(Gmail message ID: {message_id})"
                        )
                    else:
                        logger.warning(
                            f"Message-ID header not found in Gmail message {message_id}. "
                            f"Using generated Message-ID as fallback."
                        )
                        email_message_id_header = email_message_id_from_message
                except Exception as e:
                    logger.error(
                        f"Failed to fetch Message-ID from Gmail for message {message_id}: {e}. "
                        f"Using generated Message-ID as fallback. "
                        f"Threading may not work correctly.",
                        exc_info=True,
                    )
                    # Fallback to generated Message-ID if we can't fetch it
                    email_message_id_header = email_message_id_from_message
            else:
                # No message ID returned - use generated one
                email_message_id_header = email_message_id_from_message

            logger.info(
                f"Email sent successfully to {to}. "
                f"Gmail Message ID: {message_id}, "
                f"Thread ID: {response_thread_id}, "
                f"Email Message-ID: {email_message_id_header}"
            )

            # Update rate limit stats
            self._update_rate_limit_stats()

            result: Dict[str, Any] = {
                "message_id": str(message_id) if message_id else "",
            }
            if response_thread_id:
                result["thread_id"] = str(response_thread_id)
            if email_message_id_header:
                result["email_message_id"] = email_message_id_header
            return result

        except HttpError as error:
            logger.error(f"Error sending email: {error}")
            raise ExternalServiceError(f"Gmail API error: {error}")
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise ExternalServiceError(f"Failed to send email: {e}")
