"""
Context management utilities for handling memory block size limits.

This module provides functions for managing context size limits and truncating
memory blocks to fit within specified constraints. These utilities are used
by the agent runner and other memory components to ensure efficient memory usage.
"""

from typing import List, Dict

from sqlalchemy import select

from personal_assistant.database.models.memory_chunk import MemoryChunk
from personal_assistant.database.models.memory_metadata import MemoryMetadata
from personal_assistant.database.session import AsyncSessionLocal


def apply_context_limits(memory_blocks: List[dict], max_length: int) -> None:
    """
    Apply limits to context blocks before injection.

    Args:
        memory_blocks: List of memory block dictionaries
        max_length: Maximum total content length allowed
    """
    # Limit total context size
    total_content_length = sum(len(block.get("content", ""))
                               for block in memory_blocks)

    if total_content_length > max_length:
        # Truncate content to fit within limits
        truncate_context_blocks(memory_blocks, max_length)


def truncate_context_blocks(memory_blocks: List[dict], max_length: int) -> None:
    """
    Truncate context blocks to fit within size limits.

    Args:
        memory_blocks: List of memory block dictionaries (will be modified in-place)
        max_length: Maximum total content length allowed
    """
    current_length = 0
    truncated_blocks = []

    for block in memory_blocks:
        content = block.get("content", "")
        content_length = len(content)

        if current_length + content_length <= max_length:
            truncated_blocks.append(block)
            current_length += content_length
        else:
            # Truncate this block to fit
            remaining_length = max_length - current_length
            if remaining_length > 100:  # Only keep if we can keep meaningful content
                truncated_content = content[:remaining_length] + "..."
                truncated_blocks.append({
                    **block,
                    "content": truncated_content,
                    "truncated": True
                })
            break

    # Replace the original list with truncated blocks
    memory_blocks.clear()
    memory_blocks.extend(truncated_blocks)


# async def get_optimization_statistics(user_id: str = None, conversation_id: str = None) -> Dict[str, any]:
#     """
#     Get statistics about state optimization effectiveness.

#     Args:
#         user_id: Optional user ID to filter results
#         conversation_id: Optional conversation ID to filter results

#     Returns:
#         Dictionary containing optimization statistics
#     """
#     async with AsyncSessionLocal() as session:
#         # Build base query for chunks with optimization metadata
#         base_query = (
#             select(MemoryChunk)
#             .join(MemoryMetadata, MemoryChunk.id == MemoryMetadata.chunk_id)
#             .where(MemoryMetadata.key == "type")
#             .where(MemoryMetadata.value == "state")
#         )

#         if user_id:
#             base_query = base_query.where(MemoryChunk.user_id == int(user_id))

#         # Get all state chunks
#         result = await session.execute(base_query)
#         chunks = result.scalars().all()

#         # Process optimization data
#         optimization_stats = {
#             "total_states": 0,
#             "optimized_states": 0,
#             "fallback_saves": 0,
#             "total_conversation_items_saved": 0,
#             "total_context_items_saved": 0,
#             "total_conversation_items_original": 0,
#             "total_context_items_original": 0,
#             "average_compression_ratio": 0.0,
#             "optimization_failure_rate": 0.0,
#             "recent_optimizations": []
#         }

#         for chunk in chunks:
#             # Get all metadata for this chunk
#             chunk_metadata_result = await session.execute(
#                 select(MemoryMetadata)
#                 .where(MemoryMetadata.chunk_id == chunk.id)
#             )
#             chunk_metadata = {
#                 meta.key: meta.value for meta in chunk_metadata_result.scalars()}

#             # Filter by conversation_id if specified
#             if conversation_id and chunk_metadata.get("conversation_id") != conversation_id:
#                 continue

#             if "optimization_applied" in chunk_metadata:
#                 optimization_stats["optimized_states"] += 1

#                 # Get size information
#                 orig_conv = int(chunk_metadata.get(
#                     "original_conversation_length", 0))
#                 opt_conv = int(chunk_metadata.get(
#                     "optimized_conversation_length", 0))
#                 orig_context = int(chunk_metadata.get(
#                     "original_context_length", 0))
#                 opt_context = int(chunk_metadata.get(
#                     "optimized_context_length", 0))

#                 optimization_stats["total_conversation_items_original"] += orig_conv
#                 optimization_stats["total_conversation_items_saved"] += opt_conv
#                 optimization_stats["total_context_items_original"] += orig_context
#                 optimization_stats["total_context_items_saved"] += opt_context

#                 # Add to recent optimizations
#                 optimization_stats["recent_optimizations"].append({
#                     "chunk_id": chunk.id,
#                     "conversation_id": chunk_metadata.get("conversation_id"),
#                     "timestamp": chunk.created_at.isoformat(),
#                     "conversation_reduction": orig_conv - opt_conv,
#                     "context_reduction": orig_context - opt_context,
#                     "total_reduction": (orig_conv + orig_context) - (opt_conv + opt_context)
#                 })

#             elif "fallback_save" in chunk_metadata:
#                 optimization_stats["fallback_saves"] += 1

#             optimization_stats["total_states"] += 1

#         # Calculate derived statistics
#         if optimization_stats["total_states"] > 0:
#             optimization_stats["optimization_failure_rate"] = (
#                 optimization_stats["fallback_saves"] /
#                 optimization_stats["total_states"]
#             )

#         if optimization_stats["total_conversation_items_original"] > 0:
#             optimization_stats["average_compression_ratio"] = (
#                 optimization_stats["total_conversation_items_original"] /
#                 max(optimization_stats["total_conversation_items_saved"], 1)
#             )

#         # Sort recent optimizations by timestamp (newest first)
#         optimization_stats["recent_optimizations"].sort(
#             key=lambda x: x["timestamp"], reverse=True
#         )
#         optimization_stats["recent_optimizations"] = optimization_stats["recent_optimizations"][:10]

#         # Calculate total savings
#         total_original = (optimization_stats["total_conversation_items_original"] +
#                           optimization_stats["total_context_items_original"])
#         total_saved = (optimization_stats["total_conversation_items_saved"] +
#                        optimization_stats["total_context_items_saved"])

#         if total_original > 0:
#             optimization_stats["total_memory_savings_percentage"] = (
#                 (total_original - total_saved) / total_original * 100
#             )
#         else:
#             optimization_stats["total_memory_savings_percentage"] = 0.0

#         return optimization_stats
