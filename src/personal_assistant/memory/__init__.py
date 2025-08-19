"""
Memory module for agent's persistent storage and retrieval capabilities.
"""

# Configure module logger
from ..config.logging_config import get_logger

# Import context utilities
from .context_utils import apply_context_limits, truncate_context_blocks

logger = get_logger("memory")

__all__ = [
    "apply_context_limits",
    "truncate_context_blocks"
]
