from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer

from .base import Base


class TaskResult(Base):
    __tablename__ = "task_results"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    result = Column(JSON)
    completed_at = Column(DateTime)
