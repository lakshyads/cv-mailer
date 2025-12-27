"""
Gmail integration for sending emails with rate limiting and resume attachments.
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
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
import os
from config import Config
from models import DailyEmailStats, get_session

logger = logging.getLogger(__name__)


class GmailSender:
    """Gmail client for sending emails with rate limiting."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        token_file = "gmail_token.pickle"
        
        # Try to load existing token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GOOGLE_CREDENTIALS_FILE,
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Gmail API")
    
    def _check_rate_limit(self, max_retries: int = 3) -> bool:
        """
        Check if we can send an email based on daily email limits.
        Returns True if we can send, False if daily limit reached.
        """
        from sqlalchemy.exc import OperationalError
        
        for attempt in range(max_retries):
            session = get_session()
            try:
                today = datetime.now(timezone.utc).date()
                today_start = datetime.combine(today, datetime.min.time())
                
                # Get today's stats
                stats = session.query(DailyEmailStats).filter(
                    DailyEmailStats.date >= today_start
                ).first()
                
                if stats:
                    if stats.emails_sent >= Config.DAILY_EMAIL_LIMIT:
                        logger.warning(f"Daily email limit reached: {stats.emails_sent}/{Config.DAILY_EMAIL_LIMIT}")
                        return False
                else:
                    # Create new stats record (don't commit yet, just prepare)
                    stats = DailyEmailStats(date=datetime.now(timezone.utc), emails_sent=0)
                    session.add(stats)
                    session.flush()  # Flush to get ID but don't commit yet
                
                return True
                
            except OperationalError as e:
                error_str = str(e).lower()
                if "locked" in error_str and attempt < max_retries - 1:
                    wait_time = 0.05 * (2 ** attempt)
                    logger.warning(f"Database locked while checking rate limit (attempt {attempt + 1}/{max_retries}). Retrying...")
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
    
    def _update_rate_limit_stats(self, max_retries: int = 5):
        """Update daily email statistics after sending with retry logic."""
        from sqlalchemy.exc import OperationalError
        
        for attempt in range(max_retries):
            session = get_session()
            try:
                today = datetime.now(timezone.utc).date()
                today_start = datetime.combine(today, datetime.min.time())
                
                stats = session.query(DailyEmailStats).filter(
                    DailyEmailStats.date >= today_start
                ).first()
                
                if not stats:
                    stats = DailyEmailStats(date=datetime.now(timezone.utc), emails_sent=0)
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
                        wait_time = 0.1 * (2 ** attempt)
                        logger.warning(
                            f"Database locked while updating rate limit stats (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {wait_time:.2f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Error updating rate limit stats after {max_retries} attempts: {e}")
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
    
    def _create_message(
        self,
        to: str,
        subject: str,
        body: str,
        resume_path: Optional[str] = None,
        resume_drive_link: Optional[str] = None
    ) -> dict:
        """Create email message with optional resume attachment."""
        body_with_link = body
        if resume_drive_link and resume_drive_link not in body_with_link:
            drive_link_html = (
                f'<p style="margin-top: 16px;">'
                f'<strong>Resume (Google Drive):</strong> '
                f'<a href="{resume_drive_link}">Lakshya_Dev_Singh_Resume.pdf</a>'
                f'</p>'
            )
            # Prefer injecting before closing tags to keep HTML valid-ish.
            if "</div>" in body_with_link:
                body_with_link = body_with_link.replace("</div>", f"{drive_link_html}</div>", 1)
            elif "</body>" in body_with_link:
                body_with_link = body_with_link.replace("</body>", f"{drive_link_html}</body>", 1)
            else:
                body_with_link = body_with_link + drive_link_html
            logger.info("Added resume drive link to email")

        message = MIMEMultipart()
        message["to"] = to
        message["from"] = f"{Config.SENDER_NAME} <{Config.GMAIL_USER}>"
        message["subject"] = subject
        message.attach(MIMEText(body_with_link, "html"))

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
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        resume_path: Optional[str] = None,
        resume_drive_link: Optional[str] = None
    ) -> Optional[str]:
        """
        Send an email via Gmail.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (HTML)
            resume_path: Path to resume file to attach
            resume_drive_link: Google Drive link to resume
        
        Returns:
            Gmail message ID if successful, None otherwise
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
            message = self._create_message(
                to=to,
                subject=subject,
                body=body,
                resume_path=resume_path or Config.RESUME_FILE_PATH,
                resume_drive_link=resume_drive_link or Config.RESUME_DRIVE_LINK
            )
            
            # Send message
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            message_id = sent_message.get('id')
            logger.info(f"Email sent successfully to {to}. Message ID: {message_id}")
            
            # Update rate limit stats
            self._update_rate_limit_stats()
            
            return message_id
            
        except HttpError as error:
            logger.error(f"Error sending email: {error}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return None

