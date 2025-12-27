"""
Email template system for first contact and follow-up emails.
"""

import logging
from jinja2 import Template
from typing import Optional

from cv_mailer.config import Config

logger = logging.getLogger(__name__)


class EmailTemplateService:
    """Email template manager."""

    FIRST_CONTACT_SUBJECT = "Application: {{ position }} - {{ company_name }}"

    FIRST_CONTACT_TEMPLATE = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <p>Hi {{ recruiter_name or 'Hiring Manager' }},</p>
                
                <p>
                    I'm reaching out regarding the <strong>{{ position }}</strong> role at 
                    <strong>{{ company_name }}</strong>{% if location %} ({{ location }}){% endif %} 
                    listed <a href="{{ job_posting_url }}">here</a>. 
                    I currently lead the design and modernization of core services used at scale, 
                    and I bring hands-on experience owning architecture, performance, 
                    and reliability for high-traffic platforms.
                </p>

                <p>
                    At PayPal, I've been leading a team of 5 engineers on core platform services, 
                    scaling APIs to handle 125M+ requests per day 
                    while achieving P95 latencies under 14ms. 
                    I've driven system modernization initiatives, introduced multi-vendor strategies, 
                    and improved platform reliability and cost efficiency. 
                    Previously, I led cloud automation efforts that reduced time-to-market 
                    for analytics workloads to under 3 days and delivered $10M+ in cloud cost savings 
                    through provisioning and governance automation.
                </p>

                <p>
                    I enjoy operating at the intersection of architecture, execution, and mentorship, 
                    and I'm motivated by building systems that scale with both product growth 
                    and engineering teams. 
                    I'd welcome the opportunity to discuss how my experience could contribute to 
                    {{ company_name }}'s platform and long-term technical roadmap.
                </p>

                <p>
                    My resume is attached for your review. 
                    Please let me know a convenient time to connect.
                </p>

                <p>
                    Best regards,<br>
                    {{ sender_name }}<br>
                    {% if linkedin_profile %}{{ linkedin_profile }}<br>{% endif %}
                    {% if contact_information %}{{ contact_information }}{% endif %}
                </p>
                
            </div>
        </body>
        </html>
    """

    FOLLOW_UP_SUBJECT = "Following up: {{ position }} - {{ company_name }}"

    FOLLOW_UP_TEMPLATE = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <p>Hi {{ recruiter_name or 'Hiring Manager' }},</p>
                
                <p>
                    I wanted to follow up on my application for the 
                    <strong>{{ position }}</strong> position at <strong>{{ company_name }}</strong>
                    {% if location %} ({{ location }}){% endif %}.  
                    I remain very interested in the opportunity 
                    and would welcome any updates you can share.
                </p>
                
                <p>
                    Please let me know if there's anything else you need from me. 
                    Looking forward to your response.
                </p>
                
                <p>
                    Best regards,<br>
                    {{ sender_name }}<br>
                    {% if linkedin_profile %}{{ linkedin_profile }}<br>{% endif %}
                    {% if contact_information %}{{ contact_information }}{% endif %}
                </p>
            </div>
        </body>
        </html>
    """

    @classmethod
    def render_first_contact(
        cls,
        recruiter_name: Optional[str],
        company_name: str,
        position: str,
        location: Optional[str] = None,
        job_posting_url: Optional[str] = None,
        custom_message: Optional[str] = None,
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
            "recruiter_name": recruiter_name,
            "company_name": company_name,
            "position": position,
            "location": location,
            "job_posting_url": job_posting_url,
            "custom_message": custom_message,
            "sender_name": Config.SENDER_NAME,
            "linkedin_profile": getattr(Config, "LINKEDIN_PROFILE", None),
            "contact_information": getattr(Config, "CONTACT_INFORMATION", None),
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
        follow_up_number: int = 1,
    ) -> tuple[str, str]:
        """
        Render follow-up email.

        Returns:
            Tuple of (subject, body)
        """
        template = Template(cls.FOLLOW_UP_TEMPLATE)
        subject_template = Template(cls.FOLLOW_UP_SUBJECT)

        context = {
            "recruiter_name": recruiter_name,
            "company_name": company_name,
            "position": position,
            "location": location,
            "sender_name": Config.SENDER_NAME,
            "linkedin_profile": getattr(Config, "LINKEDIN_PROFILE", None),
            "contact_information": getattr(Config, "CONTACT_INFORMATION", None),
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


# Backward compatibility alias
EmailTemplate = EmailTemplateService
