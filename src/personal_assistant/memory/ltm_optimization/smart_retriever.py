"""
Smart LTM Retriever

This module provides intelligent LTM memory retrieval with relevance scoring.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

from ...config.logging_config import get_logger
from ...tools.ltm.ltm_storage import get_relevant_ltm_memories
from .config import LTMConfig

logger = get_logger("smart_retriever")


class SmartLTMRetriever:
    """Provides intelligent LTM memory retrieval"""

    def __init__(self, config: LTMConfig = None):
        self.config = config or LTMConfig()

    async def get_relevant_memories(self, user_id: int, context: str, limit: int = None) -> List[dict]:
        """Get semantically relevant memories for context"""

        if limit is None:
            limit = self.config.max_retrieved_memories

        # Get candidate memories by importance
        candidate_memories = await self._get_candidate_memories(user_id)

        if not candidate_memories:
            logger.info(f"No candidate memories found for user {user_id}")
            return []

        # Score memories by relevance
        scored_memories = []
        for memory in candidate_memories:
            relevance_score = self._calculate_relevance_score(memory, context)
            scored_memories.append((memory, relevance_score))

        # Sort by relevance and return top matches
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        # Filter out very low relevance memories
        filtered_memories = [
            memory for memory, score in scored_memories
            if score >= 0.1  # Minimum relevance threshold
        ]

        result = filtered_memories[:limit]
        logger.info(
            f"Retrieved {len(result)} relevant memories for user {user_id} (context: {context[:50]}...)")

        return result

    async def _get_candidate_memories(self, user_id: int) -> List[dict]:
        """Get candidate memories for relevance scoring"""

        try:
            # For now, use the existing get_relevant_ltm_memories function
            # In the future, this could be enhanced with database-level filtering
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

            return filtered_memories

        except Exception as e:
            logger.error(f"Error getting candidate memories: {e}")
            return []

    def _calculate_relevance_score(self, memory: dict, context: str) -> float:
        """Calculate relevance score for a memory given context"""

        score = 0.0

        # Tag-based scoring
        memory_tags = set(memory.get("tags", []))
        context_words = set(context.lower().split())

        # Check tag overlap
        tag_matches = sum(
            1 for tag in memory_tags if tag.lower() in context_words)
        if memory_tags:
            tag_score = tag_matches / len(memory_tags)
            score += tag_score * self.config.tag_scoring_weight

        # Content-based scoring
        memory_content = memory.get("content", "").lower()
        content_words = set(memory_content.split())

        # Word overlap
        word_overlap = len(content_words & context_words) / \
            max(len(content_words | context_words), 1)
        score += word_overlap * self.config.content_scoring_weight

        # Importance score boost
        importance_boost = memory.get("importance_score", 1) / 10.0
        score += importance_boost * self.config.importance_scoring_weight

        # Recency boost
        recency_boost = self._calculate_recency_boost(
            memory.get("last_accessed"))
        score += recency_boost * self.config.recency_scoring_weight

        return min(1.0, score)

    def _calculate_recency_boost(self, last_accessed: str) -> float:
        """Calculate recency boost for memory"""

        if not last_accessed:
            return 0.0

        try:
            last_accessed_dt = datetime.fromisoformat(
                last_accessed.replace('Z', '+00:00'))
            days_ago = (datetime.now(timezone.utc) - last_accessed_dt).days

            if days_ago <= self.config.very_recent_days:
                return self.config.very_recent_boost
            elif days_ago <= self.config.recent_days:
                return self.config.recent_boost
            elif days_ago <= self.config.somewhat_recent_days:
                return self.config.somewhat_recent_boost
            else:
                return 0.0
        except Exception as e:
            logger.warning(
                f"Error parsing last_accessed date '{last_accessed}': {e}")
            return 0.0

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
