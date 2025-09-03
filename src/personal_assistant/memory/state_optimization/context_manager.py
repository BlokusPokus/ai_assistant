"""
Context-aware memory management for intelligent state optimization.

This module provides intelligent optimization of memory context by:
- Extracting relevant information from conversation history
- Creating focused context based on user input
- Prioritizing context based on relevance and recency
- Managing context size limits intelligently
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from ...types.state import AgentState

logger = logging.getLogger(__name__)


class ContextManager:
    """Manages memory context optimization"""

    def __init__(self, max_context_items: int = 50):
        """
        Initialize the context manager.

        Args:
            max_context_items: Maximum number of items in memory context
        """
        self.max_context_items = max_context_items

    def optimize_memory_context(
        self, state: "AgentState", user_input: str
    ) -> List[dict]:
        """
        Optimize memory context for current user input.

        Args:
            state: Current agent state
            user_input: Current user input

        Returns:
            Optimized memory context list
        """
        logger.info(f"Optimizing memory context for user input: {user_input[:50]}...")

        # Extract relevant information from conversation history
        relevant_context = self._extract_relevant_context(
            state.conversation_history, user_input
        )
        logger.debug(f"Extracted {len(relevant_context)} relevant context items")

        # Add current focus areas
        focus_context = self._create_focus_context(state.focus, user_input)
        logger.debug(f"Created {len(focus_context)} focus context items")

        # Add recent successful tool results
        tool_context = self._extract_tool_context(state.conversation_history)
        logger.debug(f"Extracted {len(tool_context)} tool context items")

        # Add user preferences and patterns
        preference_context = self._extract_user_preferences(state.conversation_history)
        logger.debug(f"Extracted {len(preference_context)} preference context items")

        # Combine and prioritize
        optimized_context = self._prioritize_context(
            [relevant_context, focus_context, tool_context, preference_context]
        )

        # Apply size limits
        final_context = optimized_context[: self.max_context_items]

        logger.info(
            f"Memory context optimization complete: {len(final_context)} items (max: {self.max_context_items})"
        )

        return final_context

    def _extract_relevant_context(
        self, conversation_history: List[dict], user_input: str
    ) -> List[dict]:
        """
        Extract context relevant to current user input.

        Args:
            conversation_history: List of conversation history items
            user_input: Current user input

        Returns:
            List of relevant context items
        """
        relevant_items = []

        # Simple keyword matching for now (can be enhanced with semantic similarity)
        # Ensure user_input is a string before calling .lower()
        if isinstance(user_input, list):
            # If it's a list, join the items or take the first one
            user_input_str = " ".join(user_input) if user_input else ""
        else:
            user_input_str = str(user_input) if user_input else ""

        input_keywords = set(user_input_str.lower().split())

        for item in conversation_history:
            content = str(item.get("content", "")).lower()
            item_keywords = set(content.split())

            # Calculate relevance score
            if item_keywords & input_keywords:  # Intersection
                relevance_score = len(item_keywords & input_keywords) / len(
                    input_keywords
                )

                if relevance_score > 0.3:  # Threshold for relevance
                    relevant_items.append(
                        {
                            "role": "context",
                            "content": item.get("content", ""),
                            "relevance_score": relevance_score,
                            "source": "conversation_history",
                            "original_role": item.get("role", "unknown"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

        # Sort by relevance and return top items
        relevant_items.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return relevant_items[:10]  # Limit to top 10 relevant items

    def _create_focus_context(self, focus: List[str], user_input: str) -> List[dict]:
        """
        Create context based on current focus areas.

        Args:
            focus: List of current focus areas
            user_input: Current user input

        Returns:
            List of focus context items
        """
        focus_context = []

        if not focus:
            return focus_context

        # Create context items for each focus area
        for focus_area in focus:
            focus_context.append(
                {
                    "role": "context",
                    "content": f"Current focus: {focus_area}",
                    "relevance_score": 0.8,  # High relevance for focus areas
                    "source": "focus_areas",
                    "focus_area": focus_area,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return focus_context

    def _extract_tool_context(self, conversation_history: List[dict]) -> List[dict]:
        """
        Extract context from recent successful tool results.

        Args:
            conversation_history: List of conversation history items

        Returns:
            List of tool context items
        """
        tool_context = []
        recent_tools = {}  # Track most recent result per tool

        # Find the most recent successful tool results
        for item in conversation_history:
            if item.get("role") == "tool":
                tool_name = item.get("name", "")
                content = str(item.get("content", ""))

                # Only include successful tool calls
                if "Error" not in content and tool_name:
                    recent_tools[tool_name] = {
                        "role": "context",
                        "content": f"Tool {tool_name} result: {content[:100]}...",
                        "relevance_score": 0.6,  # Moderate relevance for tool results
                        "source": "tool_results",
                        "tool_name": tool_name,
                        "full_result": content,
                        "timestamp": datetime.now().isoformat(),
                    }

        # Convert to list and limit to recent tools
        tool_context = list(recent_tools.values())[:5]  # Limit to 5 most recent tools

        return tool_context

    def _extract_user_preferences(self, conversation_history: List[dict]) -> List[dict]:
        """
        Extract user preferences and patterns from conversation history.

        Args:
            conversation_history: List of conversation history items

        Returns:
            List of preference context items
        """
        preference_context = []

        # Look for patterns in user messages
        user_messages = [
            item for item in conversation_history if item.get("role") == "user"
        ]

        if len(user_messages) < 2:
            return preference_context

        # Analyze user message patterns
        preferences = self._analyze_user_preferences(user_messages)

        for preference_type, details in preferences.items():
            preference_context.append(
                {
                    "role": "context",
                    "content": f"User preference: {details['description']}",
                    "relevance_score": 0.7,  # High relevance for user preferences
                    "source": "user_preferences",
                    "preference_type": preference_type,
                    "details": details,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return preference_context[:3]  # Limit to top 3 preferences

    def _analyze_user_preferences(
        self, user_messages: List[dict]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze user messages to identify preferences and patterns.

        Args:
            user_messages: List of user message items

        Returns:
            Dictionary of identified preferences
        """
        preferences = {}

        # Analyze message length preferences
        message_lengths = [len(str(msg.get("content", ""))) for msg in user_messages]
        avg_length = (
            sum(message_lengths) / len(message_lengths) if message_lengths else 0
        )

        if avg_length > 100:
            preferences["message_length"] = {
                "description": "Prefers detailed explanations",
                "value": "detailed",
                "confidence": 0.8,
            }
        elif avg_length < 50:
            preferences["message_length"] = {
                "description": "Prefers concise responses",
                "value": "concise",
                "confidence": 0.8,
            }

        # Analyze tool usage preferences
        tool_mentions = {}
        for msg in user_messages:
            content = str(msg.get("content", "")).lower()
            if "tool" in content:
                # Extract tool names mentioned
                import re

                tool_pattern = r"(\w+)_tool"
                tools = re.findall(tool_pattern, content)
                for tool in tools:
                    tool_mentions[tool] = tool_mentions.get(tool, 0) + 1

        if tool_mentions:
            most_mentioned = max(tool_mentions.items(), key=lambda x: x[1])
            preferences["tool_preference"] = {
                "description": f"Frequently uses {most_mentioned[0]} tool",
                "value": most_mentioned[0],
                "confidence": min(most_mentioned[1] / len(user_messages), 1.0),
            }

        # Analyze communication style
        formal_indicators = ["please", "thank you", "would you", "could you"]
        casual_indicators = ["hey", "hi", "thanks", "cool", "awesome"]

        formal_count = sum(
            1
            for msg in user_messages
            for indicator in formal_indicators
            if indicator in str(msg.get("content", "")).lower()
        )
        casual_count = sum(
            1
            for msg in user_messages
            for indicator in casual_indicators
            if indicator in str(msg.get("content", "")).lower()
        )

        if formal_count > casual_count:
            preferences["communication_style"] = {
                "description": "Prefers formal communication style",
                "value": "formal",
                "confidence": 0.7,
            }
        elif casual_count > formal_count:
            preferences["communication_style"] = {
                "description": "Prefers casual communication style",
                "value": "casual",
                "confidence": 0.7,
            }

        return preferences

    def _prioritize_context(self, context_lists: List[List[dict]]) -> List[dict]:
        """
        Prioritize and combine context from multiple sources.

        Args:
            context_lists: List of context lists from different sources

        Returns:
            Prioritized and combined context list
        """
        all_context = []

        # Flatten all context lists
        for context_list in context_lists:
            all_context.extend(context_list)

        if not all_context:
            return []

        # Sort by relevance score (highest first)
        all_context.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        # Remove duplicates based on content similarity
        unique_context = self._remove_duplicate_context(all_context)

        return unique_context

    def _remove_duplicate_context(self, context_items: List[dict]) -> List[dict]:
        """
        Remove duplicate context items based on content similarity.

        Args:
            context_items: List of context items

        Returns:
            List with duplicates removed
        """
        unique_items = []
        seen_content = set()

        for item in context_items:
            content = str(item.get("content", "")).lower()
            content_hash = hash(content[:100])  # Hash first 100 chars

            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_items.append(item)

        return unique_items

    def get_context_stats(
        self, original_context: List[dict], optimized_context: List[dict]
    ) -> Dict[str, Any]:
        """
        Get statistics about context optimization.

        Args:
            original_context: Original memory context
            optimized_context: Optimized memory context

        Returns:
            Dictionary with optimization statistics
        """
        original_length = len(original_context)
        optimized_length = len(optimized_context)

        if original_length == 0:
            return {
                "original_length": 0,
                "optimized_length": 0,
                "improvement_ratio": 1.0,
                "context_quality_score": 0.0,
            }

        # Calculate improvement metrics
        improvement_ratio = (
            optimized_length / original_length if original_length > 0 else 1.0
        )

        # Calculate context quality score based on relevance scores
        avg_relevance = sum(
            item.get("relevance_score", 0) for item in optimized_context
        ) / max(len(optimized_context), 1)

        return {
            "original_length": original_length,
            "optimized_length": optimized_length,
            "improvement_ratio": improvement_ratio,
            "context_quality_score": avg_relevance,
            "optimization_timestamp": datetime.now().isoformat(),
        }
