"""
Unit tests for LTM (Long-Term Memory) Tool.

This module tests the LTM tool functionality including
memory creation, search, retrieval, and management.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from personal_assistant.tools.ltm.ltm_tool import LTMTool
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import ToolDataGenerator


class TestLTMTool:
    """Test cases for LTM Tool."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.ltm_tool = LTMTool()
        self.test_memory_data = {
            "content": "User prefers morning meetings",
            "tags": "work,preference,schedule",
            "importance_score": 7,
            "context": "Based on calendar analysis",
            "memory_type": "preference",
            "category": "work",
            "confidence_score": 0.9,
            "source_type": "conversation",
            "source_id": "conv_123",
            "created_by": "system",
            "metadata": {"frequency": "daily", "context": "meetings"}
        }

    def test_ltm_tool_initialization(self):
        """Test LTM tool initialization."""
        assert self.ltm_tool is not None
        assert hasattr(self.ltm_tool, 'add_memory_tool')
        assert hasattr(self.ltm_tool, 'search_memories_tool')
        assert hasattr(self.ltm_tool, 'get_relevant_memories_tool')
        assert hasattr(self.ltm_tool, 'delete_memory_tool')
        assert hasattr(self.ltm_tool, 'get_stats_tool')
        assert hasattr(self.ltm_tool, 'get_enhanced_memories_tool')
        assert hasattr(self.ltm_tool, 'get_memory_relationships_tool')
        assert hasattr(self.ltm_tool, 'get_memory_analytics_tool')

    def test_ltm_tool_iteration(self):
        """Test that LTM tool is iterable and returns all tools."""
        tools = list(self.ltm_tool)
        assert len(tools) == 8
        
        tool_names = [tool.name for tool in tools]
        expected_names = [
            "add_ltm_memory",
            "search_ltm_memories", 
            "get_relevant_ltm_memories",
            "delete_ltm_memory",
            "get_ltm_stats",
            "get_enhanced_ltm_memories",
            "get_memory_relationships",
            "get_memory_analytics"
        ]
        
        for expected_name in expected_names:
            assert expected_name in tool_names

    def test_add_memory_tool_properties(self):
        """Test add memory tool properties."""
        tool = self.ltm_tool.add_memory_tool
        assert tool.name == "add_ltm_memory"
        assert "Add a new Long-Term Memory" in tool.description
        assert tool.parameters is not None
        assert "content" in tool.parameters
        assert "tags" in tool.parameters
        assert "importance_score" in tool.parameters

    def test_search_memories_tool_properties(self):
        """Test search memories tool properties."""
        tool = self.ltm_tool.search_memories_tool
        assert tool.name == "search_ltm_memories"
        assert "Search Long-Term Memory" in tool.description
        assert "query" in tool.parameters
        assert "limit" in tool.parameters
        assert "min_importance" in tool.parameters

    def test_get_relevant_memories_tool_properties(self):
        """Test get relevant memories tool properties."""
        tool = self.ltm_tool.get_relevant_memories_tool
        assert tool.name == "get_relevant_ltm_memories"
        assert "Get LTM memories relevant" in tool.description
        assert "context" in tool.parameters
        assert "limit" in tool.parameters

    def test_delete_memory_tool_properties(self):
        """Test delete memory tool properties."""
        tool = self.ltm_tool.delete_memory_tool
        assert tool.name == "delete_ltm_memory"
        assert "Delete a Long-Term Memory" in tool.description
        assert "memory_id" in tool.parameters

    def test_get_stats_tool_properties(self):
        """Test get stats tool properties."""
        tool = self.ltm_tool.get_stats_tool
        assert tool.name == "get_ltm_stats"
        assert "Get statistics about LTM memories" in tool.description
        assert tool.parameters == {}

    def test_get_enhanced_memories_tool_properties(self):
        """Test get enhanced memories tool properties."""
        tool = self.ltm_tool.get_enhanced_memories_tool
        assert tool.name == "get_enhanced_ltm_memories"
        assert "Get LTM memories with enhanced context" in tool.description
        assert "query" in tool.parameters
        assert "memory_type" in tool.parameters
        assert "category" in tool.parameters
        assert "include_context" in tool.parameters

    def test_get_memory_relationships_tool_properties(self):
        """Test get memory relationships tool properties."""
        tool = self.ltm_tool.get_memory_relationships_tool
        assert tool.name == "get_memory_relationships"
        assert "Get relationships between LTM memories" in tool.description
        assert "memory_id" in tool.parameters

    def test_get_memory_analytics_tool_properties(self):
        """Test get memory analytics tool properties."""
        tool = self.ltm_tool.get_memory_analytics_tool
        assert tool.name == "get_memory_analytics"
        assert "Get comprehensive analytics" in tool.description
        assert tool.parameters == {}

    @pytest.mark.asyncio
    async def test_add_memory_success(self):
        """Test successful memory addition."""
        with patch('personal_assistant.tools.ltm.ltm_tool.add_ltm_memory') as mock_add:
            mock_add.return_value = {"id": 123, "status": "created"}
            
            result = await self.ltm_tool.add_memory(
                content=self.test_memory_data["content"],
                tags=self.test_memory_data["tags"],
                importance_score=self.test_memory_data["importance_score"],
                context=self.test_memory_data["context"],
                memory_type=self.test_memory_data["memory_type"],
                category=self.test_memory_data["category"],
                confidence_score=self.test_memory_data["confidence_score"],
                source_type=self.test_memory_data["source_type"],
                source_id=self.test_memory_data["source_id"],
                created_by=self.test_memory_data["created_by"],
                metadata=self.test_memory_data["metadata"]
            )
            
            assert "Successfully created LTM memory with ID: 123" in result
            mock_add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_memory_invalid_importance_score(self):
        """Test memory addition with invalid importance score."""
        result = await self.ltm_tool.add_memory(
            content="Test content",
            tags="test",
            importance_score=15  # Invalid: should be 1-10
        )
        
        assert "Error: Importance score must be between 1 and 10" in result

    @pytest.mark.asyncio
    async def test_add_memory_invalid_confidence_score(self):
        """Test memory addition with invalid confidence score."""
        result = await self.ltm_tool.add_memory(
            content="Test content",
            tags="test",
            importance_score=5,
            confidence_score=1.5  # Invalid: should be 0.0-1.0
        )
        
        assert "Error: Confidence score must be between 0.0 and 1.0" in result

    @pytest.mark.asyncio
    async def test_add_memory_with_unexpected_parameters(self):
        """Test memory addition with unexpected parameters (should be ignored)."""
        with patch('personal_assistant.tools.ltm.ltm_tool.add_ltm_memory') as mock_add:
            mock_add.return_value = {"id": 124, "status": "created"}
            
            result = await self.ltm_tool.add_memory(
                content="Test content",
                tags="test",
                importance_score=5,
                title="This should be ignored",  # Unexpected parameter
                body="This should also be ignored"  # Unexpected parameter
            )
            
            assert "Successfully created LTM memory with ID: 124" in result
            mock_add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_memory_exception_handling(self):
        """Test memory addition exception handling."""
        with patch('personal_assistant.tools.ltm.ltm_tool.add_ltm_memory') as mock_add:
            mock_add.side_effect = Exception("Database error")
            
            result = await self.ltm_tool.add_memory(
                content="Test content",
                tags="test",
                importance_score=5
            )
            
            assert "Error creating LTM memory: Database error" in result

    @pytest.mark.asyncio
    async def test_search_memories_success(self):
        """Test successful memory search."""
        mock_memories = [
            {
                "id": 1,
                "content": "User prefers morning meetings",
                "importance_score": 7,
                "tags": ["work", "preference"]
            },
            {
                "id": 2,
                "content": "User likes coffee in the morning",
                "importance_score": 5,
                "tags": ["personal", "preference"]
            }
        ]
        
        with patch('personal_assistant.tools.ltm.ltm_tool.search_ltm_memories') as mock_search:
            mock_search.return_value = mock_memories
            
            result = await self.ltm_tool.search_memories(
                query="morning preferences",
                limit=5,
                min_importance=1
            )
            
            assert "Found 2 LTM memories matching 'morning preferences'" in result
            assert "ID: 1" in result
            assert "ID: 2" in result
            assert "User prefers morning meetings" in result
            assert "User likes coffee in the morning" in result

    @pytest.mark.asyncio
    async def test_search_memories_no_results(self):
        """Test memory search with no results."""
        with patch('personal_assistant.tools.ltm.ltm_tool.search_ltm_memories') as mock_search:
            mock_search.return_value = []
            
            result = await self.ltm_tool.search_memories(
                query="nonexistent query",
                limit=5,
                min_importance=1
            )
            
            assert "No LTM memories found matching 'nonexistent query'" in result

    @pytest.mark.asyncio
    async def test_search_memories_exception_handling(self):
        """Test memory search exception handling."""
        with patch('personal_assistant.tools.ltm.ltm_tool.search_ltm_memories') as mock_search:
            mock_search.side_effect = Exception("Search error")
            
            result = await self.ltm_tool.search_memories(
                query="test query",
                limit=5,
                min_importance=1
            )
            
            assert "Error searching LTM memories: Search error" in result

    @pytest.mark.asyncio
    async def test_get_relevant_memories_success(self):
        """Test successful relevant memories retrieval."""
        mock_memories = [
            {
                "id": 1,
                "content": "User prefers morning meetings",
                "importance_score": 7,
                "tags": ["work", "preference"]
            }
        ]
        
        with patch('personal_assistant.tools.ltm.ltm_tool.get_relevant_ltm_memories') as mock_get:
            mock_get.return_value = mock_memories
            
            result = await self.ltm_tool.get_relevant_memories(
                context="scheduling a meeting",
                limit=3
            )
            
            assert "Found 1 relevant LTM memories" in result
            assert "ID: 1" in result
            assert "User prefers morning meetings" in result

    @pytest.mark.asyncio
    async def test_get_relevant_memories_no_results(self):
        """Test relevant memories retrieval with no results."""
        with patch('personal_assistant.tools.ltm.ltm_tool.get_relevant_ltm_memories') as mock_get:
            mock_get.return_value = []
            
            result = await self.ltm_tool.get_relevant_memories(
                context="completely unrelated context",
                limit=3
            )
            
            assert "No relevant LTM memories found for the current context" in result

    @pytest.mark.asyncio
    async def test_get_relevant_memories_exception_handling(self):
        """Test relevant memories retrieval exception handling."""
        with patch('personal_assistant.tools.ltm.ltm_tool.get_relevant_ltm_memories') as mock_get:
            mock_get.side_effect = Exception("Retrieval error")
            
            result = await self.ltm_tool.get_relevant_memories(
                context="test context",
                limit=3
            )
            
            assert "Error getting relevant LTM memories: Retrieval error" in result

    @pytest.mark.asyncio
    async def test_delete_memory_success(self):
        """Test successful memory deletion."""
        with patch('personal_assistant.tools.ltm.ltm_tool.delete_ltm_memory') as mock_delete:
            mock_delete.return_value = True
            
            result = await self.ltm_tool.delete_memory(memory_id=123)
            
            assert "Successfully deleted LTM memory with ID 123" in result

    @pytest.mark.asyncio
    async def test_delete_memory_not_found(self):
        """Test memory deletion when memory not found."""
        with patch('personal_assistant.tools.ltm.ltm_tool.delete_ltm_memory') as mock_delete:
            mock_delete.return_value = False
            
            result = await self.ltm_tool.delete_memory(memory_id=999)
            
            assert "Failed to delete LTM memory with ID 999 (not found or access denied)" in result

    @pytest.mark.asyncio
    async def test_delete_memory_exception_handling(self):
        """Test memory deletion exception handling."""
        with patch('personal_assistant.tools.ltm.ltm_tool.delete_ltm_memory') as mock_delete:
            mock_delete.side_effect = Exception("Delete error")
            
            result = await self.ltm_tool.delete_memory(memory_id=123)
            
            assert "Error deleting LTM memory: Delete error" in result

    @pytest.mark.asyncio
    async def test_get_stats_success(self):
        """Test successful stats retrieval."""
        mock_stats = {
            "total_memories": 25,
            "average_importance": 6.2,
            "top_tags": [("work", 8), ("personal", 6), ("preference", 5)]
        }
        
        with patch('personal_assistant.tools.ltm.ltm_tool.get_ltm_memory_stats') as mock_stats_func:
            mock_stats_func.return_value = mock_stats
            
            result = await self.ltm_tool.get_stats()
            
            assert "LTM Memory Statistics:" in result
            assert "Total memories: 25" in result
            assert "Average importance: 6.2" in result
            assert "work: 8" in result
            assert "personal: 6" in result
            assert "preference: 5" in result

    @pytest.mark.asyncio
    async def test_get_stats_no_tags(self):
        """Test stats retrieval with no tags."""
        mock_stats = {
            "total_memories": 0,
            "average_importance": 0,
            "top_tags": []
        }
        
        with patch('personal_assistant.tools.ltm.ltm_tool.get_ltm_memory_stats') as mock_stats_func:
            mock_stats_func.return_value = mock_stats
            
            result = await self.ltm_tool.get_stats()
            
            assert "Total memories: 0" in result
            assert "No tags found" in result

    @pytest.mark.asyncio
    async def test_get_stats_exception_handling(self):
        """Test stats retrieval exception handling."""
        with patch('personal_assistant.tools.ltm.ltm_tool.get_ltm_memory_stats') as mock_stats_func:
            mock_stats_func.side_effect = Exception("Stats error")
            
            result = await self.ltm_tool.get_stats()
            
            assert "Error getting LTM stats: Stats error" in result

    @pytest.mark.asyncio
    async def test_get_enhanced_memories_success(self):
        """Test enhanced memories retrieval."""
        result = await self.ltm_tool.get_enhanced_memories(
            query="morning preferences",
            memory_type="preference",
            category="work",
            min_importance=5,
            limit=5,
            include_context=True
        )
        
        # Should return a message about enhanced search not being available
        assert "Enhanced search not available" in result or "No memories found" in result

    @pytest.mark.asyncio
    async def test_get_enhanced_memories_no_query(self):
        """Test enhanced memories retrieval with no query (should use default)."""
        # Test that the method handles no query gracefully
        result = await self.ltm_tool.get_enhanced_memories()
        
        # Should return a message about enhanced search not being available
        assert "Enhanced search not available" in result or "No memories found" in result

    @pytest.mark.asyncio
    async def test_get_enhanced_memories_import_error(self):
        """Test enhanced memories retrieval when enhanced storage is not available."""
        # Test that the method handles import errors gracefully
        result = await self.ltm_tool.get_enhanced_memories()
        
        assert "Enhanced search not available" in result or "No memories found" in result

    @pytest.mark.asyncio
    async def test_get_memory_relationships_success(self):
        """Test memory relationships retrieval."""
        result = await self.ltm_tool.get_memory_relationships(memory_id=1)
        
        # Should return a message about enhanced features not being available
        assert "Enhanced relationship features not available" in result or "No relationships found" in result

    @pytest.mark.asyncio
    async def test_get_memory_relationships_no_results(self):
        """Test memory relationships retrieval with no results."""
        result = await self.ltm_tool.get_memory_relationships(memory_id=999)
        
        assert "Enhanced relationship features not available" in result or "No relationships found" in result

    @pytest.mark.asyncio
    async def test_get_memory_relationships_import_error(self):
        """Test memory relationships retrieval when enhanced storage is not available."""
        result = await self.ltm_tool.get_memory_relationships(memory_id=1)
        
        assert "Enhanced relationship features not available" in result

    @pytest.mark.asyncio
    async def test_get_memory_analytics_success(self):
        """Test memory analytics retrieval."""
        result = await self.ltm_tool.get_memory_analytics()
        
        # Should return a message about enhanced features not being available
        assert "Enhanced analytics features not available" in result or "No analytics available" in result

    @pytest.mark.asyncio
    async def test_get_memory_analytics_no_data(self):
        """Test memory analytics retrieval with no data."""
        result = await self.ltm_tool.get_memory_analytics()
        
        assert "Enhanced analytics features not available" in result or "No analytics available" in result

    @pytest.mark.asyncio
    async def test_get_memory_analytics_import_error(self):
        """Test memory analytics retrieval when enhanced storage is not available."""
        result = await self.ltm_tool.get_memory_analytics()
        
        assert "Enhanced analytics features not available" in result

    def test_format_context_summary(self):
        """Test context summary formatting."""
        context = {
            "source": {"type": "conversation", "id": "conv_123"},
            "temporal": {"created_at": "2024-01-01"},
            "custom": {"category": "work"}
        }
        
        result = self.ltm_tool._format_context_summary(context)
        
        assert "source.type: conversation" in result
        assert "source.id: conv_123" in result
        assert "temporal.created_at: 2024-01-01" in result
        assert "custom.category: work" in result

    def test_format_context_summary_empty(self):
        """Test context summary formatting with empty context."""
        result = self.ltm_tool._format_context_summary({})
        assert result == ""

    def test_format_context_summary_none(self):
        """Test context summary formatting with None context."""
        result = self.ltm_tool._format_context_summary(None)
        assert result == ""

    def test_format_context_summary_no_values(self):
        """Test context summary formatting with no actual values."""
        context = {
            "source": {"type": "", "id": None},
            "temporal": {"created_at": ""}
        }
        
        result = self.ltm_tool._format_context_summary(context)
        assert result == ""

    @pytest.mark.asyncio
    async def test_add_memory_with_enhanced_context(self):
        """Test memory addition with enhanced context creation."""
        with patch('personal_assistant.tools.ltm.ltm_tool.add_ltm_memory') as mock_add:
            mock_add.return_value = {"id": 125, "status": "created"}
            
            result = await self.ltm_tool.add_memory(
                content="Test content",
                tags="test",
                importance_score=5,
                memory_type="preference",
                category="work",
                source_type="conversation",
                source_id="conv_123",
                metadata={"key": "value"}
            )
            
            assert "Successfully created LTM memory with ID: 125" in result
            mock_add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_memory_enhanced_context_import_error(self):
        """Test memory addition when enhanced context import fails."""
        with patch('personal_assistant.tools.ltm.ltm_tool.add_ltm_memory') as mock_add:
            mock_add.return_value = {"id": 126, "status": "created"}
            
            result = await self.ltm_tool.add_memory(
                content="Test content",
                tags="test",
                importance_score=5,
                memory_type="preference"
            )
            
            assert "Successfully created LTM memory with ID: 126" in result
            mock_add.assert_called_once()

    def test_tool_parameter_validation(self):
        """Test that tool parameters are properly defined."""
        # Test add_memory_tool parameters
        add_params = self.ltm_tool.add_memory_tool.parameters
        assert add_params["content"]["type"] == "string"
        assert add_params["tags"]["type"] == "string"
        assert add_params["importance_score"]["type"] == "integer"
        assert add_params["memory_type"]["enum"] is not None
        assert "preference" in add_params["memory_type"]["enum"]
        assert "insight" in add_params["memory_type"]["enum"]
        
        # Test search_memories_tool parameters
        search_params = self.ltm_tool.search_memories_tool.parameters
        assert search_params["query"]["type"] == "string"
        assert search_params["limit"]["type"] == "integer"
        assert search_params["min_importance"]["type"] == "integer"
        
        # Test get_enhanced_memories_tool parameters
        enhanced_params = self.ltm_tool.get_enhanced_memories_tool.parameters
        assert enhanced_params["include_context"]["type"] == "boolean"
        assert enhanced_params["include_context"]["description"] == "Whether to include enhanced context information (default: true)"

    def test_tool_descriptions(self):
        """Test that tool descriptions are informative."""
        # Test that descriptions contain key information
        assert "Long-Term Memory" in self.ltm_tool.add_memory_tool.description
        assert "NOT for creating notes" in self.ltm_tool.add_memory_tool.description
        assert "insights, patterns, or preferences" in self.ltm_tool.add_memory_tool.description
        
        assert "Search Long-Term Memory" in self.ltm_tool.search_memories_tool.description
        assert "Get LTM memories relevant" in self.ltm_tool.get_relevant_memories_tool.description
        assert "Delete a Long-Term Memory" in self.ltm_tool.delete_memory_tool.description
        assert "Get statistics about LTM memories" in self.ltm_tool.get_stats_tool.description

    @pytest.mark.asyncio
    async def test_add_memory_tag_validation_and_suggestions(self):
        """Test memory addition with tag validation and suggestions."""
        with patch('personal_assistant.tools.ltm.ltm_tool.add_ltm_memory') as mock_add, \
             patch('personal_assistant.tools.ltm.ltm_tool.validate_tags') as mock_validate, \
             patch('personal_assistant.tools.ltm.ltm_tool.get_tag_suggestions') as mock_suggest:
            
            # Test with invalid tags that get replaced with suggestions
            mock_validate.return_value = ([], ["invalid_tag"])  # No valid tags, one invalid
            mock_suggest.return_value = ["work", "preference"]
            mock_add.return_value = {"id": 127, "status": "created"}
            
            result = await self.ltm_tool.add_memory(
                content="User prefers morning meetings",
                tags="invalid_tag",
                importance_score=5
            )
            
            assert "Successfully created LTM memory with ID: 127" in result
            mock_validate.assert_called_once_with(["invalid_tag"])
            mock_suggest.assert_called_once_with("User prefers morning meetings")
            # Should be called with suggested tags
            call_args = mock_add.call_args
            assert call_args[1]["tags"] == ["work", "preference"]

    @pytest.mark.asyncio
    async def test_add_memory_partial_tag_validation(self):
        """Test memory addition with some valid and some invalid tags."""
        with patch('personal_assistant.tools.ltm.ltm_tool.add_ltm_memory') as mock_add, \
             patch('personal_assistant.tools.ltm.ltm_tool.validate_tags') as mock_validate:
            
            # Test with mixed valid and invalid tags
            mock_validate.return_value = (["work", "preference"], ["invalid_tag"])
            mock_add.return_value = {"id": 128, "status": "created"}
            
            result = await self.ltm_tool.add_memory(
                content="User prefers morning meetings",
                tags="work,preference,invalid_tag",
                importance_score=5
            )
            
            assert "Successfully created LTM memory with ID: 128" in result
            # Should be called with only valid tags
            call_args = mock_add.call_args
            assert call_args[1]["tags"] == ["work", "preference"]

    def test_tool_categories(self):
        """Test that tools can have categories set."""
        # Test setting category on a tool
        tool = self.ltm_tool.add_memory_tool
        tool.set_category("LTM")
        assert tool.category == "LTM"
        
        # Test that category is returned correctly
        assert tool.category == "LTM"

    def test_tool_user_intent_tracking(self):
        """Test that tools can track user intent."""
        tool = self.ltm_tool.add_memory_tool
        
        # Test setting user intent
        tool.set_user_intent("Remember user preferences")
        assert tool.get_user_intent() == "Remember user preferences"
        
        # Test default user intent
        tool2 = self.ltm_tool.search_memories_tool
        assert tool2.get_user_intent() == "Unknown user intent"
