"""
Pattern Recognition Engine for LTM Optimization

This module analyzes state management data to identify patterns and convert them
into high-quality long-term memories. It focuses on conversation patterns,
tool usage patterns, and user behavior patterns from state data.
"""

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...config.logging_config import get_logger
from ...types.state import AgentState
from .config import EnhancedLTMConfig

logger = get_logger("pattern_recognition")


class PatternRecognitionEngine:
    """
    Engine for recognizing patterns in state data and converting them to memories.

    This engine analyzes:
    - Conversation flow patterns
    - Tool usage patterns
    - User behavior patterns
    - Temporal patterns
    - State-to-memory conversion
    """

    def __init__(self, config: Optional[EnhancedLTMConfig] = None):
        """Initialize the pattern recognition engine"""
        self.config = config or EnhancedLTMConfig()
        self.logger = get_logger("pattern_recognition")

    async def analyze_conversation_flow(
        self, conversation_history: List[dict]
    ) -> List[Dict[str, Any]]:
        """
        Analyze conversation patterns for memory creation.

        Args:
            conversation_history: List of conversation exchanges from state

        Returns:
            List of identified patterns ready for memory creation
        """
        if not conversation_history or len(conversation_history) < 2:
            return []

        patterns: List[Dict[str, Any]] = []

        try:
            # Analyze communication style patterns
            communication_patterns = self._analyze_communication_style(
                conversation_history
            )
            patterns.extend(communication_patterns)

            # Analyze topic preference patterns
            topic_patterns = self._analyze_topic_preferences(conversation_history)
            patterns.extend(topic_patterns)

            # Analyze response format patterns
            format_patterns = self._analyze_response_formats(conversation_history)
            patterns.extend(format_patterns)

            # Analyze conversation length patterns
            length_patterns = self._analyze_conversation_lengths(conversation_history)
            patterns.extend(length_patterns)

            self.logger.info(f"Identified {len(patterns)} conversation patterns")

        except Exception as e:
            self.logger.error(f"Error analyzing conversation flow: {e}")

        return patterns

    async def detect_tool_usage_patterns(
        self, tool_calls: List[dict]
    ) -> List[Dict[str, Any]]:
        """
        Detect patterns in tool usage from state data.

        Args:
            tool_calls: List of tool execution results from state

        Returns:
            List of tool usage patterns ready for memory creation
        """
        if not tool_calls:
            return []

        patterns: List[Dict[str, Any]] = []

        try:
            # Analyze tool preference patterns
            tool_preferences = self._analyze_tool_preferences(tool_calls)
            patterns.extend(tool_preferences)

            # Analyze tool success patterns
            success_patterns = self._analyze_tool_success_patterns(tool_calls)
            patterns.extend(success_patterns)

            # Analyze tool usage frequency
            frequency_patterns = self._analyze_tool_frequency(tool_calls)
            patterns.extend(frequency_patterns)

            # Analyze tool combination patterns
            combination_patterns = self._analyze_tool_combinations(tool_calls)
            patterns.extend(combination_patterns)

            self.logger.info(f"Identified {len(patterns)} tool usage patterns")

        except Exception as e:
            self.logger.error(f"Error detecting tool usage patterns: {e}")

        return patterns

    async def recognize_user_behavior_patterns(
        self, interactions: List[dict]
    ) -> List[Dict[str, Any]]:
        """
        Recognize user behavior patterns from state interactions.

        Args:
            interactions: List of user interactions from state

        Returns:
            List of user behavior patterns ready for memory creation
        """
        if not interactions:
            return []

        patterns: List[Dict[str, Any]] = []

        try:
            # Analyze interaction timing patterns
            timing_patterns = self._analyze_interaction_timing(interactions)
            patterns.extend(timing_patterns)

            # Analyze user preference patterns
            preference_patterns = self._analyze_user_preferences(interactions)
            patterns.extend(preference_patterns)

            # Analyze user habit patterns
            habit_patterns = self._analyze_user_habits(interactions)
            patterns.extend(habit_patterns)

            # Analyze user learning patterns
            learning_patterns = self._analyze_user_learning(interactions)
            patterns.extend(learning_patterns)

            self.logger.info(f"Identified {len(patterns)} user behavior patterns")

        except Exception as e:
            self.logger.error(f"Error recognizing user behavior patterns: {e}")

        return patterns

    async def analyze_temporal_patterns(
        self, state_data: AgentState
    ) -> List[Dict[str, Any]]:
        """
        Analyze temporal patterns from state data.

        Args:
            state_data: Complete agent state for temporal analysis

        Returns:
            List of temporal patterns ready for memory creation
        """
        patterns: List[Dict[str, Any]] = []

        try:
            # Analyze time-of-day patterns
            time_patterns = self._analyze_time_of_day_patterns(state_data)
            patterns.extend(time_patterns)

            # Analyze day-of-week patterns
            day_patterns = self._analyze_day_of_week_patterns(state_data)
            patterns.extend(day_patterns)

            # Analyze session duration patterns
            duration_patterns = self._analyze_session_duration_patterns(state_data)
            patterns.extend(duration_patterns)

            # Analyze interaction frequency patterns
            frequency_patterns = self._analyze_interaction_frequency_patterns(
                state_data
            )
            patterns.extend(frequency_patterns)

            self.logger.info(f"Identified {len(patterns)} temporal patterns")

        except Exception as e:
            self.logger.error(f"Error analyzing temporal patterns: {e}")

        return patterns

    async def convert_state_to_memories(
        self, user_id: int, state_data: AgentState
    ) -> List[Dict[str, Any]]:
        """
        Convert state data to memories using pattern recognition.

        This is the main pipeline that coordinates all pattern analysis
        and converts identified patterns to memory-ready structures.

        Args:
            user_id: User ID for memory creation
            state_data: Complete agent state for analysis

        Returns:
            List of memory-ready structures
        """
        memories = []

        try:
            # Analyze conversation patterns
            if state_data.conversation_history:
                conversation_patterns = await self.analyze_conversation_flow(
                    state_data.conversation_history
                )
                for pattern in conversation_patterns:
                    memory = self._convert_pattern_to_memory(
                        user_id, pattern, "conversation"
                    )
                    if memory:
                        memories.append(memory)

            # Analyze tool usage patterns
            if hasattr(state_data, "last_tool_result") and state_data.last_tool_result:
                tool_patterns = await self.detect_tool_usage_patterns(
                    [state_data.last_tool_result]
                )
                for pattern in tool_patterns:
                    memory = self._convert_pattern_to_memory(
                        user_id, pattern, "tool_usage"
                    )
                    if memory:
                        memories.append(memory)

            # Analyze user behavior patterns
            if state_data.history:
                # Convert tuple list to dict list if needed
                history_data = []
                for item in state_data.history:
                    if isinstance(item, tuple):
                        # Convert tuple to dict format
                        history_data.append(
                            {"interaction": item[0], "timestamp": item[1]}
                        )
                    elif isinstance(item, dict):
                        history_data.append(item)
                    else:
                        # Fallback for other types
                        history_data.append(
                            {
                                "data": str(item),
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )

                behavior_patterns = await self.recognize_user_behavior_patterns(
                    history_data
                )
                for pattern in behavior_patterns:
                    memory = self._convert_pattern_to_memory(
                        user_id, pattern, "user_behavior"
                    )
                    if memory:
                        memories.append(memory)

            # Analyze temporal patterns
            temporal_patterns = await self.analyze_temporal_patterns(state_data)
            for pattern in temporal_patterns:
                memory = self._convert_pattern_to_memory(user_id, pattern, "temporal")
                if memory:
                    memories.append(memory)

            # Analyze focus area patterns
            if state_data.focus:
                focus_patterns = self._analyze_focus_area_patterns(state_data.focus)
                for pattern in focus_patterns:
                    memory = self._convert_pattern_to_memory(user_id, pattern, "focus")
                    if memory:
                        memories.append(memory)

            self.logger.info(
                f"Converted {len(memories)} patterns to memories for user {user_id}"
            )

        except Exception as e:
            self.logger.error(f"Error converting state to memories: {e}")

        return memories

    def _analyze_communication_style(
        self, conversation_history: List[dict]
    ) -> List[Dict[str, Any]]:
        """Analyze communication style patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            # Count communication style indicators
            style_counts: Dict[str, int] = defaultdict(int)
            total_messages = len(conversation_history)

            for exchange in conversation_history:
                user_input = exchange.get("user_input", "").lower()

                if self.config.communication_style_indicators:
                    for (
                        style,
                        indicators,
                    ) in self.config.communication_style_indicators.items():
                        for indicator in indicators:
                            if indicator.lower() in user_input:
                                style_counts[style] += 1
                                break

            # Create patterns for dominant styles
            for style, count in style_counts.items():
                if count >= max(
                    2, total_messages * 0.3
                ):  # At least 2 or 30% of messages
                    patterns.append(
                        {
                            "type": "communication_style",
                            "subtype": style,
                            "confidence": min(0.9, count / total_messages),
                            "frequency": count,
                            "total_messages": total_messages,
                            "description": f"User tends to use {style} communication style",
                            "tags": ["communication", "style", style, "pattern"],
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing communication style: {e}")

        return patterns

    def _analyze_topic_preferences(
        self, conversation_history: List[dict]
    ) -> List[Dict[str, Any]]:
        """Analyze topic preference patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            # Count topic keywords
            topic_counts: Dict[str, int] = defaultdict(int)
            total_messages = len(conversation_history)

            for exchange in conversation_history:
                user_input = exchange.get("user_input", "").lower()

                if self.config.topic_preference_keywords:
                    for (
                        topic,
                        keywords,
                    ) in self.config.topic_preference_keywords.items():
                        for keyword in keywords:
                            if keyword.lower() in user_input:
                                topic_counts[topic] += 1
                                break

            # Create patterns for frequent topics
            for topic, count in topic_counts.items():
                if count >= max(
                    2, total_messages * 0.2
                ):  # At least 2 or 20% of messages
                    patterns.append(
                        {
                            "type": "topic_preference",
                            "subtype": topic,
                            "confidence": min(0.8, count / total_messages),
                            "frequency": count,
                            "total_messages": total_messages,
                            "description": f"User frequently discusses {topic} topics",
                            "tags": ["topic", "preference", topic, "pattern"],
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing topic preferences: {e}")

        return patterns

    def _analyze_response_formats(
        self, conversation_history: List[dict]
    ) -> List[Dict[str, Any]]:
        """Analyze response format preference patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            # Count response format indicators
            format_counts: Dict[str, int] = defaultdict(int)
            total_messages = len(conversation_history)

            for exchange in conversation_history:
                user_input = exchange.get("user_input", "").lower()

                if self.config.response_format_indicators:
                    for (
                        format_type,
                        indicators,
                    ) in self.config.response_format_indicators.items():
                        for indicator in indicators:
                            if indicator.lower() in user_input:
                                format_counts[format_type] += 1
                                break

            # Create patterns for preferred formats
            for format_type, count in format_counts.items():
                if count >= max(
                    2, total_messages * 0.25
                ):  # At least 2 or 25% of messages
                    patterns.append(
                        {
                            "type": "response_format",
                            "subtype": format_type,
                            "confidence": min(0.85, count / total_messages),
                            "frequency": count,
                            "total_messages": total_messages,
                            "description": f"User prefers {format_type} responses",
                            "tags": ["response", "format", format_type, "preference"],
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing response formats: {e}")

        return patterns

    def _analyze_conversation_lengths(
        self, conversation_history: List[dict]
    ) -> List[Dict[str, Any]]:
        """Analyze conversation length patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            if len(conversation_history) < 3:
                return patterns

            # Calculate average message lengths
            user_lengths = [
                len(exchange.get("user_input", "")) for exchange in conversation_history
            ]
            avg_user_length = sum(user_lengths) / len(user_lengths)

            # Determine length preference
            if avg_user_length > 100:
                length_type = "detailed"
                description = "User tends to provide detailed, lengthy inputs"
            elif avg_user_length > 50:
                length_type = "moderate"
                description = "User provides moderate length inputs"
            else:
                length_type = "concise"
                description = "User tends to provide concise, brief inputs"

            patterns.append(
                {
                    "type": "conversation_length",
                    "subtype": length_type,
                    "confidence": 0.7,
                    "avg_length": avg_user_length,
                    "total_messages": len(conversation_history),
                    "description": description,
                    "tags": ["conversation", "length", length_type, "pattern"],
                }
            )

        except Exception as e:
            self.logger.error(f"Error analyzing conversation lengths: {e}")

        return patterns

    def _analyze_tool_preferences(self, tool_calls: List[dict]) -> List[Dict[str, Any]]:
        """Analyze tool preference patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            # Count tool usage
            tool_counts: Counter[str] = Counter()
            total_tools = len(tool_calls)

            for tool_call in tool_calls:
                tool_name = tool_call.get("tool_name", "unknown")
                tool_counts[tool_name] += 1

            # Create patterns for frequently used tools
            for tool_name, count in tool_counts.items():
                if count >= max(
                    2, total_tools * 0.3
                ):  # At least 2 or 30% of tool calls
                    patterns.append(
                        {
                            "type": "tool_preference",
                            "subtype": tool_name,
                            "confidence": min(0.8, count / total_tools),
                            "frequency": count,
                            "total_tools": total_tools,
                            "description": f"User frequently uses {tool_name} tool",
                            "tags": ["tool", "preference", tool_name, "usage"],
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing tool preferences: {e}")

        return patterns

    def _analyze_tool_success_patterns(
        self, tool_calls: List[dict]
    ) -> List[Dict[str, Any]]:
        """Analyze tool success/failure patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            success_count = 0
            failure_count = 0
            total_tools = len(tool_calls)

            for tool_call in tool_calls:
                # Check for success indicators in tool results
                result = str(tool_call.get("result", "")).lower()
                if any(
                    success_indicator in result
                    for success_indicator in [
                        "success",
                        "created",
                        "updated",
                        "completed",
                    ]
                ):
                    success_count += 1
                elif any(
                    failure_indicator in result
                    for failure_indicator in ["error", "failed", "not found", "invalid"]
                ):
                    failure_count += 1

            # Create success pattern if significant
            if success_count > 0 and success_count >= total_tools * 0.6:
                patterns.append(
                    {
                        "type": "tool_success",
                        "subtype": "high_success_rate",
                        "confidence": min(0.9, success_count / total_tools),
                        "success_rate": success_count / total_tools,
                        "total_tools": total_tools,
                        "description": "User has high success rate with tools",
                        "tags": ["tool", "success", "pattern", "efficiency"],
                    }
                )

        except Exception as e:
            self.logger.error(f"Error analyzing tool success patterns: {e}")

        return patterns

    def _analyze_tool_frequency(self, tool_calls: List[dict]) -> List[Dict[str, Any]]:
        """Analyze tool usage frequency patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            if len(tool_calls) < 3:
                return patterns

            # Analyze usage frequency over time
            # This is a simplified analysis - in practice, you'd want timestamps
            usage_frequency = len(tool_calls) / max(1, len(tool_calls))

            if usage_frequency > 0.8:
                frequency_type = "high"
                description = "User frequently uses tools"
            elif usage_frequency > 0.4:
                frequency_type = "moderate"
                description = "User moderately uses tools"
            else:
                frequency_type = "low"
                description = "User infrequently uses tools"

            patterns.append(
                {
                    "type": "tool_frequency",
                    "subtype": frequency_type,
                    "confidence": 0.6,
                    "frequency_rate": usage_frequency,
                    "total_tools": len(tool_calls),
                    "description": description,
                    "tags": ["tool", "frequency", frequency_type, "pattern"],
                }
            )

        except Exception as e:
            self.logger.error(f"Error analyzing tool frequency: {e}")

        return patterns

    def _analyze_tool_combinations(
        self, tool_calls: List[dict]
    ) -> List[Dict[str, Any]]:
        """Analyze tool combination patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            if len(tool_calls) < 2:
                return patterns

            # Find common tool combinations
            tool_sequences = []
            for i in range(len(tool_calls) - 1):
                current_tool = tool_calls[i].get("tool_name", "unknown")
                next_tool = tool_calls[i + 1].get("tool_name", "unknown")
                tool_sequences.append((current_tool, next_tool))

            # Count combinations
            combination_counts = Counter(tool_sequences)

            # Create patterns for common combinations
            for (tool1, tool2), count in combination_counts.items():
                if count >= 2:  # At least 2 occurrences
                    patterns.append(
                        {
                            "type": "tool_combination",
                            "subtype": f"{tool1}_and_{tool2}",
                            "confidence": min(0.7, count / len(tool_sequences)),
                            "frequency": count,
                            "total_sequences": len(tool_sequences),
                            "description": f"User commonly uses {tool1} followed by {tool2}",
                            "tags": ["tool", "combination", tool1, tool2, "pattern"],
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing tool combinations: {e}")

        return patterns

    def _analyze_interaction_timing(
        self, interactions: List[dict]
    ) -> List[Dict[str, Any]]:
        """Analyze interaction timing patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            if len(interactions) < 3:
                return patterns

            # This is a simplified analysis - in practice, you'd want actual timestamps
            # For now, we'll analyze based on interaction order
            interaction_count = len(interactions)

            # Determine if user tends to have multiple interactions in sequence
            if interaction_count > 5:
                timing_type = "extended_session"
                description = "User tends to have extended interaction sessions"
            elif interaction_count > 2:
                timing_type = "moderate_session"
                description = "User tends to have moderate interaction sessions"
            else:
                timing_type = "brief_session"
                description = "User tends to have brief interaction sessions"

            patterns.append(
                {
                    "type": "interaction_timing",
                    "subtype": timing_type,
                    "confidence": 0.6,
                    "interaction_count": interaction_count,
                    "description": description,
                    "tags": ["interaction", "timing", timing_type, "pattern"],
                }
            )

        except Exception as e:
            self.logger.error(f"Error analyzing interaction timing: {e}")

        return patterns

    def _analyze_user_preferences(
        self, interactions: List[dict]
    ) -> List[Dict[str, Any]]:
        """Analyze user preference patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            # Look for preference indicators in interactions
            preference_indicators = self.config.get_personal_pattern_keywords()
            preference_count = 0

            for interaction in interactions:
                user_input = str(interaction.get("user_input", "")).lower()
                for indicator in preference_indicators:
                    if indicator.lower() in user_input:
                        preference_count += 1
                        break

            if preference_count > 0:
                preference_rate = preference_count / len(interactions)

                if preference_rate > 0.5:
                    preference_type = "high"
                    description = "User frequently expresses preferences"
                elif preference_rate > 0.2:
                    preference_type = "moderate"
                    description = "User moderately expresses preferences"
                else:
                    preference_type = "low"
                    description = "User infrequently expresses preferences"

                patterns.append(
                    {
                        "type": "user_preferences",
                        "subtype": preference_type,
                        "confidence": min(0.8, preference_rate),
                        "preference_rate": preference_rate,
                        "total_interactions": len(interactions),
                        "description": description,
                        "tags": ["user", "preferences", preference_type, "pattern"],
                    }
                )

        except Exception as e:
            self.logger.error(f"Error analyzing user preferences: {e}")

        return patterns

    def _analyze_user_habits(self, interactions: List[dict]) -> List[Dict[str, Any]]:
        """Analyze user habit patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            # Look for habit indicators
            habit_indicators = [
                "always",
                "never",
                "usually",
                "typically",
                "tend to",
                "avoid",
            ]
            habit_count = 0

            for interaction in interactions:
                user_input = str(interaction.get("user_input", "")).lower()
                for indicator in habit_indicators:
                    if indicator in user_input:
                        habit_count += 1
                        break

            if habit_count > 0:
                habit_rate = habit_count / len(interactions)

                if habit_rate > 0.3:
                    habit_type = "habitual"
                    description = "User frequently discusses habits and routines"
                else:
                    habit_type = "occasional"
                    description = "User occasionally discusses habits and routines"

                patterns.append(
                    {
                        "type": "user_habits",
                        "subtype": habit_type,
                        "confidence": min(0.7, habit_rate),
                        "habit_rate": habit_rate,
                        "total_interactions": len(interactions),
                        "description": description,
                        "tags": ["user", "habits", habit_type, "pattern"],
                    }
                )

        except Exception as e:
            self.logger.error(f"Error analyzing user habits: {e}")

        return patterns

    def _analyze_user_learning(self, interactions: List[dict]) -> List[Dict[str, Any]]:
        """Analyze user learning patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            # Look for learning indicators
            learning_indicators = self.config.get_learning_pattern_keywords()
            learning_count = 0

            for interaction in interactions:
                user_input = str(interaction.get("user_input", "")).lower()
                for indicator in learning_indicators:
                    if indicator.lower() in user_input:
                        learning_count += 1
                        break

            if learning_count > 0:
                learning_rate = learning_count / len(interactions)

                if learning_rate > 0.4:
                    learning_type = "active_learner"
                    description = "User actively seeks learning and understanding"
                elif learning_rate > 0.2:
                    learning_type = "moderate_learner"
                    description = "User moderately seeks learning and understanding"
                else:
                    learning_type = "passive_learner"
                    description = "User occasionally seeks learning and understanding"

                patterns.append(
                    {
                        "type": "user_learning",
                        "subtype": learning_type,
                        "confidence": min(0.75, learning_rate),
                        "learning_rate": learning_rate,
                        "total_interactions": len(interactions),
                        "description": description,
                        "tags": ["user", "learning", learning_type, "pattern"],
                    }
                )

        except Exception as e:
            self.logger.error(f"Error analyzing user learning: {e}")

        return patterns

    def _analyze_time_of_day_patterns(
        self, state_data: AgentState
    ) -> List[Dict[str, Any]]:
        """Analyze time-of-day patterns from state data"""
        patterns: List[Dict[str, Any]] = []

        try:
            # This would require actual timestamps in the state data
            # For now, return empty patterns
            # In practice, you'd analyze when the user is most active

            pass

        except Exception as e:
            self.logger.error(f"Error analyzing time-of-day patterns: {e}")

        return patterns

    def _analyze_day_of_week_patterns(
        self, state_data: AgentState
    ) -> List[Dict[str, Any]]:
        """Analyze day-of-week patterns from state data"""
        patterns: List[Dict[str, Any]] = []

        try:
            # This would require actual timestamps in the state data
            # For now, return empty patterns
            # In practice, you'd analyze which days the user is most active

            pass

        except Exception as e:
            self.logger.error(f"Error analyzing day-of-week patterns: {e}")

        return patterns

    def _analyze_session_duration_patterns(
        self, state_data: AgentState
    ) -> List[Dict[str, Any]]:
        """Analyze session duration patterns from state data"""
        patterns: List[Dict[str, Any]] = []

        try:
            # This would require actual timestamps in the state data
            # For now, return empty patterns
            # In practice, you'd analyze how long user sessions typically last

            pass

        except Exception as e:
            self.logger.error(f"Error analyzing session duration patterns: {e}")

        return patterns

    def _analyze_interaction_frequency_patterns(
        self, state_data: AgentState
    ) -> List[Dict[str, Any]]:
        """Analyze interaction frequency patterns from state data"""
        patterns: List[Dict[str, Any]] = []

        try:
            # This would require actual timestamps in the state data
            # For now, return empty patterns
            # In practice, you'd analyze how often the user interacts

            pass

        except Exception as e:
            self.logger.error(f"Error analyzing interaction frequency patterns: {e}")

        return patterns

    def _analyze_focus_area_patterns(
        self, focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze focus area patterns"""
        patterns: List[Dict[str, Any]] = []

        try:
            if not focus_areas:
                return patterns

            # Analyze focus area preferences
            focus_count = len(focus_areas)

            if focus_count > 3:
                focus_type = "broad_focus"
                description = "User has broad focus areas"
            elif focus_count > 1:
                focus_type = "moderate_focus"
                description = "User has moderate focus areas"
            else:
                focus_type = "narrow_focus"
                description = "User has narrow focus areas"

            patterns.append(
                {
                    "type": "focus_area",
                    "subtype": focus_type,
                    "confidence": 0.8,
                    "focus_count": focus_count,
                    "focus_areas": focus_areas,
                    "description": description,
                    "tags": ["focus", "area", focus_type, "pattern"],
                }
            )

        except Exception as e:
            self.logger.error(f"Error analyzing focus area patterns: {e}")

        return patterns

    def _convert_pattern_to_memory(
        self, user_id: int, pattern: Dict[str, Any], source_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Convert a recognized pattern to a memory-ready structure.

        Args:
            user_id: User ID for the memory
            pattern: Pattern data from analysis
            source_type: Type of source (conversation, tool_usage, etc.)

        Returns:
            Memory-ready structure or None if conversion fails
        """
        try:
            # Calculate importance score based on pattern confidence and frequency
            base_importance = 3  # Base importance for patterns
            confidence_boost = int(pattern.get("confidence", 0.5) * 3)
            frequency_boost = min(2, pattern.get("frequency", 1) // 2)

            importance_score = min(
                10, base_importance + confidence_boost + frequency_boost
            )

            # Create memory structure
            memory = {
                "user_id": user_id,
                "content": pattern.get("description", "Pattern identified"),
                "tags": pattern.get("tags", []),
                "importance_score": importance_score,
                "context": f"Pattern type: {pattern.get('type')}, Subtype: {pattern.get('subtype')}",
                "enhanced_context": {
                    "memory_type": "pattern",
                    "category": source_type,
                    "confidence_score": pattern.get("confidence", 0.5),
                    "source_type": source_type,
                    "metadata": {
                        "pattern_type": pattern.get("type"),
                        "pattern_subtype": pattern.get("subtype"),
                        "frequency": pattern.get("frequency", 1),
                        "total_count": pattern.get(
                            "total_messages",
                            pattern.get(
                                "total_tools", pattern.get("total_interactions", 1)
                            ),
                        ),
                    },
                },
                "memory_type": "pattern",
                "category": source_type,
                "confidence_score": pattern.get("confidence", 0.5),
                "source_type": source_type,
                "created_by": "pattern_recognition_engine",
            }

            return memory

        except Exception as e:
            self.logger.error(f"Error converting pattern to memory: {e}")
            return None

    async def analyze_state_patterns(self, state: AgentState) -> List[Dict[str, Any]]:
        """
        Analyze patterns from complete agent state data.

        This method coordinates all pattern analysis methods to provide
        comprehensive pattern recognition from state data.

        Args:
            state: Complete agent state object

        Returns:
            List of identified patterns ready for memory creation
        """
        patterns: List[Dict[str, Any]] = []

        try:
            # Analyze conversation patterns
            if hasattr(state, "conversation_history") and state.conversation_history:
                conversation_patterns = await self.analyze_conversation_flow(
                    state.conversation_history
                )
                patterns.extend(conversation_patterns)
                self.logger.info(
                    f"Found {len(conversation_patterns)} conversation patterns"
                )

            # Analyze tool usage patterns
            if hasattr(state, "last_tool_result") and state.last_tool_result:
                # Create a mock tool calls list from the last tool result
                tool_calls = [
                    {
                        "result": str(state.last_tool_result),
                        "timestamp": datetime.now().isoformat(),
                    }
                ]
                tool_patterns = await self.detect_tool_usage_patterns(tool_calls)
                patterns.extend(tool_patterns)
                self.logger.info(f"Found {len(tool_patterns)} tool usage patterns")

            # Analyze user behavior patterns
            if hasattr(state, "user_input") and state.user_input:
                # Convert string input to proper interaction format
                interaction_data = [
                    {
                        "user_input": state.user_input,
                        "timestamp": datetime.now().isoformat(),
                    }
                ]
                behavior_patterns = await self.recognize_user_behavior_patterns(
                    interaction_data
                )
                patterns.extend(behavior_patterns)
                self.logger.info(f"Found {len(behavior_patterns)} behavior patterns")

            # Analyze focus area patterns
            if hasattr(state, "focus") and state.focus:
                focus_areas = (
                    state.focus if isinstance(state.focus, list) else [state.focus]
                )
                focus_patterns = self._analyze_focus_area_patterns(focus_areas)
                patterns.extend(focus_patterns)
                self.logger.info(f"Found {len(focus_patterns)} focus area patterns")

            # Analyze temporal patterns
            temporal_patterns = await self.analyze_temporal_patterns(state)
            patterns.extend(temporal_patterns)
            self.logger.info(f"Found {len(temporal_patterns)} temporal patterns")

            self.logger.info(f"Total patterns identified: {len(patterns)}")

        except Exception as e:
            self.logger.error(f"Error analyzing state patterns: {e}")

        return patterns
