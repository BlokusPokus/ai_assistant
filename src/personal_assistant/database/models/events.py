from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from .base import Base


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    source = Column(String, default='assistant')
    external_id = Column(String)
    # New fields for event processing
    handled_at = Column(DateTime)
    # pending, processing, completed, failed
    processing_status = Column(String, default='pending')
    agent_response = Column(Text)
    last_checked = Column(DateTime)

    # Recurrence fields
    recurrence_pattern_id = Column(Integer, ForeignKey(
        'recurrence_patterns.id'), nullable=True)
    is_recurring = Column(Boolean, default=False)
    parent_event_id = Column(Integer, ForeignKey('events.id'), nullable=True)
    recurrence_instance_number = Column(Integer, nullable=True)
