"""
Conversation State Model for Task 053: Database Schema Redesign

This model represents the core conversation state in the new normalized schema,
replacing the JSON blob approach with structured, queryable data.
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone

from .base import Base


class ConversationState(Base):
    """
    Core conversation state table - replaces the JSON blob approach.

    This table stores the essential conversation information in a normalized,
    queryable format that enables efficient storage and retrieval.
    """
    __tablename__ = 'conversation_states'

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(255), unique=True,
                             nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=False, index=True)
    user_input = Column(Text)
    focus_areas = Column(JSON)  # PostgreSQL JSONB for efficient querying
    step_count = Column(Integer, default=0)
    last_tool_result = Column(JSON)  # Store tool results as structured JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(), onupdate=func.now())

    # Relationships to related tables
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "ConversationMessage", back_populates="conversation_state", cascade="all, delete-orphan")
    context_items = relationship(
        "MemoryContextItem", back_populates="conversation_state", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ConversationState(conversation_id='{self.conversation_id}', user_id={self.user_id}, step_count={self.step_count})>"

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'user_input': self.user_input,
            'focus_areas': self.focus_areas,
            'step_count': self.step_count,
            'last_tool_result': self.last_tool_result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_agent_state(cls, conversation_id: str, user_id: int, agent_state):
        """
        Create ConversationState from AgentState object.

        Args:
            conversation_id: Unique conversation identifier
            user_id: User ID for the conversation
            agent_state: AgentState object to convert

        Returns:
            ConversationState instance
        """
        return cls(
            conversation_id=conversation_id,
            user_id=user_id,
            user_input=agent_state.user_input,
            focus_areas=agent_state.focus,
            step_count=agent_state.step_count,
            last_tool_result=agent_state.last_tool_result
        )
