"""
SMS Onboarding models for interactive onboarding flow.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional

from sqlalchemy import Column, Integer, String, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base

from ...database.models.base import Base


class OnboardingStep(Enum):
    """Enumeration of onboarding flow steps."""
    WELCOME = "welcome"
    FEATURE_OVERVIEW = "feature_overview"
    QUICK_START = "quick_start"
    LEARN_MORE = "learn_more"
    SIGNUP_LINK = "signup_link"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"


class OnboardingSession(Base):
    """Model for tracking SMS onboarding conversation state."""
    
    __tablename__ = 'sms_onboarding_sessions'

    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), nullable=False)
    current_step = Column(String(50), nullable=False)
    collected_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))

    def __repr__(self):
        return f"<OnboardingSession(id={self.id}, phone='{self.phone_number}', step='{self.current_step}')>"

    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return datetime.utcnow() > self.expires_at

    def extend_expiration(self, hours: int = 1) -> None:
        """Extend the session expiration time."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)

    def get_collected_data(self, key: str, default: Any = None) -> Any:
        """Get a value from collected data."""
        return self.collected_data.get(key, default)

    def set_collected_data(self, key: str, value: Any) -> None:
        """Set a value in collected data."""
        if not self.collected_data:
            self.collected_data = {}
        self.collected_data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'current_step': self.current_step,
            'collected_data': self.collected_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }


# Create indexes for performance
Index("idx_onboarding_sessions_phone", OnboardingSession.phone_number)
Index("idx_onboarding_sessions_expires", OnboardingSession.expires_at)
Index("idx_onboarding_sessions_step", OnboardingSession.current_step)
