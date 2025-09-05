"""
Long-Term Memory (LTM) storage operations using a dedicated datatable.

This module provides a clean separation between LTM and other data types
(calendar events, notes, etc.) by using a dedicated datatable for insights
and patterns rather than the generic memory_chunks table.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, desc, select, update

from ...config.logging_config import get_logger
from ...database.crud.utils import add_record
from ...database.models.ltm_memory import LTMMemory
from ...database.session import AsyncSessionLocal
from ...utils.tag_utils import normalize_tags, validate_tags

# Enhanced imports for new functionality
try:
    from ...memory.ltm_optimization.context_structures import (
        EnhancedContext,
        MemoryType,
        SourceType,
        create_default_context,
    )

    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False
    EnhancedContext = None
    MemoryType = None
    SourceType = None
    create_default_context = None

# Set up logging
logger = get_logger("ltm_storage")


async def add_ltm_memory(
    user_id: int,
    content: str,
    tags: List[str],
    importance_score: int = 1,
    context: Optional[str] = None,
    # Enhanced parameters (optional for backward compatibility)
    enhanced_context: Optional[Union[EnhancedContext, Dict[str, Any]]] = None,
    memory_type: Optional[Union[str, MemoryType]] = None,
    category: Optional[str] = None,
    confidence_score: float = 1.0,
    source_type: Optional[Union[str, SourceType]] = None,
    source_id: Optional[str] = None,
    created_by: str = "system",
    metadata: Optional[Dict[str, Any]] = None,
    related_memory_ids: Optional[List[int]] = None,
    parent_memory_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Add a new LTM memory entry with enhanced features when available.

    This function provides backward compatibility while enabling enhanced features
    when the enhanced context structures are available.

    Args:
        user_id: User ID
        content: The memory content (insight, pattern, preference)
        tags: List of tags for categorization
        importance_score: Base importance score (1-10)
        context: Legacy context string for backward compatibility
        enhanced_context: Enhanced context object or dict with structured information
        memory_type: Type of memory (preference, insight, pattern, etc.)
        category: High-level category (work, personal, health, etc.)
        confidence_score: Confidence in accuracy (0.0-1.0)
        source_type: Source of the memory (conversation, tool_usage, etc.)
        source_id: ID of the source
        created_by: Who/what created this memory
        metadata: Additional flexible metadata
        related_memory_ids: List of related memory IDs
        parent_memory_id: Parent memory ID if this is a child

    Returns:
        Dict containing the created memory data
    """
    try:
        # Check if enhanced features are available
        if ENHANCED_FEATURES_AVAILABLE and enhanced_context:
            # Use enhanced storage if available
            return await _add_enhanced_ltm_memory(
                user_id=user_id,
                content=content,
                tags=tags,
                importance_score=importance_score,
                context=context,
                enhanced_context=enhanced_context,
                memory_type=memory_type,
                category=category,
                confidence_score=confidence_score,
                source_type=source_type,
                source_id=source_id,
                created_by=created_by,
                metadata=metadata,
                related_memory_ids=related_memory_ids,
                parent_memory_id=parent_memory_id,
            )
        else:
            # Fall back to legacy storage
            return await _add_legacy_ltm_memory(
                user_id=user_id,
                content=content,
                tags=tags,
                importance_score=importance_score,
                context=context,
            )

    except Exception as e:
        logger.error(f"Error creating LTM memory: {e}")
        raise


