"""
Smart LTM Retriever

This module provides intelligent LTM memory retrieval with relevance scoring,
state coordination, and advanced optimization features.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import hashlib
import json

from ...config.logging_config import get_logger
from ...tools.ltm.ltm_storage import get_relevant_ltm_memories
from ...types.state import AgentState
from .config import LTMConfig, EnhancedLTMConfig

logger = get_logger("smart_retriever")


class SmartLTMRetriever:
    """Provides intelligent LTM memory retrieval with state coordination"""

    def __init__(self, config: LTMConfig = None):
        self.config = config or LTMConfig()

        # Initialize caching system
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_hits = defaultdict(int)
        self._cache_misses = defaultdict(int)

        # Cache configuration
        self.cache_ttl = getattr(
            self.config, 'cache_ttl_seconds', 300)  # 5 minutes default
        self.max_cache_size = getattr(self.config, 'max_cache_entries', 1000)

        # Quality thresholds
        self.min_quality_threshold = getattr(
            self.config, 'min_quality_threshold', 0.3)
        self.optimal_quality_threshold = getattr(
            self.config, 'optimal_quality_threshold', 0.7)

    async def get_relevant_memories(
        self,
        user_id: int,
        context: str,
        limit: int = None,
        state_context: AgentState = None,
        query_complexity: str = "medium"
    ) -> List[dict]:
        """
        Get semantically relevant memories for context with state coordination

        Args:
            user_id: User ID for memory retrieval
            context: Query context for relevance scoring
            limit: Maximum number of memories to return
            state_context: Agent state for enhanced context coordination
            query_complexity: Query complexity level (simple, medium, complex)

        Returns:
            List of relevant memories sorted by relevance score
        """

        # Dynamic result limits based on query complexity
        if limit is None:
            limit = self._calculate_dynamic_limit(query_complexity, context)

        # Check cache first
        cache_key = self._generate_cache_key(
            user_id, context, limit, state_context)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            self._cache_hits[cache_key] += 1
            logger.info(
                f"Cache hit for user {user_id}, returning {len(cached_result)} cached memories")
            return cached_result

        self._cache_misses[cache_key] += 1

        # Get candidate memories by importance
        candidate_memories = await self._get_candidate_memories(user_id, state_context)

        if not candidate_memories:
            logger.info(f"No candidate memories found for user {user_id}")
            return []

        # Enhanced multi-dimensional relevance scoring
        scored_memories = []
        for memory in candidate_memories:
            relevance_score = self._calculate_enhanced_relevance_score(
                memory, context, state_context
            )

            # Quality threshold filtering
            if relevance_score >= self.min_quality_threshold:
                scored_memories.append((memory, relevance_score))

        # Sort by relevance and apply quality filtering
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        # Apply optimal quality threshold for top results
        optimal_memories = [
            memory for memory, score in scored_memories
            if score >= self.optimal_quality_threshold
        ]

        # Fill remaining slots with good quality memories
        good_memories = [
            memory for memory, score in scored_memories
            if score >= self.min_quality_threshold and score < self.optimal_quality_threshold
        ]

        # Combine and limit results
        result = optimal_memories + good_memories
        result = result[:limit]

        # Cache the result
        self._cache_result(cache_key, result)

        logger.info(
            f"Retrieved {len(result)} relevant memories for user {user_id} "
            f"(context: {context[:50]}..., complexity: {query_complexity})"
        )

        return result

    def _calculate_dynamic_limit(self, query_complexity: str, context: str) -> int:
        """Calculate dynamic result limit based on query complexity and context length"""

        base_limit = self.config.max_retrieved_memories

        # Adjust based on query complexity
        complexity_multipliers = {
            "simple": 0.5,    # Shorter queries get fewer results
            "medium": 1.0,    # Standard queries
            "complex": 1.5    # Complex queries get more results
        }

        multiplier = complexity_multipliers.get(query_complexity, 1.0)

        # Adjust based on context length
        context_length = len(context)
        if context_length < 50:
            length_multiplier = 0.7  # Short context
        elif context_length < 200:
            length_multiplier = 1.0  # Medium context
        else:
            length_multiplier = 1.3  # Long context

        dynamic_limit = int(base_limit * multiplier * length_multiplier)

        # Ensure limits are within bounds
        min_limit = max(1, int(base_limit * 0.3))
        max_limit = min(base_limit * 2, 50)  # Cap at 50 memories

        return max(min_limit, min(dynamic_limit, max_limit))

    async def _get_candidate_memories(
        self,
        user_id: int,
        state_context: AgentState = None
    ) -> List[dict]:
        """Get candidate memories with state context consideration"""

        try:
            # Get base candidate memories
            memories = await get_relevant_ltm_memories(
                user_id=user_id,
                context="",  # Empty context to get all memories
                limit=self.config.max_candidate_memories
            )

            # Filter by minimum importance
            filtered_memories = [
                memory for memory in memories
                if memory.get("importance_score", 1) >= self.config.min_importance_for_retrieval
            ]

            # Apply state context filtering if available
            if state_context and hasattr(state_context, 'focus'):
                filtered_memories = self._filter_by_state_focus(
                    filtered_memories, state_context
                )

            return filtered_memories

        except Exception as e:
            logger.error(f"Error getting candidate memories: {e}")
            return []

    def _filter_by_state_focus(self, memories: List[dict], state_context: AgentState) -> List[dict]:
        """Filter memories based on current state focus"""

        if not state_context.focus:
            return memories

        focus_areas = state_context.focus if isinstance(
            state_context.focus, list) else [state_context.focus]

        # Boost memories that match current focus
        focused_memories = []
        other_memories = []

        for memory in memories:
            memory_tags = set(memory.get("tags", []))
            memory_content = memory.get("content", "").lower()

            # Check if memory matches any focus area
            focus_match = any(
                focus.lower() in memory_content or
                any(focus.lower() in tag.lower() for tag in memory_tags)
                for focus in focus_areas
            )

            if focus_match:
                focused_memories.append(memory)
            else:
                other_memories.append(memory)

        # Return focused memories first, then others
        return focused_memories + other_memories

    def _calculate_enhanced_relevance_score(
        self,
        memory: dict,
        context: str,
        state_context: AgentState = None
    ) -> float:
        """Calculate enhanced multi-dimensional relevance score"""

        score = 0.0

        # Tag-based scoring (enhanced)
        memory_tags = set(memory.get("tags", []))
        context_words = set(context.lower().split())

        # Check tag overlap with exact and partial matches
        tag_matches = 0
        for tag in memory_tags:
            tag_lower = tag.lower()
            if tag_lower in context_words:
                tag_matches += 1.0  # Exact match
            elif any(tag_lower in word or word in tag_lower for word in context_words):
                tag_matches += 0.7  # Partial match

        if memory_tags:
            tag_score = tag_matches / len(memory_tags)
            score += tag_score * self.config.tag_scoring_weight

        # Content-based scoring (enhanced)
        memory_content = memory.get("content", "").lower()
        content_words = set(memory_content.split())

        # Word overlap with stemming consideration
        word_overlap = len(content_words & context_words) / \
            max(len(content_words | context_words), 1)
        score += word_overlap * self.config.content_scoring_weight

        # Phrase matching (check for multi-word phrases)
        context_phrases = self._extract_phrases(context)
        memory_phrases = self._extract_phrases(memory_content)
        phrase_overlap = len(context_phrases & memory_phrases) / \
            max(len(context_phrases | memory_phrases), 1)
        score += phrase_overlap * \
            getattr(self.config, 'phrase_scoring_weight', 0.2)

        # Importance score boost (enhanced)
        importance_score = memory.get("importance_score", 1)
        # Diminishing returns
        importance_boost = (importance_score / 10.0) ** 0.8
        score += importance_boost * self.config.importance_scoring_weight

        # Recency boost (enhanced)
        recency_boost = self._calculate_enhanced_recency_boost(
            memory.get("last_accessed"), memory.get("created_at")
        )
        score += recency_boost * self.config.recency_scoring_weight

        # State context boost
        if state_context:
            state_boost = self._calculate_state_context_boost(
                memory, state_context)
            score += state_boost * \
                getattr(self.config, 'state_context_weight', 0.15)

        # Memory type boost
        memory_type = memory.get("memory_type", "general")
        type_boost = self._get_memory_type_boost(memory_type)
        score += type_boost * getattr(self.config, 'type_scoring_weight', 0.1)

        # Confidence score boost
        confidence_score = memory.get("confidence_score", 0.5)
        confidence_boost = confidence_score * \
            getattr(self.config, 'confidence_scoring_weight', 0.1)
        score += confidence_boost

        return min(1.0, score)

    def _extract_phrases(self, text: str, min_length: int = 2, max_length: int = 4) -> set:
        """Extract meaningful phrases from text"""

        words = text.lower().split()
        phrases = set()

        for length in range(min_length, min(max_length + 1, len(words) + 1)):
            for i in range(len(words) - length + 1):
                phrase = " ".join(words[i:i + length])
                if len(phrase) > 3:  # Filter out very short phrases
                    phrases.add(phrase)

        return phrases

    def _calculate_enhanced_recency_boost(self, last_accessed: str, created_at: str = None) -> float:
        """Calculate enhanced recency boost considering both access and creation time"""

        try:
            # Use last accessed time if available, otherwise use creation time
            time_str = last_accessed or created_at
            if not time_str:
                return 0.0

            time_dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            days_ago = (datetime.now(timezone.utc) - time_dt).days

            # Enhanced recency calculation with smoother decay
            if days_ago <= 1:
                return 1.0  # Very recent
            elif days_ago <= 7:
                return 0.8  # Recent
            elif days_ago <= 30:
                return 0.6  # Somewhat recent
            elif days_ago <= 90:
                return 0.4  # Older
            elif days_ago <= 365:
                return 0.2  # Much older
            else:
                return 0.0  # Very old

        except Exception as e:
            logger.warning(f"Error parsing date '{time_str}': {e}")
            return 0.0

    def _calculate_state_context_boost(self, memory: dict, state_context: AgentState) -> float:
        """Calculate boost based on state context relevance"""

        boost = 0.0

        # Focus area matching
        if state_context.focus:
            focus_areas = state_context.focus if isinstance(
                state_context.focus, list) else [state_context.focus]
            memory_tags = set(memory.get("tags", []))
            memory_content = memory.get("content", "").lower()

            for focus in focus_areas:
                focus_lower = focus.lower()
                if focus_lower in memory_content:
                    boost += 0.3  # Content match
                if any(focus_lower in tag.lower() for tag in memory_tags):
                    boost += 0.2  # Tag match

        # Tool usage context matching
        if hasattr(state_context, 'last_tool_result') and state_context.last_tool_result:
            tool_result = str(state_context.last_tool_result).lower()
            memory_content = memory.get("content", "").lower()

            if any(tool_word in memory_content for tool_word in ['tool', 'function', 'api', 'automation']):
                boost += 0.2

        return min(0.5, boost)  # Cap at 0.5

    def _get_memory_type_boost(self, memory_type: str) -> float:
        """Get boost value for different memory types"""

        type_boosts = {
            "user_preference": 0.3,
            "explicit_request": 0.4,
            "tool_usage": 0.2,
            "conversation": 0.1,
            "automation": 0.2,
            "general": 0.0
        }

        return type_boosts.get(memory_type, 0.0)

    def _generate_cache_key(self, user_id: int, context: str, limit: int, state_context: AgentState = None) -> str:
        """Generate cache key for the query"""

        # Create a hash of the query parameters
        key_data = {
            'user_id': user_id,
            'context': context.lower().strip(),
            'limit': limit,
            'state_focus': state_context.focus if state_context and state_context.focus else None,
            'state_tool': str(state_context.last_tool_result) if state_context and state_context.last_tool_result else None
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[List[dict]]:
        """Get result from cache if valid"""

        if cache_key not in self._cache:
            return None

        # Check if cache entry is still valid
        if cache_key in self._cache_timestamps:
            age = datetime.now(timezone.utc) - \
                self._cache_timestamps[cache_key]
            if age.total_seconds() > self.cache_ttl:
                # Cache expired, remove it
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]
                return None

        return self._cache[cache_key]

    def _cache_result(self, cache_key: str, result: List[dict]):
        """Cache the result"""

        # Implement LRU-like cache eviction if needed
        if len(self._cache) >= self.max_cache_size:
            # Remove oldest entries (simple FIFO for now)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            if oldest_key in self._cache_timestamps:
                del self._cache_timestamps[oldest_key]

        self._cache[cache_key] = result
        self._cache_timestamps[cache_key] = datetime.now(timezone.utc)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""

        total_requests = sum(self._cache_hits.values()) + \
            sum(self._cache_misses.values())
        hit_rate = sum(self._cache_hits.values()) / \
            total_requests if total_requests > 0 else 0

        return {
            'cache_size': len(self._cache),
            'total_requests': total_requests,
            'cache_hits': sum(self._cache_hits.values()),
            'cache_misses': sum(self._cache_misses.values()),
            'hit_rate': hit_rate,
            'cache_ttl_seconds': self.cache_ttl,
            'max_cache_size': self.max_cache_size
        }

    def clear_cache(self):
        """Clear the entire cache"""
        self._cache.clear()
        self._cache_timestamps.clear()
        self._cache_hits.clear()
        self._cache_misses.clear()
        logger.info("Cache cleared")

    def get_memories_by_type(self, user_id: int, memory_type: str, limit: int = 5) -> List[dict]:
        """Get memories of a specific type"""

        # This would need to be implemented with database queries
        # For now, return empty list
        logger.info(
            f"Getting memories of type '{memory_type}' for user {user_id}")
        return []

    def get_memories_by_tags(self, user_id: int, tags: List[str], limit: int = 5) -> List[dict]:
        """Get memories with specific tags"""

        # This would need to be implemented with database queries
        # For now, return empty list
        logger.info(f"Getting memories with tags {tags} for user {user_id}")
        return []

    def get_high_importance_memories(self, user_id: int, min_importance: int = 7, limit: int = 5) -> List[dict]:
        """Get high-importance memories for a user"""

        # This would need to be implemented with database queries
        # For now, return empty list
        logger.info(
            f"Getting high-importance memories (>= {min_importance}) for user {user_id}")
        return []
