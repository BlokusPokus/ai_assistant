from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_name = Column(String)
    status = Column(String, default="pending")
    scheduled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
