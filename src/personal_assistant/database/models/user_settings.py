"""
User settings model for storing user preferences and configuration.

This model stores key-value pairs for user settings and preferences
with enhanced metadata and categorization support.
"""


from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from .base import Base


class UserSetting(Base):
    """User settings and preferences storage."""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text)
    setting_type = Column(String(50), nullable=False, default="string")
    is_public = Column(Boolean, default=False)
    validation_rules = Column(JSON)
    category = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Note: sqlite_on_conflict is not supported in current SQLAlchemy version
    # The table will use default conflict resolution behavior
