"""
LTM Learning Manager

This module manages active learning and memory creation from user interactions.
"""

import logging
from typing import List, Dict, Optional
import json

from personal_assistant.memory.ltm_optimization.memory_lifecycle import MemoryLifecycleManager

from ...config.logging_config import get_logger
from ...tools.ltm.ltm_storage import add_ltm_memory
from ...types.state import AgentState
from .config import LTMConfig
from .llm_memory_creator import LLMMemoryCreator


logger = get_logger("learning_manager")


class LTMLearningManager:
    """Manages active learning and memory creation"""

    def __init__(self, config: LTMConfig = None, llm=None):
        self.config = config or LTMConfig()
        self.llm = llm
        self.llm_memory_creator = LLMMemoryCreator(
            config, llm) if llm else None

        # Add lifecycle manager for comprehensive optimization
        self.lifecycle_manager = MemoryLifecycleManager(config)

    async def learn_from_interaction(self, user_id: int, user_input: str, agent_response: str, tool_result: str = None, conversation_context: str = None) -> List[dict]:
        """Learn from user interaction and create relevant memories using LLM"""

        created_memories = []

        if self.llm_memory_creator:
            # Use LLM-based memory creation
            try:
                llm_memories = await self.llm_memory_creator.create_memories_from_interaction(
                    user_id=user_id,
                    user_input=user_input,
                    agent_response=agent_response,
                    tool_result=tool_result,
                    conversation_context=conversation_context
                )
                created_memories.extend(llm_memories)
                logger.info(
                    f"LLM created {len(llm_memories)} memories for user {user_id}")

            except Exception as e:
                logger.error(
                    f"LLM memory creation failed: {e}, falling back to rule-based")
                # Fallback to rule-based if LLM fails
                created_memories.extend(await self._create_rule_based_memories(
                    user_id, user_input, agent_response, tool_result
                ))
        else:
            # Fallback to rule-based approach
            created_memories.extend(await self._create_rule_based_memories(
                user_id, user_input, agent_response, tool_result
            ))

        # Limit total memories per interaction
        if len(created_memories) > self.config.max_memories_per_interaction:
            created_memories = created_memories[:
                                                self.config.max_memories_per_interaction]
            logger.info(
                f"Limited memories to {self.config.max_memories_per_interaction} for user {user_id}")

        logger.info(
            f"Created {len(created_memories)} total memories for user {user_id}")
        return created_memories

    async def _create_rule_based_memories(self, user_id: int, user_input: str, agent_response: str, tool_result: str = None) -> List[dict]:
        """Fallback rule-based memory creation"""

        created_memories = []

        # Create explicit memory if requested
        if await self.should_create_explicit_memory(user_input, agent_response):
            explicit_memory = await self._create_explicit_memory(user_id, user_input, agent_response)
            if explicit_memory:
                created_memories.append(explicit_memory)

        # Create tool usage memory if applicable
        if tool_result:
            tool_memory = await self._create_tool_usage_memory(user_id, user_input, tool_result)
            if tool_memory:
                created_memories.append(tool_memory)

        return created_memories

    async def should_create_memory(self, user_input: str, response: str, tool_result: str = None) -> bool:
        """Determine if interaction warrants memory creation"""

        # Always create memories for explicit requests
        explicit_keywords = self.config.get_memory_creation_keywords()
        if any(keyword in user_input.lower() for keyword in explicit_keywords):
            return True

        # Create memories for successful tool usage
        if tool_result and "Error" not in str(tool_result):
            return True

        # Create memories for personal information
        personal_patterns = self.config.get_personal_pattern_keywords()
        if any(pattern in user_input.lower() for pattern in personal_patterns):
            return True

        # Create memories for learning moments
        learning_patterns = self.config.get_learning_pattern_keywords()
        if any(pattern in response.lower() for pattern in learning_patterns):
            return True

        return False

    async def should_create_explicit_memory(self, user_input: str, agent_response: str) -> bool:
        """Check if user explicitly requested memory creation"""

        explicit_keywords = self.config.get_memory_creation_keywords()
        return any(keyword in user_input.lower() for keyword in explicit_keywords)

    async def _create_explicit_memory(self, user_id: int, user_input: str, agent_response: str) -> Optional[dict]:
        """Create memory for explicit memory requests"""

        try:
            # Determine importance based on keywords
            importance_score = self._calculate_explicit_importance(user_input)

            # Create content
            content = f"User requested to remember: {user_input}"
            if agent_response:
                content += f"\nAgent response: {agent_response}"

            # Determine tags
            tags = self._extract_tags_from_explicit_request(user_input)

            # Determine memory type and category based on content analysis
            memory_type = self._determine_memory_type_from_content(user_input)
            category = self._determine_category_from_content(user_input)

            # Create the memory
            memory = await add_ltm_memory(
                user_id=user_id,
                content=content,
                tags=tags,
                importance_score=importance_score,
                context="Explicit memory request from user",
                memory_type=memory_type,
                category=category,
                confidence_score=0.9,  # High confidence for explicit requests
                source_type="explicit_request",
                source_id="explicit_request",
                created_by="learning_manager"
            )

            logger.info(f"Created explicit memory for user {user_id}")
            return memory

        except Exception as e:
            logger.error(f"Error creating explicit memory: {e}")
            return None

    async def _create_tool_usage_memory(self, user_id: int, user_input: str, tool_result: str) -> Optional[dict]:
        """Create memory for tool usage patterns"""

        try:
            tool_result_str = str(tool_result)

            # Determine if it was successful or failed
            if "Error" in tool_result_str:
                content = f"Tool usage failed: {user_input}"
                tags = ["tool_usage", "error", "learning"]
                importance_score = 7  # Higher importance for failures to learn from
            else:
                content = f"Tool usage successful: {user_input}"
                tags = ["tool_usage", "success", "learning"]
                importance_score = 6

            # Extract tool name if possible
            tool_name = self._extract_tool_name(user_input)
            if tool_name:
                tags.append(tool_name.lower())
                content += f" (Tool: {tool_name})"

            # Determine memory type and category
            memory_type = "tool_usage"
            category = "learning"

            # Create the memory
            memory = await add_ltm_memory(
                user_id=user_id,
                content=content,
                tags=tags,
                importance_score=importance_score,
                context="Tool usage pattern detected",
                memory_type=memory_type,
                category=category,
                confidence_score=0.8,  # Good confidence for tool usage patterns
                source_type="tool_usage",
                source_id=tool_name or "unknown_tool",
                created_by="learning_manager"
            )

            logger.info(f"Created tool usage memory for user {user_id}")
            return memory

        except Exception as e:
            logger.error(f"Error creating tool usage memory: {e}")
            return None

    def _calculate_explicit_importance(self, user_input: str) -> int:
        """Calculate importance score for explicit memory requests"""

        user_input_lower = user_input.lower()

        if any(word in user_input_lower for word in ["urgent", "critical", "important"]):
            return 9
        elif any(word in user_input_lower for word in ["remember", "save", "note"]):
            return 8
        elif any(word in user_input_lower for word in ["keep", "mind", "preference"]):
            return 7
        else:
            return 6

    def _extract_tags_from_explicit_request(self, user_input: str) -> List[str]:
        """Extract relevant tags from explicit memory request"""

        tags = ["explicit_request", "user_important"]

        # Add topic-based tags
        topic_keywords = self.config.topic_preference_keywords
        for topic, keywords in topic_keywords.items():
            if any(keyword in user_input.lower() for keyword in keywords):
                tags.append(topic)

        # Add urgency tags
        if any(word in user_input.lower() for word in ["urgent", "critical", "asap"]):
            tags.append("urgent")

        if any(word in user_input.lower() for word in ["important", "key", "essential"]):
            tags.append("important")

        return tags

    def _extract_tool_name(self, user_input: str) -> Optional[str]:
        """Extract tool name from user input"""

        # Common tool patterns
        tool_patterns = [
            r"(\w+)_tool",
            r"(\w+) tool",
            r"use (\w+)",
            r"with (\w+)",
            r"via (\w+)"
        ]

        import re
        for pattern in tool_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                tool_name = match.group(1)
                # Filter out common words that aren't tool names
                if tool_name not in ["the", "a", "an", "this", "that", "my"]:
                    return tool_name

        return None

    def _determine_memory_type_from_content(self, content: str) -> str:
        """Determine memory type based on content analysis"""
        content_lower = content.lower()

        # Explicit memory requests
        if any(word in content_lower for word in ["remember", "save", "note", "keep"]):
            return "explicit_request"

        # Preferences
        if any(word in content_lower for word in ["prefer", "like", "want", "need", "favorite"]):
            return "preference"

        # Goals
        if any(word in content_lower for word in ["goal", "target", "aim", "objective", "plan"]):
            return "goal"

        # Habits
        if any(word in content_lower for word in ["habit", "routine", "always", "usually", "typically"]):
            return "habit"

        # Insights
        if any(word in content_lower for word in ["learned", "discovered", "found", "realized", "understood"]):
            return "insight"

        # Default to insight for general information
        return "insight"

    def _determine_category_from_content(self, content: str) -> str:
        """Determine category based on content analysis"""
        content_lower = content.lower()

        # Work-related
        if any(word in content_lower for word in ["work", "job", "career", "project", "meeting", "deadline"]):
            return "work"

        # Health-related
        if any(word in content_lower for word in ["health", "exercise", "diet", "sleep", "wellness", "medical"]):
            return "health"

        # Personal
        if any(word in content_lower for word in ["family", "friend", "relationship", "personal", "home"]):
            return "personal"

        # Finance
        if any(word in content_lower for word in ["money", "finance", "budget", "expense", "investment", "saving"]):
            return "finance"

        # Education
        if any(word in content_lower for word in ["learn", "study", "education", "course", "skill", "knowledge"]):
            return "education"

        # Entertainment
        if any(word in content_lower for word in ["movie", "music", "game", "hobby", "entertainment", "fun"]):
            return "entertainment"

        # Travel
        if any(word in content_lower for word in ["travel", "trip", "vacation", "destination", "flight", "hotel"]):
            return "travel"

        # Default to general
        return "general"

    async def optimize_after_interaction(self, user_id: int, user_input: str,
                                         response: str, agent_state: AgentState) -> dict:
        """
        Perform comprehensive LTM optimization after user interaction.

        This method coordinates both learning from the interaction and lifecycle management.

        Args:
            user_id: User ID
            user_input: User's input message
            response: Agent's response
            agent_state: Current agent state

        Returns:
            dict: Optimization report with created memories and lifecycle changes
        """
        try:
            logger.info(
                f"Performing comprehensive LTM optimization for user {user_id}")

            optimization_report = {
                "created_memories": [],
                "lifecycle_changes": {},
                "learning_insights": [],
                "errors": []
            }

            # Step 1: Learn from interaction
            try:
                tool_result = getattr(agent_state, 'last_tool_result', None)
                created_memories = await self.learn_from_interaction(
                    user_id=user_id,
                    user_input=user_input,
                    agent_response=response,
                    tool_result=tool_result
                )
                optimization_report["created_memories"] = created_memories

                if created_memories:
                    logger.info(
                        f"Created {len(created_memories)} LTM memories from interaction")
                else:
                    logger.info(
                        "No new LTM memories created from this interaction")

            except Exception as e:
                error_msg = f"Error in learning from interaction: {e}"
                logger.error(error_msg)
                optimization_report["errors"].append(error_msg)

            # Step 2: Lifecycle management (if lifecycle manager is available)
            try:
                if hasattr(self, 'lifecycle_manager') and self.lifecycle_manager:
                    lifecycle_report = await self.lifecycle_manager.manage_memory_lifecycle(user_id)
                    if lifecycle_report:
                        optimization_report["lifecycle_changes"] = lifecycle_report
                        logger.info(
                            f"LTM lifecycle management completed: {lifecycle_report}")

                    # Get memory statistics
                    memory_stats = await self.lifecycle_manager.get_memory_statistics(user_id)
                    if memory_stats:
                        optimization_report["lifecycle_changes"]["statistics"] = memory_stats
                        logger.info(f"LTM statistics: {memory_stats['total_memories']} total memories, "
                                    f"avg importance: {memory_stats['average_importance']}")
                else:
                    logger.debug(
                        "No lifecycle manager available for lifecycle optimization")

            except Exception as e:
                error_msg = f"Error in lifecycle management: {e}"
                logger.warning(error_msg)
                optimization_report["errors"].append(error_msg)

            # Step 3: Generate learning insights
            try:
                insights = await self._generate_learning_insights(user_id, user_input, response, created_memories)
                optimization_report["learning_insights"] = insights

            except Exception as e:
                error_msg = f"Error generating learning insights: {e}"
                logger.warning(error_msg)
                optimization_report["errors"].append(error_msg)

            logger.info(f"LTM optimization completed for user {user_id}")
            return optimization_report

        except Exception as e:
            error_msg = f"Critical error in LTM optimization: {e}"
            logger.error(error_msg)
            return {
                "created_memories": [],
                "lifecycle_changes": {},
                "learning_insights": [],
                "errors": [error_msg]
            }

    async def _generate_learning_insights(self, user_id: int, user_input: str,
                                          response: str, created_memories: List[dict]) -> List[str]:
        """Generate insights about what was learned from the interaction"""
        insights = []

        try:
            # Analyze user input patterns
            if any(word in user_input.lower() for word in ["prefer", "like", "want", "need"]):
                insights.append("User preference detected")

            # Analyze tool usage
            if created_memories:
                tool_memories = [m for m in created_memories if m.get(
                    "memory_type") == "tool_usage"]
                if tool_memories:
                    insights.append(
                        f"Tool usage patterns learned: {len(tool_memories)} insights")

            # Analyze communication style
            if len(user_input.split()) > 20:
                insights.append("User prefers detailed communication")
            elif len(user_input.split()) < 5:
                insights.append("User prefers concise communication")

        except Exception as e:
            logger.warning(f"Error generating learning insights: {e}")

        return insights

    def is_memory_request(self, user_input: str) -> bool:
        """Check if user explicitly requested memory creation"""

        memory_keywords = [
            "remember this", "save this", "note this", "keep this in mind",
            "add to memory", "store this", "memorize", "remember",
            "important", "urgent", "critical", "preference", "habit", "pattern"
        ]

        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in memory_keywords)

    async def handle_explicit_memory_request(self, user_id: int, user_input: str, response: str, conversation_context: str) -> List[dict]:
        """Handle explicit memory creation requests using LLM memory creator"""

        try:
            logger.info(f"Handling explicit memory request for user {user_id}")

            created_memories = await self.learn_from_interaction(
                user_id=user_id,
                user_input=user_input,
                agent_response=response,
                tool_result=None,
                conversation_context=conversation_context
            )

            if created_memories:
                logger.info(
                    f"LLM created {len(created_memories)} memories from explicit request")
            else:
                logger.info("No memories created from explicit request")

            return created_memories

        except Exception as e:
            logger.warning(f"Error handling explicit memory request: {e}")
            return []
