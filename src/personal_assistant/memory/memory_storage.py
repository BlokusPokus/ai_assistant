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


# async def store_summary(user_id: str, summary: str) -> None:
#     """Store conversation summary."""
#     async with AsyncSessionLocal() as session:
#         # Convert user_id string to int
#         user_id_int = int(user_id)

#         # Create memory chunk
#         chunk_data = {
#             "user_id": user_id_int,  # Now using integer
#             "content": summary,
#             # Use timezone-aware datetime
#             "created_at": datetime.now(timezone.utc)
#         }
#         chunk = await add_record(session, MemoryChunk, chunk_data)

#         # Add metadata
#         metadata = {
#             "chunk_id": chunk.id,
#             "key": "type",
#             "value": "summary"
#         }
#         await add_record(session, MemoryMetadata, metadata)


# async def load_latest_summary(user_id: str) -> str:
#     """
#     Load the most recent summary for a user with backward compatibility.

#     This function safely retrieves the latest summary from the database, handling
#     both comprehensive JSON summaries and basic string summaries.

#     Args:
#         user_id (str): User ID as a string (will be converted to int)

#     Returns:
#         str: The summary content as a string, or empty string if not found/error

#     Raises:
#         ValueError: If user_id is empty, None, or cannot be converted to int

#     Example:
#         >>> summary = await load_latest_summary("123")
#         >>> if summary:
#         ...     print("Summary loaded successfully")
#         ... else:
#         ...     print("No summary found or error occurred")
#     """
#     # Input validation
#     if not user_id or (isinstance(user_id, str) and user_id.strip() == ""):
#         logger.error("load_latest_summary called with empty or None user_id")
#         raise ValueError("user_id cannot be empty or None")

#     try:
#         # Safe type conversion with validation
#         user_id_int = int(user_id)
#         if user_id_int <= 0:
#             logger.error(
#                 f"load_latest_summary called with invalid user_id: {user_id}")
#             raise ValueError(
#                 f"user_id must be a positive integer, got: {user_id}")

#     except ValueError as e:
#         logger.error(f"Failed to convert user_id '{user_id}' to integer: {e}")
#         raise ValueError(
#             f"user_id must be a valid integer string, got: {user_id}") from e

#     try:
#         async with AsyncSessionLocal() as session:
#             # Query for summary type metadata
#             stmt = (
#                 select(MemoryChunk)
#                 .join(MemoryMetadata)
#                 .where(
#                     MemoryChunk.user_id == user_id_int,
#                     MemoryMetadata.key == "type",
#                     MemoryMetadata.value == "summary"
#                 )
#                 .order_by(desc(MemoryChunk.created_at))
#                 .limit(1)
#             )

#             result = await session.execute(stmt)
#             chunk = result.scalar_one_or_none()

#             if not chunk:
#                 logger.info(f"No summary found for user {user_id}")
#                 return ""

#             if not chunk.content:
#                 logger.warning(
#                     f"Empty content found for summary chunk {chunk.id} for user {user_id}")
#                 return ""

#             # Check if this is a comprehensive summary (JSON format)
#             try:
#                 summary_data = json.loads(chunk.content)
#                 if isinstance(summary_data, dict) and "user_input" in summary_data:
#                     # This is a comprehensive summary, return the full JSON for proper context
#                     logger.debug(
#                         f"Loaded comprehensive JSON summary for user {user_id}")
#                     return chunk.content
#                 else:
#                     # This is a basic summary string
#                     logger.debug(
#                         f"Loaded basic summary string for user {user_id}")
#                     return chunk.content
#             except json.JSONDecodeError:
#                 # This is a basic summary string
#                 logger.debug(
#                     f"Loaded basic summary string (non-JSON) for user {user_id}")
#                 return chunk.content

#     except Exception as e:
#         logger.error(
#             f"Database error while loading summary for user {user_id}: {e}")
#         return ""


