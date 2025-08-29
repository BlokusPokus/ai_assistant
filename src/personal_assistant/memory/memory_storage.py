"""
Memory storage operations using the new database structure.
"""
import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, desc, select, alias

from ..config.logging_config import get_logger
from ..database.crud.utils import add_record
from ..database.models.agent_logs import AgentLog
from ..database.models.memory_chunk import MemoryChunk
from ..database.models.memory_metadata import MemoryMetadata

from ..database.session import AsyncSessionLocal
from ..types.state import AgentState
from .state_optimization import StateOptimizationManager
from ..rag.retriever import embed_and_index

# Set up logging
logger = get_logger("memory")

# Global state optimization manager instance
_state_optimization_manager = None


def _get_state_optimization_manager() -> StateOptimizationManager:
    """
    Get or create the global state optimization manager.

    Returns:
        StateOptimizationManager instance
    """
    global _state_optimization_manager
    if _state_optimization_manager is None:
        from ..types.state import StateConfig
        # Use default configuration - can be enhanced later with user-specific configs
        config = StateConfig()
        _state_optimization_manager = StateOptimizationManager(config)
        logger.info("🔧 State optimization manager initialized")
    return _state_optimization_manager


async def save_state(conversation_id: str, state: AgentState, user_id: str = None) -> None:
    """
    Save or update conversation state in the database with intelligent optimization.

    This function now optimizes the state before saving to prevent memory explosion:
    1. Compresses conversation history by removing redundancy
    2. Optimizes memory context based on relevance
    3. Analyzes error patterns for learning
    4. Creates intelligent summaries for old content
    5. Applies size limits intelligently

    Args:
        conversation_id (str): Unique identifier for the conversation
        state (AgentState): The conversation state to save
        user_id (str): User ID for the conversation (optional for backward compatibility)

    Raises:
        Exception: If database operations fail (handled by caller)

    Example:
        >>> state = AgentState(user_input="Hello", focus=["greeting"])
        >>> await save_state("conv_123", state, "user_456")
    """
    logger.info(f"💾 Saving state for conversation: {conversation_id}")
    logger.info(
        f"💾 Original state has {len(state.conversation_history)} conversation items")
    logger.info(
        f"💾 Original memory context has {len(state.memory_context)} items")
    logger.info(
        f"💾 Last tool result: {str(state.last_tool_result)[:100] if state.last_tool_result else 'None'}...")

    try:
        # Step 1: Optimize state before saving
        logger.info("🔧 Starting state optimization...")
        optimization_manager = _get_state_optimization_manager()

        # Create a copy for optimization to avoid modifying the original
        import copy
        state_copy = copy.deepcopy(state)

        # Apply optimization pipeline
        optimized_state = await optimization_manager.optimize_state_for_saving(state_copy)

        # Log optimization results
        conv_reduction = len(state.conversation_history) - \
            len(optimized_state.conversation_history)
        context_reduction = len(state.memory_context) - \
            len(optimized_state.memory_context)

        logger.info(f"🔧 Optimization complete:")
        logger.info(
            f"  Conversation history: {len(state.conversation_history)} → {len(optimized_state.conversation_history)} items ({conv_reduction:+d})")
        logger.info(
            f"  Memory context: {len(state.memory_context)} → {len(optimized_state.memory_context)} items ({context_reduction:+d})")

        # Get optimization report for debugging
        optimization_report = optimization_manager.get_optimization_report(
            state, optimized_state)
        logger.debug(f"🔧 Optimization report:\n{optimization_report}")

        # Step 2: Save the optimized state
        logger.info("💾 Saving optimized state to database...")

        async with AsyncSessionLocal() as session:
            # Create memory chunk with optimized state
            chunk_data = {
                "content": json.dumps(optimized_state.to_dict()),
                "embedding": None,  # JSON compatible null
                # Use timezone-aware datetime
                "created_at": datetime.now(timezone.utc)
            }

            # Add user_id if provided
            if user_id:
                chunk_data["user_id"] = int(user_id)

            logger.info(
                f"💾 Creating memory chunk with user_id: {chunk_data.get('user_id')}")
            chunk = await add_record(session, MemoryChunk, chunk_data)
            logger.info(f"💾 Created chunk with ID: {chunk.id}")

            # Add metadata entries including optimization info
            metadata_entries = [
                {"chunk_id": chunk.id, "key": "conversation_id",
                    "value": conversation_id},
                {"chunk_id": chunk.id, "key": "type", "value": "state"},
                {"chunk_id": chunk.id, "key": "last_updated",
                    "value": datetime.now(timezone.utc).isoformat()},
                {"chunk_id": chunk.id, "key": "optimization_applied", "value": "true"},
                {"chunk_id": chunk.id, "key": "original_conversation_length",
                    "value": str(len(state.conversation_history))},
                {"chunk_id": chunk.id, "key": "optimized_conversation_length",
                    "value": str(len(optimized_state.conversation_history))},
                {"chunk_id": chunk.id, "key": "original_context_length",
                    "value": str(len(state.memory_context))},
                {"chunk_id": chunk.id, "key": "optimized_context_length",
                    "value": str(len(optimized_state.memory_context))}
            ]

            logger.info(
                f"💾 Adding metadata entries: {len(metadata_entries)} entries")
            for entry in metadata_entries:
                await add_record(session, MemoryMetadata, entry)

            # Generate RAG embeddings for the memory chunk
            try:
                logger.info(
                    f"🧠 Generating RAG embeddings for chunk {chunk.id}")
                await embed_and_index(
                    document=chunk.content,
                    metadata={
                        "user_id": user_id,
                        "chunk_id": chunk.id,
                        "conversation_id": conversation_id,
                        "type": "state",
                        "source": "memory_storage"
                    }
                )
                logger.info(f"✅ RAG embeddings generated for chunk {chunk.id}")
            except Exception as e:
                logger.warning(
                    f"⚠️ Failed to generate RAG embeddings for chunk {chunk.id}: {e}")
                # Continue without embeddings - system will still work

            logger.info(
                f"✅ Successfully saved optimized state for conversation {conversation_id}")

    except Exception as e:
        logger.error(f"❌ Error during state optimization/saving: {str(e)}")
        logger.info(
            "🔄 Falling back to saving original state without optimization...")

        # Fallback: save original state if optimization fails
        try:
            async with AsyncSessionLocal() as session:
                chunk_data = {
                    "content": json.dumps(state.to_dict()),
                    "embedding": None,
                    "created_at": datetime.now(timezone.utc)
                }

                if user_id:
                    chunk_data["user_id"] = int(user_id)

                chunk = await add_record(session, MemoryChunk, chunk_data)

                metadata_entries = [
                    {"chunk_id": chunk.id, "key": "conversation_id",
                        "value": conversation_id},
                    {"chunk_id": chunk.id, "key": "type", "value": "state"},
                    {"chunk_id": chunk.id, "key": "last_updated",
                        "value": datetime.now(timezone.utc).isoformat()},
                    {"chunk_id": chunk.id, "key": "optimization_failed", "value": "true"},
                    {"chunk_id": chunk.id, "key": "fallback_save", "value": "true"}
                ]

                for entry in metadata_entries:
                    await add_record(session, MemoryMetadata, entry)

                # Generate RAG embeddings for the fallback memory chunk
                try:
                    logger.info(
                        f"🧠 Generating RAG embeddings for fallback chunk {chunk.id}")
                    await embed_and_index(
                        document=chunk.content,
                        metadata={
                            "user_id": user_id,
                            "chunk_id": chunk.id,
                            "conversation_id": conversation_id,
                            "type": "state",
                            "source": "memory_storage_fallback"
                        }
                    )
                    logger.info(
                        f"✅ RAG embeddings generated for fallback chunk {chunk.id}")
                except Exception as e:
                    logger.warning(
                        f"⚠️ Failed to generate RAG embeddings for fallback chunk {chunk.id}: {e}")
                    # Continue without embeddings - system will still work

                logger.info(
                    f"✅ Fallback save successful for conversation {conversation_id}")

        except Exception as fallback_error:
            logger.error(f"❌ Fallback save also failed: {str(fallback_error)}")
            raise fallback_error


