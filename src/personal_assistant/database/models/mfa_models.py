"""
Database models for Multi-Factor Authentication (MFA) and security events.

This module defines the database schema for:
- MFA configuration storage
- Security event logging
- Backup codes management
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .base import Base


class MFAConfiguration(Base):
    """MFA configuration for users."""

    __tablename__ = 'mfa_configurations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=False, unique=True)

    # TOTP Configuration
    totp_secret = Column(String(255), nullable=True)  # Encrypted TOTP secret
    totp_enabled = Column(Boolean, default=False)

    # SMS Configuration
    sms_enabled = Column(Boolean, default=False)
    phone_number = Column(String(20), nullable=True)

    # Backup Codes
    backup_codes = Column(JSON, nullable=True)  # List of backup codes

    # Trusted Devices
    # List of trusted device hashes
    trusted_devices = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="mfa_configuration")


class UserSession(Base):
    """User session tracking for security and management."""

    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False)

    # Device Information
    device_info = Column(JSON, nullable=True)  # Browser, OS, device details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)

    # Session Management
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")


class SecurityEvent(Base):
    """Security event logging for audit and monitoring."""

    __tablename__ = 'security_events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=True)  # Null for system events

    # Event Details
    # login, logout, mfa_setup, etc.
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=True)  # Additional event context
    # info, warning, error, critical
    severity = Column(String(20), default='info')

    # Request Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="security_events")
