"""
LTM Memory API models.

This module provides Pydantic models for LTM memory API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class LTMMemoryResponse(BaseModel):
    """Response model for LTM memory information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    content: str
    tags: List[str]
    memory_type: Optional[str]
    category: Optional[str]
    importance_score: int
    confidence_score: float
    dynamic_importance: float
    context: Optional[str]
    context_data: Optional[Dict[str, Any]]
    source_type: Optional[str]
    source_id: Optional[str]
    created_by: str
    created_at: datetime
    last_accessed: datetime
    last_modified: datetime
    access_count: int
    last_access_context: Optional[str]
    related_memory_ids: Optional[List[int]]
    parent_memory_id: Optional[int]
    memory_metadata: Optional[Dict[str, Any]]
    is_archived: bool
    archive_reason: Optional[str]


class LTMMemoryCreateRequest(BaseModel):
    """Request model for creating a new LTM memory."""
    content: str = Field(..., min_length=1, max_length=10000,
                         description="Memory content")
    tags: List[str] = Field(default_factory=list,
                            description="Tags for categorization")
    memory_type: Optional[str] = Field(
        None, max_length=50, description="Type of memory")
    category: Optional[str] = Field(
        None, max_length=100, description="Memory category")
    importance_score: int = Field(
        default=1, ge=1, le=10, description="Importance score (1-10)")
    confidence_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    context: Optional[str] = Field(None, description="Context information")
    context_data: Optional[Dict[str, Any]] = Field(
        None, description="Structured context data")
    source_type: Optional[str] = Field(
        None, max_length=50, description="Source type")
    source_id: Optional[str] = Field(
        None, max_length=100, description="Source identifier")
    created_by: str = Field(default="user", max_length=50,
                            description="Who created this memory")
    related_memory_ids: Optional[List[int]] = Field(
        None, description="Related memory IDs")
    parent_memory_id: Optional[int] = Field(
        None, description="Parent memory ID")
    memory_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata")


class LTMMemoryUpdateRequest(BaseModel):
    """Request model for updating an LTM memory."""
    content: Optional[str] = Field(
        None, min_length=1, max_length=10000, description="Memory content")
    tags: Optional[List[str]] = Field(
        None, description="Tags for categorization")
    memory_type: Optional[str] = Field(
        None, max_length=50, description="Type of memory")
    category: Optional[str] = Field(
        None, max_length=100, description="Memory category")
    importance_score: Optional[int] = Field(
        None, ge=1, le=10, description="Importance score (1-10)")
    confidence_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    context: Optional[str] = Field(None, description="Context information")
    context_data: Optional[Dict[str, Any]] = Field(
        None, description="Structured context data")
    related_memory_ids: Optional[List[int]] = Field(
        None, description="Related memory IDs")
    parent_memory_id: Optional[int] = Field(
        None, description="Parent memory ID")
    memory_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata")
    is_archived: Optional[bool] = Field(
        None, description="Whether memory is archived")
    archive_reason: Optional[str] = Field(
        None, description="Reason for archiving")


class LTMMemoryListResponse(BaseModel):
    """Response model for LTM memory list."""
    memories: List[LTMMemoryResponse]
    total: int
    skip: int
    limit: int


class LTMMemorySearchRequest(BaseModel):
    """Request model for searching LTM memories."""
    query: Optional[str] = Field(None, description="Search query")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    memory_type: Optional[str] = Field(
        None, description="Filter by memory type")
    category: Optional[str] = Field(None, description="Filter by category")
    min_importance: Optional[int] = Field(
        None, ge=1, le=10, description="Minimum importance score")
    max_importance: Optional[int] = Field(
        None, ge=1, le=10, description="Maximum importance score")
    is_archived: Optional[bool] = Field(
        None, description="Filter by archived status")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=100,
                       description="Maximum number of records to return")


class LTMContextResponse(BaseModel):
    """Response model for LTM context information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    memory_id: int
    context_type: str
    context_key: str
    context_value: Optional[str]
    confidence: float
    created_at: datetime


class LTMMemoryTagResponse(BaseModel):
    """Response model for LTM memory tag information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    memory_id: int
    tag_name: str
    tag_category: Optional[str]
    tag_importance: float
    tag_confidence: float
    usage_count: int
    first_used: datetime
    last_used: datetime


class LTMMemoryAccessResponse(BaseModel):
    """Response model for LTM memory access information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    memory_id: int
    access_timestamp: datetime
    access_context: Optional[str]
    access_method: Optional[str]
    user_query: Optional[str]
    was_relevant: Optional[bool]
    relevance_score: Optional[float]