async def load_state(conversation_id: str) -> AgentState:
    """
    Retrieve the latest saved conversation state for a given conversation ID from the database.

    This function handles various error scenarios gracefully:
    - Database connection issues
    - Corrupted or malformed JSON data
    - Missing conversation data
    - Invalid AgentState data

    The function always returns a valid AgentState object, even if the original data
    is corrupted or missing. This ensures the calling code can continue to function.

    Args:
        conversation_id (str): Unique identifier for the conversation

    Returns:
        AgentState: The conversation state, or an empty AgentState if not found/corrupted

    Example:
        >>> state = await load_state("conv_123")
        >>> if state.user_input:
        ...     print("State loaded successfully")
        ... else:
        ...     print("No state found or corrupted")
    """

    try:
        logger.info(f"🔍 Loading state for conversation: {conversation_id}")

        async with AsyncSessionLocal() as session:
            # Fixed query: Use separate JOINs with different aliases to avoid table name conflicts
            conv_meta = alias(MemoryMetadata, name="conv_meta")
            type_meta = alias(MemoryMetadata, name="type_meta")

            stmt = (
                select(MemoryChunk)
                .join(
                    conv_meta,
                    and_(
                        conv_meta.c.chunk_id == MemoryChunk.id,
                        conv_meta.c.key == "conversation_id",
                        conv_meta.c.value == conversation_id
                    )
                )
                .join(
                    type_meta,
                    and_(
                        type_meta.c.chunk_id == MemoryChunk.id,
                        type_meta.c.key == "type",
                        type_meta.c.value == "state"
                    )
                )
                .order_by(desc(MemoryChunk.created_at))
                .limit(1)
            )

            logger.info(f"🔍 Executing query: {stmt}")
            result = await session.execute(stmt)
            chunk = result.scalar_one_or_none()

            logger.info(f"🔍 Query result: chunk found = {chunk is not None}")
            if chunk:
                logger.info(f"🔍 Chunk ID: {chunk.id}")
                logger.info(
                    f"🔍 Chunk content length: {len(chunk.content) if chunk.content else 0}")
                logger.info(f"🔍 Chunk created_at: {chunk.created_at}")
                logger.info(f"🔍 Chunk user_id: {chunk.user_id}")
            else:
                logger.warning(
                    f"⚠️ No chunk found for conversation {conversation_id}")

            if not chunk:
                logger.info(
                    f"No state found for conversation {conversation_id}")
                return AgentState(user_input="")

            if not chunk.content:
                logger.warning(
                    f"Empty content found for conversation {conversation_id}")
                return AgentState(user_input="")

            try:
                # Parse JSON content
                logger.info(f"🔍 Parsing JSON content...")
                state_dict = json.loads(chunk.content)
                logger.info(
                    f"🔍 JSON parsed successfully, type: {type(state_dict)}")

                if not isinstance(state_dict, dict):
                    logger.error(
                        f"Invalid state data type for conversation {conversation_id}: expected dict, got {type(state_dict)}")
                    return AgentState(user_input="")

                logger.info(f"🔍 State dict keys: {list(state_dict.keys())}")
                logger.info(
                    f"🔍 Conversation history length: {len(state_dict.get('conversation_history', []))}")
                logger.info(
                    f"🔍 Last tool result: {str(state_dict.get('last_tool_result', 'None'))[:100] if state_dict.get('last_tool_result') else 'None'}...")

                # Create AgentState from dictionary
                # Be selective:
                agent_state = AgentState(user_input="")
                if "conversation_history" in state_dict:
                    agent_state.conversation_history = state_dict["conversation_history"]
                if "focus" in state_dict:
                    agent_state.focus = state_dict["focus"]
                if "step_count" in state_dict:
                    agent_state.step_count = state_dict["step_count"]

                logger.info(
                    f"✅ Successfully loaded state for conversation {conversation_id}")
                logger.info(
                    f"✅ Final state has {len(agent_state.conversation_history)} conversation items")
                return agent_state

            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse JSON for conversation {conversation_id}: {e}")
                return AgentState(user_input="")
            except Exception as e:
                logger.error(
                    f"Failed to create AgentState for conversation {conversation_id}: {e}")
                return AgentState(user_input="")

    except Exception as e:
        logger.error(
            f"Database error while loading state for conversation {conversation_id}: {e}")
        return AgentState(user_input="")


