"""
Password Service for secure password management.

This service provides secure password hashing and verification using bcrypt
with configurable salt rounds and password validation.
"""

import re
from typing import Tuple

import bcrypt
from fastapi import HTTPException, status


class PasswordService:
    """Service for password operations."""

    def __init__(self, salt_rounds: int = 12):
        """
        Initialize password service.

        Args:
            salt_rounds: Number of salt rounds for bcrypt (default: 12)
        """
        self.salt_rounds = salt_rounds

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string

        Raises:
            HTTPException: If password validation fails
        """
        # Validate password before hashing
        self._validate_password(password)

        # Convert password to bytes and hash
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)

        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed_password: Hashed password to check against

        Returns:
            True if password matches, False otherwise
        """
        try:
            password_bytes = password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            # If there's any error in verification, return False
            return False

    def _validate_password(self, password: str) -> bool:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            True if password meets requirements

        Raises:
            HTTPException: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long",
            )

        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter",
            )

        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one lowercase letter",
            )

        # Check for at least one digit
        if not re.search(r"\d", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one digit",
            )

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one special character",
            )

        return True

    def get_password_strength(self, password: str) -> Tuple[int, str]:
        """
        Get password strength score and description.

        Args:
            password: Password to evaluate

        Returns:
            Tuple of (score, description) where score is 0-100
        """
        score = 0

        # Length score (max 25 points)
        if len(password) >= 8:
            score += 10
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 5

        # Character variety score (max 50 points)
        if re.search(r"[A-Z]", password):
            score += 10
        if re.search(r"[a-z]", password):
            score += 10
        if re.search(r"\d", password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10
        if re.search(r'[^A-Za-z0-9!@#$%^&*(),.?":{}|<>]', password):
            score += 10

        # Complexity score (max 25 points)
        if len(set(password)) >= len(password) * 0.8:  # 80% unique characters
            score += 15
        if not re.search(r"(.)\1{2,}", password):  # No repeated characters
            score += 10

        # Determine strength level
        if score >= 80:
            strength = "Very Strong"
        elif score >= 60:
            strength = "Strong"
        elif score >= 40:
            strength = "Moderate"
        elif score >= 20:
            strength = "Weak"
        else:
            strength = "Very Weak"

        return score, strength


# Global password service instance
password_service = PasswordService()
