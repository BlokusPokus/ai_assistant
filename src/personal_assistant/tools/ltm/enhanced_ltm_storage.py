"""
Enhanced LTM Storage Operations

This module provides enhanced storage operations for the improved LTM system,
including support for structured context, relationships, and advanced metadata.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, desc, select, func, text, or_
from sqlalchemy.orm import Session

from ...config.logging_config import get_logger
from ...database.crud.utils import add_record, get_by_field
from ...database.models.ltm_memory import (
    LTMMemory, LTMContext, LTMMemoryRelationship,
    LTMMemoryAccess, LTMMemoryTag
)
from ...database.session import AsyncSessionLocal
from ...utils.tag_utils import normalize_tags, validate_tags
from ...memory.ltm_optimization.context_structures import (
    EnhancedContext, MemoryMetadata, create_default_context,
    SourceType, MemoryType
)

logger = get_logger("enhanced_ltm_storage")


async def add_enhanced_ltm_memory(
    user_id: str,
    content: str,
    tags: List[str],
    importance_score: int = 1,
    context: Optional[str] = None,
    enhanced_context: Optional[EnhancedContext] = None,
    memory_type: Optional[Union[str, MemoryType]] = None,
    category: Optional[str] = None,
    confidence_score: float = 1.0,
    source_type: Optional[Union[str, SourceType]] = None,
    source_id: Optional[str] = None,
    created_by: str = "system",
    metadata: Optional[Dict[str, Any]] = None,
    related_memory_ids: Optional[List[int]] = None,
    parent_memory_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Add a new enhanced LTM memory entry with full context support.

    Args:
        user_id: User ID
        content: The memory content (insight, pattern, preference)
        tags: List of tags for categorization
        importance_score: Base importance score (1-10)
        context: Legacy context string for backward compatibility
        enhanced_context: Enhanced context object with structured information
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
        async with AsyncSessionLocal() as session:
            # Convert user_id to int
            user_id_int = int(user_id)

            # Normalize and validate tags
            normalized_tags = normalize_tags(tags)
            valid_tags, invalid_tags = validate_tags(normalized_tags)

            if invalid_tags:
                logger.warning(
                    f"Invalid tags provided: {invalid_tags}. Using only valid tags: {valid_tags}")

            # Use only valid tags, or empty list if none valid
            final_tags = valid_tags if valid_tags else []

            # Convert enums to strings if needed
            if isinstance(memory_type, MemoryType):
                memory_type = memory_type.value
            if isinstance(source_type, SourceType):
                source_type = source_type.value

            # Create default enhanced context if none provided
            if enhanced_context is None:
                enhanced_context = create_default_context()

            # Create LTM memory entry
            memory_data = {
                "user_id": user_id_int,
                "content": content,
                "tags": final_tags,
                "memory_type": memory_type or "insight",
                "category": category or "general",
                "importance_score": importance_score,
                "confidence_score": confidence_score,
                "context": context,
                "context_data": enhanced_context.to_dict(),
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
                "is_archived": False
            }

            # Create the memory
            memory = await add_record(session, LTMMemory, memory_data)

            # Calculate dynamic importance
            memory.dynamic_importance = memory.calculate_dynamic_importance()

            # Create enhanced context entries
            await _create_context_entries(session, memory.id, enhanced_context)

            # Create tag entries
            await _create_tag_entries(session, memory.id, final_tags)

            # Create relationships if specified
            if related_memory_ids:
                await _create_memory_relationships(session, memory.id, related_memory_ids)

            await session.commit()

            logger.info(
                f"Created enhanced LTM memory {memory.id} for user {user_id} with type: {memory_type}")

            return memory.as_dict()

    except Exception as e:
        logger.error(f"Error creating enhanced LTM memory: {e}")
        raise


async def _create_context_entries(session: AsyncSessionLocal, memory_id: int, enhanced_context: EnhancedContext):
    """Create context entries for a memory"""
    try:
        # Create temporal context
        if enhanced_context.temporal:
            await add_record(session, LTMContext, {
                "memory_id": memory_id,
                "context_type": "temporal",
                "context_key": "timestamp",
                "context_value": enhanced_context.temporal.timestamp.isoformat(),
                "confidence": 1.0
            })

        # Create spatial context
        if enhanced_context.spatial:
            if enhanced_context.spatial.location:
                await add_record(session, LTMContext, {
                    "memory_id": memory_id,
                    "context_type": "spatial",
                    "context_key": "location",
                    "context_value": enhanced_context.spatial.location,
                    "confidence": 1.0
                })

        # Create social context
        if enhanced_context.social:
            if enhanced_context.social.participants:
                await add_record(session, LTMContext, {
                    "memory_id": memory_id,
                    "context_type": "social",
                    "context_key": "participants",
                    "context_value": json.dumps(enhanced_context.social.participants),
                    "confidence": 1.0
                })

        # Create environmental context
        if enhanced_context.environmental:
            if enhanced_context.environmental.weather:
                await add_record(session, LTMContext, {
                    "memory_id": memory_id,
                    "context_type": "environmental",
                    "context_key": "weather",
                    "context_value": enhanced_context.environmental.weather,
                    "confidence": 1.0
                })

        # Create technical context
        if enhanced_context.technical:
            if enhanced_context.technical.tool_name:
                await add_record(session, LTMContext, {
                    "memory_id": memory_id,
                    "context_type": "technical",
                    "context_key": "tool_name",
                    "context_value": enhanced_context.technical.tool_name,
                    "confidence": 1.0
                })

        # Create custom contexts
        for custom_context in enhanced_context.custom_contexts:
            await add_record(session, LTMContext, {
                "memory_id": memory_id,
                "context_type": "custom",
                "context_key": custom_context.context_type,
                "context_value": json.dumps(custom_context.context_data),
                "confidence": 1.0
            })

    except Exception as e:
        logger.error(f"Error creating context entries: {e}")
        raise


async def _create_tag_entries(session: AsyncSessionLocal, memory_id: int, tags: List[str]):
    """Create tag entries for a memory"""
    try:
        for tag in tags:
            await add_record(session, LTMMemoryTag, {
                "memory_id": memory_id,
                "tag_name": tag,
                "tag_category": "general",
                "tag_importance": 1.0,
                "tag_confidence": 1.0,
                "usage_count": 1,
                "first_used": datetime.utcnow(),
                "last_used": datetime.utcnow()
            })
    except Exception as e:
        logger.error(f"Error creating tag entries: {e}")
        raise


async def _create_memory_relationships(session: AsyncSessionLocal, memory_id: int, related_ids: List[int]):
    """Create memory relationships"""
    try:
        for related_id in related_ids:
            await add_record(session, LTMMemoryRelationship, {
                "source_memory_id": memory_id,
                "target_memory_id": related_id,
                "relationship_type": "related",
                "strength": 0.5,
                "description": "Automatically detected relationship"
            })
    except Exception as e:
        logger.error(f"Error creating memory relationships: {e}")
        raise


async def get_enhanced_ltm_memory(memory_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    """Get an enhanced LTM memory with full context information"""
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)

            # Get the memory
            stmt = select(LTMMemory).where(
                and_(
                    LTMMemory.id == memory_id,
                    LTMMemory.user_id == user_id_int
                )
            )
            result = await session.execute(stmt)
            memory = result.scalar_one_or_none()

            if not memory:
                return None

            # Update access statistics
            memory.update_access_stats("Direct retrieval")
            await session.commit()

            # Get enhanced context
            context_stmt = select(LTMContext).where(
                LTMContext.memory_id == memory_id)
            context_result = await session.execute(context_stmt)
            contexts = context_result.scalars().all()

            # Get relationships
            rel_stmt = select(LTMMemoryRelationship).where(
                or_(
                    LTMMemoryRelationship.source_memory_id == memory_id,
                    LTMMemoryRelationship.target_memory_id == memory_id
                )
            )
            rel_result = await session.execute(rel_stmt)
            relationships = rel_result.scalars().all()

            # Build enhanced response
            memory_dict = memory.as_dict()
            memory_dict["enhanced_context"] = _build_enhanced_context_from_db(
                contexts)
            memory_dict["relationships"] = [
                {
                    "id": rel.id,
                    "type": rel.relationship_type,
                    "strength": rel.strength,
                    "description": rel.description,
                    "related_memory_id": rel.target_memory_id if rel.source_memory_id == memory_id else rel.source_memory_id
                }
                for rel in relationships
            ]

            return memory_dict

    except Exception as e:
        logger.error(f"Error getting enhanced LTM memory: {e}")
        return None


def _build_enhanced_context_from_db(contexts: List[LTMContext]) -> Dict[str, Any]:
    """Build enhanced context from database context entries"""
    enhanced_context = {}

    for context in contexts:
        if context.context_type not in enhanced_context:
            enhanced_context[context.context_type] = {}

        enhanced_context[context.context_type][context.context_key] = context.context_value

    return enhanced_context


async def search_enhanced_ltm_memories(
    user_id: str,
    query: str,
    limit: int = 5,
    min_importance: int = 1,
    memory_type: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    source_type: Optional[str] = None,
    include_context: bool = True
) -> List[Dict[str, Any]]:
    """
    Enhanced search for LTM memories with filtering and context support.
    """
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)

            # Build base query
            stmt = select(LTMMemory).where(
                and_(
                    LTMMemory.user_id == user_id_int,
                    LTMMemory.importance_score >= min_importance,
                    LTMMemory.is_archived == False
                )
            )

            # Add filters
            if memory_type:
                stmt = stmt.where(LTMMemory.memory_type == memory_type)
            if category:
                stmt = stmt.where(LTMMemory.category == category)
            if source_type:
                stmt = stmt.where(LTMMemory.source_type == source_type)

            # Add text search
            if query:
                stmt = stmt.where(LTMMemory.content.ilike(f"%{query}%"))

            # Add tag filtering
            if tags:
                # This is a simplified tag search - could be enhanced with proper JSON operations
                for tag in tags:
                    stmt = stmt.where(LTMMemory.tags.contains([tag]))

            # Order by dynamic importance and recency
            stmt = stmt.order_by(
                desc(LTMMemory.dynamic_importance),
                desc(LTMMemory.last_accessed)
            ).limit(limit)

            result = await session.execute(stmt)
            memories = result.scalars().all()

            # Update access statistics and build response
            enhanced_memories = []
            for memory in memories:
                memory.update_access_stats(f"Search query: {query}")
                memory_dict = memory.as_dict()

                if include_context:
                    # Get context information
                    context_stmt = select(LTMContext).where(
                        LTMContext.memory_id == memory.id)
                    context_result = await session.execute(context_stmt)
                    contexts = context_result.scalars().all()
                    memory_dict["enhanced_context"] = _build_enhanced_context_from_db(
                        contexts)

                enhanced_memories.append(memory_dict)

            await session.commit()
            return enhanced_memories

    except Exception as e:
        logger.error(f"Error in enhanced LTM search: {e}")
        return []


async def get_memory_relationships(memory_id: int, user_id: str) -> List[Dict[str, Any]]:
    """Get all relationships for a specific memory"""
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)

            # Verify memory belongs to user
            memory_stmt = select(LTMMemory).where(
                and_(
                    LTMMemory.id == memory_id,
                    LTMMemory.user_id == user_id_int
                )
            )
            memory_result = await session.execute(memory_stmt)
            if not memory_result.scalar_one_or_none():
                return []

            # Get relationships
            rel_stmt = select(LTMMemoryRelationship).where(
                or_(
                    LTMMemoryRelationship.source_memory_id == memory_id,
                    LTMMemoryRelationship.target_memory_id == memory_id
                )
            )
            rel_result = await session.execute(rel_stmt)
            relationships = rel_result.scalars().all()

            # Build response
            relationship_data = []
            for rel in relationships:
                related_memory_id = rel.target_memory_id if rel.source_memory_id == memory_id else rel.source_memory_id

                # Get related memory info
                related_memory_stmt = select(LTMMemory).where(
                    LTMMemory.id == related_memory_id)
                related_memory_result = await session.execute(related_memory_stmt)
                related_memory = related_memory_result.scalar_one_or_none()

                if related_memory:
                    relationship_data.append({
                        "id": rel.id,
                        "relationship_type": rel.relationship_type,
                        "strength": rel.strength,
                        "description": rel.description,
                        "related_memory": {
                            "id": related_memory.id,
                            "content": related_memory.content[:100] + "..." if len(related_memory.content) > 100 else related_memory.content,
                            "memory_type": related_memory.memory_type,
                            "importance_score": related_memory.importance_score
                        }
                    })

            return relationship_data

    except Exception as e:
        logger.error(f"Error getting memory relationships: {e}")
        return []


async def update_memory_importance(memory_id: int, user_id: str, new_importance: int) -> bool:
    """Update memory importance and recalculate dynamic importance"""
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)

            # Get memory
            stmt = select(LTMMemory).where(
                and_(
                    LTMMemory.id == memory_id,
                    LTMMemory.user_id == user_id_int
                )
            )
            result = await session.execute(stmt)
            memory = result.scalar_one_or_none()

            if not memory:
                return False

            # Update importance
            memory.importance_score = new_importance
            memory.dynamic_importance = memory.calculate_dynamic_importance()
            memory.last_modified = datetime.utcnow()

            await session.commit()
            return True

    except Exception as e:
        logger.error(f"Error updating memory importance: {e}")
        return False


async def archive_memory(memory_id: int, user_id: str, reason: str = "User request") -> bool:
    """Archive a memory"""
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)

            # Get memory
            stmt = select(LTMMemory).where(
                and_(
                    LTMMemory.id == memory_id,
                    LTMMemory.user_id == user_id_int
                )
            )
            result = await session.execute(stmt)
            memory = result.scalar_one_or_none()

            if not memory:
                return False

            # Archive memory
            memory.is_archived = True
            memory.archive_reason = reason
            memory.last_modified = datetime.utcnow()

            await session.commit()
            return True

    except Exception as e:
        logger.error(f"Error archiving memory: {e}")
        return False


async def get_memory_analytics(user_id: str) -> Dict[str, Any]:
    """Get comprehensive analytics about user's LTM memories"""
    try:
        async with AsyncSessionLocal() as session:
            user_id_int = int(user_id)

            # Basic statistics
            total_memories = await session.execute(
                select(func.count(LTMMemory.id)).where(
                    LTMMemory.user_id == user_id_int)
            )
            total_memories = total_memories.scalar()

            # Memory type distribution
            type_distribution = await session.execute(
                select(LTMMemory.memory_type, func.count(LTMMemory.id))
                .where(LTMMemory.user_id == user_id_int)
                .group_by(LTMMemory.memory_type)
            )
            type_distribution = dict(type_distribution.fetchall())

            # Category distribution
            category_distribution = await session.execute(
                select(LTMMemory.category, func.count(LTMMemory.id))
                .where(LTMMemory.user_id == user_id_int)
                .group_by(LTMMemory.category)
            )
            category_distribution = dict(category_distribution.fetchall())

            # Average importance scores
            avg_importance = await session.execute(
                select(func.avg(LTMMemory.importance_score))
                .where(LTMMemory.user_id == user_id_int)
            )
            avg_importance = avg_importance.scalar() or 0

            avg_dynamic_importance = await session.execute(
                select(func.avg(LTMMemory.dynamic_importance))
                .where(LTMMemory.user_id == user_id_int)
            )
            avg_dynamic_importance = avg_dynamic_importance.scalar() or 0

            # Most accessed memories
            most_accessed = await session.execute(
                select(LTMMemory.id, LTMMemory.content, LTMMemory.access_count)
                .where(LTMMemory.user_id == user_id_int)
                .order_by(desc(LTMMemory.access_count))
                .limit(5)
            )
            most_accessed = [
                {"id": m.id, "content": m.content[:100] +
                    "...", "access_count": m.access_count}
                for m in most_accessed.scalars().all()
            ]

            return {
                "total_memories": total_memories,
                "type_distribution": type_distribution,
                "category_distribution": category_distribution,
                "average_importance": round(avg_importance, 2),
                "average_dynamic_importance": round(avg_dynamic_importance, 2),
                "most_accessed_memories": most_accessed
            }

    except Exception as e:
        logger.error(f"Error getting memory analytics: {e}")
        return {}