async def get_conversation_timestamp(user_id: int, conversation_id: str) -> Optional[datetime]:
    """Get last update time for a conversation for a specific user."""
    try:

        async with AsyncSessionLocal() as session:
            try:
                # Get the chunk_id for this conversation AND user
                stmt = (
                    select(MemoryChunk.id)
                    .join(MemoryMetadata, MemoryMetadata.chunk_id == MemoryChunk.id)
                    .where(
                        MemoryChunk.user_id == user_id,
                        MemoryMetadata.key == "conversation_id",
                        MemoryMetadata.value == conversation_id
                    )
                    .order_by(desc(MemoryChunk.created_at))
                    .limit(1)
                )
                result = await session.execute(stmt)
                chunk_id = result.scalar_one_or_none()

                if not chunk_id:
                    logger.info(
                        f"No chunk found for conversation {conversation_id} and user {user_id}")
                    return None

                # Get the actual timestamp from the memory_chunks table instead of metadata
                stmt = (
                    select(MemoryChunk.created_at)
                    .where(MemoryChunk.id == chunk_id)
                )
                result = await session.execute(stmt)
                timestamp = result.scalar_one_or_none()

                if not timestamp:
                    logger.warning(
                        f"No timestamp found for conversation {conversation_id} and user {user_id}")
                    return None

                # The timestamp from the database is already timezone-aware
                logger.debug(
                    f"Successfully loaded timestamp for conversation {conversation_id} and user {user_id}: {timestamp}")
                return timestamp
            except Exception as e:
                logger.error(
                    f"Database error while getting timestamp for conversation {conversation_id} and user {user_id}: {e}")
                return None

    except Exception as e:
        logger.error(
            f"Database error while getting timestamp for conversation {conversation_id} and user {user_id}: {e}")
        return None


async def log_agent_interaction(
    user_id: int,
    user_input: str,
    agent_response: str,
    tool_called: str = None,
    tool_output: str = None,
    memory_used: list = None,
    timestamp: datetime = None
):
    """Log a single agent interaction to agent_logs."""
    async with AsyncSessionLocal() as session:
        await add_record(
            session,
            AgentLog,
            {
                "user_id": user_id,
                "user_input": user_input,
                "agent_response": agent_response,
                "tool_called": tool_called,
                "tool_output": tool_output,
                "memory_used": memory_used,
                # Use timezone-aware datetime
                "timestamp": timestamp or datetime.now(timezone.utc)
            }
        )
