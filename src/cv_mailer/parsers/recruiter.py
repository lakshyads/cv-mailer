"""
Parser for extracting recruiter information from Google Sheets cells.
Handles multiple recruiters in a single cell.
"""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class RecruiterParser:
    """Parse recruiter information from various formats."""

    @staticmethod
    def parse_recruiters(cell_value: str) -> List[Dict[str, str]]:
        """
        Parse recruiter information from a cell that may contain multiple recruiters.

        Expected formats:
        1. "Name - email@domain.com, Name2 - email2@domain.com"
        2. "Name - email@domain.com"
        3. "email@domain.com" (name will be None)
        4. "Name" (email will be None)

        Args:
            cell_value: The cell content from Google Sheets

        Returns:
            List of dictionaries with 'name' and 'email' keys
        """
        if not cell_value or not cell_value.strip():
            return []

        # Normalize the input: remove extra whitespace, handle newlines
        cell_value = " ".join(cell_value.split())

        recruiters = []

        # Email pattern for matching
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        # First, try to find all "Name - email" patterns using regex
        # This is more robust than splitting by comma first
        # Pattern: (name part) - (email)
        # The name part can contain any characters except the dash-email pattern
        pattern = r"([^,]+?)\s*-\s*(" + email_pattern + r")"
        matches = re.finditer(pattern, cell_value)

        for match in matches:
            name = match.group(1).strip()
            email = match.group(2).strip()
            recruiters.append({"name": name if name else None, "email": email})

        # If we found patterns, use them. Otherwise, try a different approach
        if not recruiters:
            # Fallback: split by comma and parse each part
            parts = [p.strip() for p in cell_value.split(",")]

            for part in parts:
                if not part:
                    continue

                # Try to match "Name - email@domain.com" pattern
                # Use a more permissive pattern that handles various dash styles
                match = re.match(r"^(.+?)\s*[-–—]\s*(" + email_pattern + r")$", part.strip())

                if match:
                    # Format: "Name - email@domain.com"
                    name = match.group(1).strip()
                    email = match.group(2).strip()
                    recruiters.append({"name": name if name else None, "email": email})
                else:
                    # Check if it's just an email
                    email_match = re.search(email_pattern, part)
                    if email_match:
                        email = email_match.group(0)
                        # Try to extract name from before the email
                        before_email = part[: email_match.start()].strip()
                        # Remove trailing dash if present
                        if before_email.endswith("-"):
                            before_email = before_email[:-1].strip()
                        name = before_email if before_email else None
                        recruiters.append({"name": name, "email": email})
                    else:
                        # Just a name, no email - skip it
                        logger.warning(f"Could not parse recruiter info (no email found): {part}")
                        continue

        # Remove duplicates (same email) - case insensitive
        seen_emails = set()
        unique_recruiters = []
        for recruiter in recruiters:
            if recruiter.get("email"):
                email_lower = recruiter["email"].lower()
                if email_lower not in seen_emails:
                    seen_emails.add(email_lower)
                    unique_recruiters.append(recruiter)
            else:
                # Keep recruiters without emails for now (might want to log this)
                logger.warning(f"Recruiter entry has no email: {recruiter}")

        logger.info(f"Parsed {len(unique_recruiters)} unique recruiters from: {cell_value[:50]}...")
        return unique_recruiters

    @staticmethod
    def extract_primary_recruiter(cell_value: str) -> Optional[Dict[str, str]]:
        """
        Extract the first recruiter from a cell (for backward compatibility).

        Args:
            cell_value: The cell content

        Returns:
            Dictionary with 'name' and 'email' keys, or None
        """
        recruiters = RecruiterParser.parse_recruiters(cell_value)
        return recruiters[0] if recruiters else None

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
