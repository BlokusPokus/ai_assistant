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
