from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text

from .base import Base


class EventCreationLog(Base):
    __tablename__ = "event_creation_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_input = Column(Text)
    parsed_details = Column(JSON)  # Store parsed event details as JSON
    created_events = Column(Integer, default=0)  # Number of events created
    errors = Column(Text, nullable=True)  # Error messages if any
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<EventCreationLog(id={self.id}, user_id={self.user_id}, created_events={self.created_events})>"

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_input": self.user_input,
            "parsed_details": self.parsed_details,
            "created_events": self.created_events,
            "errors": self.errors,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
