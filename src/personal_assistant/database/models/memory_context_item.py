"""
Memory Context Item Model for Task 053: Database Schema Redesign

This model represents individual memory context items in the new normalized schema,
enabling efficient querying and quality-based filtering of context information.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class MemoryContextItem(Base):
    """
    Memory context items table - stores individual context pieces with quality metrics.

    This table enables intelligent context loading based on relevance scores,
    source types, and focus areas without loading entire memory context.
    """

    __tablename__ = "memory_context_items"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(
        String(255),
        ForeignKey("conversation_states.conversation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # 'ltm', 'rag', 'focus', 'preferences', 'conversation'
    source = Column(String(50), nullable=False, index=True)
    content = Column(Text)
    # 0.0 to 1.0 relevance score
    relevance_score = Column(Float, default=0.5, index=True)
    # 'fact', 'preference', 'focus_area', 'tool_result', 'conversation_summary'
    context_type = Column(String(50), index=True)
    # Original role in conversation if applicable
    original_role = Column(String(50), index=True)
    focus_area = Column(String(100), index=True)  # Associated focus area
    # Type of preference if applicable
    preference_type = Column(String(100), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    additional_data = Column(JSON)  # Additional data as JSON

    # Relationship to conversation state
    conversation_state = relationship(
        "ConversationState", back_populates="context_items"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_context_conversation_source", "conversation_id", "source"),
        Index("idx_context_relevance", "conversation_id", "relevance_score"),
        Index("idx_context_type", "context_type"),
        Index("idx_context_focus", "focus_area"),
        Index("idx_context_timestamp", "timestamp"),
    )

    def __repr__(self):
        return f"<MemoryContextItem(id={self.id}, source='{self.source}', type='{self.context_type}', relevance={self.relevance_score:.2f})>"

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "source": self.source,
            "content": self.content,
            "relevance_score": self.relevance_score,
            "context_type": self.context_type,
            "original_role": self.original_role,
            "focus_area": self.focus_area,
            "preference_type": self.preference_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "additional_data": self.additional_data,
        }

    @classmethod
    def from_memory_context_item(
        cls, conversation_id: str, item: dict, source: str = "conversation"
    ):
        """
        Create MemoryContextItem from memory context item.

        Args:
            conversation_id: Conversation identifier
            item: Memory context item dictionary
            source: Source of the context item

        Returns:
            MemoryContextItem instance
        """
        # Extract metadata, excluding fields that have dedicated columns
        metadata_fields = [
            "id",
            "source",
            "content",
            "relevance_score",
            "context_type",
            "original_role",
            "focus_area",
            "preference_type",
            "timestamp",
        ]
        metadata = {k: v for k, v in item.items() if k not in metadata_fields}

        # Get content and ensure it's a string
        content = item.get("content", "")
        if not isinstance(content, str):
            if isinstance(content, dict):
                # If content is a dict, move it to metadata and create a summary
                metadata["original_content"] = content
                content = (
                    f"[{item.get('context_type', 'fact').upper()}] {source} context"
                )
            else:
                # Convert any other type to string
                content = str(content)

        return cls(
            conversation_id=conversation_id,
            source=source,
            content=content,
            relevance_score=item.get("relevance_score", 0.5),
            context_type=item.get("context_type", "fact"),
            original_role=item.get("role"),
            focus_area=item.get("focus_area"),
            preference_type=item.get("preference_type"),
            additional_data=metadata if metadata else None,
        )

    @classmethod
    def from_focus_area(
        cls, conversation_id: str, focus_area: str, relevance_score: float = 0.8
    ):
        """
        Create MemoryContextItem from focus area.

        Args:
            conversation_id: Conversation identifier
            focus_area: Focus area string
            relevance_score: Relevance score for this focus area

        Returns:
            MemoryContextItem instance
        """
        return cls(
            conversation_id=conversation_id,
            source="focus",
            content=f"Focus area: {focus_area}",
            relevance_score=relevance_score,
            context_type="focus_area",
            focus_area=focus_area,
        )

    @classmethod
    def from_ltm_item(
        cls, conversation_id: str, ltm_item: dict, relevance_score: float = 0.7
    ):
        """
        Create MemoryContextItem from LTM (Long-Term Memory) item.

        Args:
            conversation_id: Conversation identifier
            ltm_item: LTM item dictionary
            relevance_score: Relevance score for this LTM item

        Returns:
            MemoryContextItem instance
        """
        return cls(
            conversation_id=conversation_id,
            source="ltm",
            content=ltm_item.get("content", ""),
            relevance_score=relevance_score,
            context_type="fact",
            additional_data=ltm_item.get("metadata", {}),
        )

    @classmethod
    def from_rag_item(
        cls, conversation_id: str, rag_item: dict, relevance_score: float = 0.6
    ):
        """
        Create MemoryContextItem from RAG (Retrieval-Augmented Generation) item.

        Args:
            conversation_id: Conversation identifier
            rag_item: RAG item dictionary
            relevance_score: Relevance score for this RAG item

        Returns:
            MemoryContextItem instance
        """
        return cls(
            conversation_id=conversation_id,
            source="rag",
            content=rag_item.get("content", ""),
            relevance_score=relevance_score,
            context_type="fact",
            additional_data=rag_item.get("metadata", {}),
        )
