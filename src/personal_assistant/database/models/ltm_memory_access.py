"""
LTM Memory Access Model for tracking detailed access patterns.

This model provides insights into how memories are used
and helps optimize retrieval and importance scoring.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base


class LTMMemoryAccess(Base):
    """
    Tracks detailed access patterns for LTM memories.

    This table provides insights into how memories are used
    and helps optimize retrieval and importance scoring.
    """

    __tablename__ = "ltm_memory_access"

    id = Column(Integer, primary_key=True)
    memory_id = Column(Integer, ForeignKey("ltm_memories.id"), nullable=False)

    # Access details
    access_timestamp = Column(DateTime, default=datetime.utcnow)
    access_context = Column(Text, nullable=True)  # what triggered this access
    # search, direct, related, etc.
    access_method = Column(String(50), nullable=True)
    # user query that led to this access
    user_query = Column(Text, nullable=True)

    # Access result
    # whether the memory was actually useful
    was_relevant = Column(Boolean, nullable=True)
    # how relevant it was (0.0-1.0)
    relevance_score = Column(Float, nullable=True)

    # Relationship to memory
    memory = relationship("LTMMemory", back_populates="access_logs")

    def __repr__(self):
        return f"<LTMMemoryAccess(id={self.id}, memory_id={self.memory_id}, timestamp={self.access_timestamp})>"

    def as_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "memory_id": self.memory_id,
            "access_timestamp": self.access_timestamp.isoformat()
            if self.access_timestamp
            else None,
            "access_context": self.access_context,
            "access_method": self.access_method,
            "user_query": self.user_query,
            "was_relevant": self.was_relevant,
            "relevance_score": self.relevance_score,
        }
