"""
OAuth State Model

This model stores OAuth state parameters for CSRF protection and flow
management. State parameters are used to prevent cross-site request forgery
attacks during OAuth flows.
"""

from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Index, Integer, String, Text

from personal_assistant.database.models.base import Base


class OAuthState(Base):
    __tablename__ = "oauth_state"

    id = Column(Integer, primary_key=True)
    state_token = Column(String(255), nullable=False, unique=True)  # Unique state token
    # google, microsoft, notion, youtube
    provider = Column(String(50), nullable=False)
    # User ID if known at state creation
    user_id = Column(Integer, nullable=True)
    redirect_uri = Column(Text, nullable=True)  # Intended redirect URI
    # Fixed (matches database)    state_metadata = Column(Text, nullable=True)  # Additional state metadata
    scopes = Column(ARRAY(Text), nullable=True)  # type: ignore
    is_used = Column(Boolean, default=False)  # Whether state has been consumed
    expires_at = Column(DateTime, nullable=False)  # State expiration time
    created_at = Column(DateTime, default=datetime.utcnow)

    # Index for performance
    __table_args__ = (
        Index("idx_oauth_states_token", "state_token"),
        Index("idx_oauth_states_expires", "expires_at"),
    )

    def __repr__(self):
        return f"<OAuthState(id={self.id}, state_token='{self.state_token[:10]}...', provider='{self.provider}', is_used={self.is_used})>"
