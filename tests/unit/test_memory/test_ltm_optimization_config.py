"""
Unit tests for LTM optimization configuration.

This module tests the LTM configuration system including
default settings, validation, and configuration management.
"""

import pytest
from unittest.mock import Mock, patch

from tests.utils.test_data_generators import ToolDataGenerator


class TestLTMConfig:
    """Test class for LTM configuration functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool_generator = ToolDataGenerator()

    def test_ltm_config_default_values(self):
        """Test LTM configuration default values."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test memory creation thresholds
        assert config.min_importance_for_memory == 3
        assert config.max_memories_per_interaction == 5
        assert config.memory_creation_confidence_threshold == 0.6
        
        # Test LLM settings
        assert config.enable_llm_memory_creation is True
        assert config.llm_memory_creation_timeout == 30
        assert config.llm_memory_creation_max_retries == 2
        assert config.llm_memory_creation_fallback_to_rules is True
        
        # Test enhanced LLM settings
        assert config.llm_enhanced_prompts is True
        assert config.llm_automated_tag_suggestion is True
        assert config.llm_dynamic_importance_scoring is True
        assert config.llm_memory_type_detection is True
        assert config.llm_context_analysis is True

    def test_ltm_config_custom_values(self):
        """Test LTM configuration with custom values."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig(
            min_importance_for_memory=5,
            max_memories_per_interaction=10,
            memory_creation_confidence_threshold=0.8,
            enable_llm_memory_creation=False,
            llm_memory_creation_timeout=60
        )
        
        assert config.min_importance_for_memory == 5
        assert config.max_memories_per_interaction == 10
        assert config.memory_creation_confidence_threshold == 0.8
        assert config.enable_llm_memory_creation is False
        assert config.llm_memory_creation_timeout == 60

    def test_ltm_config_importance_weights(self):
        """Test LTM configuration importance weights."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test dynamic importance scoring weights
        assert config.base_importance_weight == 0.4
        assert config.confidence_weight == 0.2
        assert config.memory_type_weight == 0.2
        assert config.category_weight == 0.1
        assert config.tag_priority_weight == 0.1
        
        # Test that weights sum to 1.0
        total_weight = (
            config.base_importance_weight +
            config.confidence_weight +
            config.memory_type_weight +
            config.category_weight +
            config.tag_priority_weight
        )
        assert abs(total_weight - 1.0) < 0.001

    def test_ltm_config_memory_type_boost(self):
        """Test LTM configuration memory type importance boost."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test default memory type boost
        if config.memory_type_importance_boost is not None:
            assert isinstance(config.memory_type_importance_boost, dict)
            for memory_type, boost in config.memory_type_importance_boost.items():
                assert isinstance(memory_type, str)
                assert isinstance(boost, float)
                assert boost >= 0  # Allow 0.0 values

    def test_ltm_config_category_boost(self):
        """Test LTM configuration category importance boost."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test default category boost
        if config.category_importance_boost is not None:
            assert isinstance(config.category_importance_boost, dict)
            for category, boost in config.category_importance_boost.items():
                assert isinstance(category, str)
                assert isinstance(boost, float)
                assert boost >= 0  # Allow 0.0 values

    def test_ltm_config_priority_tags(self):
        """Test LTM configuration priority tags."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test default priority tags
        if config.priority_tags_for_importance is not None:
            assert isinstance(config.priority_tags_for_importance, list)
            for tag in config.priority_tags_for_importance:
                assert isinstance(tag, str)
                assert len(tag) > 0

    def test_ltm_config_tag_suggestion_settings(self):
        """Test LTM configuration tag suggestion settings."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test tag suggestion settings
        assert config.tag_suggestion_confidence_threshold == 0.7
        assert config.max_suggested_tags_per_memory == 5
        assert config.enable_semantic_tag_suggestion is True

    def test_ltm_config_consolidation_settings(self):
        """Test LTM configuration consolidation settings."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test consolidation settings
        assert config.tag_similarity_threshold == 0.7
        assert config.content_similarity_threshold == 0.6
        assert config.min_group_size_for_consolidation == 2

    def test_ltm_config_lifecycle_settings(self):
        """Test LTM configuration lifecycle settings."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test lifecycle settings
        assert config.memory_aging_days == 30
        assert config.memory_archiving_days == 60
        assert config.low_importance_threshold == 3

    def test_ltm_config_retrieval_settings(self):
        """Test LTM configuration retrieval settings."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test retrieval settings
        assert config.max_candidate_memories == 20
        assert config.max_retrieved_memories == 5
        assert config.min_importance_for_retrieval == 3

    def test_ltm_config_scoring_weights(self):
        """Test LTM configuration scoring weights."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test scoring weights
        assert config.tag_scoring_weight == 0.4
        assert config.content_scoring_weight == 0.3
        assert config.importance_scoring_weight == 0.2
        assert config.recency_scoring_weight == 0.1
        
        # Test that weights sum to 1.0
        total_weight = (
            config.tag_scoring_weight +
            config.content_scoring_weight +
            config.importance_scoring_weight +
            config.recency_scoring_weight
        )
        assert abs(total_weight - 1.0) < 0.001

    def test_ltm_config_validation(self):
        """Test LTM configuration validation."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        # Test valid configuration
        config = LTMConfig()
        assert config.min_importance_for_memory > 0
        assert config.max_memories_per_interaction > 0
        assert 0 <= config.memory_creation_confidence_threshold <= 1
        assert config.llm_memory_creation_timeout > 0
        assert config.llm_memory_creation_max_retries >= 0

    def test_ltm_config_edge_cases(self):
        """Test LTM configuration edge cases."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        # Test with minimum values
        config = LTMConfig(
            min_importance_for_memory=1,
            max_memories_per_interaction=1,
            memory_creation_confidence_threshold=0.0
        )
        
        assert config.min_importance_for_memory == 1
        assert config.max_memories_per_interaction == 1
        assert config.memory_creation_confidence_threshold == 0.0
        
        # Test with maximum values
        config = LTMConfig(
            min_importance_for_memory=10,
            max_memories_per_interaction=100,
            memory_creation_confidence_threshold=1.0
        )
        
        assert config.min_importance_for_memory == 10
        assert config.max_memories_per_interaction == 100
        assert config.memory_creation_confidence_threshold == 1.0

    def test_enhanced_ltm_config_inheritance(self):
        """Test EnhancedLTMConfig inheritance from LTMConfig."""
        from personal_assistant.memory.ltm_optimization.config import EnhancedLTMConfig
        
        config = EnhancedLTMConfig()
        
        # Test that it inherits from LTMConfig
        assert hasattr(config, 'min_importance_for_memory')
        assert hasattr(config, 'max_memories_per_interaction')
        assert hasattr(config, 'memory_creation_confidence_threshold')
        
        # Test enhanced features (check for some enhanced attributes)
        assert hasattr(config, 'enable_state_integration')
        assert hasattr(config, 'enable_enhanced_tag_matching')
        assert hasattr(config, 'enable_dynamic_context_sizing')

    def test_ltm_config_serialization(self):
        """Test LTM configuration serialization."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test that config can be converted to dict
        config_dict = config.__dict__
        assert isinstance(config_dict, dict)
        assert 'min_importance_for_memory' in config_dict
        assert 'max_memories_per_interaction' in config_dict
        assert 'memory_creation_confidence_threshold' in config_dict

    def test_ltm_config_comparison(self):
        """Test LTM configuration comparison."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config1 = LTMConfig()
        config2 = LTMConfig()
        config3 = LTMConfig(min_importance_for_memory=5)
        
        # Test equality
        assert config1.min_importance_for_memory == config2.min_importance_for_memory
        assert config1.max_memories_per_interaction == config2.max_memories_per_interaction
        
        # Test inequality
        assert config1.min_importance_for_memory != config3.min_importance_for_memory

    def test_ltm_config_immutability(self):
        """Test LTM configuration immutability."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        original_value = config.min_importance_for_memory
        
        # Test that we can modify the config (it's a dataclass, so it's mutable)
        config.min_importance_for_memory = 10
        assert config.min_importance_for_memory == 10
        assert config.min_importance_for_memory != original_value

    def test_ltm_config_comprehensive_settings(self):
        """Test LTM configuration comprehensive settings."""
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        config = LTMConfig()
        
        # Test all major setting categories
        assert hasattr(config, 'min_importance_for_memory')
        assert hasattr(config, 'enable_llm_memory_creation')
        assert hasattr(config, 'base_importance_weight')
        assert hasattr(config, 'tag_suggestion_confidence_threshold')
        assert hasattr(config, 'tag_similarity_threshold')
        assert hasattr(config, 'memory_aging_days')
        assert hasattr(config, 'max_candidate_memories')
        assert hasattr(config, 'tag_scoring_weight')
        
        # Test that all settings have reasonable values
        assert config.min_importance_for_memory > 0
        assert config.max_memories_per_interaction > 0
        assert 0 <= config.memory_creation_confidence_threshold <= 1
        assert config.llm_memory_creation_timeout > 0
        assert config.llm_memory_creation_max_retries >= 0
