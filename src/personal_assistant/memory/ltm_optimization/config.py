"""
LTM Optimization Configuration

This module provides configuration settings for the LTM optimization system.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class LTMConfig:
    """Configuration for LTM optimization system"""

    # Memory creation thresholds
    min_importance_for_memory: int = 3
    max_memories_per_interaction: int = 5
    memory_creation_confidence_threshold: float = 0.6

    # LLM-based memory creation settings
    enable_llm_memory_creation: bool = True
    llm_memory_creation_timeout: int = 30  # seconds
    llm_memory_creation_max_retries: int = 2
    llm_memory_creation_fallback_to_rules: bool = True

    # Enhanced LLM settings for Phase 3
    llm_enhanced_prompts: bool = True
    llm_automated_tag_suggestion: bool = True
    llm_dynamic_importance_scoring: bool = True
    llm_memory_type_detection: bool = True
    llm_context_analysis: bool = True

    # Dynamic importance scoring weights
    base_importance_weight: float = 0.4
    confidence_weight: float = 0.2
    memory_type_weight: float = 0.2
    category_weight: float = 0.1
    tag_priority_weight: float = 0.1

    # Memory type importance adjustments
    memory_type_importance_boost: Dict[str, float] = None

    # Category importance adjustments
    category_importance_boost: Dict[str, float] = None

    # Priority tags for importance boosting
    priority_tags_for_importance: List[str] = None

    # Automated tag suggestion settings
    tag_suggestion_confidence_threshold: float = 0.7
    max_suggested_tags_per_memory: int = 5
    enable_semantic_tag_suggestion: bool = True
    tag_suggestion_fallback_tags: List[str] = None

    # Memory consolidation settings
    tag_similarity_threshold: float = 0.7
    content_similarity_threshold: float = 0.6
    min_group_size_for_consolidation: int = 2

    # Memory lifecycle settings
    memory_aging_days: int = 30
    memory_archiving_days: int = 60
    low_importance_threshold: int = 3
    importance_reduction_on_aging: int = 1

    # Retrieval settings
    max_candidate_memories: int = 20
    max_retrieved_memories: int = 5
    min_importance_for_retrieval: int = 3

    # Context optimization settings
    max_context_length: int = 1000
    max_memories_per_type: int = 3

    # Scoring weights
    tag_scoring_weight: float = 0.4
    content_scoring_weight: float = 0.3
    importance_scoring_weight: float = 0.2
    recency_scoring_weight: float = 0.1

    # Recency boost settings
    very_recent_days: int = 1
    recent_days: int = 7
    somewhat_recent_days: int = 30
    very_recent_boost: float = 0.1
    recent_boost: float = 0.05
    somewhat_recent_boost: float = 0.02

    # Enhanced Smart Retriever settings (Phase 2.1)
    cache_ttl_seconds: int = 300  # 5 minutes default cache TTL
    max_cache_entries: int = 1000  # Maximum cache entries
    min_quality_threshold: float = 0.3  # Minimum relevance score for inclusion
    # Optimal relevance score for top results
    optimal_quality_threshold: float = 0.7

    # Enhanced scoring weights
    phrase_scoring_weight: float = 0.2  # Weight for phrase matching
    state_context_weight: float = 0.15  # Weight for state context relevance
    type_scoring_weight: float = 0.1  # Weight for memory type scoring
    confidence_scoring_weight: float = 0.1  # Weight for confidence score

    # Dynamic Context Management settings (Phase 3.1)
    min_context_length: int = 100  # Minimum context length
    max_context_length: int = 2000  # Maximum context length
    optimal_context_length: int = 800  # Optimal context length
    simple_query_threshold: int = 50  # Threshold for simple queries
    complex_query_threshold: int = 200  # Threshold for complex queries
    focus_boost_multiplier: float = 1.5  # Multiplier for focus area matches
    state_context_weight: float = 0.3  # Weight for state context relevance

    # Pattern detection settings
    communication_style_indicators: Dict[str, List[str]] = None
    topic_preference_keywords: Dict[str, List[str]] = None
    tool_preference_patterns: List[str] = None
    response_format_indicators: Dict[str, List[str]] = None

    def __post_init__(self):
        """Initialize default pattern detection settings if not provided"""
        if self.communication_style_indicators is None:
            self.communication_style_indicators = {
                "formal": ["please", "thank you", "would you mind", "if you could"],
                "casual": ["hey", "cool", "awesome", "thanks"],
                "detailed": ["can you explain", "tell me more", "what do you mean"],
                "concise": ["just", "only", "simple", "quick"],
            }

        if self.topic_preference_keywords is None:
            self.topic_preference_keywords = {
                "work": ["meeting", "project", "deadline", "work", "office", "job"],
                "personal": ["family", "home", "personal", "private", "life"],
                "health": ["exercise", "diet", "health", "wellness", "fitness"],
                "finance": ["budget", "money", "expense", "investment", "finance"],
                "travel": ["trip", "vacation", "travel", "hotel", "flight"],
            }

        if self.tool_preference_patterns is None:
            self.tool_preference_patterns = [
                "tool",
                "success",
                "error",
                "created",
                "deleted",
                "updated",
            ]

        if self.response_format_indicators is None:
            self.response_format_indicators = {
                "detailed": [
                    "explain",
                    "tell me more",
                    "what do you mean",
                    "how does this work",
                ],
                "concise": ["just", "only", "simple", "quick", "brief"],
                "structured": ["list", "steps", "organize", "categorize"],
                "visual": ["show me", "display", "picture", "diagram"],
            }

        # Initialize Phase 3 enhanced settings if not provided
        if self.memory_type_importance_boost is None:
            self.memory_type_importance_boost = {
                "preference": 1.0,  # User preferences are important
                "pattern": 0.8,  # Behavioral patterns are valuable
                "habit": 0.7,  # Habits show consistency
                "communication": 0.6,  # Communication style is useful
                "learning": 0.5,  # Learning patterns are helpful
                "tool_usage": 0.4,  # Tool usage patterns are moderate
                "interest": 0.3,  # Topic interests are lower priority
                "general": 0.0,  # General insights get no boost
            }

        if self.category_importance_boost is None:
            self.category_importance_boost = {
                "work": 0.5,  # Work-related memories are important
                "health": 0.4,  # Health-related memories are valuable
                "finance": 0.3,  # Finance-related memories are useful
                "personal": 0.2,  # Personal memories are moderate
                "education": 0.1,  # Education-related memories are helpful
                "general": 0.0,  # General category gets no boost
            }

        if self.priority_tags_for_importance is None:
            self.priority_tags_for_importance = [
                "important",
                "urgent",
                "critical",
                "preference",
                "habit",
                "pattern",
            ]

        if self.tag_suggestion_fallback_tags is None:
            self.tag_suggestion_fallback_tags = [
                "general",
                "miscellaneous",
                "conversation",
                "insight",
            ]

    def get_memory_creation_keywords(self) -> List[str]:
        """Get keywords that always trigger memory creation"""
        return [
            "remember this",
            "save this",
            "note this",
            "keep this in mind",
            "important",
            "urgent",
            "critical",
            "preference",
            "habit",
            "pattern",
        ]

    def get_personal_pattern_keywords(self) -> List[str]:
        """Get keywords that indicate personal information"""
        return [
            "i prefer",
            "i like",
            "i dislike",
            "i always",
            "i never",
            "my preference",
            "my habit",
            "my routine",
            "i work",
            "i live",
            "i usually",
            "i typically",
            "i tend to",
            "i avoid",
        ]

    def get_learning_pattern_keywords(self) -> List[str]:
        """Get keywords that indicate learning moments"""
        return [
            "learned",
            "figured out",
            "discovered",
            "realized",
            "now i know",
            "i understand",
            "this helps",
        ]


@dataclass
class EnhancedLTMConfig(LTMConfig):
    """Enhanced configuration for improved LTM system with state integration"""

    # Memory creation thresholds (lowered for more active learning)
    min_importance_for_memory: int = 2  # Was 3
    memory_creation_confidence_threshold: float = 0.4  # Was 0.6
    max_memories_per_interaction: int = 8  # Was 5

    # State integration settings
    enable_state_integration: bool = True  # NEW: Integrate with state management
    state_data_weight: float = 0.3  # NEW: Weight for state-based insights
    tool_usage_pattern_weight: float = 0.4  # NEW: Weight for tool patterns

    # Enhanced retrieval settings (NO semantic search)
    enable_enhanced_tag_matching: bool = True
    enhanced_tag_weight: float = 0.4
    content_weight: float = 0.3
    importance_weight: float = 0.2
    recency_weight: float = 0.1

    # Dynamic context sizing
    enable_dynamic_context_sizing: bool = True
    min_context_length: int = 400  # Was fixed 800
    max_context_length: int = 1200  # Was fixed 800
    context_quality_threshold: float = 0.6

    # Memory lifecycle
    enable_smart_consolidation: bool = True
    consolidation_similarity_threshold: float = 0.8
    enable_usage_based_aging: bool = True
    memory_archiving_threshold: float = 0.3

    # State-LTM coordination settings
    enable_state_ltm_coordination: bool = True
    state_context_weight: float = 0.4
    ltm_context_weight: float = 0.6
    coordination_quality_threshold: float = 0.7

    # Pattern recognition from state data
    enable_pattern_recognition: bool = True
    conversation_pattern_weight: float = 0.4
    tool_usage_pattern_weight: float = 0.3
    user_behavior_pattern_weight: float = 0.3
    temporal_pattern_weight: float = 0.2

    # Memory quality validation
    enable_memory_quality_validation: bool = True
    min_memory_quality_score: float = 0.5
    quality_validation_confidence_threshold: float = 0.6

    # Performance optimization
    enable_caching: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes
    enable_query_optimization: bool = True
    max_query_timeout_seconds: int = 10

    # Analytics and monitoring
    enable_analytics: bool = True
    analytics_sampling_rate: float = 0.1  # 10% of operations
    performance_metrics_enabled: bool = True
