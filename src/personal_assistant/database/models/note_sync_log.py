from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from .base import Base


class NoteSyncLog(Base):
    __tablename__ = "note_sync_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    note_id = Column(Integer, ForeignKey("notes.id"))
    synced_at = Column(DateTime, default=datetime.utcnow)
    sync_status = Column(String)
