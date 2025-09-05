from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from personal_assistant.auth.constants import TOKEN_TYPE_REFRESH

from .base import Base


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, nullable=False, unique=True)
    # refresh, access, reset, etc.
    token_type = Column(String, default=TOKEN_TYPE_REFRESH)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)  # Manual token revocation
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)  # Track token usage

    # Relationship to User
    user = relationship("User", back_populates="auth_tokens")
