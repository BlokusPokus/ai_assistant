"""
Enhanced Memory Lifecycle Module with State Integration

This module provides comprehensive memory lifecycle management with state integration,
including smart consolidation, usage-based aging, intelligent archiving, and
storage optimization coordinated with state management data.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ...config.logging_config import get_logger
from ...tools.ltm.ltm_storage import add_ltm_memory
from ...types.state import AgentState
from .config import EnhancedLTMConfig, LTMConfig

logger = get_logger("memory_lifecycle")


# ============================================================================
# ENHANCED MEMORY LIFECYCLE MANAGEMENT WITH STATE INTEGRATION
# ============================================================================


class EnhancedMemoryLifecycleManager:
    """Enhanced memory lifecycle manager with state integration"""

    def __init__(self, config: Optional[EnhancedLTMConfig] = None):
        self.config = config or EnhancedLTMConfig()
        self.logger = get_logger("enhanced_memory_lifecycle")

    async def manage_memory_lifecycle_with_state(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> Dict[str, Any]:
        """
        Manage memory lifecycle with state context integration

        Args:
            user_id: User ID for memory management
            state_context: Current agent state for context-aware lifecycle decisions

        Returns:
            Dictionary with lifecycle management results
        """

        lifecycle_report: Dict[str, Any] = {
            "archived": 0,
            "consolidated": 0,
            "deleted": 0,
            "updated": 0,
            "state_integrated": 0,
            "performance_metrics": {},
        }

        try:
            # Step 1: State-aware memory aging
            aged_memories: List[Dict[str, Any]] = await self._age_memories_with_state_context(
                user_id, state_context
            )
            lifecycle_report["updated"] += len(aged_memories)

            # Step 2: State-coordinated consolidation
            consolidated_memories: List[Dict[str, Any]] = await self._consolidate_memories_with_state(
                user_id, state_context
            )
            lifecycle_report["consolidated"] += len(consolidated_memories)

            # Step 3: Intelligent archiving based on state patterns
            archived_memories: List[Dict[str, Any]] = await self._archive_memories_intelligently(
                user_id, state_context
            )
            lifecycle_report["archived"] += len(archived_memories)

            # Step 4: Storage optimization with state coordination
            storage_optimization: Dict[str, Any] = await self._optimize_storage_with_state(
                user_id, state_context
            )
            lifecycle_report["performance_metrics"][
                "storage_optimization"
            ] = storage_optimization

            # Step 5: State-LTM lifecycle coordination
            state_coordination: int = await self._coordinate_state_ltm_lifecycle(
                user_id, state_context
            )
            lifecycle_report["state_integrated"] += state_coordination

            self.logger.info(
                f"Enhanced lifecycle management completed for user {user_id}: {lifecycle_report}"
            )
            return lifecycle_report

        except Exception as e:
            self.logger.error(
                f"Error in enhanced lifecycle management for user {user_id}: {e}"
            )
            return lifecycle_report

    async def _age_memories_with_state_context(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> List[Dict[str, Any]]:
        """Age memories with state context awareness"""

        try:
            # Get memories that need aging
            memories_to_age = await self._get_memories_for_aging(user_id, state_context)

            aged_memories = []
            for memory in memories_to_age:
                # Calculate aging based on state context
                aging_factor = self._calculate_state_aware_aging_factor(
                    memory, state_context
                )

                # Apply aging
                new_importance = self._apply_aging_to_memory(memory, aging_factor)
                if new_importance != memory.get("importance_score", 1):
                    await self._update_memory_importance(memory["id"], new_importance)
                    memory["importance_score"] = new_importance
                    aged_memories.append(memory)

            self.logger.info(
                f"State-aware aging applied to {len(aged_memories)} memories for user {user_id}"
            )
            return aged_memories

        except Exception as e:
            self.logger.error(f"Error in state-aware aging for user {user_id}: {e}")
            return []

    async def _consolidate_memories_with_state(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> List[Dict[str, Any]]:
        """Consolidate memories with state context coordination"""

        try:
            # Get memories for consolidation
            memories = await self._get_memories_for_consolidation(
                user_id, state_context
            )

            if not memories:
                return []

            # Group memories by state-aware similarity
            memory_groups = self._group_memories_by_state_aware_similarity(
                memories, state_context
            )

            # Consolidate each group
            consolidated_memories = []
            for group in memory_groups:
                if len(group) >= self.config.min_group_size_for_consolidation:
                    consolidated = await self._consolidate_group_with_state(
                        user_id, group, state_context
                    )
                    if consolidated:
                        consolidated_memories.append(consolidated)

                        # Mark original memories for deletion
                        await self._mark_memories_for_deletion(
                            user_id, [m["id"] for m in group]
                        )

            self.logger.info(
                f"State-aware consolidation completed: {len(consolidated_memories)} groups for user {user_id}"
            )
            return consolidated_memories

        except Exception as e:
            self.logger.error(
                f"Error in state-aware consolidation for user {user_id}: {e}"
            )
            return []

    async def _archive_memories_intelligently(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> List[Dict[str, Any]]:
        """Intelligently archive memories based on state patterns"""

        try:
            # Get memories for potential archiving
            candidate_memories = await self._get_memories_for_archiving(
                user_id, state_context
            )

            archived_memories = []
            for memory in candidate_memories:
                # Calculate archiving score based on state context
                archiving_score = self._calculate_state_aware_archiving_score(
                    memory, state_context
                )

                if archiving_score >= self.config.memory_archiving_threshold:
                    await self._archive_memory_with_state_context(
                        memory["id"], state_context
                    )
                    archived_memories.append(memory)

            self.logger.info(
                f"Intelligent archiving completed: {len(archived_memories)} memories for user {user_id}"
            )
            return archived_memories

        except Exception as e:
            self.logger.error(f"Error in intelligent archiving for user {user_id}: {e}")
            return []

    async def _optimize_storage_with_state(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> Dict[str, Any]:
        """Optimize storage with state context coordination"""

        try:
            optimization_results = {
                "compression_applied": 0,
                "storage_reduced_bytes": 0,
                "indexes_optimized": 0,
                "cache_cleaned": 0,
            }

            # Apply compression to old, low-importance memories
            compression_result = await self._apply_storage_compression(
                user_id, state_context
            )
            optimization_results["compression_applied"] = compression_result.get(
                "compressed", 0
            )
            optimization_results["storage_reduced_bytes"] = compression_result.get(
                "bytes_saved", 0
            )

            # Optimize database indexes
            index_optimization = await self._optimize_database_indexes(user_id)
            optimization_results["indexes_optimized"] = index_optimization.get(
                "optimized", 0
            )

            # Clean up cache
            cache_cleanup = await self._cleanup_cache(user_id)
            optimization_results["cache_cleaned"] = cache_cleanup.get("cleaned", 0)

            self.logger.info(
                f"Storage optimization completed for user {user_id}: {optimization_results}"
            )
            return optimization_results

        except Exception as e:
            self.logger.error(f"Error in storage optimization for user {user_id}: {e}")
            return {}

    async def _coordinate_state_ltm_lifecycle(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> int:
        """Coordinate LTM lifecycle with state management"""

        try:
            coordination_count = 0

            if not state_context:
                return coordination_count

            # Coordinate memory lifecycle with state focus changes
            if hasattr(state_context, "focus") and state_context.focus:
                focus_coordination = await self._coordinate_with_focus_changes(
                    user_id, state_context.focus
                )
                coordination_count += focus_coordination

            # Coordinate with tool usage patterns
            if (
                hasattr(state_context, "last_tool_result")
                and state_context.last_tool_result
            ):
                tool_coordination = await self._coordinate_with_tool_patterns(
                    user_id, state_context.last_tool_result
                )
                coordination_count += tool_coordination

            # Coordinate with conversation patterns
            if (
                hasattr(state_context, "conversation_history")
                and state_context.conversation_history
            ):
                conversation_coordination = (
                    await self._coordinate_with_conversation_patterns(
                        user_id, state_context.conversation_history
                    )
                )
                coordination_count += conversation_coordination

            self.logger.info(
                f"State-LTM lifecycle coordination completed: {coordination_count} actions for user {user_id}"
            )
            return coordination_count

        except Exception as e:
            self.logger.error(
                f"Error in state-LTM coordination for user {user_id}: {e}"
            )
            return 0

    def _calculate_state_aware_aging_factor(
        self, memory: Dict[str, Any], state_context: Optional["AgentState"] = None
    ) -> float:
        """Calculate aging factor based on state context"""

        base_aging_factor = 1.0

        if not state_context:
            return base_aging_factor

        # Adjust aging based on current focus
        if hasattr(state_context, "focus") and state_context.focus:
            focus_areas = (
                state_context.focus
                if isinstance(state_context.focus, list)
                else [state_context.focus]
            )
            memory_tags = set(memory.get("tags", []))
            memory_content = memory.get("content", "").lower()

            # Reduce aging for memories relevant to current focus
            for focus in focus_areas:
                if focus.lower() in memory_content or any(
                    focus.lower() in tag.lower() for tag in memory_tags
                ):
                    base_aging_factor *= 0.7  # Age slower
                    break

        # Adjust aging based on tool usage relevance
        if (
            hasattr(state_context, "last_tool_result")
            and state_context.last_tool_result
        ):
            str(state_context.last_tool_result).lower()
            memory_content = memory.get("content", "").lower()

            if any(
                tool_word in memory_content
                for tool_word in ["tool", "function", "api", "automation"]
            ):
                base_aging_factor *= 0.8  # Age slower for tool-related memories

        return max(0.3, base_aging_factor)  # Minimum aging factor

    def _apply_aging_to_memory(self, memory: dict, aging_factor: float) -> float:
        """Apply aging factor to memory importance"""

        current_importance = memory.get("importance_score", 1)
        importance_reduction = self.config.importance_reduction_on_aging * aging_factor

        new_importance = max(1, current_importance - importance_reduction)
        return new_importance

    def _group_memories_by_state_aware_similarity(
        self, memories: List[Dict[str, Any]], state_context: Optional["AgentState"] = None
    ) -> List[List[dict]]:
        """Group memories by state-aware similarity"""

        groups = []
        processed = set()

        for i, memory in enumerate(memories):
            if i in processed:
                continue

            group = [memory]
            processed.add(i)

            # Find similar memories with state context consideration
            for j, other_memory in enumerate(memories[i + 1 :], i + 1):
                if j in processed:
                    continue

                if self._are_memories_similar_with_state(
                    memory, other_memory, state_context
                ):
                    group.append(other_memory)
                    processed.add(j)

            groups.append(group)

        return groups

    def _are_memories_similar(self, memory1: dict, memory2: dict) -> bool:
        """Check if two memories are similar enough to consolidate"""

        # Check tag overlap
        tags1 = set(memory1.get("tags", []))
        tags2 = set(memory2.get("tags", []))

        if tags1 and tags2:
            tag_overlap = len(tags1 & tags2) / max(len(tags1 | tags2), 1)
            if tag_overlap > self.config.tag_similarity_threshold:
                return True

        # Check content similarity (simple keyword matching for now)
        content1 = memory1.get("content", "").lower()
        content2 = memory2.get("content", "").lower()

        words1 = set(content1.split())
        words2 = set(content2.split())

        if words1 and words2:
            word_overlap = len(words1 & words2) / max(len(words1 | words2), 1)
            if word_overlap > self.config.content_similarity_threshold:
                return True

        return False

    def _are_memories_similar_with_state(
        self, memory1: Dict[str, Any], memory2: Dict[str, Any], state_context: Optional["AgentState"] = None
    ) -> bool:
        """Check if memories are similar with state context consideration"""

        # Base similarity check
        base_similarity = self._are_memories_similar(memory1, memory2)

        if not base_similarity or not state_context:
            return base_similarity

        # Enhanced similarity with state context
        state_similarity = self._calculate_state_context_similarity(
            memory1, memory2, state_context
        )

        # Combine base and state similarity
        combined_similarity = (base_similarity * 0.7) + (state_similarity * 0.3)

        return combined_similarity > self.config.consolidation_similarity_threshold

    def _calculate_state_context_similarity(
        self, memory1: dict, memory2: dict, state_context: "AgentState"
    ) -> float:
        """Calculate similarity based on state context"""

        similarity_score = 0.0

        # Focus area similarity
        if hasattr(state_context, "focus") and state_context.focus:
            focus_areas = (
                state_context.focus
                if isinstance(state_context.focus, list)
                else [state_context.focus]
            )

            memory1_focus_match = any(
                focus.lower() in memory1.get("content", "").lower()
                or any(focus.lower() in tag.lower() for tag in memory1.get("tags", []))
                for focus in focus_areas
            )

            memory2_focus_match = any(
                focus.lower() in memory2.get("content", "").lower()
                or any(focus.lower() in tag.lower() for tag in memory2.get("tags", []))
                for focus in focus_areas
            )

            if memory1_focus_match and memory2_focus_match:
                similarity_score += 0.5

        # Tool usage similarity
        if (
            hasattr(state_context, "last_tool_result")
            and state_context.last_tool_result
        ):
            str(state_context.last_tool_result).lower()

            memory1_tool_match = any(
                tool_word in memory1.get("content", "").lower()
                for tool_word in ["tool", "function", "api", "automation"]
            )

            memory2_tool_match = any(
                tool_word in memory2.get("content", "").lower()
                for tool_word in ["tool", "function", "api", "automation"]
            )

            if memory1_tool_match and memory2_tool_match:
                similarity_score += 0.3

        return min(1.0, similarity_score)

    def _calculate_state_aware_archiving_score(
        self, memory: Dict[str, Any], state_context: Optional["AgentState"] = None
    ) -> float:
        """Calculate archiving score based on state context"""

        base_score = 0.0

        # Base archiving factors
        importance = memory.get("importance_score", 1)
        age_days = self._calculate_memory_age_days(memory)

        # Lower importance = higher archiving score
        base_score += (10 - importance) / 10.0 * 0.4

        # Older memories = higher archiving score
        if age_days > 365:
            base_score += 0.4
        elif age_days > 180:
            base_score += 0.3
        elif age_days > 90:
            base_score += 0.2
        elif age_days > 30:
            base_score += 0.1

        # State context adjustments
        if state_context:
            # Reduce archiving score for memories relevant to current focus
            if hasattr(state_context, "focus") and state_context.focus:
                focus_areas = (
                    state_context.focus
                    if isinstance(state_context.focus, list)
                    else [state_context.focus]
                )
                memory_tags = set(memory.get("tags", []))
                memory_content = memory.get("content", "").lower()

                for focus in focus_areas:
                    if focus.lower() in memory_content or any(
                        focus.lower() in tag.lower() for tag in memory_tags
                    ):
                        base_score *= 0.6  # Less likely to archive
                        break

            # Reduce archiving score for tool-related memories if tools are being used
            if (
                hasattr(state_context, "last_tool_result")
                and state_context.last_tool_result
            ):
                memory_content = memory.get("content", "").lower()
                if any(
                    tool_word in memory_content
                    for tool_word in ["tool", "function", "api", "automation"]
                ):
                    base_score *= 0.7  # Less likely to archive

        return min(1.0, base_score)

    def _calculate_memory_age_days(self, memory: dict) -> int:
        """Calculate memory age in days"""

        try:
            created_at = memory.get("created_at")
            if not created_at:
                return 0

            if isinstance(created_at, str):
                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            else:
                created_dt = created_at

            age_delta = datetime.now(timezone.utc) - created_dt
            return age_delta.days

        except Exception:
            return 0

    async def _consolidate_group_with_state(
        self, user_id: int, memory_group: List[Dict[str, Any]], state_context: Optional["AgentState"] = None
    ) -> Optional[Dict[str, Any]]:
        """Consolidate a group of memories with state context"""

        try:
            if not memory_group:
                return None

            # Sort by importance, recency, and state relevance
            sorted_group = sorted(
                memory_group,
                key=lambda x: (
                    x.get("importance_score", 1),
                    self._calculate_state_relevance_score(x, state_context),
                    x.get("created_at", ""),
                ),
                reverse=True,
            )

            # Use the most relevant memory as the base
            sorted_group[0]

            # Combine content and tags with state context consideration
            combined_content = self._combine_memory_content_with_state(
                memory_group, state_context
            )
            combined_tags = self._combine_memory_tags_with_state(
                memory_group, state_context
            )

            # Create consolidated memory with state metadata
            consolidated_data = {
                "user_id": user_id,
                "content": combined_content,
                "tags": combined_tags,
                "importance_score": max(
                    m.get("importance_score", 1) for m in memory_group
                ),
                "metadata": {
                    "type": "consolidated",
                    "original_count": len(memory_group),
                    "consolidated_at": datetime.now(timezone.utc).isoformat(),
                    "original_memory_ids": [m["id"] for m in memory_group],
                    "state_context": {
                        "focus": state_context.focus
                        if state_context and hasattr(state_context, "focus")
                        else None,
                        "tool_usage": bool(
                            state_context
                            and hasattr(state_context, "last_tool_result")
                            and state_context.last_tool_result
                        ),
                    }
                    if state_context
                    else None,
                },
            }

            # Save consolidated memory
            memory_id = await add_ltm_memory(
                user_id=user_id,
                content=consolidated_data["content"],
                tags=consolidated_data["tags"],
                importance_score=consolidated_data.get("importance_score", 1),
                context=consolidated_data.get("context"),
                memory_type=consolidated_data.get("memory_type"),
                category=consolidated_data.get("category"),
                confidence_score=consolidated_data.get("confidence_score", 1.0),
                source_type=consolidated_data.get("source_type"),
                source_id=consolidated_data.get("source_id"),
                created_by=consolidated_data.get("created_by", "system"),
                metadata=consolidated_data.get("metadata")
            )
            if memory_id:
                self.logger.info(
                    f"Created state-aware consolidated memory {memory_id} from {len(memory_group)} memories"
                )
                return {"id": memory_id, **consolidated_data}

        except Exception as e:
            self.logger.error(f"Error consolidating memory group with state: {e}")

        return None

    def _calculate_state_relevance_score(
        self, memory: Dict[str, Any], state_context: Optional["AgentState"] = None
    ) -> float:
        """Calculate state relevance score for a memory"""

        if not state_context:
            return 0.0

        score = 0.0

        # Focus area relevance
        if hasattr(state_context, "focus") and state_context.focus:
            focus_areas = (
                state_context.focus
                if isinstance(state_context.focus, list)
                else [state_context.focus]
            )
            memory_tags = set(memory.get("tags", []))
            memory_content = memory.get("content", "").lower()

            for focus in focus_areas:
                if focus.lower() in memory_content:
                    score += 0.4
                elif any(focus.lower() in tag.lower() for tag in memory_tags):
                    score += 0.3

        # Tool usage relevance
        if (
            hasattr(state_context, "last_tool_result")
            and state_context.last_tool_result
        ):
            memory_content = memory.get("content", "").lower()
            if any(
                tool_word in memory_content
                for tool_word in ["tool", "function", "api", "automation"]
            ):
                score += 0.3

        return min(1.0, score)

    def _combine_memory_content_with_state(
        self, memory_group: List[Dict[str, Any]], state_context: Optional["AgentState"] = None
    ) -> str:
        """Combine memory content with state context consideration"""

        if not memory_group:
            return ""

        if len(memory_group) == 1:
            return memory_group[0].get("content", "")

        # For multiple memories, combine with state-aware prioritization
        content_parts = []

        # Sort by state relevance for better content ordering
        sorted_group = sorted(
            memory_group,
            key=lambda x: self._calculate_state_relevance_score(x, state_context),
            reverse=True,
        )

        for i, memory in enumerate(sorted_group):
            content = memory.get("content", "")
            if content:
                # Add state context indicator if relevant
                state_indicator = ""
                if (
                    state_context
                    and self._calculate_state_relevance_score(memory, state_context)
                    > 0.5
                ):
                    state_indicator = " [State-Relevant]"

                content_parts.append(f"{i+1}. {content}{state_indicator}")

        return "\n\n".join(content_parts)

    def _combine_memory_tags_with_state(
        self, memory_group: List[Dict[str, Any]], state_context: Optional["AgentState"] = None
    ) -> List[str]:
        """Combine memory tags with state context consideration"""

        all_tags = set()
        state_relevant_tags = set()

        for memory in memory_group:
            tags = memory.get("tags", [])
            all_tags.update(tags)

            # Identify state-relevant tags
            if (
                state_context
                and self._calculate_state_relevance_score(memory, state_context) > 0.5
            ):
                state_relevant_tags.update(tags)

        # Prioritize state-relevant tags
        combined_tags = list(state_relevant_tags) + [
            tag for tag in all_tags if tag not in state_relevant_tags
        ]

        return combined_tags

    async def _coordinate_with_focus_changes(
        self, user_id: int, focus_areas: List[str]
    ) -> int:
        """Coordinate memory lifecycle with focus area changes"""

        try:
            coordination_count = 0

            # Boost importance of memories related to new focus areas
            focus_memories = await self._get_memories_by_focus_areas(
                user_id, focus_areas
            )

            for memory in focus_memories:
                current_importance = memory.get("importance_score", 1)
                new_importance = min(10, current_importance + 1)

                if new_importance != current_importance:
                    await self._update_memory_importance(memory["id"], new_importance)
                    coordination_count += 1

            self.logger.info(
                f"Focus change coordination: {coordination_count} memories updated for user {user_id}"
            )
            return coordination_count

        except Exception as e:
            self.logger.error(f"Error in focus change coordination: {e}")
            return 0

    async def _coordinate_with_tool_patterns(
        self, user_id: int, tool_result: Any
    ) -> int:
        """Coordinate memory lifecycle with tool usage patterns"""

        try:
            coordination_count = 0

            # Boost importance of tool-related memories
            tool_memories = await self._get_tool_related_memories(user_id)

            for memory in tool_memories:
                current_importance = memory.get("importance_score", 1)
                new_importance = min(10, current_importance + 0.5)

                if new_importance != current_importance:
                    await self._update_memory_importance(memory["id"], new_importance)
                    coordination_count += 1

            self.logger.info(
                f"Tool pattern coordination: {coordination_count} memories updated for user {user_id}"
            )
            return coordination_count

        except Exception as e:
            self.logger.error(f"Error in tool pattern coordination: {e}")
            return 0

    async def _coordinate_with_conversation_patterns(
        self, user_id: int, conversation_history: List[dict]
    ) -> int:
        """Coordinate memory lifecycle with conversation patterns"""

        try:
            coordination_count = 0

            # Analyze conversation patterns and adjust memory lifecycle accordingly
            if len(conversation_history) > 10:
                # Long conversations might indicate complex topics - preserve related memories
                recent_topics = self._extract_recent_conversation_topics(
                    conversation_history[-10:]
                )

                for topic in recent_topics:
                    topic_memories = await self._get_memories_by_topic(user_id, topic)

                    for memory in topic_memories:
                        current_importance = memory.get("importance_score", 1)
                        new_importance = min(10, current_importance + 0.3)

                        if new_importance != current_importance:
                            await self._update_memory_importance(
                                memory["id"], new_importance
                            )
                            coordination_count += 1

            self.logger.info(
                f"Conversation pattern coordination: {coordination_count} memories updated for user {user_id}"
            )
            return coordination_count

        except Exception as e:
            self.logger.error(f"Error in conversation pattern coordination: {e}")
            return 0

    def _extract_recent_conversation_topics(
        self, recent_conversations: List[dict]
    ) -> List[str]:
        """Extract topics from recent conversations"""

        topics = set()

        for conversation in recent_conversations:
            # Handle different content formats
            content_raw = conversation.get("content", "")

            # Convert to string if it's not already
            if isinstance(content_raw, dict):
                # If content is a dict, try to extract text from common fields
                content = str(
                    content_raw.get(
                        "text",
                        content_raw.get("message", content_raw.get("content", "")),
                    )
                )
            else:
                content = str(content_raw)

            content = content.lower()

            # Simple topic extraction based on keywords
            if any(word in content for word in ["work", "project", "meeting"]):
                topics.add("work")
            if any(word in content for word in ["health", "exercise", "diet"]):
                topics.add("health")
            if any(word in content for word in ["family", "home", "personal"]):
                topics.add("personal")
            if any(word in content for word in ["finance", "money", "budget"]):
                topics.add("finance")

        return list(topics)

    # Placeholder methods for database operations
    async def _get_memories_for_aging(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> List[Dict[str, Any]]:
        """Get memories that need aging"""
        # This would need to be implemented with actual database queries
        self.logger.warning(
            "_get_memories_for_aging not implemented - returning empty list"
        )
        return []

    async def _get_memories_for_consolidation(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> List[Dict[str, Any]]:
        """Get memories for consolidation"""
        # This would need to be implemented with actual database queries
        self.logger.warning(
            "_get_memories_for_consolidation not implemented - returning empty list"
        )
        return []

    async def _get_memories_for_archiving(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> List[Dict[str, Any]]:
        """Get memories for archiving"""
        # This would need to be implemented with actual database queries
        self.logger.warning(
            "_get_memories_for_archiving not implemented - returning empty list"
        )
        return []

    async def _apply_storage_compression(
        self, user_id: int, state_context: Optional["AgentState"] = None
    ) -> Dict[str, Any]:
        """Apply storage compression"""
        # This would need to be implemented with actual compression logic
        self.logger.warning(
            "_apply_storage_compression not implemented - returning placeholder"
        )
        return {"compressed": 0, "bytes_saved": 0}

    async def _optimize_database_indexes(self, user_id: int) -> Dict[str, Any]:
        """Optimize database indexes"""
        # This would need to be implemented with actual database optimization
        self.logger.warning(
            "_optimize_database_indexes not implemented - returning placeholder"
        )
        return {"optimized": 0}

    async def _cleanup_cache(self, user_id: int) -> Dict[str, Any]:
        """Clean up cache"""
        # This would need to be implemented with actual cache cleanup
        self.logger.warning("_cleanup_cache not implemented - returning placeholder")
        return {"cleaned": 0}

    async def _get_memories_by_focus_areas(
        self, user_id: int, focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Get memories by focus areas"""
        # This would need to be implemented with actual database queries
        self.logger.warning(
            "_get_memories_by_focus_areas not implemented - returning empty list"
        )
        return []

    async def _get_tool_related_memories(self, user_id: int) -> List[Dict[str, Any]]:
        """Get tool-related memories"""
        # This would need to be implemented with actual database queries
        self.logger.warning(
            "_get_tool_related_memories not implemented - returning empty list"
        )
        return []

    async def _get_memories_by_topic(self, user_id: int, topic: str) -> List[Dict[str, Any]]:
        """Get memories by topic"""
        # This would need to be implemented with actual database queries
        self.logger.warning(
            "_get_memories_by_topic not implemented - returning empty list"
        )
        return []

    async def _archive_memory_with_state_context(
        self, memory_id: str, state_context: Optional["AgentState"] = None
    ) -> bool:
        """Archive memory with state context"""
        # This would need to be implemented with actual database updates
        self.logger.info(f"Would archive memory {memory_id} with state context")
        return True

    async def _update_memory_importance(
        self, memory_id: str, new_importance: float
    ) -> bool:
        """Update memory importance score"""
        # This would need to be implemented with actual database updates
        self.logger.info(
            f"Would update memory {memory_id} importance to {new_importance}"
        )
        return True

    async def _mark_memories_for_deletion(
        self, user_id: int, memory_ids: List[str]
    ) -> bool:
        """Mark memories for deletion"""
        # This would need to be implemented with actual database updates
        self.logger.info(f"Would mark {len(memory_ids)} memories for deletion")
        return True

    async def optimize_user_memories(self, user_id: int) -> Dict[str, Any]:
        """
        Optimize user memories using the enhanced lifecycle management.

        This method provides a simplified interface for the learning manager
        to trigger memory optimization.

        Args:
            user_id: User ID for memory optimization

        Returns:
            Dictionary with optimization results
        """
        try:
            # Use the enhanced lifecycle management without state context
            # (state context will be provided by the calling method)
            results = await self.manage_memory_lifecycle_with_state(user_id, None)

            self.logger.info(
                f"Memory optimization completed for user {user_id}: {results}"
            )
            return results

        except Exception as e:
            self.logger.error(f"Error optimizing user memories for user {user_id}: {e}")
            return {
                "archived": 0,
                "consolidated": 0,
                "deleted": 0,
                "updated": 0,
                "state_integrated": 0,
                "performance_metrics": {},
            }


