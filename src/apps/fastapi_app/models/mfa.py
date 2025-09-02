"""
MFA (Multi-Factor Authentication) API models.

This module provides Pydantic models for MFA API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class MFAConfigurationResponse(BaseModel):
    """Response model for MFA configuration information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    mfa_type: str
    is_enabled: bool
    secret_key: Optional[str]  # Only for admin operations
    backup_codes: Optional[List[str]]  # Only for admin operations
    last_used: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class MFAConfigurationCreateRequest(BaseModel):
    """Request model for creating MFA configuration."""
    mfa_type: str = Field(..., description="Type of MFA (totp, sms, email)")
    is_enabled: bool = Field(
        default=True, description="Whether MFA is enabled")


class MFAConfigurationUpdateRequest(BaseModel):
    """Request model for updating MFA configuration."""
    mfa_type: Optional[str] = Field(
        None, description="Type of MFA (totp, sms, email)")
    is_enabled: Optional[bool] = Field(
        None, description="Whether MFA is enabled")


class UserSessionResponse(BaseModel):
    """Response model for user session information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    session_token: str
    device_info: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    is_active: bool
    last_activity: datetime
    expires_at: datetime
    created_at: datetime


class UserSessionCreateRequest(BaseModel):
    """Request model for creating user session."""
    device_info: Optional[Dict[str, Any]] = Field(
        None, description="Device information")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    expires_at: Optional[datetime] = Field(
        None, description="Session expiration time")


class SecurityEventResponse(BaseModel):
    """Response model for security event information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    event_type: str
    severity: str
    description: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Optional[Dict[str, Any]]
    resolved: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[int]
    created_at: datetime


class SecurityEventCreateRequest(BaseModel):
    """Request model for creating security event."""
    user_id: Optional[int] = Field(None, description="User ID")
    event_type: str = Field(..., min_length=1, max_length=50,
                            description="Type of security event")
    severity: str = Field(...,
                          description="Severity level (low, medium, high, critical)")
    description: str = Field(..., min_length=1,
                             max_length=1000, description="Event description")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata")


class SecurityEventUpdateRequest(BaseModel):
    """Request model for updating security event."""
    resolved: Optional[bool] = Field(
        None, description="Whether event is resolved")
    resolved_by: Optional[int] = Field(
        None, description="User ID who resolved the event")


class MFASetupResponse(BaseModel):
    """Response model for MFA setup."""
    qr_code_url: Optional[str] = Field(
        None, description="QR code URL for TOTP setup")
    secret_key: str = Field(..., description="Secret key for manual setup")
    backup_codes: List[str] = Field(..., description="Backup codes")


class MFAVerifyRequest(BaseModel):
    """Request model for MFA verification."""
    code: str = Field(..., min_length=6, max_length=6,
                      description="MFA verification code")
    mfa_type: str = Field(..., description="Type of MFA (totp, sms, email)")


class MFAVerifyResponse(BaseModel):
    """Response model for MFA verification."""
    success: bool = Field(...,
                          description="Whether verification was successful")
    message: str = Field(..., description="Verification message")
    session_token: Optional[str] = Field(
        None, description="Session token if successful")


class UserSessionListResponse(BaseModel):
    """Response model for user session list."""
    sessions: List[UserSessionResponse]
    total: int
    skip: int
    limit: int


class SecurityEventListResponse(BaseModel):
    """Response model for security event list."""
    events: List[SecurityEventResponse]
    total: int
    skip: int
    limit: int


class UserSessionSearchRequest(BaseModel):
    """Request model for searching user sessions."""
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    is_active: Optional[bool] = Field(
        None, description="Filter by active status")
    created_after: Optional[datetime] = Field(
        None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(
        None, description="Filter by creation date")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=100,
                       description="Maximum number of records to return")


class SecurityEventSearchRequest(BaseModel):
    """Request model for searching security events."""
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    event_type: Optional[str] = Field(None, description="Filter by event type")
    severity: Optional[str] = Field(None, description="Filter by severity")
    resolved: Optional[bool] = Field(
        None, description="Filter by resolved status")
    created_after: Optional[datetime] = Field(
        None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(
        None, description="Filter by creation date")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=100,
                       description="Maximum number of records to return")
