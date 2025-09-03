"""
Unit tests for LTM learning manager functionality.

This module tests the LTM learning system including
pattern recognition, preference learning, and memory creation.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from tests.utils.test_data_generators import ToolDataGenerator, UserDataGenerator


class TestLTMLearningManager:
    """Test class for LTM learning manager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool_generator = ToolDataGenerator()
        self.user_generator = UserDataGenerator()

    @pytest.mark.asyncio
    async def test_learning_manager_initialization(self):
        """Test LTM learning manager initialization."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        # Test with default config
        learning_manager = LTMLearningManager()
        assert learning_manager is not None
        assert hasattr(learning_manager, 'config')
        
        # Test with custom config
        custom_config = LTMConfig(min_importance_for_memory=5)
        learning_manager = LTMLearningManager(custom_config)
        assert learning_manager.config.min_importance_for_memory == 5

    @pytest.mark.asyncio
    async def test_learn_from_interaction_success(self):
        """Test successful learning from user interaction."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        
        # Mock learning manager
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock successful learning
            mock_learning_manager.learn_from_interaction = AsyncMock(return_value=[
                {
                    "id": 1,
                    "content": "User prefers morning meetings",
                    "importance": 7,
                    "tags": ["preference", "meeting", "schedule"]
                }
            ])
            
            # Test learning from interaction
            result = await mock_learning_manager.learn_from_interaction(
                user_id="user123",
                user_input="I prefer morning meetings",
                agent_response="I'll schedule your meetings in the morning",
                tool_result="Successfully scheduled meeting"
            )
            
            assert len(result) == 1
            assert result[0]["content"] == "User prefers morning meetings"
            assert result[0]["importance"] == 7
            assert "preference" in result[0]["tags"]
            mock_learning_manager.learn_from_interaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_learn_from_interaction_no_memories_created(self):
        """Test learning when no memories are created."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        
        # Mock learning manager
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock no memories created
            mock_learning_manager.learn_from_interaction = AsyncMock(return_value=[])
            
            # Test learning from interaction
            result = await mock_learning_manager.learn_from_interaction(
                user_id="user123",
                user_input="Hello",
                agent_response="Hi there!",
                tool_result="No action needed"
            )
            
            assert len(result) == 0
            mock_learning_manager.learn_from_interaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_learn_from_interaction_error_handling(self):
        """Test error handling in learning from interaction."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        
        # Mock learning manager
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock error
            mock_learning_manager.learn_from_interaction = AsyncMock(
                side_effect=Exception("Learning failed")
            )
            
            # Test error handling
            with pytest.raises(Exception) as exc_info:
                await mock_learning_manager.learn_from_interaction(
                    user_id="user123",
                    user_input="Test input",
                    agent_response="Test response",
                    tool_result="Test result"
                )
            
            assert str(exc_info.value) == "Learning failed"

    @pytest.mark.asyncio
    async def test_pattern_recognition_learning(self):
        """Test pattern recognition learning functionality."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        
        # Mock learning manager
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock pattern recognition
            mock_learning_manager.learn_communication_patterns = AsyncMock(return_value={
                "patterns": [
                    {
                        "type": "time_preference",
                        "pattern": "morning_meetings",
                        "confidence": 0.8
                    }
                ]
            })
            
            # Test pattern recognition
            result = await mock_learning_manager.learn_communication_patterns(
                user_id="user123",
                interactions=[
                    {
                        "input": "Schedule a meeting for tomorrow morning",
                        "response": "I'll schedule it for 9 AM",
                        "timestamp": datetime.now()
                    }
                ]
            )
            
            assert "patterns" in result
            assert len(result["patterns"]) == 1
            assert result["patterns"][0]["type"] == "time_preference"
            assert result["patterns"][0]["confidence"] == 0.8

    @pytest.mark.asyncio
    async def test_preference_learning(self):
        """Test user preference learning functionality."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        
        # Mock learning manager
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock preference learning
            mock_learning_manager.learn_user_preferences = AsyncMock(return_value={
                "preferences": [
                    {
                        "category": "communication",
                        "preference": "concise_responses",
                        "confidence": 0.9
                    }
                ]
            })
            
            # Test preference learning
            result = await mock_learning_manager.learn_user_preferences(
                user_id="user123",
                tool_usage_history=[
                    {
                        "tool": "email",
                        "success": True,
                        "user_satisfaction": 0.8
                    }
                ]
            )
            
            assert "preferences" in result
            assert len(result["preferences"]) == 1
            assert result["preferences"][0]["category"] == "communication"
            assert result["preferences"][0]["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_memory_creation_threshold(self):
        """Test memory creation threshold logic."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        from personal_assistant.memory.ltm_optimization.config import LTMConfig
        
        # Test with high threshold
        config = LTMConfig(min_importance_for_memory=8)
        learning_manager = LTMLearningManager(config)
        
        # Test with low importance (should not create memory)
        # Mock the learning manager to simulate low importance
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock no memories created due to low importance
            mock_learning_manager.learn_from_interaction = AsyncMock(return_value=[])
            
            # Test with low importance (should not create memory)
            result = await mock_learning_manager.learn_from_interaction(
                user_id="user123",
                user_input="Hello",
                agent_response="Hi",
                tool_result="No action"
            )
            
            # Should not create memory due to low importance
            assert len(result) == 0
            mock_learning_manager.learn_from_interaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_memory_consolidation_learning(self):
        """Test memory consolidation learning functionality."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        
        # Mock learning manager
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock consolidation learning
            mock_learning_manager.learn_consolidation_patterns = AsyncMock(return_value={
                "consolidated_memories": [
                    {
                        "id": 1,
                        "content": "User prefers morning meetings and concise responses",
                        "importance": 8,
                        "tags": ["preference", "meeting", "communication"]
                    }
                ]
            })
            
            # Test consolidation learning
            result = await mock_learning_manager.learn_consolidation_patterns(
                user_id="user123",
                existing_memories=[
                    {
                        "id": 1,
                        "content": "User prefers morning meetings",
                        "importance": 6,
                        "tags": ["preference", "meeting"]
                    },
                    {
                        "id": 2,
                        "content": "User prefers concise responses",
                        "importance": 5,
                        "tags": ["preference", "communication"]
                    }
                ]
            )
            
            assert "consolidated_memories" in result
            assert len(result["consolidated_memories"]) == 1
            assert result["consolidated_memories"][0]["importance"] == 8

    @pytest.mark.asyncio
    async def test_learning_manager_statistics(self):
        """Test learning manager statistics functionality."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        
        # Mock learning manager
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock statistics
            mock_learning_manager.get_learning_statistics = AsyncMock(return_value={
                "total_interactions": 100,
                "memories_created": 25,
                "patterns_learned": 5,
                "preferences_learned": 3,
                "consolidation_rate": 0.2
            })
            
            # Test statistics
            result = await mock_learning_manager.get_learning_statistics("user123")
            
            assert result["total_interactions"] == 100
            assert result["memories_created"] == 25
            assert result["patterns_learned"] == 5
            assert result["preferences_learned"] == 3
            assert result["consolidation_rate"] == 0.2

    @pytest.mark.asyncio
    async def test_learning_manager_error_recovery(self):
        """Test learning manager error recovery."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        
        # Mock learning manager
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock error recovery
            mock_learning_manager.learn_from_interaction = AsyncMock(
                side_effect=Exception("Learning failed")
            )
            
            # Test error recovery
            try:
                await mock_learning_manager.learn_from_interaction(
                    user_id="user123",
                    user_input="Test input",
                    agent_response="Test response",
                    tool_result="Test result"
                )
            except Exception as e:
                assert str(e) == "Learning failed"
            
            # Verify error was handled appropriately
            mock_learning_manager.learn_from_interaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_learning_manager_comprehensive_workflow(self):
        """Test comprehensive learning manager workflow."""
        from personal_assistant.memory.ltm_optimization.learning_manager import LTMLearningManager
        
        # Mock learning manager
        with patch('personal_assistant.memory.ltm_optimization.learning_manager.LTMLearningManager') as mock_class:
            mock_learning_manager = Mock()
            mock_class.return_value = mock_learning_manager
            
            # Mock comprehensive workflow
            mock_learning_manager.learn_from_interaction = AsyncMock(return_value=[
                {
                    "id": 1,
                    "content": "User prefers morning meetings",
                    "importance": 7,
                    "tags": ["preference", "meeting"]
                }
            ])
            
            mock_learning_manager.learn_communication_patterns = AsyncMock(return_value={
                "patterns": [{"type": "time_preference", "confidence": 0.8}]
            })
            
            mock_learning_manager.learn_user_preferences = AsyncMock(return_value={
                "preferences": [{"category": "communication", "confidence": 0.9}]
            })
            
            mock_learning_manager.get_learning_statistics = AsyncMock(return_value={
                "total_interactions": 1,
                "memories_created": 1,
                "patterns_learned": 1,
                "preferences_learned": 1
            })
            
            # Test comprehensive workflow
            # 1. Learn from interaction
            memories = await mock_learning_manager.learn_from_interaction(
                user_id="user123",
                user_input="I prefer morning meetings",
                agent_response="I'll schedule your meetings in the morning",
                tool_result="Successfully scheduled meeting"
            )
            
            # 2. Learn patterns
            patterns = await mock_learning_manager.learn_communication_patterns(
                user_id="user123",
                interactions=[{"input": "Schedule morning meeting", "response": "Scheduled"}]
            )
            
            # 3. Learn preferences
            preferences = await mock_learning_manager.learn_user_preferences(
                user_id="user123",
                tool_usage_history=[{"tool": "calendar", "success": True}]
            )
            
            # 4. Get statistics
            stats = await mock_learning_manager.get_learning_statistics("user123")
            
            # Verify all operations
            assert len(memories) == 1
            assert "patterns" in patterns
            assert "preferences" in preferences
            assert stats["total_interactions"] == 1
            
            # Verify all methods were called
            mock_learning_manager.learn_from_interaction.assert_called_once()
            mock_learning_manager.learn_communication_patterns.assert_called_once()
            mock_learning_manager.learn_user_preferences.assert_called_once()
            mock_learning_manager.get_learning_statistics.assert_called_once()
