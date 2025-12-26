"""
Email template system for first contact and follow-up emails.
"""
import logging
from jinja2 import Template
from typing import Dict, Optional
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)


class EmailTemplate:
    """Email template manager."""
    
    FIRST_CONTACT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <p>Dear {{ recruiter_name or 'Hiring Manager' }},</p>
        
        <p>I hope this email finds you well. I am writing to express my interest in the <strong>{{ position }}</strong> position at <strong>{{ company_name }}</strong>{% if location %} ({{ location }}){% endif %}.</p>
        
        {% if job_posting_url %}
        <p>I came across this opportunity{% if job_posting_url %} <a href="{{ job_posting_url }}">here</a>{% endif %} and I am excited about the possibility of contributing to your team.</p>
        {% endif %}
        
        {% if custom_message %}
        <p>{{ custom_message }}</p>
        {% else %}
        <p>With my background and experience, I believe I would be a valuable addition to {{ company_name }}. I have attached my resume for your review, and I would welcome the opportunity to discuss how my skills and experience align with your needs.</p>
        {% endif %}
        
        <p>Thank you for considering my application. I look forward to hearing from you.</p>
        
        <p>Best regards,<br>
        {{ sender_name }}</p>
    </div>
</body>
</html>
"""
    
    FOLLOW_UP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <p>Dear {{ recruiter_name or 'Hiring Manager' }},</p>
        
        <p>I wanted to follow up on my previous email regarding the <strong>{{ position }}</strong> position at <strong>{{ company_name }}</strong>{% if location %} ({{ location }}){% endif %}.</p>
        
        <p>I remain very interested in this opportunity and would appreciate any updates on the status of my application. I am happy to provide any additional information that might be helpful in your evaluation process.</p>
        
        <p>Thank you for your time and consideration.</p>
        
        <p>Best regards,<br>
        {{ sender_name }}</p>
    </div>
</body>
</html>
"""
    
    FIRST_CONTACT_SUBJECT = "Application for {{ position }} Position at {{ company_name }}"
    FOLLOW_UP_SUBJECT = "Follow-up: Application for {{ position }} Position at {{ company_name }}"
    
    @classmethod
    def render_first_contact(
        cls,
        recruiter_name: Optional[str],
        company_name: str,
        position: str,
        location: Optional[str] = None,
        job_posting_url: Optional[str] = None,
        custom_message: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Render first contact email.
        
        Args:
            custom_message: Optional custom message from sheet. If provided, replaces default message.
        
        Returns:
            Tuple of (subject, body)
        """
        template = Template(cls.FIRST_CONTACT_TEMPLATE)
        subject_template = Template(cls.FIRST_CONTACT_SUBJECT)
        
        context = {
            'recruiter_name': recruiter_name,
            'company_name': company_name,
            'position': position,
            'location': location,
            'job_posting_url': job_posting_url,
            'custom_message': custom_message,
            'sender_name': Config.SENDER_NAME
        }
        
        subject = subject_template.render(**context)
        body = template.render(**context)
        
        return subject, body
    
    @classmethod
    def render_follow_up(
        cls,
        recruiter_name: Optional[str],
        company_name: str,
        position: str,
        location: Optional[str] = None,
        follow_up_number: int = 1
    ) -> tuple[str, str]:
        """
        Render follow-up email.
        
        Returns:
            Tuple of (subject, body)
        """
        template = Template(cls.FOLLOW_UP_TEMPLATE)
        subject_template = Template(cls.FOLLOW_UP_SUBJECT)
        
        context = {
            'recruiter_name': recruiter_name,
            'company_name': company_name,
            'position': position,
            'location': location,
            'sender_name': Config.SENDER_NAME
        }
        
        subject = subject_template.render(**context)
        body = template.render(**context)
        
        return subject, body
    
    @classmethod
    def get_subject_prefix(cls, is_follow_up: bool, follow_up_number: int = 0) -> str:
        """Get subject prefix based on email type."""
        if is_follow_up and follow_up_number > 0:
            return f"Re: Follow-up #{follow_up_number} - "
        elif is_follow_up:
            return "Re: Follow-up - "
        return ""

