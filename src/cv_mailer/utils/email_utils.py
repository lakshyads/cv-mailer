"""
Email utility functions for threading and message processing.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def extract_message_id_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    """
    Recursively extract Message-ID header from Gmail API message payload.

    Gmail messages can have nested payloads for multipart messages, so we need
    to search recursively through all parts.

    Args:
        payload: Gmail API message payload dictionary

    Returns:
        Message-ID header value if found, None otherwise
    """
    headers = payload.get("headers", [])
    for header in headers:
        if header.get("name", "").lower() == "message-id":
            value = header.get("value", "")
            if value:
                return str(value)

    # Check nested parts for multipart messages
    parts = payload.get("parts", [])
    for part in parts:
        msg_id = extract_message_id_from_payload(part)
        if msg_id:
            return msg_id

    return None


def format_message_id_for_header(message_id: str) -> str:
    """
    Format a Message-ID for use in email headers.

    Ensures the Message-ID is in the correct format with angle brackets.

    Args:
        message_id: Message-ID string (may or may not have angle brackets)

    Returns:
        Formatted Message-ID with angle brackets
    """
    message_id = message_id.strip()
    if not message_id.startswith("<"):
        message_id = f"<{message_id}>"
    return message_id


def build_references_chain(previous_references: Optional[str], previous_message_id: str) -> str:
    """
    Build a References header chain for email threading.

    The References header contains all Message-IDs in the conversation chain,
    ordered from oldest to newest.

    Args:
        previous_references: Existing References header from previous email (optional)
        previous_message_id: Message-ID of the previous email

    Returns:
        Space-separated list of Message-IDs in angle brackets format
    """
    references_parts = []

    # Add existing references chain if present
    if previous_references:
        # Parse existing references (space-separated Message-IDs)
        refs_list = previous_references.split()
        references_parts.extend(refs_list)

    # Add the previous email's Message-ID to the chain
    # Ensure it's in angle brackets format
    prev_msg_id = format_message_id_for_header(previous_message_id)
    if prev_msg_id not in references_parts:
        references_parts.append(prev_msg_id)

    return " ".join(references_parts)


def clean_subject_for_reply(original_subject: str) -> str:
    """
    Clean and format subject line for reply emails.

    Removes existing "Re: " prefix if present, then adds a new one.
    This ensures proper threading in Gmail.

    Args:
        original_subject: Original subject line from previous email

    Returns:
        Subject line with "Re: " prefix
    """
    clean_subject = original_subject
    if clean_subject.lower().startswith("re: "):
        clean_subject = clean_subject[4:]
    return f"Re: {clean_subject}"
