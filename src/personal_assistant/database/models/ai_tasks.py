from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY

from .base import Base


class AITask(Base):
    __tablename__ = "ai_tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Task classification
    # 'reminder', 'automated_task', 'periodic_task'
    task_type = Column(String(50), nullable=False)

    # Scheduling
    # 'once', 'daily', 'weekly', 'monthly', 'custom'
    schedule_type = Column(String(20), nullable=False)
    schedule_config = Column(JSON)  # cron expression, interval, etc.
    next_run_at = Column(DateTime)
    last_run_at = Column(DateTime)

    # Status and tracking
    # 'active', 'paused', 'completed', 'failed'
    status = Column(String(20), default="active")

    # AI processing
    ai_context = Column(Text)  # context for AI processing
    # ['sms', 'email', 'in_app']
    notification_channels = Column(ARRAY(String), default=[])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AITask(id={self.id}, title='{self.title}', task_type='{self.task_type}', status='{self.status}')>"

    def as_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "schedule_type": self.schedule_type,
            "schedule_config": self.schedule_config,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "status": self.status,
            "ai_context": self.ai_context,
            "notification_channels": self.notification_channels or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_due(self) -> bool:
        """Check if task is due for execution."""
        if self.status != "active":
            return False
        if not self.next_run_at:
            return False
        return datetime.utcnow() >= self.next_run_at

    def should_notify(self) -> bool:
        """Check if task should send notifications."""
        return "sms" in (self.notification_channels or [])
