"""
LTM Optimization Configuration

This module provides configuration settings for the LTM optimization system.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


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
                "concise": ["just", "only", "simple", "quick"]
            }

        if self.topic_preference_keywords is None:
            self.topic_preference_keywords = {
                "work": ["meeting", "project", "deadline", "work", "office", "job"],
                "personal": ["family", "home", "personal", "private", "life"],
                "health": ["exercise", "diet", "health", "wellness", "fitness"],
                "finance": ["budget", "money", "expense", "investment", "finance"],
                "travel": ["trip", "vacation", "travel", "hotel", "flight"]
            }

        if self.tool_preference_patterns is None:
            self.tool_preference_patterns = [
                "tool", "success", "error", "created", "deleted", "updated"
            ]

        if self.response_format_indicators is None:
            self.response_format_indicators = {
                "detailed": ["explain", "tell me more", "what do you mean", "how does this work"],
                "concise": ["just", "only", "simple", "quick", "brief"],
                "structured": ["list", "steps", "organize", "categorize"],
                "visual": ["show me", "display", "picture", "diagram"]
            }

        # Initialize Phase 3 enhanced settings if not provided
        if self.memory_type_importance_boost is None:
            self.memory_type_importance_boost = {
                "preference": 1.0,      # User preferences are important
                "pattern": 0.8,          # Behavioral patterns are valuable
                "habit": 0.7,            # Habits show consistency
                "communication": 0.6,    # Communication style is useful
                "learning": 0.5,         # Learning patterns are helpful
                "tool_usage": 0.4,       # Tool usage patterns are moderate
                "interest": 0.3,         # Topic interests are lower priority
                "general": 0.0           # General insights get no boost
            }

        if self.category_importance_boost is None:
            self.category_importance_boost = {
                "work": 0.5,             # Work-related memories are important
                "health": 0.4,           # Health-related memories are valuable
                "finance": 0.3,           # Finance-related memories are useful
                "personal": 0.2,          # Personal memories are moderate
                "education": 0.1,         # Education-related memories are helpful
                "general": 0.0            # General category gets no boost
            }

        if self.priority_tags_for_importance is None:
            self.priority_tags_for_importance = [
                "important", "urgent", "critical", "preference", "habit", "pattern"
            ]

        if self.tag_suggestion_fallback_tags is None:
            self.tag_suggestion_fallback_tags = [
                "general", "miscellaneous", "conversation", "insight"
            ]

    def get_memory_creation_keywords(self) -> List[str]:
        """Get keywords that always trigger memory creation"""
        return [
            "remember this", "save this", "note this", "keep this in mind",
            "important", "urgent", "critical", "preference", "habit", "pattern"
        ]

    def get_personal_pattern_keywords(self) -> List[str]:
        """Get keywords that indicate personal information"""
        return [
            "i prefer", "i like", "i dislike", "i always", "i never",
            "my preference", "my habit", "my routine", "i work", "i live",
            "i usually", "i typically", "i tend to", "i avoid"
        ]

    def get_learning_pattern_keywords(self) -> List[str]:
        """Get keywords that indicate learning moments"""
        return [
            "learned", "figured out", "discovered", "realized",
            "now i know", "i understand", "this helps"
        ]
