"""
OAuth Audit Log Model

This model tracks all OAuth-related activities for security, compliance,
and debugging purposes. It provides a complete audit trail of OAuth operations.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, ARRAY
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship

from personal_assistant.database.models.base import Base


class OAuthAuditLog(Base):
    __tablename__ = 'oauth_audit_log'

    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey(
        'oauth_integrations.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # connect, disconnect, token_refresh, scope_change, etc.
    action = Column(String(100), nullable=False)
    # google, microsoft, notion, youtube
    provider = Column(String(50), nullable=False)
    # Scopes involved in the action
    scopes = Column(ARRAY(String), nullable=True)
    # IP address of the action (PostgreSQL inet type)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)  # User agent of the action
    # Whether the action was successful
    success = Column(Boolean, nullable=False)
    # Error message if action failed
    error_message = Column(Text, nullable=True)
    # Duration of the action in milliseconds
    duration_ms = Column(Integer, nullable=True)
    action_metadata = Column(JSON, nullable=True)  # Additional action details
    # When the action occurred
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(20), nullable=False,
                    default='pending')  # Status of the action
    details = Column(JSON, nullable=True)  # Additional details

    # Relationships
    integration = relationship("OAuthIntegration", back_populates="audit_logs")
    user = relationship("User")

    def __repr__(self):
        return f"<OAuthAuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}', status='{self.status}', provider='{self.provider}')>"
