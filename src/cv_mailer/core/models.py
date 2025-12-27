"""
Database models for tracking job applications and email communications.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Enum as SQLEnum,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from cv_mailer.core.enums import JobStatus, EmailType, EmailStatus

Base = declarative_base()

# Junction table for many-to-many relationship between JobApplication and Recruiter
job_application_recruiter = Table(
    "job_application_recruiter",
    Base.metadata,
    Column("job_application_id", Integer, ForeignKey("job_applications.id"), primary_key=True),
    Column("recruiter_id", Integer, ForeignKey("recruiters.id"), primary_key=True),
)


class JobApplication(Base):
    """Job application record."""

    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True)
    spreadsheet_row_id = Column(
        String(255), nullable=False
    )  # Row identifier (can be "sheet_name_row" for multi-sheet)
    sheet_name = Column(String(255))  # Name of the sheet this came from

    # Job details
    company_name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    location = Column(String(255))
    job_posting_url = Column(Text)
    expected_salary = Column(String(255))  # Expected salary from sheet
    custom_message = Column(Text)  # Custom message from sheet to include in email

    # Status tracking
    status = Column(SQLEnum(JobStatus), default=JobStatus.DRAFT)
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    applied_at = Column(DateTime)
    closed_at = Column(DateTime)

    # Relationships
    emails = relationship(
        "EmailRecord", back_populates="job_application", cascade="all, delete-orphan"
    )
    recruiters = relationship(
        "Recruiter", secondary=job_application_recruiter, back_populates="job_applications"
    )

    def __repr__(self):
        return (
            f"<JobApplication(id={self.id}, company={self.company_name}, position={self.position})>"
        )


class EmailRecord(Base):
    """Email communication record."""

    __tablename__ = "email_records"

    id = Column(Integer, primary_key=True)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)

    # Email details
    email_type = Column(SQLEnum(EmailType), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(255))

    # Status
    status = Column(SQLEnum(EmailStatus), default=EmailStatus.PENDING)
    gmail_message_id = Column(String(255))  # Gmail message ID for tracking
    error_message = Column(Text)

    # Follow-up tracking
    is_follow_up = Column(Boolean, default=False)
    follow_up_number = Column(Integer, default=0)  # 0 = first contact, 1+ = follow-up number

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)

    # Relationships
    job_application = relationship("JobApplication", back_populates="emails")

    def __repr__(self):
        return f"<EmailRecord(id={self.id}, type={self.email_type}, status={self.status})>"


class Recruiter(Base):
    """Recruiter information."""

    __tablename__ = "recruiters"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, unique=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job_applications = relationship(
        "JobApplication", secondary=job_application_recruiter, back_populates="recruiters"
    )

    def __repr__(self):
        return f"<Recruiter(id={self.id}, name={self.name}, email={self.email})>"


class ResponseRecord(Base):
    """Record of responses received from recruiters."""

    __tablename__ = "response_records"

    id = Column(Integer, primary_key=True)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    email_record_id = Column(Integer, ForeignKey("email_records.id"))

    # Response details
    response_type = Column(String(50))  # positive, negative, neutral, interview_request
    response_text = Column(Text)
    responded_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job_application = relationship("JobApplication")


class DailyEmailStats(Base):
    """Daily email sending statistics for rate limiting."""

    __tablename__ = "daily_email_stats"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=True, nullable=False)
    emails_sent = Column(Integer, default=0)
    last_email_sent_at = Column(DateTime)
