"""
Conversation Message Model for Task 053: Database Schema Redesign

This model represents individual conversation messages in the new normalized schema,
enabling efficient querying and analysis of conversation flow.
"""


from typing import Optional

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class ConversationMessage(Base):
    """
    Individual conversation messages table - stores each message with metadata.

    This table enables efficient querying of conversation history, tool calls,
    and message analysis without loading entire conversation state.
    """

    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(
        String(255),
        ForeignKey("conversation_states.conversation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # 'user', 'assistant', 'tool', 'system'
    role = Column(String(50), nullable=False, index=True)
    content = Column(Text)
    # 'user_input', 'assistant_response', 'tool_call', 'tool_result', 'system_message'
    message_type = Column(String(50), index=True)
    tool_name = Column(String(100), index=True)  # For tool-related messages
    # 'success', 'failed', 'pending'
    tool_success = Column(String(10), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    additional_data = Column(JSON)  # Additional message data as JSON

    # Relationship to conversation state
    conversation_state = relationship("ConversationState", back_populates="messages")

    # Indexes for performance
    __table_args__ = (
        Index("idx_message_conversation_role", "conversation_id", "role"),
        Index("idx_message_timestamp", "conversation_id", "timestamp"),
        Index("idx_message_type", "message_type"),
        Index("idx_message_tool", "tool_name", "tool_success"),
    )

    def __repr__(self):
        return f"<ConversationMessage(id={self.id}, role='{self.role}', type='{self.message_type}', conversation_id='{self.conversation_id}')>"

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "message_type": self.message_type,
            "tool_name": self.tool_name,
            "tool_success": self.tool_success,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "additional_data": self.additional_data,
        }

    @classmethod
    def from_conversation_item(
        cls, conversation_id: str, item, message_type: Optional[str] = None
    ):
        """
        Create ConversationMessage from conversation history item.

        Args:
            conversation_id: Conversation identifier
            item: Conversation history item (could be dict, message object, etc.)
            message_type: Type of message (auto-detected if not provided)

        Returns:
            ConversationMessage instance
        """
        # Handle different types of conversation items
        if isinstance(item, dict):
            role = item.get("role", "unknown")
            content = item.get("content", "")
            tool_name = item.get("tool_name")
            tool_success = item.get("tool_success")
            additional_data = {
                k: v
                for k, v in item.items()
                if k not in ["role", "content", "tool_name", "tool_success"]
            }
        elif hasattr(item, "role"):
            role = item.role
            content = getattr(item, "content", "")
            tool_name = getattr(item, "tool_name", None)
            tool_success = getattr(item, "tool_success", None)
            additional_data = {}
        else:
            # Fallback for unknown item types
            role = "unknown"
            content = str(item)
            tool_name = None
            tool_success = None
            additional_data = {}

        # Ensure content is always a string
        if not isinstance(content, str):
            if isinstance(content, dict):
                # If content is a dict, move it to additional_data and create a summary
                additional_data["original_content"] = content
                content = f"[{role.upper()}] {message_type or 'message'}"
            else:
                # Convert any other type to string
                content = str(content)

        # Auto-detect message type if not provided
        if not message_type:
            if role == "user":
                message_type = "user_input"
            elif role == "assistant":
                message_type = "assistant_response"
            elif role == "tool":
                message_type = "tool_call" if tool_name else "tool_result"
            elif role == "system":
                message_type = "system_message"
            else:
                message_type = "unknown"

        return cls(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_type=message_type,
            tool_name=tool_name,
            tool_success=tool_success,
            additional_data=additional_data,
        )
