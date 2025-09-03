from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from .base import Base


class EventProcessingLog(Base):
    __tablename__ = "event_processing_log"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    processed_at = Column(DateTime, default=datetime.utcnow)
    agent_response = Column(Text)
    # pending, processing, completed, failed
    processing_status = Column(String)
    error_message = Column(Text)
