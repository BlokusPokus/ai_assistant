"""
Context Quality Validation for LTM Optimization

This module provides validation and quality assessment for LTM context
injection, ensuring that only relevant, high-quality memories are
included in the context provided to the LLM.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import re

from ...config.logging_config import get_logger
from ...types.state import AgentState
from .config import EnhancedLTMConfig

logger = get_logger("context_quality")


class ContextQualityValidator:
    """
    Validates memory relevance and context quality for optimal LLM performance.

    This class ensures that:
    - Only relevant memories are included in context
    - Context quality meets minimum thresholds
    - Redundancy is detected and eliminated
    - State-LTM coordination is maintained
    """

    def __init__(self, config: EnhancedLTMConfig = None):
        """Initialize the context quality validator"""
        self.config = config or EnhancedLTMConfig()
        self.logger = get_logger("context_quality")

    async def validate_memory_relevance(
        self,
        memory: Dict[str, Any],
        context: str,
        user_input: str = None
    ) -> float:
        """
        Validate memory relevance for the given context.

        Args:
            memory: Memory object to validate
            context: Current conversation context
            user_input: Current user input for relevance scoring

        Returns:
            Relevance score between 0.0 and 1.0
        """

        try:
            relevance_score = 0.0

            # Tag relevance (40%)
            tag_score = self._score_tag_relevance(memory, context, user_input)
            relevance_score += tag_score * 0.4

            # Content relevance (30%)
            content_score = self._score_content_relevance(
                memory, context, user_input)
            relevance_score += content_score * 0.3

            # Temporal relevance (20%)
            temporal_score = self._score_temporal_relevance(memory)
            relevance_score += temporal_score * 0.2

            # State coordination relevance (10%)
            state_score = self._score_state_coordination_relevance(
                memory, context)
            relevance_score += state_score * 0.1

            self.logger.debug(
                f"Memory relevance score: {relevance_score:.2f} for memory: {memory.get('content', '')[:50]}...")

            return relevance_score

        except Exception as e:
            self.logger.error(f"Error validating memory relevance: {e}")
            return 0.0

    async def score_context_quality(
        self,
        memories: List[Dict[str, Any]],
        user_input: str,
        max_context_length: int = None
    ) -> float:
        """
        Score overall context quality for a set of memories.

        Args:
            memories: List of memories to evaluate
            user_input: Current user input for context evaluation
            max_context_length: Maximum allowed context length

        Returns:
            Overall context quality score between 0.0 and 1.0
        """

        try:
            if not memories:
                return 0.0

            # Calculate individual memory scores
            memory_scores = []
            total_length = 0

            for memory in memories:
                # Get memory relevance score
                relevance_score = await self.validate_memory_relevance(
                    memory, "context_evaluation", user_input
                )
                memory_scores.append(relevance_score)

                # Calculate context length
                memory_content = memory.get('content', '')
                total_length += len(memory_content)

            # Calculate average relevance score
            avg_relevance = sum(memory_scores) / \
                len(memory_scores) if memory_scores else 0.0

            # Length optimization score
            length_score = self._score_context_length(
                total_length, max_context_length)

            # Diversity score (avoid too many similar memories)
            diversity_score = self._score_memory_diversity(memories)

            # Overall quality score
            quality_score = (avg_relevance * 0.6 +
                             length_score * 0.2 + diversity_score * 0.2)

            self.logger.info(
                f"Context quality score: {quality_score:.2f} for {len(memories)} memories")

            return quality_score

        except Exception as e:
            self.logger.error(f"Error scoring context quality: {e}")
            return 0.0

    async def detect_redundancy(
        self,
        memories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect and remove redundant memories from the context.

        Args:
            memories: List of memories to analyze

        Returns:
            List of memories with redundancy removed
        """

        try:
            if len(memories) <= 1:
                return memories

            # Group memories by similarity
            memory_groups = self._group_similar_memories(memories)

            # Select best memory from each group
            deduplicated_memories = []

            for group in memory_groups:
                if len(group) == 1:
                    deduplicated_memories.append(group[0])
                else:
                    # Select the best memory from the group
                    best_memory = self._select_best_memory_from_group(group)
                    deduplicated_memories.append(best_memory)

            removed_count = len(memories) - len(deduplicated_memories)
            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} redundant memories")

            return deduplicated_memories

        except Exception as e:
            self.logger.error(f"Error detecting redundancy: {e}")
            return memories

    async def optimize_context_for_state(
        self,
        memories: List[Dict[str, Any]],
        state_data: AgentState,
        user_input: str,
        max_context_length: int = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Optimize context for state management integration.

        This method ensures that the context is optimized for the current
        user state and provides the most relevant information.

        Args:
            memories: List of candidate memories
            state_data: Current agent state
            user_input: Current user input
            max_context_length: Maximum context length

        Returns:
            Tuple of (optimized_memories, quality_score)
        """

        try:
            # Filter memories by state relevance
            state_relevant_memories = []

            for memory in memories:
                state_relevance = await self._assess_state_relevance(memory, state_data, user_input)
                if state_relevance >= self.config.coordination_quality_threshold:
                    state_relevant_memories.append(memory)

            # Remove redundancy
            deduplicated_memories = await self.detect_redundancy(state_relevant_memories)

            # Score final context quality
            quality_score = await self.score_context_quality(
                deduplicated_memories, user_input, max_context_length
            )

            # Apply length limits if specified
            if max_context_length:
                deduplicated_memories = self._apply_context_length_limits(
                    deduplicated_memories, max_context_length
                )

            self.logger.info(
                f"State-optimized context: {len(deduplicated_memories)} memories, quality: {quality_score:.2f}")

            return deduplicated_memories, quality_score

        except Exception as e:
            self.logger.error(f"Error optimizing context for state: {e}")
            return memories, 0.0

    def _score_tag_relevance(
        self,
        memory: Dict[str, Any],
        context: str,
        user_input: str = None
    ) -> float:
        """Score memory tag relevance"""

        try:
            memory_tags = memory.get('tags', [])
            if not memory_tags:
                return 0.0

            # Extract keywords from context and user input
            context_keywords = self._extract_keywords(
                context) if context else []
            user_keywords = self._extract_keywords(
                user_input) if user_input else []

            all_keywords = context_keywords + user_keywords

            # Calculate tag overlap
            relevant_tags = 0
            for tag in memory_tags:
                tag_lower = tag.lower()
                for keyword in all_keywords:
                    if tag_lower in keyword.lower() or keyword.lower() in tag_lower:
                        relevant_tags += 1
                        break

            # Calculate relevance score
            if not all_keywords:
                return 0.5  # Neutral score if no keywords

            relevance_score = relevant_tags / len(memory_tags)

            return min(1.0, relevance_score)

        except Exception as e:
            self.logger.error(f"Error scoring tag relevance: {e}")
            return 0.0

    def _score_content_relevance(
        self,
        memory: Dict[str, Any],
        context: str,
        user_input: str = None
    ) -> float:
        """Score memory content relevance"""

        try:
            memory_content = memory.get('content', '').lower()
            if not memory_content:
                return 0.0

            # Extract keywords from context and user input
            context_keywords = self._extract_keywords(
                context) if context else []
            user_keywords = self._extract_keywords(
                user_input) if user_input else []

            all_keywords = context_keywords + user_keywords

            # Calculate content keyword overlap
            relevant_keywords = 0
            for keyword in all_keywords:
                if keyword.lower() in memory_content:
                    relevant_keywords += 1

            # Calculate relevance score
            if not all_keywords:
                return 0.5  # Neutral score if no keywords

            relevance_score = relevant_keywords / len(all_keywords)

            return min(1.0, relevance_score)

        except Exception as e:
            self.logger.error(f"Error scoring content relevance: {e}")
            return 0.0

    def _score_temporal_relevance(self, memory: Dict[str, Any]) -> float:
        """Score memory temporal relevance"""

        try:
            # This is a simplified temporal scoring
            # In practice, you'd want to analyze actual timestamps

            # For now, return a base score
            # Newer memories would get higher scores
            return 0.7

        except Exception as e:
            self.logger.error(f"Error scoring temporal relevance: {e}")
            return 0.5

    def _score_state_coordination_relevance(
        self,
        memory: Dict[str, Any],
        context: str
    ) -> float:
        """Score how well memory coordinates with current state"""

        try:
            # This would analyze how well the memory fits with current state
            # For now, return a base score
            return 0.6

        except Exception as e:
            self.logger.error(
                f"Error scoring state coordination relevance: {e}")
            return 0.5

    def _score_context_length(self, total_length: int, max_length: int = None) -> float:
        """Score context length optimization"""

        try:
            if not max_length:
                max_length = self.config.max_context_length

            # Optimal length is around 70-80% of max
            optimal_length = max_length * 0.75

            if total_length <= optimal_length:
                # Good length
                return 1.0
            elif total_length <= max_length:
                # Acceptable length
                return 0.7
            else:
                # Too long
                return 0.3

        except Exception as e:
            self.logger.error(f"Error scoring context length: {e}")
            return 0.5

    def _score_memory_diversity(self, memories: List[Dict[str, Any]]) -> float:
        """Score memory diversity to avoid too many similar memories"""

        try:
            if len(memories) <= 1:
                return 1.0

            # Analyze memory types and categories
            memory_types = [m.get('memory_type', 'unknown') for m in memories]
            categories = [m.get('category', 'unknown') for m in memories]

            # Calculate diversity scores
            type_diversity = len(set(memory_types)) / len(memory_types)
            category_diversity = len(set(categories)) / len(categories)

            # Overall diversity score
            diversity_score = (type_diversity + category_diversity) / 2

            return diversity_score

        except Exception as e:
            self.logger.error(f"Error scoring memory diversity: {e}")
            return 0.5

    def _group_similar_memories(self, memories: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group memories by similarity for redundancy detection"""

        try:
            if len(memories) <= 1:
                return [memories]

            # Simple grouping by memory type and category
            # In practice, you'd want more sophisticated similarity detection
            groups = defaultdict(list)

            for memory in memories:
                memory_type = memory.get('memory_type', 'unknown')
                category = memory.get('category', 'unknown')

                # Create group key
                group_key = f"{memory_type}_{category}"
                groups[group_key].append(memory)

            return list(groups.values())

        except Exception as e:
            self.logger.error(f"Error grouping similar memories: {e}")
            return [memories]

    def _select_best_memory_from_group(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best memory from a group of similar memories"""

        try:
            if len(group) == 1:
                return group[0]

            # Score memories by importance and confidence
            scored_memories = []

            for memory in group:
                importance = memory.get('importance_score', 1)
                confidence = memory.get('confidence_score', 0.5)

                # Combined score
                score = (importance * 0.6) + (confidence * 0.4)
                scored_memories.append((score, memory))

            # Return memory with highest score
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            return scored_memories[0][1]

        except Exception as e:
            self.logger.error(f"Error selecting best memory from group: {e}")
            return group[0] if group else {}

    async def _assess_state_relevance(
        self,
        memory: Dict[str, Any],
        state_data: AgentState,
        user_input: str
    ) -> float:
        """Assess how relevant a memory is to current state"""

        try:
            relevance_score = 0.0

            # Focus area relevance
            if state_data.focus and memory.get('category'):
                category = memory['category'].lower()
                focus_lower = [f.lower() for f in state_data.focus]

                if any(focus in category or category in focus for focus in focus_lower):
                    relevance_score += 0.4

            # User input relevance
            if user_input and memory.get('content'):
                content_lower = memory['content'].lower()
                input_lower = user_input.lower()

                # Check for keyword overlap
                input_words = set(input_lower.split())
                content_words = set(content_lower.split())

                overlap = len(input_words.intersection(content_words))
                if overlap > 0:
                    relevance_score += min(0.3, overlap * 0.1)

            # Memory type relevance
            memory_type = memory.get('memory_type', 'general')
            if memory_type in ['preference', 'pattern']:
                relevance_score += 0.2

            # Importance relevance
            importance = memory.get('importance_score', 1)
            if importance >= 7:
                relevance_score += 0.1

            return min(1.0, relevance_score)

        except Exception as e:
            self.logger.error(f"Error assessing state relevance: {e}")
            return 0.0

    def _apply_context_length_limits(
        self,
        memories: List[Dict[str, Any]],
        max_length: int
    ) -> List[Dict[str, Any]]:
        """Apply context length limits to memories"""

        try:
            if not memories:
                return memories

            # Sort memories by importance and relevance
            scored_memories = []
            for memory in memories:
                importance = memory.get('importance_score', 1)
                confidence = memory.get('confidence_score', 0.5)
                score = (importance * 0.7) + (confidence * 0.3)
                scored_memories.append((score, memory))

            scored_memories.sort(key=lambda x: x[0], reverse=True)

            # Select memories within length limit
            selected_memories = []
            current_length = 0

            for score, memory in scored_memories:
                memory_content = memory.get('content', '')
                memory_length = len(memory_content)

                if current_length + memory_length <= max_length:
                    selected_memories.append(memory)
                    current_length += memory_length
                else:
                    break

            return selected_memories

        except Exception as e:
            self.logger.error(f"Error applying context length limits: {e}")
            return memories

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for relevance scoring"""

        try:
            if not text:
                return []

            # Simple keyword extraction
            # Remove common words and extract meaningful terms
            common_words = {'the', 'a', 'an', 'and', 'or', 'but',
                            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

            words = re.findall(r'\b\w+\b', text.lower())
            keywords = [
                word for word in words if word not in common_words and len(word) > 2]

            return keywords[:10]  # Limit to top 10 keywords

        except Exception as e:
            self.logger.error(f"Error extracting keywords: {e}")
            return []
