"""
Chat API models for Task 073: Chat Integration with Agent Service.

This module defines Pydantic models for chat-related API requests and responses,
enabling type-safe communication between frontend and backend.
"""

from datetime import datetime
from typing import List, Optional, Union, Any

from pydantic import BaseModel, Field, field_validator


class MessageCreate(BaseModel):
    """Request model for creating a new message."""
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID (optional)")


class MessageResponse(BaseModel):
    """Response model for a message."""
    id: int
    conversation_id: str
    role: str
    content: str
    message_type: Optional[str] = None
    tool_name: Optional[str] = None
    tool_success: Optional[str] = None
    timestamp: datetime
    additional_data: Optional[dict] = None

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response model for a conversation."""
    id: int
    conversation_id: str
    user_id: int
    user_input: Optional[str] = None
    focus_areas: Optional[Union[dict, list, str]] = None
    step_count: int = 0
    last_tool_result: Optional[Union[dict, str]] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    @field_validator('focus_areas', mode='before')
    @classmethod
    def validate_focus_areas(cls, v):
        """Convert focus_areas to dict if it's a list or string."""
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, list):
            return {"areas": v}
        if isinstance(v, str):
            return {"description": v}
        return v

    @field_validator('last_tool_result', mode='before')
    @classmethod
    def validate_last_tool_result(cls, v):
        """Convert last_tool_result to dict if it's a string."""
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            return {"result": v}
        return v

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Response model for conversation list."""
    conversations: List[ConversationResponse]
    total: int
    page: int
    per_page: int


class ChatWebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str = Field(..., description="Message type: 'message', 'typing', 'error', 'connection'")
    data: dict = Field(..., description="Message data")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class SendMessageResponse(BaseModel):
    """Response model for sending a message."""
    user_message: MessageResponse
    ai_message: MessageResponse
    conversation_id: str


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    error_code: Optional[str] = None
