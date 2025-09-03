from datetime import datetime

from sqlalchemy import (
    JSON,
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


class LTMMemory(Base):
    """
    Long-Term Memory (LTM) model for storing insights, patterns, and preferences.

    This model is separate from the generic memory_chunks table to provide
    a clean distinction between LTM and other data types (calendar events, notes, etc.).

    Enhanced with:
    - Structured context information
    - Automated intelligence features
    - Enhanced metadata tracking
    - Relationship capabilities
    """

    __tablename__ = "ltm_memories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Memory content (insight, pattern, preference)
    content = Column(Text, nullable=False)

    # Enhanced categorization and organization
    tags = Column(JSON, nullable=False)  # List of tags for categorization
    # Type: preference, insight, pattern, fact, etc.
    memory_type = Column(String(50), nullable=True)
    # High-level category (work, personal, health, etc.)
    category = Column(String(100), nullable=True)

    # Enhanced importance scoring
    # Base importance score (1-10)
    importance_score = Column(Integer, default=1)
    # Confidence in accuracy (0.0-1.0)
    confidence_score = Column(Float, default=1.0)
    # Computed importance including usage patterns
    dynamic_importance = Column(Float, default=1.0)

    # Enhanced context information
    # Legacy context field for backward compatibility
    context = Column(Text, nullable=True)
    # Structured context information
    context_data = Column(JSON, nullable=True)

    # Source and creation tracking
    # conversation, tool_usage, manual, pattern_detection
    source_type = Column(String(50), nullable=True)
    # ID of the source (conversation_id, tool_name, etc.)
    source_id = Column(String(100), nullable=True)
    # Who/what created this memory
    created_by = Column(String(50), default="system")

    # Enhanced timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow)

    # Usage tracking
    access_count = Column(Integer, default=0)  # How many times accessed
    last_access_context = Column(Text, nullable=True)  # Context of last access

    # Relationship tracking
    # List of related memory IDs
    related_memory_ids = Column(JSON, nullable=True)
    parent_memory_id = Column(
        Integer, ForeignKey("ltm_memories.id"), nullable=True
    )  # Parent memory if this is a child

    # Metadata
    # Additional flexible metadata
    memory_metadata = Column(JSON, nullable=True)
    is_archived = Column(Boolean, default=False)  # Whether memory is archived
    archive_reason = Column(Text, nullable=True)  # Why memory was archived

    def __repr__(self):
        return f"<LTMMemory(id={self.id}, user_id={self.user_id}, content='{self.content[:50]}...', importance={self.importance_score}, type={self.memory_type})>"

    def as_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "tags": self.tags,
            "memory_type": self.memory_type,
            "category": self.category,
            "importance_score": self.importance_score,
            "confidence_score": self.confidence_score,
            "dynamic_importance": self.dynamic_importance,
            "context": self.context,
            "context_data": self.context_data,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_accessed": self.last_accessed.isoformat()
            if self.last_accessed
            else None,
            "last_modified": self.last_modified.isoformat()
            if self.last_modified
            else None,
            "access_count": self.access_count,
            "last_access_context": self.last_access_context,
            "related_memory_ids": self.related_memory_ids,
            "parent_memory_id": self.parent_memory_id,
            "metadata": self.memory_metadata,
            "is_archived": self.is_archived,
            "archive_reason": self.archive_reason,
        }

    def update_access_stats(self, access_context: str = None):
        """Update access statistics when memory is retrieved."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        if access_context:
            self.last_access_context = access_context

    def calculate_dynamic_importance(self) -> float:
        """Calculate dynamic importance based on various factors."""
        # Base importance
        base_score = float(self.importance_score)

        # Recency boost (memories accessed recently get a boost)
        days_since_access = (
            (datetime.utcnow() - self.last_accessed).days if self.last_accessed else 30
        )
        recency_boost = max(0, (30 - days_since_access) / 30) * 0.2

        # Usage boost (frequently accessed memories get a boost)
        usage_boost = min(0.3, self.access_count * 0.05)

        # Confidence boost
        confidence_boost = (self.confidence_score - 0.5) * 0.2

        # Calculate final dynamic importance
        dynamic_score = base_score + recency_boost + usage_boost + confidence_boost

        # Ensure it stays within reasonable bounds
        return max(1.0, min(10.0, dynamic_score))

    # Relationships to related tables
    contexts = relationship(
        "LTMContext", back_populates="memory", cascade="all, delete-orphan"
    )
    access_logs = relationship(
        "LTMMemoryAccess", back_populates="memory", cascade="all, delete-orphan"
    )
    tag_entries = relationship(
        "LTMMemoryTag", back_populates="memory", cascade="all, delete-orphan"
    )

    # Self-referential relationships
    parent_memory = relationship(
        "LTMMemory", remote_side=[id], back_populates="child_memories"
    )
    child_memories = relationship("LTMMemory", back_populates="parent_memory")
