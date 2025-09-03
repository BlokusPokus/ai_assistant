"""
OAuth Token Model

This model stores encrypted OAuth tokens (access tokens, refresh tokens)
for each OAuth integration. Tokens are encrypted at rest for security.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from personal_assistant.database.models.base import Base


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True)
    integration_id = Column(
        Integer, ForeignKey("oauth_integrations.id"), nullable=False
    )
    access_token = Column(Text, nullable=False)  # Access token value
    refresh_token = Column(Text, nullable=True)  # Refresh token value
    # access_token, refresh_token, id_token
    token_type = Column(String(20), nullable=False, default="Bearer")
    expires_at = Column(DateTime, nullable=False)  # Token expiration time
    scope = Column(Text, nullable=True)  # Token scope (singular, matches DB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)  # Last time token was used
    usage_count = Column(Integer, default=0)  # Number of times token was used

    # Relationships
    integration = relationship("OAuthIntegration", back_populates="tokens")

    def __repr__(self):
        return f"<OAuthToken(id={self.id}, integration_id={self.integration_id}, token_type='{self.token_type}')>"