async def _add_enhanced_ltm_memory(
    user_id: int,
    content: str,
    tags: List[str],
    importance_score: int = 1,
    context: Optional[str] = None,
    enhanced_context: Optional[Union[EnhancedContext, Dict[str, Any]]] = None,
    memory_type: Optional[Union[str, MemoryType]] = None,
    category: Optional[str] = None,
    confidence_score: float = 1.0,
    source_type: Optional[Union[str, SourceType]] = None,
    source_id: Optional[str] = None,
    created_by: str = "system",
    metadata: Optional[Dict[str, Any]] = None,
    related_memory_ids: Optional[List[int]] = None,
    parent_memory_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Enhanced LTM memory creation with full context support"""
    try:
        # Validate required fields
        if not content or not content.strip():
            raise ValueError("Content is required and cannot be empty")

        if not tags or len(tags) == 0:
            raise ValueError("At least one tag is required")

        if not 1 <= importance_score <= 10:
            raise ValueError("Importance score must be between 1 and 10")

        # Ensure memory_type and category have meaningful values
        if not memory_type or memory_type == "":
            memory_type = "insight"  # Default to insight if not specified
            logger.info("Memory type not specified, defaulting to 'insight'")

        if not category or category == "":
            category = "general"  # Default to general if not specified
            logger.info("Category not specified, defaulting to 'general'")

        # Validate confidence score
        if not 0.0 <= confidence_score <= 1.0:
            confidence_score = 1.0  # Default to high confidence if invalid
            logger.warning(
                f"Invalid confidence score {confidence_score}, defaulting to 1.0"
            )

        # Convert dict to EnhancedContext if needed
        if isinstance(enhanced_context, dict):
            enhanced_context = EnhancedContext.from_dict(enhanced_context)
        elif enhanced_context is None:
            enhanced_context = create_default_context()

        # Convert enums to strings if needed
        if isinstance(memory_type, MemoryType):
            memory_type = memory_type.value
        if isinstance(source_type, SourceType):
            source_type = source_type.value

        async with AsyncSessionLocal() as session:
            # user_id is already an integer

            # Normalize and validate tags
            normalized_tags = normalize_tags(tags)
            valid_tags, invalid_tags = validate_tags(
                normalized_tags, enable_smart_fallback=True
            )

            if invalid_tags:
                logger.warning(
                    f"Invalid tags provided: {invalid_tags}. Using only valid tags: {valid_tags}"
                )

            # Use only valid tags, or default to ['general'] if none valid
            final_tags = valid_tags if valid_tags else ["general"]

            # Ensure all tags are lowercase strings (database requirement)
            final_tags = [str(tag).lower().strip() for tag in final_tags if tag]

            # Create LTM memory entry
            memory_data = {
                "user_id": user_id,
                "content": content,
                "tags": final_tags,
                "memory_type": memory_type,
                "category": category,
                "importance_score": importance_score,
                "confidence_score": confidence_score,
                "context": context,
                "context_data": enhanced_context.to_dict()
                if hasattr(enhanced_context, "to_dict")
                else enhanced_context,
                "source_type": source_type,
                "source_id": source_id,
                "created_by": created_by,
                "related_memory_ids": related_memory_ids or [],
                "parent_memory_id": parent_memory_id,
                "memory_metadata": metadata or {},
                "created_at": datetime.utcnow(),
                "last_accessed": datetime.utcnow(),
                "last_modified": datetime.utcnow(),
                "access_count": 0,
                "is_archived": False,
            }

            # Create the memory
            memory = await add_record(session, LTMMemory, memory_data)

            # Calculate and set dynamic importance after creation
            calculated_importance = memory.calculate_dynamic_importance()
            # Use update to set the dynamic importance
            await session.execute(
                update(LTMMemory)
                .where(LTMMemory.id == memory.id)
                .values(dynamic_importance=calculated_importance)
            )

            await session.commit()

            logger.info(
                f"Created enhanced LTM memory {memory.id} for user {user_id} with type: {memory_type}, category: {category}"
            )

            return dict(memory.as_dict())

    except Exception as e:
        logger.error(f"Error creating enhanced LTM memory: {e}")
        raise


async def _add_legacy_ltm_memory(
    user_id: int,
    content: str,
    tags: List[str],
    importance_score: int = 1,
    context: Optional[str] = None,
) -> Dict[str, Any]:
    """Legacy LTM memory creation for backward compatibility"""
    try:
        async with AsyncSessionLocal() as session:
            # user_id is already an integer

            # Normalize and validate tags
            normalized_tags = normalize_tags(tags)
            valid_tags, invalid_tags = validate_tags(
                normalized_tags, enable_smart_fallback=True
            )

            if invalid_tags:
                logger.warning(
                    f"Invalid tags provided: {invalid_tags}. Using only valid tags: {valid_tags}"
                )

            # Use only valid tags, or default to ['general'] if none valid
            final_tags = valid_tags if valid_tags else ["general"]

            # Ensure all tags are lowercase strings (database requirement)
            final_tags = [str(tag).lower().strip() for tag in final_tags if tag]

            # Create LTM memory entry with legacy structure
            memory_data = {
                "user_id": user_id,
                "content": content,
                "tags": final_tags,
                "importance_score": importance_score,
                "context": context,
                "created_at": datetime.utcnow(),
                "last_accessed": datetime.utcnow(),
            }

            memory = await add_record(session, LTMMemory, memory_data)

            logger.info(f"Created legacy LTM memory {memory.id} for user {user_id}")

            return {
                "id": memory.id,
                "content": memory.content,
                "tags": memory.tags,
                "importance_score": memory.importance_score,
                "context": memory.context,
                "created_at": memory.created_at.isoformat(),
                "last_accessed": memory.last_accessed.isoformat(),
            }

    except Exception as e:
        logger.error(f"Error creating legacy LTM memory: {e}")
        raise


async def search_ltm_memories(
    user_id: int, query: str, limit: int = 5, min_importance: int = 1
) -> List[Dict[str, Any]]:
    """
    Search LTM memories by content similarity.

    Args:
        user_id: User ID
        query: Search query
        limit: Maximum number of results
        min_importance: Minimum importance score to include

    Returns:
        List of matching memories
    """
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)

            # Simple text search for now (can be enhanced with embeddings later)
            stmt = (
                select(LTMMemory)
                .where(
                    and_(
                        LTMMemory.user_id == user_id_int,
                        LTMMemory.importance_score >= min_importance,
                        LTMMemory.content.ilike(f"%{query}%"),
                    )
                )
                .order_by(
                    desc(LTMMemory.importance_score), desc(LTMMemory.last_accessed)
                )
                .limit(limit)
            )

            result = await session.execute(stmt)
            memories = result.scalars().all()

            # Update last_accessed for retrieved memories
            for memory in memories:
                memory.last_accessed = datetime.utcnow()

            await session.commit()

            return [
                {
                    "id": memory.id,
                    "content": memory.content,
                    "tags": memory.tags,
                    "importance_score": memory.importance_score,
                    "context": memory.context,
                    "created_at": memory.created_at.isoformat(),
                    "last_accessed": memory.last_accessed.isoformat(),
                }
                for memory in memories
            ]

    except Exception as e:
        logger.error(f"Error searching LTM memories: {e}")
        return []


async def get_relevant_ltm_memories(
    user_id: int, context: str, limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Get LTM memories relevant to the current context.

    Args:
        user_id: User ID
        context: Current conversation context
        limit: Maximum number of results

    Returns:
        List of relevant memories
    """
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)
            logger.info(
                f"Querying LTM memories for user {user_id_int} with context: {context[:100]}..."
            )

            # Get memories with tags that match context keywords
            # This is a simple implementation - can be enhanced with better matching
            context_keywords = context.lower().split()
            logger.info(f"Context keywords extracted: {context_keywords}")

            # Find memories with matching tags
            stmt = (
                select(LTMMemory)
                .where(
                    and_(
                        LTMMemory.user_id == user_id_int,
                        LTMMemory.importance_score >= 3,  # Only important memories
                    )
                )
                .order_by(
                    desc(LTMMemory.importance_score), desc(LTMMemory.last_accessed)
                )
                .limit(limit)
            )

            logger.info(f"Executing query: {stmt}")
            result = await session.execute(stmt)
            memories = result.scalars().all()

            logger.info(f"Found {len(memories)} total memories for user {user_id_int}")

            # Filter by relevance (simple tag matching for now)
            relevant_memories = []
            for memory in memories:
                # Parse tags from memory object
                memory_tags = memory.tags or []

                # Convert to lowercase for matching
                if isinstance(memory_tags, list):
                    memory_tags = [tag.lower() for tag in memory_tags]
                else:
                    memory_tags = []
                logger.debug(f"Memory {memory.id} tags: {memory_tags}")

                if any(keyword in memory_tags for keyword in context_keywords):
                    logger.info(f"Memory {memory.id} matches context keywords")
                    relevant_memories.append(memory)
                else:
                    logger.debug(f"Memory {memory.id} does not match context keywords")

            logger.info(
                f"Found {len(relevant_memories)} relevant memories after filtering"
            )

            # Update last_accessed for retrieved memories
            for memory in relevant_memories:
                memory.last_accessed = datetime.utcnow()

            await session.commit()

            # Convert to dict format
            formatted_memories = []
            for memory in relevant_memories:
                # Parse tags from memory object
                parsed_tags = memory.tags or []

                formatted_memories.append(
                    {
                        "id": memory.id,
                        "content": memory.content,
                        "tags": parsed_tags,
                        "importance_score": memory.importance_score,
                        "context": memory.context,
                        "created_at": memory.created_at.isoformat()
                        if memory.created_at
                        else None,
                        "last_accessed": memory.last_accessed.isoformat()
                        if memory.last_accessed
                        else None,
                    }
                )

            logger.info(f"Returning {len(formatted_memories)} formatted memories")
            return formatted_memories

    except Exception as e:
        logger.error(f"Error in get_relevant_ltm_memories: {e}")
        raise


