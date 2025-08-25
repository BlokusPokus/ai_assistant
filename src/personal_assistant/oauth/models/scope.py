"""
OAuth Scope Model

This model defines the available scopes for each OAuth provider and tracks
which scopes are granted to each integration.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from personal_assistant.database.models.base import Base


class OAuthScope(Base):
    __tablename__ = 'oauth_scopes'

    id = Column(Integer, primary_key=True)
    # google, microsoft, notion, youtube
    provider = Column(String(50), nullable=False)
    # e.g., 'calendar.readonly', 'drive.readwrite'
    scope_name = Column(String(100), nullable=False)
    display_name = Column(String(255), nullable=False)  # Human-readable name
    description = Column(Text, nullable=True)  # Detailed description
    category = Column(String(50), nullable=True)  # calendar, drive, mail, etc.
    # Whether scope allows write access
    is_readonly = Column(Boolean, default=True)
    # Whether scope is required for basic functionality
    is_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # Whether scope is available
    # Provider-specific metadata
    provider_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<OAuthScope(id={self.id}, provider='{self.provider}', scope_name='{self.scope_name}', is_active={self.is_active})>"
