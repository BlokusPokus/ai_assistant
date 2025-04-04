from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(String)
    channel = Column(String)  # e.g., 'sms', 'email'
    status = Column(String, default='pending')
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
