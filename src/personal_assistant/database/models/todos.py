"""
Todo database model for enhanced task management with missed counter and auto-segmentation.

This model supports:
- Basic CRUD operations for todos
- Missed deadline tracking
- Auto-segmentation of complex tasks
- Behavioral analytics and insights
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base


class Todo(Base):
    """Enhanced todo model with missed counter and segmentation features."""
    
    __tablename__ = "todos"
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic todo fields
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    done_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default='medium')  # 'high', 'medium', 'low'
    category = Column(String(50), nullable=True)
    status = Column(String(20), default='pending')  # 'pending', 'in_progress', 'completed', 'cancelled'
    
    # Missed counter fields
    missed_count = Column(Integer, default=0, nullable=False)
    last_missed_at = Column(DateTime, nullable=True)
    
    # Segmentation fields
    is_segmented = Column(Boolean, default=False, nullable=False)
    parent_task_id = Column(Integer, ForeignKey("todos.id"), nullable=True)
    segmentation_triggered_at = Column(DateTime, nullable=True)
    
    # Analytics fields
    completion_patterns = Column(JSONB, nullable=True)
    user_insights = Column(JSONB, nullable=True)
    segmentation_suggestions = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="todos")
    parent_task = relationship("Todo", remote_side=[id], backref="subtasks")
    
    def __repr__(self):
        return f"<Todo(id={self.id}, title='{self.title}', status='{self.status}', missed_count={self.missed_count})>"
    
    def as_dict(self):
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'done_date': self.done_date.isoformat() if self.done_date else None,
            'priority': self.priority,
            'category': self.category,
            'status': self.status,
            'missed_count': self.missed_count,
            'last_missed_at': self.last_missed_at.isoformat() if self.last_missed_at else None,
            'is_segmented': self.is_segmented,
            'parent_task_id': self.parent_task_id,
            'segmentation_triggered_at': self.segmentation_triggered_at.isoformat() if self.segmentation_triggered_at else None,
            'completion_patterns': self.completion_patterns,
            'user_insights': self.user_insights,
            'segmentation_suggestions': self.segmentation_suggestions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_overdue': self.is_overdue(),
            'can_be_segmented': self.can_be_segmented()
        }
    
    def is_overdue(self) -> bool:
        """Check if the todo is overdue."""
        if not self.due_date or self.status in ['completed', 'cancelled']:
            return False
        return datetime.utcnow() > self.due_date
    
    def is_approaching_threshold(self, threshold: int = 3) -> bool:
        """Check if the todo is approaching the missed threshold."""
        return self.missed_count >= threshold - 1
    
    def has_reached_threshold(self, threshold: int = 3) -> bool:
        """Check if the todo has reached the missed threshold."""
        return self.missed_count >= threshold
    
    def can_be_segmented(self) -> bool:
        """Check if the todo can be segmented."""
        return (
            not self.is_segmented and 
            self.status in ['pending', 'in_progress'] and
            self.has_reached_threshold()
        )
