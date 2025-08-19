"""
LTM Optimization Module

This module provides comprehensive long-term memory optimization capabilities
including learning, context management, and memory lifecycle management.
"""

# Import main learning manager
from .learning_manager import LTMLearningManager

# Import consolidated modules
from .learning import ConversationPatternLearner, UserPreferenceLearner, get_learners
from .context_management import (
    ContextOptimizationManager,
    MemoryContext,
    TemporalContext,
    SpatialContext,
    SocialContext,
    EnvironmentalContext,
    create_temporal_context,
    get_context_manager
)
from .memory_lifecycle import (
    MemoryLifecycleManager,
    MemoryConsolidator,
    get_lifecycle_manager,
    get_consolidator,
    get_lifecycle_components
)

# Import other essential modules
from .llm_memory_creator import LLMMemoryCreator
from .smart_retriever import SmartLTMRetriever
from .config import LTMConfig

# Configure module logger
from ...config.logging_config import get_logger
logger = get_logger("ltm_optimization")

__all__ = [
    # Main manager
    "LTMLearningManager",

    # Learning components
    "ConversationPatternLearner",
    "UserPreferenceLearner",
    "get_learners",

    # Context management
    "ContextOptimizationManager",
    "MemoryContext",
    "TemporalContext",
    "SpatialContext",
    "SocialContext",
    "EnvironmentalContext",
    "create_temporal_context",
    "get_context_manager",

    # Memory lifecycle
    "MemoryLifecycleManager",
    "MemoryConsolidator",
    "get_lifecycle_manager",
    "get_consolidator",
    "get_lifecycle_components",

    # Core functionality
    "LLMMemoryCreator",
    "SmartLTMRetriever",
    "LTMConfig"
]
