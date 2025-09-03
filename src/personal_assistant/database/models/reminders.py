from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from .base import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String, nullable=False)
    remind_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent = Column(Boolean, default=False)
