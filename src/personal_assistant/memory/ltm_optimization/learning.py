"""
Consolidated Learning Module

This module combines pattern learning and preference learning functionality
into a single, manageable interface for LTM optimization.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

from ...config.logging_config import get_logger
from ...tools.ltm.ltm_storage import add_ltm_memory
from .config import LTMConfig

logger = get_logger("learning")


class ConversationPatternLearner:
    """Learns patterns from conversation history"""

    def __init__(self, config: LTMConfig = None):
        self.config = config or LTMConfig()

    async def learn_patterns(
        self, user_id: int, user_input: str, agent_response: str
    ) -> List[dict]:
        """Learn patterns from conversation and create memories"""

        patterns = []

        # Communication style patterns
        communication_pattern = self._analyze_communication_style(
            user_input, agent_response
        )
        if communication_pattern:
            patterns.append(communication_pattern)

        # Topic preference patterns
        topic_pattern = self._analyze_topic_preferences(user_input)
        if topic_pattern:
            patterns.append(topic_pattern)

        # Time-based patterns
        time_pattern = self._analyze_time_patterns(user_input)
        if time_pattern:
            patterns.append(time_pattern)

        # Create memory entries for each pattern
        created_memories = []
        for pattern in patterns:
            memory = await self._create_pattern_memory(user_id, pattern)
            if memory:
                created_memories.append(memory)

        logger.info(
            f"Created {len(created_memories)} pattern memories for user {user_id}"
        )
        return created_memories

    def _analyze_communication_style(
        self, user_input: str, agent_response: str
    ) -> Optional[dict]:
        """Analyze user's communication style preferences"""

        detected_styles = []
        for style, indicators in self.config.communication_style_indicators.items():
            if any(indicator in user_input.lower() for indicator in indicators):
                detected_styles.append(style)

        if detected_styles:
            confidence = len(detected_styles) / len(
                self.config.communication_style_indicators
            )
            if confidence >= self.config.memory_creation_confidence_threshold:
                return {
                    "type": "communication_style",
                    "content": f"User prefers {', '.join(detected_styles)} communication style",
                    "confidence": confidence,
                    "tags": ["communication", "preference", "style"] + detected_styles,
                }

        return None

    def _analyze_topic_preferences(self, user_input: str) -> Optional[dict]:
        """Analyze user's topic preferences"""

        detected_topics = []
        for topic, keywords in self.config.topic_preference_keywords.items():
            if any(keyword in user_input.lower() for keyword in keywords):
                detected_topics.append(topic)

        if detected_topics:
            confidence = len(detected_topics) / len(
                self.config.topic_preference_keywords
            )
            if confidence >= self.config.memory_creation_confidence_threshold:
                return {
                    "type": "topic_preference",
                    "content": f"User shows interest in {', '.join(detected_topics)} topics",
                    "confidence": confidence,
                    "tags": ["topic", "preference", "interest"] + detected_topics,
                }

        return None

    def _analyze_time_patterns(self, user_input: str) -> Optional[dict]:
        """Analyze time-based patterns in user input"""

        time_keywords = [
            "morning",
            "afternoon",
            "evening",
            "night",
            "today",
            "tomorrow",
            "weekend",
        ]
        detected_times = [word for word in time_keywords if word in user_input.lower()]

        if detected_times:
            confidence = len(detected_times) / len(time_keywords)
            if confidence >= self.config.memory_creation_confidence_threshold:
                return {
                    "type": "time_pattern",
                    "content": f"User shows time preference for {', '.join(detected_times)}",
                    "confidence": confidence,
                    "tags": ["time", "preference", "pattern"] + detected_times,
                }

        return None

    async def _create_pattern_memory(
        self, user_id: int, pattern: dict
    ) -> Optional[dict]:
        """Create a memory entry for a detected pattern"""

        try:
            memory_data = {
                "user_id": user_id,
                "content": pattern["content"],
                "tags": pattern["tags"],
                "metadata": {
                    "type": pattern["type"],
                    "confidence": pattern["confidence"],
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                },
            }

            memory_id = await add_ltm_memory(memory_data)
            if memory_id:
                logger.info(f"Created pattern memory: {pattern['type']}")
                return {"id": memory_id, **pattern}

        except Exception as e:
            logger.error(f"Failed to create pattern memory: {e}")

        return None


