"""
Conversation API models.

This module provides Pydantic models for conversation API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class ConversationStateResponse(BaseModel):
    """Response model for conversation state information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: str
    user_id: int
    user_input: Optional[str]
    focus_areas: Optional[Dict[str, Any]]
    step_count: int
    last_tool_result: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ConversationStateCreateRequest(BaseModel):
    """Request model for creating a new conversation state."""
    conversation_id: str = Field(..., min_length=1, max_length=255,
                                 description="Unique conversation identifier")
    user_input: Optional[str] = Field(
        None, description="User input for this conversation")
    focus_areas: Optional[Dict[str, Any]] = Field(
        None, description="Focus areas for the conversation")
    step_count: int = Field(default=0, ge=0, description="Current step count")
    last_tool_result: Optional[Dict[str, Any]] = Field(
        None, description="Last tool result")


class ConversationStateUpdateRequest(BaseModel):
    """Request model for updating a conversation state."""
    user_input: Optional[str] = Field(
        None, description="User input for this conversation")
    focus_areas: Optional[Dict[str, Any]] = Field(
        None, description="Focus areas for the conversation")
    step_count: Optional[int] = Field(
        None, ge=0, description="Current step count")
    last_tool_result: Optional[Dict[str, Any]] = Field(
        None, description="Last tool result")


class ConversationMessageResponse(BaseModel):
    """Response model for conversation message information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: str
    role: str
    content: Optional[str]
    message_type: Optional[str]
    tool_name: Optional[str]
    tool_success: Optional[str]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]


class ConversationMessageCreateRequest(BaseModel):
    """Request model for creating a new conversation message."""
    conversation_id: str = Field(..., min_length=1,
                                 max_length=255, description="Conversation identifier")
    role: str = Field(..., min_length=1, max_length=50,
                      description="Message role (user, assistant, system)")
    content: Optional[str] = Field(None, description="Message content")
    message_type: Optional[str] = Field(
        None, max_length=50, description="Type of message")
    tool_name: Optional[str] = Field(
        None, max_length=100, description="Tool name if applicable")
    tool_success: Optional[str] = Field(
        None, max_length=10, description="Tool success status")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata")


class MemoryContextItemResponse(BaseModel):
    """Response model for memory context item information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: str
    source: str
    content: Optional[str]
    relevance_score: Optional[float]
    context_type: Optional[str]
    original_role: Optional[str]
    focus_area: Optional[str]
    preference_type: Optional[str]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]


class MemoryContextItemCreateRequest(BaseModel):
    """Request model for creating a new memory context item."""
    conversation_id: str = Field(..., min_length=1,
                                 max_length=255, description="Conversation identifier")
    source: str = Field(..., min_length=1, max_length=50,
                        description="Source of the context item")
    content: Optional[str] = Field(None, description="Context content")
    relevance_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Relevance score")
    context_type: Optional[str] = Field(
        None, max_length=50, description="Type of context")
    original_role: Optional[str] = Field(
        None, max_length=50, description="Original role")
    focus_area: Optional[str] = Field(
        None, max_length=100, description="Focus area")
    preference_type: Optional[str] = Field(
        None, max_length=100, description="Preference type")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata")


class ConversationListResponse(BaseModel):
    """Response model for conversation list."""
    conversations: List[ConversationStateResponse]
    total: int
    skip: int
    limit: int


class ConversationSearchRequest(BaseModel):
    """Request model for searching conversations."""
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    conversation_id: Optional[str] = Field(
        None, description="Filter by conversation ID")
    focus_areas: Optional[Dict[str, Any]] = Field(
        None, description="Filter by focus areas")
    min_step_count: Optional[int] = Field(
        None, ge=0, description="Minimum step count")
    max_step_count: Optional[int] = Field(
        None, ge=0, description="Maximum step count")
    created_after: Optional[datetime] = Field(
        None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(
        None, description="Filter by creation date")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=100,
                       description="Maximum number of records to return")
