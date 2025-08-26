"""
Phone number validation and normalization service.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PhoneValidator:
    """Service for validating and normalizing phone numbers."""

    def __init__(self):
        # Common phone number patterns
        self.patterns = {
            'us_canada': r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
            'international': r'^\+[1-9]\d{1,14}$',
            'e164': r'^\+[1-9]\d{1,14}$'
        }

    def normalize_phone_number(self, phone_number: str) -> Optional[str]:
        """
        Normalize phone number to E.164 format.

        Args:
            phone_number: Raw phone number string

        Returns:
            Normalized phone number in E.164 format or None if invalid
        """
        if not phone_number:
            return None

        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)

        # Handle multiple plus signs - keep only the first one
        if cleaned.count('+') > 1:
            first_plus = cleaned.find('+')
            cleaned = cleaned[first_plus:].replace('+', '')
            cleaned = '+' + cleaned

        # Handle US/Canada numbers
        if cleaned.startswith('1') and len(cleaned) == 11:
            return f"+{cleaned}"
        elif len(cleaned) == 10:
            return f"+1{cleaned}"
        elif cleaned.startswith('+1') and len(cleaned) == 12:
            return cleaned
        elif cleaned.startswith('+') and len(cleaned) >= 12 and len(cleaned) <= 16:
            return cleaned

        logger.warning(f"Invalid phone number format: {phone_number}")
        return None

    def is_valid_phone_number(self, phone_number: str) -> bool:
        """
        Check if phone number is valid.

        Args:
            phone_number: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        normalized = self.normalize_phone_number(phone_number)
        return normalized is not None

    def format_phone_number(self, phone_number: str, format_type: str = 'e164') -> Optional[str]:
        """
        Format phone number to specified format.

        Args:
            phone_number: Phone number to format
            format_type: Desired format ('e164', 'national', 'international')

        Returns:
            Formatted phone number or None if invalid
        """
        normalized = self.normalize_phone_number(phone_number)
        if not normalized:
            return None

        if format_type == 'e164':
            return normalized
        elif format_type == 'national':
            # Remove + and format as national
            if normalized.startswith('+1'):
                number = normalized[2:]
                return f"({number[:3]}) {number[3:6]}-{number[6:]}"
            else:
                return normalized
        elif format_type == 'international':
            return normalized

        return normalized
