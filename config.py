"""
Configuration management for CV Mailer application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Google API
    GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    
    # Google Sheets
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    WORKSHEET_NAME: str = os.getenv("WORKSHEET_NAME", "Sheet1")  # Used if PROCESS_ALL_SHEETS is False
    PROCESS_ALL_SHEETS: bool = os.getenv("PROCESS_ALL_SHEETS", "true").lower() == "true"
    SHEET_NAME_FILTER: Optional[str] = os.getenv("SHEET_NAME_FILTER")  # Optional regex pattern
    
    # Gmail
    GMAIL_USER: str = os.getenv("GMAIL_USER", "")
    SENDER_NAME: str = os.getenv("SENDER_NAME", "Job Applicant")
    
    # Resume
    RESUME_FILE_PATH: Optional[str] = os.getenv("RESUME_FILE_PATH")
    RESUME_DRIVE_LINK: Optional[str] = os.getenv("RESUME_DRIVE_LINK")
    
    # Rate Limiting
    EMAIL_DELAY_MIN: int = int(os.getenv("EMAIL_DELAY_MIN", "60"))
    EMAIL_DELAY_MAX: int = int(os.getenv("EMAIL_DELAY_MAX", "120"))
    DAILY_EMAIL_LIMIT: int = int(os.getenv("DAILY_EMAIL_LIMIT", "50"))
    
    # Follow-up
    FOLLOW_UP_DAYS: int = int(os.getenv("FOLLOW_UP_DAYS", "7"))
    MAX_FOLLOW_UPS: int = int(os.getenv("MAX_FOLLOW_UPS", "3"))
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "cv_mailer.db")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "cv_mailer.log")
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not cls.SPREADSHEET_ID:
            errors.append("SPREADSHEET_ID is required")
        
        if not cls.GMAIL_USER:
            errors.append("GMAIL_USER is required")
        
        if not cls.RESUME_FILE_PATH and not cls.RESUME_DRIVE_LINK:
            errors.append("Either RESUME_FILE_PATH or RESUME_DRIVE_LINK must be set")
        
        if not Path(cls.GOOGLE_CREDENTIALS_FILE).exists():
            errors.append(f"Google credentials file not found: {cls.GOOGLE_CREDENTIALS_FILE}")
        
        return errors