async def delete_ltm_memory(user_id: int, memory_id: int) -> bool:
    """
    Delete an LTM memory entry.

    Args:
        user_id: User ID
        memory_id: Memory ID to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)

            # Find and delete the memory
            stmt = select(LTMMemory).where(
                and_(LTMMemory.id == memory_id, LTMMemory.user_id == user_id_int)
            )

            result = await session.execute(stmt)
            memory = result.scalar_one_or_none()

            if memory:
                await session.delete(memory)
                await session.commit()
                logger.info(f"Deleted LTM memory {memory_id} for user {user_id}")
                return True
            else:
                logger.warning(f"LTM memory {memory_id} not found for user {user_id}")
                return False

    except Exception as e:
        logger.error(f"Error deleting LTM memory: {e}")
        return False


async def get_ltm_memory_stats(user_id: int) -> Dict[str, Any]:
    """
    Get statistics about LTM memories for a user.

    Args:
        user_id: User ID

    Returns:
        Dictionary with memory statistics
    """
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)

            # Get total count
            total_stmt = select(LTMMemory).where(LTMMemory.user_id == user_id_int)
            total_result = await session.execute(total_stmt)
            total_memories = len(total_result.scalars().all())

            # Get average importance score
            avg_stmt = select(LTMMemory.importance_score).where(
                LTMMemory.user_id == user_id_int
            )
            avg_result = await session.execute(avg_stmt)
            importance_scores = [row[0] for row in avg_result.fetchall()]
            avg_importance = (
                sum(importance_scores) / len(importance_scores)
                if importance_scores
                else 0
            )

            # Get most common tags
            all_tags = []
            tags_stmt = select(LTMMemory.tags).where(LTMMemory.user_id == user_id_int)
            tags_result = await session.execute(tags_stmt)
            for row in tags_result.fetchall():
                all_tags.extend(row[0])

            # Count tag frequency
            tag_counts: dict[str, int] = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Get top 5 tags
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "total_memories": total_memories,
                "average_importance": round(avg_importance, 2),
                "top_tags": top_tags,
                "user_id": user_id,
            }

    except Exception as e:
        logger.error(f"Error getting LTM memory stats: {e}")
        return {
            "total_memories": 0,
            "average_importance": 0,
            "top_tags": [],
            "user_id": user_id,
        }
