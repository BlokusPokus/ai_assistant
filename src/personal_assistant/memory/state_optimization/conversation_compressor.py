"""
Conversation history compression for intelligent memory management.

This module provides intelligent compression of conversation history by:
- Removing duplicate tool calls
- Filtering out failed attempts after successful ones
- Grouping similar operations
- Removing redundant assistant messages
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationCompressor:
    """Compresses conversation history by removing redundancy and failed attempts"""

    def __init__(self, min_history_length: int = 10):
        """
        Initialize the conversation compressor.

        Args:
            min_history_length: Minimum length before compression is applied
        """
        self.min_history_length = min_history_length

    def compress_conversation_history(self, history: List[dict]) -> List[dict]:
        """
        Compress conversation history intelligently.

        Args:
            history: List of conversation history items

        Returns:
            Compressed conversation history
        """
        if len(history) <= self.min_history_length:
            logger.debug(
                f"No compression needed for history of length {len(history)}")
            return history

        logger.info(
            f"Compressing conversation history from {len(history)} to optimized size")

        # Step 1: Remove duplicate tool calls
        deduplicated = self._remove_duplicate_tool_calls(history)
        logger.debug(f"After deduplication: {len(deduplicated)} items")

        # Step 2: Filter out failed attempts after successful ones
        filtered = self._filter_failed_attempts(deduplicated)
        logger.debug(f"After filtering: {len(filtered)} items")

        # Step 3: Group similar operations
        grouped = self._group_similar_operations(filtered)
        logger.debug(f"After grouping: {len(grouped)} items")

        # Step 4: Remove redundant assistant messages
        cleaned = self._remove_redundant_assistant_messages(grouped)
        logger.debug(f"After cleaning: {len(cleaned)} items")

        compression_ratio = len(history) / max(len(cleaned), 1)
        logger.info(
            f"Compression complete: {compression_ratio:.2f}x reduction")

        return cleaned

    def _remove_duplicate_tool_calls(self, history: List[dict]) -> List[dict]:
        """
        Remove duplicate tool calls with same parameters.

        Args:
            history: Conversation history items

        Returns:
            History with duplicate tool calls removed
        """
        seen_tools = {}
        compressed = []

        for item in history:
            if item.get("role") == "tool":
                tool_key = self._create_tool_key(item)

                if tool_key not in seen_tools:
                    # First occurrence of this tool call
                    seen_tools[tool_key] = item
                    compressed.append(item)
                else:
                    # Update with latest result, but don't add duplicate
                    seen_tools[tool_key] = item
                    # Replace the previous occurrence
                    for i, existing_item in enumerate(compressed):
                        if (existing_item.get("role") == "tool" and
                                self._create_tool_key(existing_item) == tool_key):
                            compressed[i] = item
                            break
            else:
                compressed.append(item)

        return compressed

    def _create_tool_key(self, item: dict) -> str:
        """
        Create a unique key for a tool call.

        Args:
            item: Tool call item

        Returns:
            Unique key for the tool call
        """
        tool_name = item.get("name", "")
        content = str(item.get("content", ""))

        # Extract meaningful parameters from content
        if "Error" in content:
            # For errors, include error type
            error_type = self._extract_error_type(content)
            return f"{tool_name}:error:{error_type}"
        else:
            # For successful calls, include success indicator
            return f"{tool_name}:success"

    def _extract_error_type(self, content: str) -> str:
        """
        Extract error type from error content.

        Args:
            content: Error content string

        Returns:
            Categorized error type
        """
        content_lower = content.lower()

        if "validation" in content_lower:
            return "validation_error"
        elif "not found" in content_lower or "undefined" in content_lower:
            return "not_found_error"
        elif "permission" in content_lower or "access" in content_lower:
            return "permission_error"
        elif "timeout" in content_lower or "async" in content_lower:
            return "execution_error"
        else:
            return "general_error"

    def _filter_failed_attempts(self, history: List[dict]) -> List[dict]:
        """
        Filter out failed attempts after successful ones.

        Args:
            history: Conversation history items

        Returns:
            History with failed attempts filtered
        """
        tool_results = {}
        filtered = []

        for item in history:
            if item.get("role") == "tool":
                tool_name = item.get("name", "")
                content = str(item.get("content", ""))

                if "Error" in content:
                    # Only keep errors if we don't have a successful result
                    if (tool_name not in tool_results or
                            "Error" in str(tool_results[tool_name].get("content", ""))):
                        filtered.append(item)
                        tool_results[tool_name] = item
                else:
                    # Successful result - replace any previous errors
                    tool_results[tool_name] = item
                    # Remove previous error for this tool
                    filtered = [item for item in filtered if not (
                        item.get("role") == "tool" and
                        item.get("name") == tool_name and
                        "Error" in str(item.get("content", ""))
                    )]
                    filtered.append(item)
            else:
                filtered.append(item)

        return filtered

    def _group_similar_operations(self, history: List[dict]) -> List[dict]:
        """
        Group similar operations to reduce redundancy.

        Args:
            history: Conversation history items

        Returns:
            History with similar operations grouped
        """
        # For now, return as-is. This can be enhanced later with semantic grouping
        return history

    def _remove_redundant_assistant_messages(self, history: List[dict]) -> List[dict]:
        """
        Remove redundant assistant messages.

        Args:
            history: Conversation history items

        Returns:
            History with redundant assistant messages removed
        """
        cleaned = []
        last_assistant_content = None

        for item in history:
            if item.get("role") == "assistant":
                content = item.get("content", "")

                # Skip if this is essentially the same as the last assistant message
                if (last_assistant_content and
                        self._is_similar_content(content, last_assistant_content)):
                    continue

                last_assistant_content = content
                cleaned.append(item)
            else:
                cleaned.append(item)

        return cleaned

    def _is_similar_content(self, content1: str, content2: str) -> bool:
        """
        Check if two content strings are similar.

        Args:
            content1: First content string
            content2: Second content string

        Returns:
            True if content is similar
        """
        # Simple similarity check - can be enhanced with semantic analysis
        if not content1 or not content2:
            return False

        # Normalize content
        norm1 = content1.lower().strip()
        norm2 = content2.lower().strip()

        # Check for exact match
        if norm1 == norm2:
            return True

        # Check for high similarity (one contains the other)
        if len(norm1) > 20 and len(norm2) > 20:
            if norm1 in norm2 or norm2 in norm1:
                return True

        # Check for tool usage similarity
        if "tool" in norm1 and "tool" in norm2:
            # Extract tool names
            tools1 = self._extract_tool_names(norm1)
            tools2 = self._extract_tool_names(norm2)

            if tools1 and tools2 and tools1 == tools2:
                return True

        return False

    def _extract_tool_names(self, content: str) -> List[str]:
        """
        Extract tool names from content.

        Args:
            content: Content string

        Returns:
            List of tool names found
        """
        # Simple extraction - look for "tool_name" patterns
        import re
        tool_pattern = r'(\w+)_tool'
        matches = re.findall(tool_pattern, content)
        return list(set(matches))

    def get_compression_stats(self, original_history: List[dict], compressed_history: List[dict]) -> Dict[str, Any]:
        """
        Get statistics about the compression operation.

        Args:
            original_history: Original conversation history
            compressed_history: Compressed conversation history

        Returns:
            Dictionary with compression statistics
        """
        original_length = len(original_history)
        compressed_length = len(compressed_history)

        if original_length == 0:
            return {
                "original_length": 0,
                "compressed_length": 0,
                "compression_ratio": 1.0,
                "reduction_percentage": 0.0
            }

        compression_ratio = original_length / compressed_length
        reduction_percentage = (
            (original_length - compressed_length) / original_length) * 100

        return {
            "original_length": original_length,
            "compressed_length": compressed_length,
            "compression_ratio": compression_ratio,
            "reduction_percentage": reduction_percentage,
            "timestamp": datetime.now().isoformat()
        }
