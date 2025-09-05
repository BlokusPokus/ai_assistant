from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from .base import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_synced = Column(DateTime)
