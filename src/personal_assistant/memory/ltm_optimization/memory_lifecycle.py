"""
Consolidated Memory Lifecycle Module

This module combines memory lifecycle management and memory consolidation
into a single, manageable interface for LTM memory lifecycle operations.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta

from ...config.logging_config import get_logger
from ...tools.ltm.ltm_storage import add_ltm_memory, delete_ltm_memory
from .config import LTMConfig

logger = get_logger("memory_lifecycle")


# ============================================================================
# MEMORY LIFECYCLE MANAGEMENT
# ============================================================================

class MemoryLifecycleManager:
    """Manages memory lifecycle (aging, archiving, deletion)"""

    def __init__(self, config: LTMConfig = None):
        self.config = config or LTMConfig()

    async def manage_memory_lifecycle(self, user_id: int) -> dict:
        """Manage memory lifecycle for a user"""

        lifecycle_report = {
            "archived": 0,
            "consolidated": 0,
            "deleted": 0,
            "updated": 0
        }

        try:
            # Step 1: Age old memories
            aged_memories = await self._age_old_memories(user_id)
            lifecycle_report["updated"] += len(aged_memories)

            # Step 2: Archive low-importance old memories
            archived_memories = await self._archive_low_importance_memories(user_id)
            lifecycle_report["archived"] += len(archived_memories)

            # Step 3: Remove duplicate memories
            removed_duplicates = await self._remove_duplicate_memories(user_id)
            lifecycle_report["deleted"] += len(removed_duplicates)

            logger.info(
                f"Lifecycle management completed for user {user_id}: {lifecycle_report}")
            return lifecycle_report

        except Exception as e:
            logger.error(
                f"Error in lifecycle management for user {user_id}: {e}")
            return lifecycle_report

    async def _age_old_memories(self, user_id: int) -> List[dict]:
        """Age old memories by reducing importance scores"""

        try:
            # Get memories older than configured days
            old_memories = await self._get_old_memories(user_id, self.config.memory_aging_days)

            aged_memories = []
            for memory in old_memories:
                # Reduce importance score for old memories
                current_importance = memory.get("importance_score", 1)
                new_importance = max(
                    1, current_importance - self.config.importance_reduction_on_aging)

                if new_importance != current_importance:
                    # Update the memory importance (this would need to be implemented)
                    await self._update_memory_importance(memory["id"], new_importance)
                    aged_memories.append(memory)

            logger.info(
                f"Aged {len(aged_memories)} memories for user {user_id}")
            return aged_memories

        except Exception as e:
            logger.error(f"Error aging memories for user {user_id}: {e}")
            return []

    async def _archive_low_importance_memories(self, user_id: int) -> List[dict]:
        """Archive low-importance old memories"""

        try:
            # Get memories older than configured days with importance below threshold
            low_importance_memories = await self._get_low_importance_old_memories(
                user_id,
                self.config.memory_archiving_days,
                self.config.low_importance_threshold
            )

            archived_memories = []
            for memory in low_importance_memories:
                # Archive the memory (this would need to be implemented)
                await self._archive_memory(memory["id"])
                archived_memories.append(memory)

            logger.info(
                f"Archived {len(archived_memories)} low-importance memories for user {user_id}")
            return archived_memories

        except Exception as e:
            logger.error(f"Error archiving memories for user {user_id}: {e}")
            return []

    async def _remove_duplicate_memories(self, user_id: int) -> List[dict]:
        """Remove duplicate memories"""

        try:
            # Get all user memories
            memories = await self._get_all_user_memories(user_id)

            if not memories:
                return []

            # Find duplicates
            duplicates = self._find_duplicate_memories(memories)

            # Remove duplicates
            removed_duplicates = []
            for duplicate_group in duplicates:
                # Keep the most important one, remove the rest
                sorted_group = sorted(duplicate_group, key=lambda x: x.get(
                    "importance_score", 1), reverse=True)
                to_remove = sorted_group[1:]  # Keep the first (most important)

                for memory in to_remove:
                    await delete_ltm_memory(memory["id"])
                    removed_duplicates.append(memory)

            logger.info(
                f"Removed {len(removed_duplicates)} duplicate memories for user {user_id}")
            return removed_duplicates

        except Exception as e:
            logger.error(f"Error removing duplicates for user {user_id}: {e}")
            return []

    def _find_duplicate_memories(self, memories: List[dict]) -> List[List[dict]]:
        """Find groups of duplicate memories"""

        duplicate_groups = []
        processed = set()

        for i, memory in enumerate(memories):
            if i in processed:
                continue

            group = [memory]
            processed.add(i)

            # Find similar memories
            for j, other_memory in enumerate(memories[i+1:], i+1):
                if j in processed:
                    continue

                if self._are_memories_similar(memory, other_memory):
                    group.append(other_memory)
                    processed.add(j)

            if len(group) > 1:
                duplicate_groups.append(group)

        return duplicate_groups

    def _are_memories_similar(self, memory1: dict, memory2: dict) -> bool:
        """Check if two memories are similar enough to be considered duplicates"""

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

    async def _get_old_memories(self, user_id: int, days_old: int) -> List[dict]:
        """Get memories older than specified days"""

        # This would need to be implemented with actual database queries
        # For now, return empty list
        logger.warning(
            "_get_old_memories not implemented - returning empty list")
        return []

    async def _get_low_importance_old_memories(self, user_id: int, days_old: int, importance_threshold: float) -> List[dict]:
        """Get old memories with importance below threshold"""

        # This would need to be implemented with actual database queries
        # For now, return empty list
        logger.warning(
            "_get_low_importance_old_memories not implemented - returning empty list")
        return []

    async def _get_all_user_memories(self, user_id: int) -> List[dict]:
        """Get all memories for a user"""

        # This would need to be implemented with actual database queries
        # For now, return empty list
        logger.warning(
            "_get_all_user_memories not implemented - returning empty list")
        return []

    async def _update_memory_importance(self, memory_id: str, new_importance: float) -> bool:
        """Update memory importance score"""

        # This would need to be implemented with actual database updates
        # For now, just log and return True
        logger.info(
            f"Would update memory {memory_id} importance to {new_importance}")
        return True

    async def _archive_memory(self, memory_id: str) -> bool:
        """Archive a memory"""

        # This would need to be implemented with actual database updates
        # For now, just log and return True
        logger.info(f"Would archive memory {memory_id}")
        return True


# ============================================================================
# MEMORY CONSOLIDATION
# ============================================================================

class MemoryConsolidator:
    """Consolidates related and redundant memories"""

    def __init__(self, config: LTMConfig = None):
        self.config = config or LTMConfig()

    async def consolidate_user_memories(self, user_id: int) -> List[dict]:
        """Consolidate user's memories to reduce redundancy"""

        try:
            # Get all user memories
            memories = await self._get_all_user_memories(user_id)

            if not memories:
                logger.info(f"No memories to consolidate for user {user_id}")
                return []

            # Group memories by similarity
            memory_groups = self._group_similar_memories(memories)

            # Consolidate each group
            consolidated_memories = []
            for group in memory_groups:
                if len(group) >= self.config.min_group_size_for_consolidation:
                    consolidated = await self._consolidate_group(user_id, group)
                    if consolidated:
                        consolidated_memories.append(consolidated)

                        # Mark original memories for deletion
                        await self._mark_memories_for_deletion(user_id, [m["id"] for m in group])

            logger.info(
                f"Consolidated {len(consolidated_memories)} memory groups for user {user_id}")
            return consolidated_memories

        except Exception as e:
            logger.error(
                f"Error consolidating memories for user {user_id}: {e}")
            return []

    def _group_similar_memories(self, memories: List[dict]) -> List[List[dict]]:
        """Group memories by similarity"""

        groups = []
        processed = set()

        for i, memory in enumerate(memories):
            if i in processed:
                continue

            group = [memory]
            processed.add(i)

            # Find similar memories
            for j, other_memory in enumerate(memories[i+1:], i+1):
                if j in processed:
                    continue

                if self._are_memories_similar(memory, other_memory):
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

    async def _consolidate_group(self, user_id: int, memory_group: List[dict]) -> Optional[dict]:
        """Consolidate a group of similar memories"""

        try:
            if not memory_group:
                return None

            # Sort by importance and recency
            sorted_group = sorted(
                memory_group,
                key=lambda x: (
                    x.get("importance_score", 1),
                    x.get("created_at", "")
                ),
                reverse=True
            )

            # Use the most important memory as the base
            base_memory = sorted_group[0]

            # Combine content and tags
            combined_content = self._combine_memory_content(memory_group)
            combined_tags = self._combine_memory_tags(memory_group)

            # Create consolidated memory
            consolidated_data = {
                "user_id": user_id,
                "content": combined_content,
                "tags": combined_tags,
                "metadata": {
                    "type": "consolidated",
                    "original_count": len(memory_group),
                    "consolidated_at": datetime.now(timezone.utc).isoformat(),
                    "original_memory_ids": [m["id"] for m in memory_group]
                }
            }

            # Save consolidated memory
            memory_id = await add_ltm_memory(consolidated_data)
            if memory_id:
                logger.info(
                    f"Created consolidated memory {memory_id} from {len(memory_group)} memories")
                return {"id": memory_id, **consolidated_data}

        except Exception as e:
            logger.error(f"Error consolidating memory group: {e}")

        return None

    def _combine_memory_content(self, memory_group: List[dict]) -> str:
        """Combine content from multiple memories"""

        if not memory_group:
            return ""

        if len(memory_group) == 1:
            return memory_group[0].get("content", "")

        # For multiple memories, combine in a structured way
        content_parts = []
        for i, memory in enumerate(memory_group):
            content = memory.get("content", "")
            if content:
                content_parts.append(f"{i+1}. {content}")

        return "\n\n".join(content_parts)

    def _combine_memory_tags(self, memory_group: List[dict]) -> List[str]:
        """Combine tags from multiple memories"""

        all_tags = set()
        for memory in memory_group:
            tags = memory.get("tags", [])
            all_tags.update(tags)

        return list(all_tags)

    async def _mark_memories_for_deletion(self, user_id: int, memory_ids: List[str]) -> bool:
        """Mark memories for deletion after consolidation"""

        try:
            for memory_id in memory_ids:
                # This would need to be implemented with actual database updates
                # For now, just log the action
                logger.info(f"Would mark memory {memory_id} for deletion")

            return True

        except Exception as e:
            logger.error(f"Error marking memories for deletion: {e}")
            return False

    async def _get_all_user_memories(self, user_id: int) -> List[dict]:
        """Get all memories for a user"""

        # This would need to be implemented with actual database queries
        # For now, return empty list
        logger.warning(
            "_get_all_user_memories not implemented - returning empty list")
        return []


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_lifecycle_manager(config: LTMConfig = None) -> MemoryLifecycleManager:
    """Get memory lifecycle manager with configuration"""
    return MemoryLifecycleManager(config)


def get_consolidator(config: LTMConfig = None) -> MemoryConsolidator:
    """Get memory consolidator with configuration"""
    return MemoryConsolidator(config)


def get_lifecycle_components(config: LTMConfig = None) -> tuple[MemoryLifecycleManager, MemoryConsolidator]:
    """Get both lifecycle manager and consolidator with shared configuration"""
    shared_config = config or LTMConfig()
    return MemoryLifecycleManager(shared_config), MemoryConsolidator(shared_config)