# async def query_ltm(user_id: str, tags: List[str] = None) -> List[Dict]:
#     """Query long-term memory with optional tags."""
#     async with AsyncSessionLocal() as session:
#         # Convert user_id string to int
#         user_id_int = int(user_id)

#         # Base query for LTM chunks
#         stmt = (
#             select(MemoryChunk)
#             .join(MemoryMetadata, MemoryMetadata.chunk_id == MemoryChunk.id)
#             .where(
#                 MemoryChunk.user_id == user_id_int,
#                 MemoryMetadata.key == "type",
#                 MemoryMetadata.value == "ltm"
#             )
#         )

#         # Add tag filtering if specified
#         if tags:
#             # Use a subquery to find chunks that have the specified tags
#             tag_subquery = (
#                 select(MemoryMetadata.chunk_id)
#                 .where(
#                     MemoryMetadata.key == "tag",
#                     MemoryMetadata.value.in_(tags)
#                 )
#             )
#             stmt = stmt.where(MemoryChunk.id.in_(tag_subquery))

#         result = await session.execute(stmt)
#         chunks = result.scalars().all()

#         # Format results - load metadata within session
#         formatted_results = []
#         for chunk in chunks:
#             # Get metadata for this chunk within the session
#             metadata_stmt = select(MemoryMetadata).where(
#                 MemoryMetadata.chunk_id == chunk.id)
#             metadata_result = await session.execute(metadata_stmt)
#             metadata_entries = metadata_result.scalars().all()

#             # Create metadata dict
#             metadata_dict = {meta.key: meta.value for meta in metadata_entries}

#             formatted_results.append({
#                 "content": chunk.content,
#                 "metadata": metadata_dict
#             })

#         return formatted_results


# async def add_ltm_entry(user_id: str, entry: dict) -> None:
#     """Add a structured long-term memory entry."""
#     async with AsyncSessionLocal() as session:
#         # Convert user_id string to int
#         user_id_int = int(user_id)

#         # Create the memory chunk
#         chunk_data = {
#             "user_id": user_id_int,  # Now using integer
#             "content": entry.get("content"),
#             # Use timezone-aware datetime
#             "created_at": datetime.now(timezone.utc)
#         }
#         chunk = await add_record(session, MemoryChunk, chunk_data)

#         # Add metadata entries
#         metadata_entries = [
#             {"chunk_id": chunk.id, "key": "type", "value": "ltm"},
#             {"chunk_id": chunk.id, "key": "timestamp",
#              "value": datetime.now(timezone.utc).isoformat()}  # Use timezone-naive datetime
#         ]

#         # Add any additional metadata from entry
#         for key, value in entry.items():
#             if key != "content":
#                 metadata_entries.append({
#                     "chunk_id": chunk.id,
#                     "key": key,
#                     "value": str(value)
#                 })

#         for metadata in metadata_entries:
#             await add_record(session, MemoryMetadata, metadata)


# async def validate_memory_data() -> Dict[str, any]:
#     """
#     Validate memory data integrity and identify issues.

#     Returns:
#         Dict containing validation results and statistics
#     """
#     async with AsyncSessionLocal() as session:
#         results = {
#             "orphaned_chunks": [],
#             "orphaned_metadata": [],
#             "inconsistent_metadata": [],
#             "statistics": {}
#         }

#         # Find memory chunks without user_id
#         stmt = select(MemoryChunk).where(
#             MemoryChunk.user_id.is_(None) | (MemoryChunk.user_id == 0)
#         )
#         result = await session.execute(stmt)
#         orphaned_chunks = result.scalars().all()
#         results["orphaned_chunks"] = [
#             {"id": chunk.id, "user_id": chunk.user_id,
#                 "created_at": chunk.created_at}
#             for chunk in orphaned_chunks
#         ]

