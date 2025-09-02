"""
Unit tests for DynamicContextManager

Tests the dynamic context optimization with state coordination,
memory prioritization, and intelligent summarization.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from personal_assistant.memory.ltm_optimization.context_management import DynamicContextManager
from personal_assistant.memory.ltm_optimization.config import EnhancedLTMConfig
from personal_assistant.types.state import AgentState


class TestDynamicContextManager:
    """Test the DynamicContextManager class"""

    @pytest.fixture
    def config(self):
        """Create enhanced LTM config for testing"""
        config = EnhancedLTMConfig()
        config.min_context_length = 100
        config.max_context_length = 2000
        config.optimal_context_length = 800
        config.simple_query_threshold = 50
        config.complex_query_threshold = 200
        config.focus_boost_multiplier = 1.5
        config.state_context_weight = 0.3
        return config

    @pytest.fixture
    def context_manager(self, config):
        """Create DynamicContextManager instance for testing"""
        return DynamicContextManager(config)

    @pytest.fixture
    def sample_memories(self):
        """Sample memories for testing"""
        return [
            {
                "id": "1",
                "content": "User prefers concise responses and quick solutions",
                "tags": ["preference", "communication", "efficiency"],
                "importance_score": 9,
                "confidence_score": 0.95,
                "memory_type": "user_preference",
                "last_accessed": "2024-01-01T10:00:00Z",
                "created_at": "2024-01-01T09:00:00Z"
            },
            {
                "id": "2",
                "content": "User works in software development and automation",
                "tags": ["work", "software", "development", "automation"],
                "importance_score": 8,
                "confidence_score": 0.9,
                "memory_type": "general",
                "last_accessed": "2024-01-02T10:00:00Z",
                "created_at": "2024-01-02T09:00:00Z"
            },
            {
                "id": "3",
                "content": "User likes automation tools and efficiency improvements",
                "tags": ["automation", "tools", "efficiency", "preference"],
                "importance_score": 7,
                "confidence_score": 0.85,
                "memory_type": "user_preference",
                "last_accessed": "2024-01-03T10:00:00Z",
                "created_at": "2024-01-03T09:00:00Z"
            }
        ]

    @pytest.fixture
    def sample_state(self):
        """Sample agent state for testing"""
        state = AgentState(user_input="test")
        state.focus = ["software development", "automation"]
        state.last_tool_result = "Successfully created automation script"
        return state

    def test_init(self, context_manager, config):
        """Test context manager initialization"""
        assert context_manager.config == config
        assert context_manager.min_context_length == 100
        assert context_manager.max_context_length == 2000
        assert context_manager.optimal_context_length == 800
        assert context_manager.simple_query_threshold == 50
        assert context_manager.complex_query_threshold == 200
        assert context_manager.focus_boost_multiplier == 1.5
        assert context_manager.state_context_weight == 0.3

    def test_calculate_dynamic_context_size_simple(self, context_manager):
        """Test dynamic context size calculation for simple queries"""
        size = context_manager._calculate_dynamic_context_size(
            "short query", "simple", None)
        # 800 * 0.6 * 0.8 = 384, but min is 100
        assert size == 384

    def test_calculate_dynamic_context_size_medium(self, context_manager):
        """Test dynamic context size calculation for medium queries"""
        size = context_manager._calculate_dynamic_context_size(
            "medium length query", "medium", None)
        # 800 * 1.0 * 0.8 = 640 (input length < 50, so 0.8 multiplier)
        assert size == 640

    def test_calculate_dynamic_context_size_complex(self, context_manager):
        """Test dynamic context size calculation for complex queries"""
        long_input = "very long complex query " * 20  # 500 characters
        size = context_manager._calculate_dynamic_context_size(
            long_input, "complex", None)
        # 800 * 1.4 * 1.3 = 1456
        assert size == 1456

    def test_calculate_dynamic_context_size_with_state(self, context_manager, sample_state):
        """Test dynamic context size calculation with state context"""
        size = context_manager._calculate_dynamic_context_size(
            "test query", "medium", sample_state)
        # 800 * 1.0 * 0.8 * 1.2 = 768 (input length < 50, so 0.8 multiplier)
        assert size == 768

    def test_calculate_dynamic_context_size_bounds(self, context_manager):
        """Test dynamic context size respects bounds"""
        # Test minimum bound
        size = context_manager._calculate_dynamic_context_size(
            "very short", "simple", None)
        assert size >= 100

        # Test maximum bound
        very_long_input = "very long input " * 100  # 1600 characters
        size = context_manager._calculate_dynamic_context_size(
            very_long_input, "complex", None)
        assert size <= 2000

    @pytest.mark.asyncio
    async def test_prioritize_memories_with_state(self, context_manager, sample_state):
        """Test memory prioritization with state context"""
        memories = [
            {
                "id": "1",
                "content": "software development patterns",
                "tags": ["software", "development"],
                "importance_score": 8,
                "memory_type": "general"
            },
            {
                "id": "2",
                "content": "general information",
                "tags": ["general"],
                "importance_score": 6,
                "memory_type": "general"
            }
        ]

        prioritized = await context_manager._prioritize_memories_with_state(
            memories, "software development", sample_state, [
                "software development"]
        )

        # Should prioritize software development memory first
        assert len(prioritized) == 2
        assert prioritized[0]["id"] == "1"  # Software development first
        assert prioritized[1]["id"] == "2"  # General second

    def test_calculate_comprehensive_memory_score(self, context_manager, sample_state):
        """Test comprehensive memory score calculation"""
        memory = {
            "content": "software development best practices",
            "tags": ["software", "development", "best_practices"],
            "importance_score": 8,
            "confidence_score": 0.9,
            "memory_type": "general",
            "last_accessed": "2024-01-01T10:00:00Z"
        }

        score = context_manager._calculate_comprehensive_memory_score(
            memory, "software development", sample_state, [
                "software development"]
        )

        assert score > 0.5  # Should have good score
        assert score <= 1.0  # Should be capped at 1.0

    def test_calculate_enhanced_relevance_boost(self, context_manager):
        """Test enhanced relevance boost calculation"""
        memory = {
            "content": "software development patterns and best practices",
            "tags": ["software", "development", "patterns"]
        }

        boost = context_manager._calculate_enhanced_relevance_boost(
            memory, "software development patterns"
        )

        assert boost > 0.1  # Should have some relevance
        assert boost <= 0.3  # Should be within expected range

    def test_calculate_enhanced_recency_boost(self, context_manager):
        """Test enhanced recency boost calculation"""
        # Mock current time to be 2024-01-02T00:00:00Z
        with patch('personal_assistant.memory.ltm_optimization.context_management.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
            mock_datetime.fromisoformat = datetime.fromisoformat

            # Very recent (same day)
            boost = context_manager._calculate_enhanced_recency_boost(
                "2024-01-01T23:00:00Z")
            assert boost == 0.4

            # Recent (within 7 days)
            boost = context_manager._calculate_enhanced_recency_boost(
                "2023-12-30T10:00:00Z")
            assert boost == 0.3

            # Older (within 30 days)
            boost = context_manager._calculate_enhanced_recency_boost(
                "2023-12-15T10:00:00Z")
            assert boost == 0.2

    def test_calculate_enhanced_type_boost(self, context_manager):
        """Test enhanced type boost calculation"""
        assert context_manager._calculate_enhanced_type_boost(
            "user_preference") == 0.25
        assert context_manager._calculate_enhanced_type_boost(
            "explicit_request") == 0.3
        assert context_manager._calculate_enhanced_type_boost("general") == 0.0
        assert context_manager._calculate_enhanced_type_boost(
            "unknown_type") == 0.0

    def test_calculate_state_context_boost(self, context_manager, sample_state):
        """Test state context boost calculation"""
        memory = {
            "content": "software development patterns and automation tools",
            "tags": ["software", "development", "automation"]
        }

        boost = context_manager._calculate_state_context_boost(
            memory, sample_state)
        assert boost > 0.0  # Should have some boost
        assert boost <= 0.12  # Should be capped appropriately

    def test_calculate_focus_area_boost(self, context_manager):
        """Test focus area boost calculation"""
        memory = {
            "content": "software development best practices",
            "tags": ["software", "development"]
        }

        focus_areas = ["software development", "automation"]
        boost = context_manager._calculate_focus_area_boost(
            memory, focus_areas)
        assert boost > 0.0  # Should have some boost
        assert boost <= 0.45  # Should be within expected range

    def test_extract_phrases(self, context_manager):
        """Test phrase extraction from text"""
        text = "software development best practices"
        phrases = context_manager._extract_phrases(text)

        assert "software development" in phrases
        assert "development best" in phrases
        assert "best practices" in phrases
        assert "software development best practices" in phrases

    def test_select_memories_intelligently(self, context_manager):
        """Test intelligent memory selection"""
        memories = [
            {"id": "1", "content": "short memory",
                "tags": [], "memory_type": "general"},
            {"id": "2", "content": "medium length memory with more content",
                "tags": ["tag1"], "memory_type": "general"},
            {"id": "3", "content": "very long memory with extensive content that exceeds the target length",
                "tags": ["tag1", "tag2"], "memory_type": "general"}
        ]

        # Mock the estimation method
        with patch.object(context_manager, '_estimate_memory_length') as mock_estimate:
            mock_estimate.side_effect = [50, 100, 200]

            selected = context_manager._select_memories_intelligently(
                memories, 200)

            # Should select first two memories (50 + 100 = 150 <= 200)
            assert len(selected) == 2
            assert selected[0]["id"] == "1"
            assert selected[1]["id"] == "2"

    def test_estimate_memory_length(self, context_manager):
        """Test memory length estimation"""
        memory = {
            "content": "test content",
            "tags": ["tag1", "tag2"],
            "memory_type": "user_preference"
        }

        length = context_manager._estimate_memory_length(memory)
        # Base: 12 + tags: 9 + prefix: 17 + buffer: 20 = 58
        assert length == 58

    def test_create_shortened_memory(self, context_manager):
        """Test memory shortening"""
        memory = {
            "id": "1",
            "content": "This is a long memory. It has multiple sentences. We need to shorten it.",
            "tags": ["tag1"],
            "memory_type": "general"
        }

        shortened = context_manager._create_shortened_memory(memory, 50)
        assert shortened is not None
        assert len(shortened["content"]) <= 50
        assert shortened["_shortened"] is True

    def test_format_context_with_summarization(self, context_manager):
        """Test context formatting with summarization"""
        memories = [
            {"id": "1", "content": "preference memory", "tags": [
                "pref"], "memory_type": "user_preference"},
            {"id": "2", "content": "general memory",
                "tags": ["gen"], "memory_type": "general"}
        ]

        context = context_manager._format_context_with_summarization(
            memories, 1000)

        assert "**User Preference:**" in context
        assert "**General:**" in context
        assert "preference memory" in context
        assert "general memory" in context

    def test_group_memories_by_type(self, context_manager):
        """Test memory grouping by type"""
        memories = [
            {"id": "1", "memory_type": "user_preference"},
            {"id": "2", "memory_type": "general"},
            {"id": "3", "memory_type": "user_preference"}
        ]

        grouped = context_manager._group_memories_by_type(memories)

        assert "user_preference" in grouped
        assert "general" in grouped
        assert len(grouped["user_preference"]) == 2
        assert len(grouped["general"]) == 1

    def test_format_memory_group(self, context_manager):
        """Test memory group formatting"""
        memories = [
            {"content": "high importance memory", "tags": [
                "important"], "importance_score": 9},
            {"content": "medium importance memory",
                "tags": ["medium"], "importance_score": 6},
            {"content": "low importance memory",
                "tags": ["low"], "importance_score": 3}
        ]

        formatted = context_manager._format_memory_group(
            "user_preference", memories)

        assert "**User Preference:**" in formatted
        assert "🔴 high importance memory" in formatted
        assert "🟡 medium importance memory" in formatted
        assert "🟢 low importance memory" in formatted

    def test_summarize_context(self, context_manager):
        """Test context summarization"""
        context = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

        summarized = context_manager._summarize_context(context, 20)

        assert len(summarized) <= 20
        assert "Line 1" in summarized
        assert "more memories" in summarized or len(summarized) <= 20

    def test_truncate_context_intelligently(self, context_manager):
        """Test intelligent context truncation"""
        context = "Section 1\n\nContent 1\nContent 2\n\nSection 2\n\nContent 3\nContent 4"

        truncated = context_manager._truncate_context_intelligently(
            context, 30)

        assert len(truncated) <= 30
        assert "Section 1" in truncated

    def test_truncate_section(self, context_manager):
        """Test section truncation"""
        section = "Header\nLine 1\nLine 2\nLine 3"

        truncated = context_manager._truncate_section(section, 20)

        assert len(truncated) <= 20
        assert "Header" in truncated

    def test_get_context_stats(self, context_manager):
        """Test context statistics"""
        context = "Line 1\nLine 2\n\nSection 2\n\nLine 3"

        stats = context_manager.get_context_stats(context)

        assert stats["length"] == len(context)
        assert stats["lines"] == 6  # Includes empty lines from double newlines
        assert stats["sections"] == 3
        assert "efficiency" in stats
        assert "compression_ratio" in stats

    @pytest.mark.asyncio
    async def test_optimize_context_with_state_integration(self, context_manager, sample_state, sample_memories):
        """Test full integration of context optimization with state"""
        context = await context_manager.optimize_context_with_state(
            sample_memories,
            "software development automation",
            sample_state,
            ["software development"],
            "complex"
        )

        assert len(context) > 0
        assert "software development" in context.lower() or "automation" in context.lower()

        # Should respect dynamic sizing
        assert len(context) <= 2000  # Max context length
        assert len(context) >= 100   # Min context length

    def test_context_manager_configuration(self, context_manager):
        """Test that configuration is properly applied"""
        assert context_manager.min_context_length == 100
        assert context_manager.max_context_length == 2000
        assert context_manager.optimal_context_length == 800
        assert context_manager.simple_query_threshold == 50
        assert context_manager.complex_query_threshold == 200
        assert context_manager.focus_boost_multiplier == 1.5
        assert context_manager.state_context_weight == 0.3
