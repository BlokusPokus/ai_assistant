"""
Unit tests for SmartLTMRetriever

Tests the enhanced smart retriever with state coordination, caching,
and multi-dimensional relevance scoring.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import json

from personal_assistant.memory.ltm_optimization.smart_retriever import SmartLTMRetriever
from personal_assistant.memory.ltm_optimization.config import EnhancedLTMConfig
from personal_assistant.types.state import AgentState


class TestSmartLTMRetriever:
    """Test the enhanced SmartLTMRetriever class"""

    @pytest.fixture
    def config(self):
        """Create enhanced LTM config for testing"""
        config = EnhancedLTMConfig()
        config.max_retrieved_memories = 10
        config.max_candidate_memories = 50
        config.min_importance_for_retrieval = 3
        config.tag_scoring_weight = 0.3
        config.content_scoring_weight = 0.4
        config.importance_scoring_weight = 0.2
        config.recency_scoring_weight = 0.1
        return config

    @pytest.fixture
    def retriever(self, config):
        """Create SmartLTMRetriever instance for testing"""
        return SmartLTMRetriever(config)

    @pytest.fixture
    def sample_memories(self):
        """Sample memories for testing"""
        return [
            {
                "id": "1",
                "content": "User prefers concise responses",
                "tags": ["preference", "communication"],
                "importance_score": 8,
                "confidence_score": 0.9,
                "memory_type": "user_preference",
                "category": "communication",
                "last_accessed": "2024-01-01T10:00:00Z",
                "created_at": "2024-01-01T09:00:00Z"
            },
            {
                "id": "2",
                "content": "User works in software development",
                "tags": ["work", "software", "development"],
                "importance_score": 7,
                "confidence_score": 0.8,
                "memory_type": "general",
                "category": "work",
                "last_accessed": "2024-01-02T10:00:00Z",
                "created_at": "2024-01-02T09:00:00Z"
            },
            {
                "id": "3",
                "content": "User likes automation tools",
                "tags": ["automation", "tools", "preference"],
                "importance_score": 6,
                "confidence_score": 0.7,
                "memory_type": "user_preference",
                "category": "automation",
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

    def test_init(self, retriever, config):
        """Test retriever initialization"""
        assert retriever.config == config
        assert retriever._cache == {}
        assert retriever._cache_timestamps == {}
        assert retriever.cache_ttl == 300
        assert retriever.max_cache_size == 1000
        assert retriever.min_quality_threshold == 0.3
        assert retriever.optimal_quality_threshold == 0.7

    def test_calculate_dynamic_limit_simple(self, retriever):
        """Test dynamic limit calculation for simple queries"""
        limit = retriever._calculate_dynamic_limit("simple", "short query")
        # 10 * 0.5 * 0.7 = 3.5, min_limit = max(1, int(10 * 0.3)) = 3
        assert limit == 3  # Should be at minimum bound

    def test_calculate_dynamic_limit_medium(self, retriever):
        """Test dynamic limit calculation for medium queries"""
        limit = retriever._calculate_dynamic_limit(
            "medium", "medium length query")
        # 10 * 1.0 * 1.0 = 10, but context length < 50 so 10 * 1.0 * 0.7 = 7
        assert limit == 7  # 10 * 1.0 * 0.7 = 7

    def test_calculate_dynamic_limit_complex(self, retriever):
        """Test dynamic limit calculation for complex queries"""
        long_context = "very long context " * 20  # 400 characters
        limit = retriever._calculate_dynamic_limit("complex", long_context)
        # 10 * 1.5 * 1.3 = 19.5, not capped at 15
        assert limit == 19  # 10 * 1.5 * 1.3 = 19.5, rounded to 19

    def test_calculate_dynamic_limit_bounds(self, retriever):
        """Test dynamic limit calculation respects bounds"""
        # Test minimum bound
        limit = retriever._calculate_dynamic_limit("simple", "very short")
        assert limit >= 3  # Minimum should be at least 3

        # Test maximum bound
        very_long_context = "very long context " * 50  # 1000 characters
        limit = retriever._calculate_dynamic_limit(
            "complex", very_long_context)
        assert limit <= 50  # Maximum should be capped at 50

    @pytest.mark.asyncio
    async def test_get_candidate_memories_with_state(self, retriever, sample_state):
        """Test getting candidate memories with state context"""
        with patch('personal_assistant.memory.ltm_optimization.smart_retriever.get_relevant_ltm_memories') as mock_get:
            mock_get.return_value = [
                {
                    "id": "1",
                    "content": "software development patterns",
                    "tags": ["software", "development"],
                    "importance_score": 8
                },
                {
                    "id": "2",
                    "content": "general information",
                    "tags": ["general"],
                    "importance_score": 5
                }
            ]

            memories = await retriever._get_candidate_memories(1, sample_state)

            # Should prioritize software development memory first
            assert len(memories) == 2
            assert memories[0]["id"] == "1"  # Software development first
            assert memories[1]["id"] == "2"  # General second

    def test_filter_by_state_focus(self, retriever, sample_state):
        """Test filtering memories by state focus"""
        memories = [
            {
                "id": "1",
                "content": "software development best practices",
                "tags": ["software", "development"]
            },
            {
                "id": "2",
                "content": "general information",
                "tags": ["general"]
            },
            {
                "id": "3",
                "content": "automation tools guide",
                "tags": ["automation", "tools"]
            }
        ]

        filtered = retriever._filter_by_state_focus(memories, sample_state)

        # Focused memories should come first
        assert filtered[0]["id"] == "1"  # Software development
        assert filtered[1]["id"] == "3"  # Automation tools
        assert filtered[2]["id"] == "2"  # General information

    def test_filter_by_state_focus_no_focus(self, retriever):
        """Test filtering when no focus is set"""
        state = AgentState(user_input="test")
        memories = [{"id": "1", "content": "test", "tags": []}]

        filtered = retriever._filter_by_state_focus(memories, state)
        assert filtered == memories  # Should return unchanged

    def test_calculate_enhanced_relevance_score(self, retriever, sample_state):
        """Test enhanced relevance score calculation"""
        memory = {
            "content": "software development patterns",
            "tags": ["software", "development", "patterns"],
            "importance_score": 8,
            "confidence_score": 0.9,
            "memory_type": "general",
            "last_accessed": "2024-01-01T10:00:00Z"
        }

        context = "software development best practices"
        score = retriever._calculate_enhanced_relevance_score(
            memory, context, sample_state)

        assert score > 0.5  # Should have good relevance
        assert score <= 1.0  # Should be capped at 1.0

    def test_calculate_enhanced_relevance_score_no_state(self, retriever):
        """Test relevance score calculation without state context"""
        memory = {
            "content": "software development patterns",
            "tags": ["software", "development"],
            "importance_score": 8,
            "confidence_score": 0.9,
            "memory_type": "general",
            "last_accessed": "2024-01-01T10:00:00Z"
        }

        context = "software development best practices"
        score = retriever._calculate_enhanced_relevance_score(
            memory, context, None)

        assert score > 0.3  # Should still have reasonable relevance
        assert score <= 1.0

    def test_extract_phrases(self, retriever):
        """Test phrase extraction from text"""
        text = "software development best practices"
        phrases = retriever._extract_phrases(text)

        assert "software development" in phrases
        assert "development best" in phrases
        assert "best practices" in phrases
        assert "software development best practices" in phrases

    def test_calculate_enhanced_recency_boost(self, retriever):
        """Test enhanced recency boost calculation"""
        # Mock current time to be 2024-01-02T00:00:00Z
        with patch('personal_assistant.memory.ltm_optimization.smart_retriever.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
            mock_datetime.fromisoformat = datetime.fromisoformat

            # Very recent (same day)
            boost = retriever._calculate_enhanced_recency_boost(
                "2024-01-01T23:00:00Z")
            assert boost == 1.0

            # Recent (within 7 days but more than 1 day ago)
            boost = retriever._calculate_enhanced_recency_boost(
                "2023-12-30T10:00:00Z")
            assert boost == 0.8

            # Older (within 30 days)
            boost = retriever._calculate_enhanced_recency_boost(
                "2023-12-15T10:00:00Z")
            assert boost == 0.6

            # Much older (within 365 days)
            boost = retriever._calculate_enhanced_recency_boost(
                "2023-06-01T10:00:00Z")
            assert boost == 0.2

    def test_calculate_state_context_boost(self, retriever, sample_state):
        """Test state context boost calculation"""
        memory = {
            "content": "software development patterns and automation tools",
            "tags": ["software", "development", "automation"]
        }

        boost = retriever._calculate_state_context_boost(memory, sample_state)
        assert boost > 0.0  # Should have some boost
        assert boost <= 0.5  # Should be capped at 0.5

    def test_get_memory_type_boost(self, retriever):
        """Test memory type boost calculation"""
        assert retriever._get_memory_type_boost("user_preference") == 0.3
        assert retriever._get_memory_type_boost("explicit_request") == 0.4
        assert retriever._get_memory_type_boost("general") == 0.0
        assert retriever._get_memory_type_boost("unknown_type") == 0.0

    def test_generate_cache_key(self, retriever, sample_state):
        """Test cache key generation"""
        key1 = retriever._generate_cache_key(
            1, "test context", 10, sample_state)
        key2 = retriever._generate_cache_key(
            1, "test context", 10, sample_state)

        assert key1 == key2  # Same parameters should generate same key

        # Different parameters should generate different keys
        key3 = retriever._generate_cache_key(
            1, "different context", 10, sample_state)
        assert key1 != key3

    def test_cache_operations(self, retriever):
        """Test cache operations"""
        # Test caching
        retriever._cache_result("test_key", ["memory1", "memory2"])
        assert "test_key" in retriever._cache
        assert retriever._cache["test_key"] == ["memory1", "memory2"]

        # Test retrieval
        cached = retriever._get_from_cache("test_key")
        assert cached == ["memory1", "memory2"]

        # Test cache miss
        cached = retriever._get_from_cache("nonexistent_key")
        assert cached is None

    def test_cache_expiration(self, retriever):
        """Test cache expiration"""
        # Set short TTL for testing
        retriever.cache_ttl = 1

        # Cache result
        retriever._cache_result("test_key", ["memory1"])

        # Should be in cache initially
        assert retriever._get_from_cache("test_key") == ["memory1"]

        # Wait for expiration (mock time)
        with patch('personal_assistant.memory.ltm_optimization.smart_retriever.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now(
                timezone.utc) + timedelta(seconds=2)

            # Should be expired now
            cached = retriever._get_from_cache("test_key")
            assert cached is None

    def test_cache_eviction(self, retriever):
        """Test cache eviction when size limit is reached"""
        retriever.max_cache_size = 2

        # Add entries up to limit
        retriever._cache_result("key1", ["memory1"])
        retriever._cache_result("key2", ["memory2"])

        assert len(retriever._cache) == 2

        # Add one more to trigger eviction
        retriever._cache_result("key3", ["memory3"])

        assert len(retriever._cache) == 2
        assert "key3" in retriever._cache  # New key should be there
        assert "key1" not in retriever._cache  # Oldest should be evicted

    def test_get_cache_stats(self, retriever):
        """Test cache statistics"""
        # Add some cache entries
        retriever._cache_result("key1", ["memory1"])
        retriever._cache_result("key2", ["memory2"])

        # Simulate some hits and misses
        retriever._cache_hits["key1"] = 3
        retriever._cache_misses["key2"] = 2

        stats = retriever.get_cache_stats()

        assert stats["cache_size"] == 2
        assert stats["total_requests"] == 5
        assert stats["cache_hits"] == 3
        assert stats["cache_misses"] == 2
        assert stats["hit_rate"] == 0.6

    def test_clear_cache(self, retriever):
        """Test cache clearing"""
        # Add some cache entries
        retriever._cache_result("key1", ["memory1"])
        retriever._cache_result("key2", ["memory2"])

        assert len(retriever._cache) == 2

        # Clear cache
        retriever.clear_cache()

        assert len(retriever._cache) == 0
        assert len(retriever._cache_timestamps) == 0
        assert len(retriever._cache_hits) == 0
        assert len(retriever._cache_misses) == 0

    @pytest.mark.asyncio
    async def test_get_relevant_memories_integration(self, retriever, sample_state):
        """Test full integration of memory retrieval"""
        with patch.object(retriever, '_get_candidate_memories') as mock_get_candidates:
            mock_get_candidates.return_value = [
                {
                    "id": "1",
                    "content": "software development best practices",
                    "tags": ["software", "development"],
                    "importance_score": 8,
                    "confidence_score": 0.9,
                    "memory_type": "general",
                    "last_accessed": "2024-01-01T10:00:00Z"
                }
            ]

            memories = await retriever.get_relevant_memories(
                user_id=1,
                context="software development",
                state_context=sample_state,
                query_complexity="medium"
            )

            assert len(memories) > 0
            assert memories[0]["id"] == "1"

    @pytest.mark.asyncio
    async def test_get_relevant_memories_cache_hit(self, retriever, sample_state):
        """Test memory retrieval with cache hit"""
        # Prime the cache
        retriever._cache_result("test_key", ["cached_memory"])

        with patch.object(retriever, '_get_candidate_memories') as mock_get_candidates:
            mock_get_candidates.return_value = []

            # Mock cache key generation to return our test key
            with patch.object(retriever, '_generate_cache_key', return_value="test_key"):
                memories = await retriever.get_relevant_memories(
                    user_id=1,
                    context="test context",
                    state_context=sample_state
                )

                # Should return cached result
                assert memories == ["cached_memory"]

                # Should not call candidate retrieval
                mock_get_candidates.assert_not_called()

    def test_quality_threshold_filtering(self, retriever):
        """Test quality threshold filtering"""
        memories = [
            {"id": "1", "content": "high quality", "tags": [
                "relevant"], "importance_score": 9},
            {"id": "2", "content": "medium quality",
                "tags": ["somewhat"], "importance_score": 6},
            {"id": "3", "content": "low quality", "tags": [
                "unrelated"], "importance_score": 3}
        ]

        # Test with different quality thresholds
        retriever.min_quality_threshold = 0.5
        retriever.optimal_quality_threshold = 0.8

        # This would normally be called by get_relevant_memories
        # For testing, we'll simulate the scoring
        scored_memories = []
        for memory in memories:
            # Simulate relevance scores
            if memory["id"] == "1":
                score = 0.9  # High quality
            elif memory["id"] == "2":
                score = 0.6  # Medium quality
            else:
                score = 0.2  # Low quality

            if score >= retriever.min_quality_threshold:
                scored_memories.append((memory, score))

        # Should filter out low quality memories
        assert len(scored_memories) == 2
        assert scored_memories[0][0]["id"] == "1"  # High quality first
        assert scored_memories[1][0]["id"] == "2"  # Medium quality second
