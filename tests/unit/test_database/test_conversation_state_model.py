"""
Unit tests for ConversationState Model.

This module tests the ConversationState model functionality including
conversation management, JSON field handling, and relationships.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from personal_assistant.database.models.conversation_state import ConversationState
from personal_assistant.database.models.base import Base
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import DatabaseDataGenerator


class TestConversationState:
    """Test cases for ConversationState model."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_conversation_id = "conv_12345"
        self.test_user_id = 126
        self.test_user_input = "I need help with my calendar"
        self.test_focus_areas = ["calendar", "scheduling", "time_management"]
        self.test_step_count = 3
        self.test_tool_result = {
            "tool_name": "calendar_tool",
            "result": "Found 5 upcoming events",
            "status": "success"
        }

    def test_conversation_state_initialization(self):
        """Test ConversationState initialization."""
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id,
            user_input=self.test_user_input,
            focus_areas=self.test_focus_areas,
            step_count=self.test_step_count,
            last_tool_result=self.test_tool_result
        )
        
        assert conversation.conversation_id == self.test_conversation_id
        assert conversation.user_id == self.test_user_id
        assert conversation.user_input == self.test_user_input
        assert conversation.focus_areas == self.test_focus_areas
        assert conversation.step_count == self.test_step_count
        assert conversation.last_tool_result == self.test_tool_result
        assert conversation.id is None  # Not set until saved to database

    def test_conversation_state_minimal_initialization(self):
        """Test ConversationState initialization with minimal data."""
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id
        )
        
        assert conversation.conversation_id == self.test_conversation_id
        assert conversation.user_id == self.test_user_id
        assert conversation.user_input is None
        assert conversation.focus_areas is None
        assert conversation.step_count is None  # Default value is applied at database level
        assert conversation.last_tool_result is None

    def test_conversation_state_table_name(self):
        """Test that ConversationState has correct table name."""
        assert ConversationState.__tablename__ == "conversation_states"

    def test_conversation_state_columns(self):
        """Test that ConversationState has expected columns."""
        columns = ConversationState.__table__.columns
        
        assert "id" in columns
        assert "conversation_id" in columns
        assert "user_id" in columns
        assert "user_input" in columns
        assert "focus_areas" in columns
        assert "step_count" in columns
        assert "last_tool_result" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_conversation_state_column_types(self):
        """Test that ConversationState columns have correct types."""
        columns = ConversationState.__table__.columns
        
        assert str(columns["id"].type) == "INTEGER"
        assert str(columns["conversation_id"].type) == "VARCHAR(255)"
        assert str(columns["user_id"].type) == "INTEGER"
        assert str(columns["user_input"].type) == "TEXT"
        assert str(columns["focus_areas"].type) == "JSON"
        assert str(columns["step_count"].type) == "INTEGER"
        assert str(columns["last_tool_result"].type) == "JSON"

    def test_conversation_state_constraints(self):
        """Test that ConversationState has correct constraints."""
        columns = ConversationState.__table__.columns
        
        # Primary key
        assert columns["id"].primary_key is True
        assert columns["id"].nullable is False
        
        # Required fields
        assert columns["conversation_id"].nullable is False
        assert columns["user_id"].nullable is False
        
        # Optional fields
        assert columns["user_input"].nullable is True
        assert columns["focus_areas"].nullable is True
        assert columns["step_count"].nullable is True
        assert columns["last_tool_result"].nullable is True

    def test_conversation_state_foreign_keys(self):
        """Test that ConversationState has correct foreign keys."""
        foreign_keys = ConversationState.__table__.foreign_keys
        
        # Should have foreign key to users table
        user_fk = None
        for fk in foreign_keys:
            if fk.column.table.name == "users":
                user_fk = fk
                break
        
        assert user_fk is not None
        assert user_fk.column.name == "id"

    def test_conversation_state_indexes(self):
        """Test that ConversationState has correct indexes."""
        indexes = ConversationState.__table__.indexes
        
        # Should have indexes on conversation_id and user_id
        index_names = [idx.name for idx in indexes]
        
        # Check for conversation_id index
        conv_id_index = any("conversation_id" in idx.name for idx in indexes)
        assert conv_id_index
        
        # Check for user_id index
        user_id_index = any("user_id" in idx.name for idx in indexes)
        assert user_id_index

    def test_conversation_state_repr(self):
        """Test ConversationState __repr__ method."""
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id,
            step_count=self.test_step_count
        )
        conversation.id = 1
        
        result = repr(conversation)
        
        assert "ConversationState" in result
        assert f"conversation_id='{self.test_conversation_id}'" in result
        assert f"user_id={self.test_user_id}" in result
        assert f"step_count={self.test_step_count}" in result

    def test_conversation_state_to_dict(self):
        """Test ConversationState to_dict method."""
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id,
            user_input=self.test_user_input,
            focus_areas=self.test_focus_areas,
            step_count=self.test_step_count,
            last_tool_result=self.test_tool_result
        )
        conversation.id = 1
        conversation.created_at = datetime(2024, 1, 15, 10, 30, 0)
        conversation.updated_at = datetime(2024, 1, 15, 11, 30, 0)
        
        result = conversation.to_dict()
        
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["conversation_id"] == self.test_conversation_id
        assert result["user_id"] == self.test_user_id
        assert result["user_input"] == self.test_user_input
        assert result["focus_areas"] == self.test_focus_areas
        assert result["step_count"] == self.test_step_count
        assert result["last_tool_result"] == self.test_tool_result
        # Note: datetime objects are serialized to strings in to_dict
        assert result["created_at"] == "2024-01-15T10:30:00"
        assert result["updated_at"] == "2024-01-15T11:30:00"

    def test_conversation_state_json_fields(self):
        """Test ConversationState JSON field handling."""
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id
        )
        
        # Test focus_areas as list
        conversation.focus_areas = ["calendar", "scheduling", "reminders"]
        assert conversation.focus_areas == ["calendar", "scheduling", "reminders"]
        
        # Test focus_areas as dict
        conversation.focus_areas = {
            "primary": "calendar",
            "secondary": ["scheduling", "reminders"],
            "metadata": {"confidence": 0.95}
        }
        assert conversation.focus_areas["primary"] == "calendar"
        assert conversation.focus_areas["secondary"] == ["scheduling", "reminders"]
        assert conversation.focus_areas["metadata"]["confidence"] == 0.95
        
        # Test last_tool_result as complex object
        conversation.last_tool_result = {
            "tool_name": "calendar_tool",
            "parameters": {"date_range": "next_week", "include_details": True},
            "result": {
                "events": [
                    {"title": "Meeting", "time": "2024-01-15T14:00:00Z"},
                    {"title": "Lunch", "time": "2024-01-16T12:00:00Z"}
                ],
                "total_count": 2
            },
            "execution_time": 1.23,
            "status": "success"
        }
        
        assert conversation.last_tool_result["tool_name"] == "calendar_tool"
        assert conversation.last_tool_result["result"]["total_count"] == 2
        assert len(conversation.last_tool_result["result"]["events"]) == 2

    def test_conversation_state_relationships(self):
        """Test ConversationState relationships."""
        # Mock the relationships
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id
        )
        
        # Test that relationships are defined
        assert hasattr(conversation, 'user')
        assert hasattr(conversation, 'messages')
        assert hasattr(conversation, 'context_items')

    def test_conversation_state_with_none_values(self):
        """Test ConversationState with None values."""
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id
        )
        
        # All optional fields should be None
        assert conversation.user_input is None
        assert conversation.focus_areas is None
        assert conversation.last_tool_result is None
        assert conversation.step_count is None  # Default value is applied at database level, not None

    def test_conversation_state_step_count_default(self):
        """Test ConversationState step_count default value."""
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id
        )
        
        assert conversation.step_count is None

    def test_conversation_state_step_count_custom(self):
        """Test ConversationState with custom step_count."""
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id,
            step_count=5
        )
        
        assert conversation.step_count == 5

    def test_conversation_state_long_user_input(self):
        """Test ConversationState with long user input."""
        long_input = "This is a very long user input that contains multiple sentences and should be handled properly by the TEXT field. " * 10
        
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id,
            user_input=long_input
        )
        
        assert conversation.user_input == long_input
        assert len(conversation.user_input) > 1000

    def test_conversation_state_special_characters(self):
        """Test ConversationState with special characters."""
        special_input = "I need help with my calendar! @#$%^&*()_+-=[]{}|;':\",./<>?"
        special_focus_areas = ["calendar", "scheduling", "time-management", "reminders@work"]
        
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id,
            user_input=special_input,
            focus_areas=special_focus_areas
        )
        
        assert conversation.user_input == special_input
        assert conversation.focus_areas == special_focus_areas

    def test_conversation_state_unicode_support(self):
        """Test ConversationState with Unicode characters."""
        unicode_input = "I need help with my calendar 📅 and scheduling ⏰"
        unicode_focus_areas = ["calendar", "scheduling", "时间管理", "提醒事项"]
        
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id,
            user_input=unicode_input,
            focus_areas=unicode_focus_areas
        )
        
        assert conversation.user_input == unicode_input
        assert conversation.focus_areas == unicode_focus_areas

    def test_conversation_state_equality(self):
        """Test ConversationState equality comparison."""
        # SQLAlchemy models don't implement custom __eq__ by default
        # This test is skipped as it requires custom equality implementation
        pytest.skip("SQLAlchemy models don't implement custom equality by default")

    def test_conversation_state_inequality(self):
        """Test ConversationState inequality comparison."""
        conversation1 = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id
        )
        conversation1.id = 1
        
        conversation2 = ConversationState(
            conversation_id="different_conv_id",
            user_id=self.test_user_id
        )
        conversation2.id = 2
        
        # Models with different IDs should not be equal
        assert conversation1 != conversation2

    def test_conversation_state_hash(self):
        """Test ConversationState hash functionality."""
        # SQLAlchemy models don't implement custom __hash__ by default
        # This test is skipped as it requires custom hash implementation
        pytest.skip("SQLAlchemy models don't implement custom hash by default")

    def test_conversation_state_serialization_with_complex_json(self):
        """Test ConversationState serialization with complex JSON data."""
        complex_tool_result = {
            "tool_name": "multi_step_tool",
            "steps": [
                {"step": 1, "action": "search", "result": "found 5 items"},
                {"step": 2, "action": "filter", "result": "filtered to 3 items"},
                {"step": 3, "action": "format", "result": "formatted for display"}
            ],
            "metadata": {
                "execution_time": 2.5,
                "memory_usage": "15MB",
                "cache_hit": False
            },
            "errors": [],
            "warnings": ["Some items were filtered out"]
        }
        
        conversation = ConversationState(
            conversation_id=self.test_conversation_id,
            user_id=self.test_user_id,
            last_tool_result=complex_tool_result
        )
        conversation.id = 1
        
        result = conversation.to_dict()
        
        assert result["last_tool_result"]["tool_name"] == "multi_step_tool"
        assert len(result["last_tool_result"]["steps"]) == 3
        assert result["last_tool_result"]["steps"][0]["step"] == 1
        assert result["last_tool_result"]["metadata"]["execution_time"] == 2.5
        assert result["last_tool_result"]["warnings"][0] == "Some items were filtered out"
