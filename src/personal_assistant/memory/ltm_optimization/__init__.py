"""
LTM Optimization Module

This module provides comprehensive long-term memory optimization capabilities
including learning, context management, and memory lifecycle management.
"""

# Configure module logger
from ...config.logging_config import get_logger
from .analytics import LTMAnalytics
from .config import EnhancedLTMConfig, LTMConfig
from .context_management import (
    ContextOptimizationManager,
    DynamicContextManager,
    EnvironmentalContext,
    MemoryContext,
    SocialContext,
    SpatialContext,
    TemporalContext,
    create_temporal_context,
    get_context_manager,
)

# Import consolidated modules
from .learning import ConversationPatternLearner, UserPreferenceLearner, get_learners

# Import main learning manager
from .learning_manager import LTMLearningManager

# Import other essential modules
from .llm_memory_creator import LLMMemoryCreator
from .memory_lifecycle import (
    EnhancedMemoryLifecycleManager,
    MemoryConsolidator,
    MemoryLifecycleManager,
    get_consolidator,
    get_enhanced_lifecycle_manager,
    get_lifecycle_components,
    get_lifecycle_manager,
)
from .pattern_recognition import PatternRecognitionEngine
from .smart_retriever import SmartLTMRetriever

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
    "DynamicContextManager",
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
    "EnhancedMemoryLifecycleManager",
    "get_lifecycle_manager",
    "get_consolidator",
    "get_lifecycle_components",
    "get_enhanced_lifecycle_manager",
    # Core functionality
    "LLMMemoryCreator",
    "SmartLTMRetriever",
    "LTMConfig",
    "EnhancedLTMConfig",
    "PatternRecognitionEngine",
    "LTMAnalytics",
]