class UserPreferenceLearner:
    """Learns user preferences from interactions"""

    def __init__(self, config: LTMConfig = None):
        self.config = config or LTMConfig()

    async def learn_preferences(
        self,
        user_id: int,
        user_input: str,
        agent_response: str,
        tool_result: str = None,
    ) -> List[dict]:
        """Learn user preferences and create memories"""

        preferences = []

        # Tool usage preferences
        if tool_result:
            tool_preference = self._analyze_tool_preference(user_input, tool_result)
            if tool_preference:
                preferences.append(tool_preference)

        # Response format preferences
        format_preference = self._analyze_response_format_preference(
            user_input, agent_response
        )
        if format_preference:
            preferences.append(format_preference)

        # Timing preferences
        timing_preference = self._analyze_timing_preferences(user_input)
        if timing_preference:
            preferences.append(timing_preference)

        # Create memory entries for each preference
        created_memories = []
        for preference in preferences:
            memory = await self._create_preference_memory(user_id, preference)
            if memory:
                created_memories.append(memory)

        logger.info(
            f"Created {len(created_memories)} preference memories for user {user_id}"
        )
        return created_memories

    def _analyze_tool_preference(
        self, user_input: str, tool_result: str
    ) -> Optional[dict]:
        """Analyze user's tool usage preferences"""

        tool_result_str = str(tool_result).lower()

        # Check for errors
        if "error" in tool_result_str:
            # Extract tool name from user input or result
            tool_name = self._extract_tool_name_from_input(user_input) or "unknown_tool"
            return {
                "type": "tool_preference",
                "content": f"User encountered error with {tool_name} tool - may need alternative approach",
                "confidence": 0.8,
                "tags": ["tool_preference", "error", "learning", tool_name.lower()],
            }

        # Check for successful tool usage
        success_indicators = [
            "success",
            "created",
            "deleted",
            "updated",
            "found",
            "completed",
        ]
        if any(indicator in tool_result_str for indicator in success_indicators):
            tool_name = self._extract_tool_name_from_input(user_input) or "unknown_tool"
            return {
                "type": "tool_preference",
                "content": f"User successfully used {tool_name} tool",
                "confidence": 0.9,
                "tags": ["tool_preference", "success", tool_name.lower()],
            }

        return None

    def _analyze_response_format_preference(
        self, user_input: str, agent_response: str
    ) -> Optional[dict]:
        """Analyze user's preferred response format"""

        detected_formats = []
        for format_type, indicators in self.config.response_format_indicators.items():
            if any(indicator in user_input.lower() for indicator in indicators):
                detected_formats.append(format_type)

        if detected_formats:
            confidence = len(detected_formats) / len(
                self.config.response_format_indicators
            )
            if confidence >= self.config.memory_creation_confidence_threshold:
                return {
                    "type": "response_format_preference",
                    "content": f"User prefers {', '.join(detected_formats)} response format",
                    "confidence": confidence,
                    "tags": ["response_format", "preference", "style"]
                    + detected_formats,
                }

        return None

    def _analyze_timing_preferences(self, user_input: str) -> Optional[dict]:
        """Analyze user's timing preferences"""

        timing_keywords = [
            "quick",
            "fast",
            "slow",
            "detailed",
            "brief",
            "comprehensive",
        ]
        detected_timing = [
            word for word in timing_keywords if word in user_input.lower()
        ]

        if detected_timing:
            confidence = len(detected_timing) / len(timing_keywords)
            if confidence >= self.config.memory_creation_confidence_threshold:
                return {
                    "type": "timing_preference",
                    "content": f"User prefers {', '.join(detected_timing)} responses",
                    "confidence": confidence,
                    "tags": ["timing", "preference", "speed"] + detected_timing,
                }

        return None

    def _extract_tool_name_from_input(self, user_input: str) -> Optional[str]:
        """Extract tool name from user input"""

        # Look for common tool-related patterns
        tool_patterns = [r"use (\w+)", r"with (\w+)", r"via (\w+)", r"through (\w+)"]

        for pattern in tool_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                return match.group(1)

        return None

    async def _create_preference_memory(
        self, user_id: int, preference: dict
    ) -> Optional[dict]:
        """Create a memory entry for a detected preference"""

        try:
            memory_data = {
                "user_id": user_id,
                "content": preference["content"],
                "tags": preference["tags"],
                "metadata": {
                    "type": preference["type"],
                    "confidence": preference["confidence"],
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                },
            }

            memory_id = await add_ltm_memory(memory_data)
            if memory_id:
                logger.info(f"Created preference memory: {preference['type']}")
                return {"id": memory_id, **preference}

        except Exception as e:
            logger.error(f"Failed to create preference memory: {e}")

        return None


# Convenience function to get both learners
def get_learners(
    config: LTMConfig = None,
) -> tuple[ConversationPatternLearner, UserPreferenceLearner]:
    """Get both pattern and preference learners with shared configuration"""
    shared_config = config or LTMConfig()
    return ConversationPatternLearner(shared_config), UserPreferenceLearner(
        shared_config
    )
