"""
OAuth Integration Model

This model represents a user's OAuth integration with a specific provider
(Google, Microsoft, Notion, YouTube) and stores the connection status,
scopes, and metadata.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, ARRAY
from sqlalchemy.orm import relationship

from personal_assistant.database.models.base import Base


class OAuthIntegration(Base):
    __tablename__ = 'oauth_integrations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # google, microsoft, notion, youtube
    provider = Column(String(50), nullable=False)
    # User ID from provider
    provider_user_id = Column(String(255), nullable=True)
    # pending, active, expired, revoked
    status = Column(String(20), default='pending')
    scopes = Column(ARRAY(Text), nullable=True)  # Array of granted scopes
    # Provider-specific metadata
    provider_metadata = Column(JSON, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    # Error message if integration failed
    error_message = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)  # Number of consecutive errors

    # Relationships
    # Removed back_populates to avoid circular import issues
    user = relationship("User")
    tokens = relationship(
        "OAuthToken", back_populates="integration", cascade="all, delete-orphan")
    consents = relationship(
        "OAuthConsent", back_populates="integration", cascade="all, delete-orphan")
    audit_logs = relationship(
        "OAuthAuditLog", back_populates="integration", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<OAuthIntegration(id={self.id}, user_id={self.user_id}, provider='{self.provider}', status='{self.status}')>"
