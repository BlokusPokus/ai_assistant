"""
LTM Context Model for enhanced context information.

This model stores structured context data that provides rich information
about when, why, and how LTM memories were created.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class LTMContext(Base):
    """
    Enhanced context information for LTM memories.

    This table stores structured context data that provides rich information
    about when, why, and how memories were created.
    """
    __tablename__ = 'ltm_contexts'

    id = Column(Integer, primary_key=True)
    memory_id = Column(Integer, ForeignKey('ltm_memories.id'), nullable=False)

    # Context categorization
    # temporal, spatial, social, environmental, etc.
    context_type = Column(String(50), nullable=False)
    # specific context identifier
    context_key = Column(String(100), nullable=False)
    context_value = Column(Text, nullable=True)  # context value or description

    # Metadata
    # confidence in this context information
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to memory
    memory = relationship("LTMMemory", back_populates="contexts")

    def __repr__(self):
        return f"<LTMContext(id={self.id}, memory_id={self.memory_id}, type={self.context_type}, key={self.context_key})>"

    def as_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "memory_id": self.memory_id,
            "context_type": self.context_type,
            "context_key": self.context_key,
            "context_value": self.context_value,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
