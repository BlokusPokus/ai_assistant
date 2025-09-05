"""
Metrics logging utilities for monitoring system performance and behavior.

This module provides utilities for logging various types of metrics including
context injection, performance, and error metrics.
"""

from typing import Any, Dict, List

from ..config.logging_config import get_logger

logger = get_logger("metrics")


class MetricsLogger:
    """Handles logging of various system metrics"""

    @staticmethod
    def log_context_metrics(memory_blocks: List[dict], agent_state: Any) -> None:
        """
        Log detailed metrics about context injection for monitoring and debugging.

        Args:
            memory_blocks (List[dict]): The memory blocks that were added
            agent_state (Any): The agent state after context injection
        """
        try:
            # Calculate content statistics
            total_content_length = sum(
                len(block.get("content", "")) for block in memory_blocks
            )
            ltm_blocks = [b for b in memory_blocks if b.get("source") == "ltm"]
            rag_blocks = [b for b in memory_blocks if b.get("source") == "rag"]

            # Log detailed metrics
            logger.debug(f"Context injection metrics:")
            logger.debug(f"  - Total blocks: {len(memory_blocks)}")
            logger.debug(f"  - LTM blocks: {len(ltm_blocks)}")
            logger.debug(f"  - RAG blocks: {len(rag_blocks)}")
            logger.debug(f"  - Total content length: {total_content_length} characters")
            logger.debug(
                f"  - Final memory context size: {len(agent_state.memory_context)}"
            )

            # Log content previews for debugging
            if ltm_blocks:
                ltm_preview = (
                    ltm_blocks[0]["content"][:100] + "..."
                    if len(ltm_blocks[0]["content"]) > 100
                    else ltm_blocks[0]["content"]
                )
                logger.debug(f"  - LTM content preview: {ltm_preview}")

            if rag_blocks:
                rag_preview = (
                    rag_blocks[0]["content"][:100] + "..."
                    if len(rag_blocks[0]["content"]) > 100
                    else rag_blocks[0]["content"]
                )
                logger.debug(f"  - RAG content preview: {rag_preview}")

        except Exception as e:
            logger.warning(f"Failed to log context metrics: {e}")
            # Don't let metrics logging failure affect the main functionality

    @staticmethod
    def log_performance_metrics(operation: str, duration: float, **kwargs) -> None:
        """
        Log performance metrics for various operations.

        Args:
            operation (str): Name of the operation being measured
            duration (float): Duration in seconds
            **kwargs: Additional metrics to log
        """
        try:
            logger.info(f"Performance metrics - {operation}: {duration:.3f}s")

            # Log additional metrics if provided
            for key, value in kwargs.items():
                if isinstance(value, (int, float)):
                    logger.info(f"  - {key}: {value}")
                else:
                    logger.debug(f"  - {key}: {value}")

        except Exception as e:
            logger.warning(f"Failed to log performance metrics: {e}")

    @staticmethod
    def log_error_metrics(error: Exception, context: str, **kwargs) -> None:
        """
        Log error metrics for monitoring and debugging.

        Args:
            error (Exception): The error that occurred
            context (str): Context where the error occurred
            **kwargs: Additional error context
        """
        try:
            logger.error(
                f"Error metrics - {context}: {type(error).__name__}: {str(error)}"
            )

            # Log additional error context if provided
            for key, value in kwargs.items():
                logger.debug(f"  - {key}: {value}")

        except Exception as e:
            logger.warning(f"Failed to log error metrics: {e}")

    @staticmethod
    def log_memory_metrics(memory_stats: Dict[str, Any]) -> None:
        """
        Log memory-related metrics.

        Args:
            memory_stats (Dict[str, Any]): Dictionary containing memory statistics
        """
        try:
            logger.info("Memory metrics:")
            for key, value in memory_stats.items():
                if isinstance(value, (int, float)):
                    logger.info(f"  - {key}: {value}")
                else:
                    logger.debug(f"  - {key}: {value}")

        except Exception as e:
            logger.warning(f"Failed to log memory metrics: {e}")
