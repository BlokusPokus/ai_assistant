"""
Phone management models for user phone number operations.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class PhoneNumberBase(BaseModel):
    """Base model for phone number operations."""

    phone_number: str = Field(..., description="Phone number in international format")
    is_primary: bool = Field(
        False, description="Whether this is the primary phone number"
    )

    @validator("phone_number")
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", v)

        # Must start with + and have 10-15 digits
        if not cleaned.startswith("+"):
            raise ValueError("Phone number must start with +")

        digits_only = cleaned[1:]  # Remove the +
        if not (10 <= len(digits_only) <= 15):
            raise ValueError("Phone number must have 10-15 digits after +")

        if not digits_only.isdigit():
            raise ValueError("Phone number must contain only digits after +")

        return cleaned


class PhoneNumberCreate(PhoneNumberBase):
    """Model for creating a new phone number."""


class PhoneNumberUpdate(BaseModel):
    """Model for updating a phone number."""

    phone_number: Optional[str] = Field(None, description="New phone number")
    is_primary: Optional[bool] = Field(
        None, description="Whether this is the primary phone number"
    )

    @validator("phone_number")
    def validate_phone_number(cls, v):
        """Validate phone number format if provided."""
        if v is None:
            return v

        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", v)

        # Must start with + and have 10-15 digits
        if not cleaned.startswith("+"):
            raise ValueError("Phone number must start with +")

        digits_only = cleaned[1:]  # Remove the +
        if not (10 <= len(digits_only) <= 15):
            raise ValueError("Phone number must have 10-15 digits after +")

        if not digits_only.isdigit():
            raise ValueError("Phone number must contain only digits after +")

        return cleaned


class PhoneNumberResponse(BaseModel):
    """Model for phone number responses."""

    id: int
    user_id: int
    phone_number: str
    is_primary: bool
    is_verified: bool
    verification_method: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PhoneNumberListResponse(BaseModel):
    """Model for listing user phone numbers."""

    phone_numbers: list[PhoneNumberResponse]
    total_count: int
    primary_phone_id: Optional[int] = None


class PhoneNumberVerificationRequest(BaseModel):
    """Model for requesting phone number verification."""

    phone_number: str = Field(..., description="Phone number to verify")

    @validator("phone_number")
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", v)

        # Must start with + and have 10-15 digits
        if not cleaned.startswith("+"):
            raise ValueError("Phone number must start with +")

        digits_only = cleaned[1:]  # Remove the +
        if not (10 <= len(digits_only) <= 15):
            raise ValueError("Phone number must have 10-15 digits after +")

        if not digits_only.isdigit():
            raise ValueError("Phone number must contain only digits after +")

        return cleaned


class PhoneNumberVerificationCode(BaseModel):
    """Model for phone number verification code."""

    phone_number: str = Field(..., description="Phone number being verified")
    verification_code: str = Field(
        ..., min_length=6, max_length=6, description="6-digit verification code"
    )

    @validator("verification_code")
    def validate_verification_code(cls, v):
        """Validate verification code format."""
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Verification code must be exactly 6 digits")
        return v


class PhoneNumberVerificationResponse(BaseModel):
    """Model for phone number verification response."""

    success: bool
    message: str
    phone_number: str
    verification_status: str  # 'pending', 'verified', 'failed'
    expires_at: Optional[datetime] = None


class PhoneNumberDeleteResponse(BaseModel):
    """Model for phone number deletion response."""

    success: bool
    message: str
    deleted_phone_number: str
    remaining_phone_count: int
