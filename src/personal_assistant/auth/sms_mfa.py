"""
SMS-based Multi-Factor Authentication (MFA) Service.

This service provides:
- SMS verification code generation and validation
- Rate limiting and abuse prevention
- Integration with existing Twilio setup
- Code expiration and attempt limits
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

from personal_assistant.config.settings import settings


class SMSMFAService:
    """Service for SMS-based Multi-Factor Authentication."""

    def __init__(self, twilio_client=None):
        """
        Initialize SMS MFA service.

        Args:
            twilio_client: Twilio client instance (optional for testing)
        """
        self.twilio_client = twilio_client
        self.verification_codes: Dict[str, Dict] = {}
        self.rate_limit_attempts = settings.MFA_SMS_RATE_LIMIT
        self.rate_limit_window_minutes = settings.MFA_SMS_RATE_WINDOW_MINUTES
        self.code_expiration_minutes = 10
        self.max_attempts_per_code = 3

    def send_verification_code(self, phone_number: str) -> str:
        """
        Send SMS verification code and return code ID.

        Args:
            phone_number: Phone number to send code to

        Returns:
            Code ID for verification

        Raises:
            ValueError: If rate limit exceeded
        """
        # Check rate limiting
        if self.is_rate_limited(phone_number):
            raise ValueError(
                f"Rate limit exceeded. Maximum {self.rate_limit_attempts} "
                f"attempts per {self.rate_limit_window_minutes} minutes. "
                "Please try again later."
            )

        # Generate 6-digit code
        code = str(secrets.randbelow(1000000)).zfill(6)
        code_id = secrets.token_urlsafe(16)

        # Store code with expiration and metadata
        self.verification_codes[code_id] = {
            "phone_number": phone_number,
            "code": code,
            "expires_at": datetime.utcnow()
            + timedelta(minutes=self.code_expiration_minutes),
            "attempts": 0,
            "created_at": datetime.utcnow(),
            "last_attempt": None,
        }

        # Send SMS if Twilio client is available
        if self.twilio_client:
            try:
                message = (
                    f"Your verification code is: {code}. "
                    f"Valid for {self.code_expiration_minutes} minutes. "
                    "Do not share this code with anyone."
                )
                self.twilio_client.send_sms(phone_number, message)
            except Exception as e:
                # Log error but don't fail the request
                # In production, this should be logged to monitoring system
                print(f"Failed to send SMS: {e}")

        return code_id

    def verify_code(self, code_id: str, code: str) -> bool:
        """
        Verify SMS code and return success status.

        Args:
            code_id: Code ID from send_verification_code
            code: Code to verify

        Returns:
            True if code is valid, False otherwise
        """
        if code_id not in self.verification_codes:
            return False

        verification_data = self.verification_codes[code_id]

        # Check expiration
        if datetime.utcnow() > verification_data["expires_at"]:
            del self.verification_codes[code_id]
            return False

        # Check attempts
        if verification_data["attempts"] >= self.max_attempts_per_code:
            del self.verification_codes[code_id]
            return False

        # Update attempt count and timestamp
        verification_data["attempts"] += 1
        verification_data["last_attempt"] = datetime.utcnow()

        # Verify code
        if verification_data["code"] == code:
            # Success - remove code and return True
            del self.verification_codes[code_id]
            return True

        return False

    def is_rate_limited(self, phone_number: str) -> bool:
        """
        Check if phone number is rate limited.

        Args:
            phone_number: Phone number to check

        Returns:
            True if rate limited, False otherwise
        """
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.rate_limit_window_minutes)

        # Count recent attempts for this phone number
        recent_attempts = 0

        for code_id, data in list(self.verification_codes.items()):
            # Clean up expired codes while checking
            if data["expires_at"] < now:
                del self.verification_codes[code_id]
                continue

            if (
                data["phone_number"] == phone_number
                and data["created_at"] > window_start
            ):
                recent_attempts += 1

        return recent_attempts >= self.rate_limit_attempts  # type: ignore

    def get_remaining_attempts(self, phone_number: str) -> int:
        """
        Get remaining attempts for a phone number in current window.

        Args:
            phone_number: Phone number to check

        Returns:
            Number of remaining attempts
        """
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.rate_limit_window_minutes)

        recent_attempts = sum(
            1
            for data in self.verification_codes.values()
            if (
                data["phone_number"] == phone_number
                and data["created_at"] > window_start
            )
        )

        return max(0, self.rate_limit_attempts - recent_attempts)  # type: ignore

    def get_next_attempt_time(self, phone_number: str) -> Optional[datetime]:
        """
        Get the next time when attempts will be allowed for a phone number.

        Args:
            phone_number: Phone number to check

        Returns:
            Next attempt time or None if not rate limited
        """
        if not self.is_rate_limited(phone_number):
            return None

        # Find the oldest attempt in the current window
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.rate_limit_window_minutes)

        oldest_attempt = None
        for data in self.verification_codes.values():
            if (
                data["phone_number"] == phone_number
                and data["created_at"] > window_start
            ):
                if oldest_attempt is None or data["created_at"] < oldest_attempt:
                    oldest_attempt = data["created_at"]

        if oldest_attempt:
            return oldest_attempt + timedelta(minutes=self.rate_limit_window_minutes)  # type: ignore

        return None

    def cleanup_expired_codes(self):
        """Clean up expired verification codes."""
        now = datetime.utcnow()
        expired_codes = [
            code_id
            for code_id, data in self.verification_codes.items()
            if data["expires_at"] < now
        ]

        for code_id in expired_codes:
            del self.verification_codes[code_id]

    def get_verification_status(self, code_id: str) -> Optional[Dict]:
        """
        Get verification code status without consuming it.

        Args:
            code_id: Code ID to check

        Returns:
            Verification data or None if not found
        """
        if code_id not in self.verification_codes:
            return None

        data = self.verification_codes[code_id].copy()

        # Check if expired
        if datetime.utcnow() > data["expires_at"]:
            return None

        # Calculate remaining attempts
        data["remaining_attempts"] = self.max_attempts_per_code - data["attempts"]

        # Calculate time until expiration
        time_until_expiry = data["expires_at"] - datetime.utcnow()
        data["expires_in_seconds"] = int(time_until_expiry.total_seconds())

        return data

    def resend_code(self, phone_number: str) -> Optional[str]:
        """
        Resend verification code to the same phone number.

        Args:
            phone_number: Phone number to resend to

        Returns:
            New code ID or None if rate limited
        """
        # Check if we can resend
        if self.is_rate_limited(phone_number):
            return None

        # Remove any existing codes for this phone number
        existing_codes = [
            code_id
            for code_id, data in self.verification_codes.items()
            if data["phone_number"] == phone_number
        ]

        for code_id in existing_codes:
            del self.verification_codes[code_id]

        # Send new code
        return self.send_verification_code(phone_number)