#         # Find orphaned metadata (no corresponding chunk)
#         stmt = (
#             select(MemoryMetadata)
#             .outerjoin(MemoryChunk, MemoryMetadata.chunk_id == MemoryChunk.id)
#             .where(MemoryChunk.id.is_(None))
#         )
#         result = await session.execute(stmt)
#         orphaned_metadata = result.scalars().all()
#         results["orphaned_metadata"] = [
#             {"id": meta.id, "chunk_id": meta.chunk_id,
#                 "key": meta.key, "value": meta.value}
#             for meta in orphaned_metadata
#         ]

#         # Find inconsistent metadata patterns
#         stmt = (
#             select(MemoryMetadata.chunk_id)
#             .group_by(MemoryMetadata.chunk_id)
#             .having(
#                 (func.count(case((MemoryMetadata.key == "conversation_id", 1))) == 0) |
#                 (func.count(case((MemoryMetadata.key == "type", 1))) == 0) |
#                 (func.count(case((MemoryMetadata.key == "last_updated", 1))) == 0)
#             )
#         )
#         result = await session.execute(stmt)
#         inconsistent_chunks = result.scalars().all()
#         results["inconsistent_metadata"] = list(inconsistent_chunks)

#         # Get statistics
#         total_chunks = await session.execute(select(func.count(MemoryChunk.id)))
#         total_metadata = await session.execute(select(func.count(MemoryMetadata.id)))
#         users_with_data = await session.execute(
#             select(func.count(func.distinct(MemoryChunk.user_id)))
#         )

#         results["statistics"] = {
#             "total_chunks": total_chunks.scalar(),
#             "total_metadata": total_metadata.scalar(),
#             "users_with_data": users_with_data.scalar(),
#             "orphaned_chunks_count": len(results["orphaned_chunks"]),
#             "orphaned_metadata_count": len(results["orphaned_metadata"]),
#             "inconsistent_metadata_count": len(results["inconsistent_metadata"])
#         }

#         return results


# async def get_memory_data_summary() -> Dict[str, any]:
#     """
#     Get a comprehensive summary of memory data state.

#     Returns:
#         Dict containing data summary and statistics
#     """
#     async with AsyncSessionLocal() as session:
#         # Get basic statistics
#         total_chunks = await session.execute(select(func.count(MemoryChunk.id)))
#         total_metadata = await session.execute(select(func.count(MemoryMetadata.id)))

#         # Get user distribution
#         user_distribution = await session.execute(
#             select(MemoryChunk.user_id, func.count(MemoryChunk.id))
#             .group_by(MemoryChunk.user_id)
#             .order_by(MemoryChunk.user_id)
#         )
#         user_distribution = user_distribution.all()

#         # Get metadata type distribution
#         metadata_types = await session.execute(
#             select(MemoryMetadata.key, func.count(MemoryMetadata.id))
#             .group_by(MemoryMetadata.key)
#             .order_by(func.count(MemoryMetadata.id).desc())
#         )
#         metadata_types = metadata_types.all()

#         # Get recent activity
#         recent_chunks = await session.execute(
#             select(MemoryChunk)
#             .order_by(desc(MemoryChunk.created_at))
#             .limit(10)
#         )
#         recent_chunks = recent_chunks.scalars().all()

#         return {
#             "statistics": {
#                 "total_chunks": total_chunks.scalar(),
#                 "total_metadata": total_metadata.scalar(),
#                 "unique_users": len([u for u in user_distribution if u[0] is not None and u[0] != 0])
#             },
#             "user_distribution": [
#                 {"user_id": user_id, "chunk_count": count}
#                 for user_id, count in user_distribution
#             ],
#             "metadata_types": [
#                 {"key": key, "count": count}
#                 for key, count in metadata_types
#             ],
#             "recent_chunks": [
#                 {
#                     "id": chunk.id,
#                     "user_id": chunk.user_id,
#                     "created_at": chunk.created_at,
#                     "content_preview": chunk.content[:50] if chunk.content else None
#                 }
#                 for chunk in recent_chunks
#             ]
#         }
