"""
OAuth Consent Model

This model tracks user consent for OAuth scopes and maintains an audit trail
of consent decisions for compliance and security purposes.
"""

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from personal_assistant.database.models.base import Base


class OAuthConsent(Base):
    __tablename__ = "oauth_consents"

    id = Column(Integer, primary_key=True)
    integration_id = Column(
        Integer, ForeignKey("oauth_integrations.id"), nullable=False
    )
    scopes = Column(ARRAY(Text), nullable=False)  # Array of granted scopes
    # When consent was granted
    granted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # When consent expires
    # IP address when consent was given
    ip_address = Column(String(45), nullable=True)
    # User agent when consent was given
    user_agent = Column(Text, nullable=True)
    consent_version = Column(
        String(20), nullable=False, default="1.0"
    )  # Consent version
    # Whether consent is revoked
    is_revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime, nullable=True)  # When consent was revoked
    # Reason for revocation
    revoked_reason = Column(String(100), nullable=True)

    # Relationships
    integration = relationship("OAuthIntegration", back_populates="consents")

    def __repr__(self):
        return f"<OAuthConsent(id={self.id}, integration_id={self.integration_id}, scopes={self.scopes}, is_revoked={self.is_revoked})>"
