"""
LTM Memory Relationship Model for tracking relationships between memories.

This model enables finding related memories and building
memory networks for better understanding and retrieval.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class LTMMemoryRelationship(Base):
    """
    Tracks relationships between LTM memories.

    This table enables finding related memories and building
    memory networks for better understanding and retrieval.
    """
    __tablename__ = 'ltm_memory_relationships'

    id = Column(Integer, primary_key=True)
    source_memory_id = Column(Integer, ForeignKey(
        'ltm_memories.id'), nullable=False)
    target_memory_id = Column(Integer, ForeignKey(
        'ltm_memories.id'), nullable=False)

    # Relationship details
    # similar, related, opposite, prerequisite, etc.
    relationship_type = Column(String(50), nullable=False)
    strength = Column(Float, default=1.0)  # relationship strength (0.0-1.0)
    # description of the relationship
    description = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source_memory = relationship("LTMMemory", foreign_keys=[source_memory_id])
    target_memory = relationship("LTMMemory", foreign_keys=[target_memory_id])

    def __repr__(self):
        return f"<LTMMemoryRelationship(id={self.id}, source={self.source_memory_id}, target={self.target_memory_id}, type={self.relationship_type})>"

    def as_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "source_memory_id": self.source_memory_id,
            "target_memory_id": self.target_memory_id,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None
        }
