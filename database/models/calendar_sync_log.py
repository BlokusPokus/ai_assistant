from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base


class CalendarSyncLog(Base):
    __tablename__ = 'calendar_sync_log'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    synced_at = Column(DateTime, default=datetime.utcnow)
    sync_status = Column(String)