# ============================================================================
# LEGACY CLASSES (Maintained for backward compatibility)
# ============================================================================


class MemoryLifecycleManager:
    """Legacy memory lifecycle manager (maintained for backward compatibility)"""

    def __init__(self, config: Optional[LTMConfig] = None):
        self.config = config or LTMConfig()
        self.enhanced_manager = EnhancedMemoryLifecycleManager(EnhancedLTMConfig())

    async def manage_memory_lifecycle(self, user_id: int) -> dict:
        """Legacy method - delegates to enhanced manager"""
        return await self.enhanced_manager.manage_memory_lifecycle_with_state(
            user_id, None
        )


class MemoryConsolidator:
    """Legacy memory consolidator (maintained for backward compatibility)"""

    def __init__(self, config: Optional[LTMConfig] = None):
        self.config = config or LTMConfig()
        self.enhanced_manager = EnhancedMemoryLifecycleManager(EnhancedLTMConfig())

    async def consolidate_user_memories(self, user_id: int) -> List[Dict[str, Any]]:
        """Legacy method - delegates to enhanced manager"""
        return await self.enhanced_manager._consolidate_memories_with_state(
            user_id, None
        )

    def _are_memories_similar(self, memory1: dict, memory2: dict) -> bool:
        """Legacy similarity check"""
        # Check tag overlap
        tags1 = set(memory1.get("tags", []))
        tags2 = set(memory2.get("tags", []))

        if tags1 and tags2:
            tag_overlap = len(tags1 & tags2) / max(len(tags1 | tags2), 1)
            if tag_overlap > self.config.tag_similarity_threshold:
                return True

        # Check content similarity
        content1 = memory1.get("content", "").lower()
        content2 = memory2.get("content", "").lower()

        words1 = set(content1.split())
        words2 = set(content2.split())

        if words1 and words2:
            word_overlap = len(words1 & words2) / max(len(words1 | words2), 1)
            if word_overlap > self.config.content_similarity_threshold:
                return True

        return False


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def get_enhanced_lifecycle_manager(
    config: Optional[EnhancedLTMConfig] = None,
) -> EnhancedMemoryLifecycleManager:
    """Get enhanced memory lifecycle manager with configuration"""
    return EnhancedMemoryLifecycleManager(config)


def get_lifecycle_manager(config: Optional[LTMConfig] = None) -> MemoryLifecycleManager:
    """Get legacy memory lifecycle manager with configuration"""
    return MemoryLifecycleManager(config)


def get_consolidator(config: Optional[LTMConfig] = None) -> MemoryConsolidator:
    """Get legacy memory consolidator with configuration"""
    return MemoryConsolidator(config)


def get_lifecycle_components(
    config: Optional[LTMConfig] = None, 
) -> tuple[MemoryLifecycleManager, MemoryConsolidator]:
    """Get both legacy lifecycle manager and consolidator with shared configuration"""
    shared_config = config or LTMConfig()
    return MemoryLifecycleManager(shared_config), MemoryConsolidator(shared_config)
