"""
LTM Learning Manager

This module manages active learning and memory creation from user interactions.
"""

from typing import Any, Dict, List, Optional

from personal_assistant.memory.ltm_optimization.memory_lifecycle import (
    EnhancedMemoryLifecycleManager,
)

from ...config.logging_config import get_logger
from ...tools.ltm.ltm_storage import add_ltm_memory
from ...types.state import AgentState
from .config import EnhancedLTMConfig, LTMConfig
from .llm_memory_creator import LLMMemoryCreator
from .pattern_recognition import PatternRecognitionEngine

logger = get_logger("learning_manager")


class LTMLearningManager:
    """Manages active learning and memory creation"""

    def __init__(self, config: LTMConfig = None, llm=None):
        self.config = config or LTMConfig()
        self.llm = llm
        self.llm_memory_creator = LLMMemoryCreator(config, llm) if llm else None

        # Add lifecycle manager for comprehensive optimization
        self.lifecycle_manager = EnhancedMemoryLifecycleManager(config)

        # Add pattern recognition engine for state integration
        if isinstance(config, EnhancedLTMConfig) and config.enable_state_integration:
            self.pattern_engine = PatternRecognitionEngine(config)
        else:
            self.pattern_engine = None

    async def learn_from_interaction(
        self,
        user_id: int,
        user_input: str,
        agent_response: str,
        tool_result: str = None,
        conversation_context: str = None,
    ) -> List[dict]:
        """Learn from user interaction and create relevant memories using LLM"""

        created_memories = []

        if self.llm_memory_creator:
            # Use LLM-based memory creation
            try:
                llm_memories = (
                    await self.llm_memory_creator.create_memories_from_interaction(
                        user_id=user_id,
                        user_input=user_input,
                        agent_response=agent_response,
                        tool_result=tool_result,
                        conversation_context=conversation_context,
                    )
                )
                created_memories.extend(llm_memories)
                logger.info(
                    f"LLM created {len(llm_memories)} memories for user {user_id}"
                )

            except Exception as e:
                logger.error(
                    f"LLM memory creation failed: {e}, falling back to rule-based"
                )
                # Fallback to rule-based if LLM fails
                created_memories.extend(
                    await self._create_rule_based_memories(
                        user_id, user_input, agent_response, tool_result
                    )
                )
        else:
            # Fallback to rule-based approach
            created_memories.extend(
                await self._create_rule_based_memories(
                    user_id, user_input, agent_response, tool_result
                )
            )

        # Limit total memories per interaction
        if len(created_memories) > self.config.max_memories_per_interaction:
            created_memories = created_memories[
                : self.config.max_memories_per_interaction
            ]
            logger.info(
                f"Limited memories to {self.config.max_memories_per_interaction} for user {user_id}"
            )

        logger.info(
            f"Created {len(created_memories)} total memories for user {user_id}"
        )
        return created_memories

    async def learn_from_state_data(
        self, user_id: int, state_data: AgentState
    ) -> List[dict]:
        """
        Learn from state management data using pattern recognition.

        This method integrates with the completed state management system
        to create memories from conversation patterns, tool usage patterns,
        and user behavior patterns.

        Args:
            user_id: User ID for memory creation
            state_data: Complete agent state for analysis

        Returns:
            List of created memories from state data
        """
        if not self.pattern_engine:
            logger.warning(
                "Pattern recognition engine not available for state integration"
            )
            return []

        created_memories = []

        try:
            # Use pattern recognition engine to analyze state data
            state_memories = await self.pattern_engine.convert_state_to_memories(
                user_id, state_data
            )

            # Store memories in LTM storage
            for memory_data in state_memories:
                try:
                    # Extract memory fields
                    memory = await add_ltm_memory(
                        user_id=memory_data["user_id"],
                        content=memory_data["content"],
                        tags=memory_data["tags"],
                        importance_score=memory_data["importance_score"],
                        context=memory_data["context"],
                        enhanced_context=memory_data.get("enhanced_context"),
                        memory_type=memory_data.get("memory_type"),
                        category=memory_data.get("category"),
                        confidence_score=memory_data.get("confidence_score"),
                        source_type=memory_data.get("source_type"),
                        created_by=memory_data.get("created_by", "state_integration"),
                    )

                    if memory:
                        created_memories.append(memory)
                        logger.info(
                            f"Created state-based memory: {memory_data.get('content', '')[:50]}..."
                        )

                except Exception as e:
                    logger.error(f"Failed to store state-based memory: {e}")
                    continue

            logger.info(
                f"Created {len(created_memories)} memories from state data for user {user_id}"
            )

        except Exception as e:
            logger.error(f"Error learning from state data: {e}")

        return created_memories

    async def learn_from_interaction_with_state(
        self,
        user_id: int,
        user_input: str,
        agent_response: str,
        state_data: AgentState,
        tool_result: str = None,
        conversation_context: str = None,
    ) -> List[dict]:
        """
        Learn from user interaction AND state data for comprehensive memory creation.

        This method combines traditional interaction learning with state-based
        pattern recognition for maximum memory creation effectiveness.

        Args:
            user_id: User ID for memory creation
            user_input: Current user input
            agent_response: Current agent response
            state_data: Complete agent state for analysis
            tool_result: Tool execution result if applicable
            conversation_context: Additional conversation context

        Returns:
            List of all created memories (interaction + state-based)
        """
        all_memories = []

        try:
            # Learn from current interaction
            interaction_memories = await self.learn_from_interaction(
                user_id, user_input, agent_response, tool_result, conversation_context
            )
            all_memories.extend(interaction_memories)

            # Learn from state data (if enabled)
            if (
                isinstance(self.config, EnhancedLTMConfig)
                and self.config.enable_state_integration
            ):
                state_memories = await self.learn_from_state_data(user_id, state_data)
                all_memories.extend(state_memories)

                logger.info(
                    f"Combined learning: {len(interaction_memories)} interaction + {len(state_memories)} state memories"
                )
            else:
                logger.info(
                    f"State integration disabled, created {len(interaction_memories)} interaction memories"
                )

            # Apply memory limits
            max_memories = getattr(self.config, "max_memories_per_interaction", 5)
            if len(all_memories) > max_memories:
                # Prioritize memories by importance and confidence
                all_memories.sort(
                    key=lambda m: (
                        m.get("importance_score", 1),
                        m.get("confidence_score", 0.5),
                    ),
                    reverse=True,
                )
                all_memories = all_memories[:max_memories]
                logger.info(
                    f"Limited total memories to {max_memories} for user {user_id}"
                )

        except Exception as e:
            logger.error(f"Error in combined learning: {e}")

        return all_memories

    async def _create_rule_based_memories(
        self,
        user_id: int,
        user_input: str,
        agent_response: str,
        tool_result: str = None,
    ) -> List[dict]:
        """Fallback rule-based memory creation"""

        created_memories = []

        # Create explicit memory if requested
        if await self.should_create_explicit_memory(user_input, agent_response):
            explicit_memory = await self._create_explicit_memory(
                user_id, user_input, agent_response
            )
            if explicit_memory:
                created_memories.append(explicit_memory)

        # Create tool usage memory if applicable
        if tool_result:
            tool_memory = await self._create_tool_usage_memory(
                user_id, user_input, tool_result
            )
            if tool_memory:
                created_memories.append(tool_memory)

        return created_memories

    async def should_create_memory(
        self, user_input: str, response: str, tool_result: str = None
    ) -> bool:
        """Determine if interaction warrants memory creation"""

        # Always create memories for explicit requests
        if await self.should_create_explicit_memory(user_input, response):
            return True

        # Check if tool usage occurred
        if tool_result:
            return True

        # Check for important keywords
        important_keywords = self.config.get_memory_creation_keywords()
        user_input_lower = user_input.lower()

        for keyword in important_keywords:
            if keyword.lower() in user_input_lower:
                return True

        # Check for personal pattern keywords
        personal_keywords = self.config.get_personal_pattern_keywords()
        for keyword in personal_keywords:
            if keyword.lower() in user_input_lower:
                return True

        # Check for learning pattern keywords
        learning_keywords = self.config.get_learning_pattern_keywords()
        for keyword in learning_keywords:
            if keyword.lower() in user_input_lower:
                return True

        return False

    async def should_create_explicit_memory(
        self, user_input: str, response: str
    ) -> bool:
        """Check if user explicitly requested memory creation"""

        explicit_indicators = [
            "remember this",
            "save this",
            "note this",
            "keep this in mind",
            "important",
            "urgent",
            "critical",
        ]

        user_input_lower = user_input.lower()
        for indicator in explicit_indicators:
            if indicator in user_input_lower:
                return True

        return False

    async def _create_explicit_memory(
        self, user_id: int, user_input: str, response: str
    ) -> Optional[dict]:
        """Create memory for explicit memory requests"""

        try:
            # Extract key information
            content = f"User explicitly requested to remember: {user_input}"
            tags = ["explicit", "user_request", "important"]

            # Determine importance based on keywords
            importance_score = 8  # High importance for explicit requests

            # Create memory
            memory = await add_ltm_memory(
                user_id=user_id,
                content=content,
                tags=tags,
                importance_score=importance_score,
                context=f"User input: {user_input}\nAgent response: {response}",
                memory_type="explicit_request",
                category="user_preference",
                confidence_score=0.9,
                source_type="conversation",
                created_by="explicit_request",
            )

            return memory

        except Exception as e:
            logger.error(f"Failed to create explicit memory: {e}")
            return None

    async def _create_tool_usage_memory(
        self, user_id: int, user_input: str, tool_result: str
    ) -> Optional[dict]:
        """Create memory for tool usage"""

        try:
            # Extract tool information from result
            content = f"Tool usage: {user_input}"
            tags = ["tool_usage", "automation"]

            # Determine importance based on tool success
            if "success" in tool_result.lower() or "created" in tool_result.lower():
                importance_score = 6
                tags.append("successful")
            elif "error" in tool_result.lower() or "failed" in tool_result.lower():
                importance_score = 7  # Higher importance for failures to learn from
                tags.append("failed")
            else:
                importance_score = 5
                tags.append("completed")

            # Create memory
            memory = await add_ltm_memory(
                user_id=user_id,
                content=content,
                tags=tags,
                importance_score=importance_score,
                context=f"User input: {user_input}\nTool result: {tool_result}",
                memory_type="tool_usage",
                category="automation",
                confidence_score=0.8,
                source_type="tool_execution",
                created_by="tool_usage_tracker",
            )

            return memory

        except Exception as e:
            logger.error(f"Failed to create tool usage memory: {e}")
            return None

    async def get_memory_creation_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics about memory creation for a user"""

        try:
            # This would typically query the database for statistics
            # For now, return basic structure
            stats = {
                "total_memories": 0,
                "memories_this_session": 0,
                "memory_types": {},
                "importance_distribution": {},
                "recent_memories": [],
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get memory creation stats: {e}")
            return {}

    async def optimize_memory_creation(self, user_id: int) -> Dict[str, Any]:
        """Optimize memory creation parameters based on user patterns"""

        try:
            # This would analyze user patterns and adjust thresholds
            # For now, return basic structure
            optimization = {
                "adjusted_thresholds": {},
                "recommended_changes": [],
                "user_patterns": {},
            }

            return optimization

        except Exception as e:
            logger.error(f"Failed to optimize memory creation: {e}")
            return {}

    async def optimize_after_interaction(
        self, user_id: int, user_input: str, response: str, updated_state: AgentState
    ) -> Dict[str, Any]:
        """
        Perform comprehensive LTM optimization after an interaction.

        This method coordinates memory creation, pattern recognition,
        and lifecycle management to optimize the LTM system.

        Args:
            user_id: User ID for optimization
            user_input: User's input text
            response: Agent's response
            updated_state: Current agent state after interaction

        Returns:
            Dictionary containing optimization results
        """
        try:
            optimization_results = {
                "memories_created": 0,
                "patterns_detected": 0,
                "lifecycle_optimizations": 0,
                "state_integration_success": False,
            }

            # Create memories from the interaction
            if self.llm_memory_creator:
                try:
                    memories = await self.learn_from_interaction(
                        user_id=user_id,
                        user_input=user_input,
                        agent_response=response,
                        tool_result=str(updated_state.last_tool_result)
                        if updated_state.last_tool_result
                        else None,
                        conversation_context=f"State focus: {updated_state.focus}",
                    )
                    optimization_results["memories_created"] = len(memories)
                    logger.info(
                        f"Created {len(memories)} memories during optimization for user {user_id}"
                    )
                except Exception as e:
                    logger.warning(f"Memory creation during optimization failed: {e}")

            # Analyze patterns from state data if pattern engine is available
            if self.pattern_engine and updated_state:
                try:
                    patterns = await self.pattern_engine.analyze_state_patterns(
                        updated_state
                    )
                    optimization_results["patterns_detected"] = (
                        len(patterns) if patterns else 0
                    )
                    logger.info(
                        f"Detected {optimization_results['patterns_detected']} patterns during optimization for user {user_id}"
                    )
                except Exception as e:
                    logger.warning(f"Pattern analysis during optimization failed: {e}")

            # Perform lifecycle optimizations
            if self.lifecycle_manager:
                try:
                    lifecycle_results = (
                        await self.lifecycle_manager.optimize_user_memories(user_id)
                    )
                    optimization_results[
                        "lifecycle_optimizations"
                    ] = lifecycle_results.get("optimizations_applied", 0)
                    logger.info(
                        f"Applied {optimization_results['lifecycle_optimizations']} lifecycle optimizations for user {user_id}"
                    )
                except Exception as e:
                    logger.warning(f"Lifecycle optimization failed: {e}")

            # Mark state integration as successful if we processed state data
            if updated_state:
                optimization_results["state_integration_success"] = True

            logger.info(
                f"LTM optimization completed for user {user_id}: {optimization_results}"
            )
            return optimization_results

        except Exception as e:
            logger.error(f"LTM optimization failed for user {user_id}: {e}")
            return {
                "error": str(e),
                "memories_created": 0,
                "patterns_detected": 0,
                "lifecycle_optimizations": 0,
                "state_integration_success": False,
            }

    def is_memory_request(self, user_input: str) -> bool:
        """
        Check if user input contains an explicit memory request.

        Args:
            user_input: User's input text

        Returns:
            True if input contains memory request keywords
        """
        if not user_input:
            return False

        # Convert to lowercase for case-insensitive matching
        input_lower = user_input.lower()

        # Keywords that indicate explicit memory requests
        memory_keywords = [
            "remember this",
            "save this",
            "memorize",
            "keep in mind",
            "don't forget",
            "note this",
            "store this",
            "remember that",
            "save that",
        ]

        return any(keyword in input_lower for keyword in memory_keywords)

    async def handle_explicit_memory_request(
        self, user_id: int, user_input: str, response: str, context: str
    ) -> Optional[dict]:
        """
        Handle explicit memory requests from users.

        Args:
            user_id: User ID for memory creation
            user_input: User's input containing memory request
            response: Agent's response to the request
            context: Additional context for the memory

        Returns:
            Created memory object or None if failed
        """
        try:
            if not self.is_memory_request(user_input):
                return None

            logger.info(f"Processing explicit memory request for user {user_id}")

            # Extract the content to remember (remove request keywords)
            content = user_input
            for keyword in [
                "remember this",
                "save this",
                "memorize",
                "keep in mind",
                "don't forget",
                "note this",
                "store this",
                "remember that",
                "save that",
            ]:
                content = content.replace(keyword, "").strip()

            # If content is empty after removing keywords, use the full input
            if not content:
                content = user_input

            # Create high-priority memory for explicit requests
            memory = await add_ltm_memory(
                user_id=user_id,
                content=content,
                tags=["explicit_request", "high_priority", "user_directed"],
                importance_score=9,  # Very high importance for explicit requests
                context=f"User explicitly requested to remember: {user_input}\nAgent response: {response}\nContext: {context}",
                memory_type="explicit_request",
                category="user_preference",
                confidence_score=0.95,  # High confidence for explicit requests
                source_type="explicit_request",
                created_by="explicit_memory_handler",
            )

            logger.info(
                f"Created explicit memory for user {user_id}: {memory.get('id', 'unknown')}"
            )
            return memory

        except Exception as e:
            logger.error(
                f"Failed to handle explicit memory request for user {user_id}: {e}"
            )
            return None
