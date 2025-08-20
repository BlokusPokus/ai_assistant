from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)  # Store bcrypt hash
    is_active = Column(Boolean, default=True)  # Account status
    is_verified = Column(Boolean, default=False)  # Email verification status
    verification_token = Column(
        String, nullable=True)  # For email verification
    password_reset_token = Column(String, nullable=True)  # For password reset
    password_reset_expires = Column(
        DateTime, nullable=True)  # Password reset expiry
    last_login = Column(DateTime, nullable=True)  # Last successful login
    failed_login_attempts = Column(Integer, default=0)  # Failed login counter
    locked_until = Column(DateTime, nullable=True)  # Account lockout expiry
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Add relationship to memory chunks
    memory_chunks = relationship(
        "MemoryChunk", back_populates="user", cascade="all, delete-orphan")

    # Add relationship to auth tokens
    auth_tokens = relationship(
        "AuthToken", back_populates="user", cascade="all, delete-orphan")

    # Add relationship to MFA configuration
    mfa_configuration = relationship(
        "MFAConfiguration", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # Add relationship to user sessions
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan")

    # Add relationship to security events
    security_events = relationship(
        "SecurityEvent", back_populates="user", cascade="all, delete-orphan")
