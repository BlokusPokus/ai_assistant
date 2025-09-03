"""
LTM Memory Tag Model for enhanced tag management.

This model provides better tag organization and enables
tag-based analytics and relationship discovery.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class LTMMemoryTag(Base):
    """
    Enhanced tag management for LTM memories.

    This table provides better tag organization and enables
    tag-based analytics and relationship discovery.
    """

    __tablename__ = "ltm_memory_tags"

    id = Column(Integer, primary_key=True)
    memory_id = Column(Integer, ForeignKey("ltm_memories.id"), nullable=False)
    tag_name = Column(String(100), nullable=False)

    # Tag metadata
    # work, personal, health, etc.
    tag_category = Column(String(50), nullable=True)
    # importance of this tag for this memory
    tag_importance = Column(Float, default=1.0)
    tag_confidence = Column(Float, default=1.0)  # confidence in tag assignment

    # Tag usage
    # how many times this tag has been used
    usage_count = Column(Integer, default=1)
    first_used = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)

    # Relationship to memory
    memory = relationship("LTMMemory", back_populates="tag_entries")

    def __repr__(self):
        return f"<LTMMemoryTag(id={self.id}, memory_id={self.memory_id}, tag={self.tag_name})>"

    def as_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "memory_id": self.memory_id,
            "tag_name": self.tag_name,
            "tag_category": self.tag_category,
            "tag_importance": self.tag_importance,
            "tag_confidence": self.tag_confidence,
            "usage_count": self.usage_count,
            "first_used": self.first_used.isoformat() if self.first_used else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }
