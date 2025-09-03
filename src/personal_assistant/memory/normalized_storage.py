"""
Normalized Storage Layer for Task 053: Database Schema Redesign

This module implements the new storage layer using normalized database tables
instead of JSON blobs, providing better performance, queryability, and maintainability.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.logging_config import get_logger
from ..database.models.conversation_message import ConversationMessage

# Import the new models
from ..database.models.conversation_state import ConversationState
from ..database.models.memory_context_item import MemoryContextItem
from ..database.session import AsyncSessionLocal
from ..rag.retriever import embed_and_index
from ..types.state import AgentState, StateConfig
from .state_optimization import StateOptimizationManager

logger = get_logger("normalized_storage")

# Global state optimization manager instance
_state_optimization_manager = None


def _get_state_optimization_manager() -> StateOptimizationManager:
    """Get or create the global state optimization manager."""
    global _state_optimization_manager
    if _state_optimization_manager is None:
        config = StateConfig()
        _state_optimization_manager = StateOptimizationManager(config)
        logger.info("🔧 State optimization manager initialized for normalized storage")
    return _state_optimization_manager


async def save_state_normalized(
    conversation_id: str, state: AgentState, user_id: int = None
) -> None:
    """
    Save conversation state using the new normalized database schema.

    This function replaces the JSON blob approach with structured, normalized tables:
    1. Saves core conversation state to conversation_states table
    2. Saves individual messages to conversation_messages table
    3. Saves memory context items to memory_context_items table
    4. Maintains referential integrity with foreign keys
    5. Enables efficient querying and partial updates

    Args:
        conversation_id: Unique identifier for the conversation
        state: The conversation state to save
        user_id: User ID for the conversation (required for normalized storage)

    Raises:
        ValueError: If user_id is not provided
        Exception: If database operations fail
    """
    if not user_id:
        raise ValueError("user_id is required for normalized storage")

    logger.info(
        f"💾 Saving state using normalized schema for conversation: {conversation_id}"
    )
    logger.info(
        f"💾 Original state has {len(state.conversation_history)} conversation items"
    )
    logger.info(f"💾 Original memory context has {len(state.memory_context)} items")

    try:
        # Step 1: Optimize state before saving (reuse existing optimization)
        logger.info("🔧 Starting state optimization...")
        optimization_manager = _get_state_optimization_manager()

        # Create a copy for optimization to avoid modifying the original
        import copy

        state_copy = copy.deepcopy(state)
        optimized_state = await optimization_manager.optimize_state_for_saving(
            state_copy
        )

        # Log optimization results
        conv_reduction = len(state.conversation_history) - len(
            optimized_state.conversation_history
        )
        context_reduction = len(state.memory_context) - len(
            optimized_state.memory_context
        )

        logger.info(f"🔧 Optimization complete:")
        logger.info(
            f"  Conversation history: {len(state.conversation_history)} → {len(optimized_state.conversation_history)} items ({conv_reduction:+d})"
        )
        logger.info(
            f"  Memory context: {len(state.memory_context)} → {len(optimized_state.memory_context)} items ({context_reduction:+d})"
        )

        # Step 2: Save using normalized schema
        logger.info("💾 Saving optimized state using normalized schema...")

        async with AsyncSessionLocal() as session:
            # Check if conversation already exists
            existing_state = await session.execute(
                select(ConversationState).where(
                    ConversationState.conversation_id == conversation_id
                )
            )
            existing_state = existing_state.scalar_one_or_none()

            if existing_state:
                # Update existing conversation state
                logger.info(
                    f"🔄 Updating existing conversation state: {conversation_id}"
                )
                existing_state.user_input = optimized_state.user_input
                existing_state.focus_areas = optimized_state.focus
                existing_state.step_count = optimized_state.step_count
                existing_state.last_tool_result = optimized_state.last_tool_result
                existing_state.updated_at = datetime.now(timezone.utc)
                conversation_state = existing_state
            else:
                # Create new conversation state
                logger.info(f"🆕 Creating new conversation state: {conversation_id}")
                conversation_state = ConversationState.from_agent_state(
                    conversation_id, user_id, optimized_state
                )
                session.add(conversation_state)
                await session.flush()  # Get the ID

            # Step 3: Save conversation messages
            logger.info(
                f"💬 Saving {len(optimized_state.conversation_history)} conversation messages..."
            )

            # Clear existing messages if updating
            if existing_state:
                await session.execute(
                    select(ConversationMessage).where(
                        ConversationMessage.conversation_id == conversation_id
                    )
                )
                existing_messages = await session.execute(
                    select(ConversationMessage).where(
                        ConversationMessage.conversation_id == conversation_id
                    )
                )
                for msg in existing_messages.scalars():
                    await session.delete(msg)

            # Save new messages
            for item in optimized_state.conversation_history:
                message = ConversationMessage.from_conversation_item(
                    conversation_id, item
                )
                session.add(message)

            # Step 4: Save memory context items
            logger.info(
                f"🧠 Saving {len(optimized_state.memory_context)} memory context items..."
            )

            # Clear existing context items if updating
            if existing_state:
                existing_context = await session.execute(
                    select(MemoryContextItem).where(
                        MemoryContextItem.conversation_id == conversation_id
                    )
                )
                for ctx in existing_context.scalars():
                    await session.delete(ctx)

            # Save new context items
            for item in optimized_state.memory_context:
                context_item = MemoryContextItem.from_memory_context_item(
                    conversation_id, item
                )
                session.add(context_item)

            # Step 5: Save focus areas as context items
            if optimized_state.focus:
                logger.info(f"🎯 Saving {len(optimized_state.focus)} focus areas...")
                for focus_area in optimized_state.focus:
                    focus_item = MemoryContextItem.from_focus_area(
                        conversation_id, focus_area
                    )
                    session.add(focus_item)

            # Commit all changes
            await session.commit()
            logger.info(
                f"✅ Successfully saved state using normalized schema for conversation {conversation_id}"
            )

            # Step 6: Generate RAG embeddings for the conversation state
            try:
                logger.info(
                    f"🧠 Generating RAG embeddings for conversation {conversation_id}"
                )

                # Create a summary for RAG indexing
                rag_content = f"Conversation: {conversation_id}\nUser Input: {optimized_state.user_input}\nFocus Areas: {', '.join(optimized_state.focus) if optimized_state.focus else 'None'}"

                await embed_and_index(
                    document=rag_content,
                    metadata={
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "type": "conversation_state",
                        "source": "normalized_storage",
                        "storage_method": "normalized",
                    },
                )
                logger.info(
                    f"✅ RAG embeddings generated for conversation {conversation_id}"
                )
            except Exception as e:
                logger.warning(
                    f"⚠️ Failed to generate RAG embeddings for conversation {conversation_id}: {e}"
                )
                # Continue without embeddings - system will still work

    except Exception as e:
        logger.error(f"❌ Error during normalized state saving: {str(e)}")
        raise


async def load_state_normalized(
    conversation_id: str,
    user_id: int = None,
    max_messages: int = 50,
    max_context_items: int = 20,
    min_relevance_score: float = 0.3,
) -> Optional[AgentState]:
    """
    Load conversation state using the new normalized database schema.

    This function provides intelligent, selective loading:
    1. Loads core conversation state efficiently
    2. Loads only relevant messages based on limits
    3. Loads high-quality context items based on relevance scores
    4. Reconstructs AgentState object with loaded data

    Args:
        conversation_id: Unique identifier for the conversation
        user_id: User ID for the conversation (optional, for validation)
        max_messages: Maximum number of messages to load
        max_context_items: Maximum number of context items to load
        min_relevance_score: Minimum relevance score for context items

    Returns:
        AgentState object if found, None otherwise
    """
    logger.info(
        f"📂 Loading state using normalized schema for conversation: {conversation_id}"
    )

    try:
        async with AsyncSessionLocal() as session:
            # Step 1: Load conversation state
            logger.info("📋 Loading conversation state...")
            state_result = await session.execute(
                select(ConversationState).where(
                    ConversationState.conversation_id == conversation_id
                )
            )
            conversation_state = state_result.scalar_one_or_none()

            if not conversation_state:
                logger.warning(f"⚠️ No conversation state found for: {conversation_id}")
                return None

            # Validate user_id if provided
            if user_id and conversation_state.user_id != user_id:
                logger.warning(
                    f"⚠️ User ID mismatch for conversation {conversation_id}"
                )
                return None

            # Step 2: Load conversation messages (most recent first)
            logger.info(f"💬 Loading up to {max_messages} conversation messages...")
            messages_result = await session.execute(
                select(ConversationMessage)
                .where(ConversationMessage.conversation_id == conversation_id)
                .order_by(desc(ConversationMessage.timestamp))
                .limit(max_messages)
            )
            messages = messages_result.scalars().all()

            # Convert messages back to conversation history format
            conversation_history = []
            for msg in reversed(messages):  # Reverse to get chronological order
                history_item = {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                }

                # Add tool-specific information if available
                if msg.tool_name:
                    history_item["tool_name"] = msg.tool_name
                if msg.tool_success:
                    history_item["tool_success"] = msg.tool_success
                if msg.additional_data:
                    history_item.update(
                        json.loads(msg.additional_data)
                        if isinstance(msg.additional_data, str)
                        else msg.additional_data
                    )

                conversation_history.append(history_item)

            # Step 3: Load memory context items (highest relevance first)
            logger.info(
                f"🧠 Loading up to {max_context_items} context items with relevance >= {min_relevance_score}..."
            )
            context_result = await session.execute(
                select(MemoryContextItem)
                .where(
                    and_(
                        MemoryContextItem.conversation_id == conversation_id,
                        MemoryContextItem.relevance_score >= min_relevance_score,
                    )
                )
                .order_by(desc(MemoryContextItem.relevance_score))
                .limit(max_context_items)
            )
            context_items = context_result.scalars().all()

            # Convert context items back to memory context format
            memory_context = []
            for ctx in context_items:
                context_item = {
                    "content": ctx.content,
                    "source": ctx.source,
                    "relevance_score": ctx.relevance_score,
                    "context_type": ctx.context_type,
                }

                # Add optional fields if available
                if ctx.original_role:
                    context_item["role"] = ctx.original_role
                if ctx.focus_area:
                    context_item["focus_area"] = ctx.focus_area
                if ctx.preference_type:
                    context_item["preference_type"] = ctx.preference_type
                if ctx.additional_data:
                    try:
                        metadata = (
                            json.loads(ctx.additional_data)
                            if isinstance(ctx.additional_data, str)
                            else ctx.additional_data
                        )
                        context_item.update(metadata)
                    except json.JSONDecodeError:
                        logger.warning(
                            f"⚠️ Failed to parse metadata for context item {ctx.id}"
                        )

                memory_context.append(context_item)

            # Step 4: Reconstruct AgentState object
            logger.info("🔧 Reconstructing AgentState object...")

            # Extract focus areas from context items
            focus_areas = []
            for ctx in context_items:
                if ctx.focus_area and ctx.focus_area not in focus_areas:
                    focus_areas.append(ctx.focus_area)

            # If no focus areas found in context, use the stored ones
            if not focus_areas and conversation_state.focus_areas:
                focus_areas = conversation_state.focus_areas

            # Create AgentState
            agent_state = AgentState(
                user_input=conversation_state.user_input or "",
                memory_context=memory_context,
                conversation_history=conversation_history,
                focus=focus_areas,
                step_count=conversation_state.step_count or 0,
                last_tool_result=conversation_state.last_tool_result,
            )

            logger.info(f"✅ Successfully loaded state using normalized schema:")
            logger.info(f"  Messages loaded: {len(conversation_history)}")
            logger.info(f"  Context items loaded: {len(memory_context)}")
            logger.info(f"  Focus areas: {focus_areas}")

            return agent_state

    except Exception as e:
        logger.error(f"❌ Error during normalized state loading: {str(e)}")
        raise


async def update_state_partial(
    conversation_id: str, updates: Dict[str, Any], user_id: int = None
) -> bool:
    """
    Update specific parts of a conversation state using normalized schema.

    This function enables efficient partial updates without loading/saving entire state:
    1. Updates only specified fields in conversation_states
    2. Adds new messages without replacing all messages
    3. Updates context items incrementally
    4. Maintains data consistency and referential integrity

    Args:
        conversation_id: Unique identifier for the conversation
        updates: Dictionary of fields to update
        user_id: User ID for validation

    Returns:
        True if update successful, False otherwise
    """
    logger.info(f"🔄 Updating state partially for conversation: {conversation_id}")

    try:
        async with AsyncSessionLocal() as session:
            # Verify conversation exists and user has access
            state_result = await session.execute(
                select(ConversationState).where(
                    ConversationState.conversation_id == conversation_id
                )
            )
            conversation_state = state_result.scalar_one_or_none()

            if not conversation_state:
                logger.warning(f"⚠️ No conversation state found for: {conversation_id}")
                return False

            if user_id and conversation_state.user_id != user_id:
                logger.warning(
                    f"⚠️ User ID mismatch for conversation {conversation_id}"
                )
                return False

            # Update conversation state fields
            updated = False
            if "user_input" in updates:
                conversation_state.user_input = updates["user_input"]
                updated = True

            if "focus_areas" in updates:
                conversation_state.focus_areas = updates["focus_areas"]
                updated = True

            if "step_count" in updates:
                conversation_state.step_count = updates["step_count"]
                updated = True

            if "last_tool_result" in updates:
                conversation_state.last_tool_result = updates["last_tool_result"]
                updated = True

            if updated:
                conversation_state.updated_at = datetime.now(timezone.utc)
                logger.info(
                    f"✅ Updated conversation state fields for {conversation_id}"
                )

            # Add new messages if provided
            if "new_messages" in updates:
                new_messages = updates["new_messages"]
                logger.info(f"💬 Adding {len(new_messages)} new messages...")

                for message_data in new_messages:
                    message = ConversationMessage.from_conversation_item(
                        conversation_id, message_data
                    )
                    session.add(message)

                logger.info(f"✅ Added {len(new_messages)} new messages")

            # Add new context items if provided
            if "new_context_items" in updates:
                new_context_items = updates["new_context_items"]
                logger.info(f"🧠 Adding {len(new_context_items)} new context items...")

                for context_data in new_context_items:
                    context_item = MemoryContextItem.from_memory_context_item(
                        conversation_id, context_data
                    )
                    session.add(context_item)

                logger.info(f"✅ Added {len(new_context_items)} new context items")

            # Commit changes
            await session.commit()
            logger.info(
                f"✅ Successfully updated state partially for conversation {conversation_id}"
            )
            return True

    except Exception as e:
        logger.error(f"❌ Error during partial state update: {str(e)}")
        return False


async def delete_conversation_normalized(
    conversation_id: str, user_id: int = None
) -> bool:
    """
    Delete a conversation and all related data using normalized schema.

    This function leverages CASCADE deletes to efficiently remove:
    1. Conversation state
    2. All related messages
    3. All related context items
    4. Associated metadata

    Args:
        conversation_id: Unique identifier for the conversation
        user_id: User ID for validation

    Returns:
        True if deletion successful, False otherwise
    """
    logger.info(f"🗑️ Deleting conversation using normalized schema: {conversation_id}")

    try:
        async with AsyncSessionLocal() as session:
            # Verify conversation exists and user has access
            state_result = await session.execute(
                select(ConversationState).where(
                    ConversationState.conversation_id == conversation_id
                )
            )
            conversation_state = state_result.scalar_one_or_none()

            if not conversation_state:
                logger.warning(f"⚠️ No conversation state found for: {conversation_id}")
                return False

            if user_id and conversation_state.user_id != user_id:
                logger.warning(
                    f"⚠️ User ID mismatch for conversation {conversation_id}"
                )
                return False

            # Delete conversation state (CASCADE will handle related records)
            await session.delete(conversation_state)
            await session.commit()

            logger.info(
                f"✅ Successfully deleted conversation {conversation_id} and all related data"
            )
            return True

    except Exception as e:
        logger.error(f"❌ Error during conversation deletion: {str(e)}")
        return False
