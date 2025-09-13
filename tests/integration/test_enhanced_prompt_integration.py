"""
Integration tests for enhanced prompt engineering system.

This module tests the integration between enhanced prompt systems including:
- TaskExecutor and AIEvaluatorPrompts integration
- Metadata system integration
- End-to-end prompt workflows
- Cross-system consistency
- Performance and quality validation
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

from personal_assistant.tools.ai_scheduler.core.executor import TaskExecutor
from personal_assistant.prompts.ai_evaluator_prompts import AIEvaluatorPrompts
from personal_assistant.database.models.ai_tasks import AITask


@pytest.mark.asyncio
class TestEnhancedPromptIntegration:
    """Test class for enhanced prompt system integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.executor = TaskExecutor()
        
        # Create mock AITask
        self.mock_task = Mock(spec=AITask)
        self.mock_task.id = 1
        self.mock_task.title = "Integration Test Reminder"
        self.mock_task.description = "Test reminder for integration testing"
        self.mock_task.task_type = "reminder"
        self.mock_task.schedule_type = "one_time"
        self.mock_task.schedule_config = None
        self.mock_task.user_id = 123
        self.mock_task.ai_context = "Integration test context"
        self.mock_task.created_at = datetime.utcnow()
        self.mock_task.last_run_at = None

        # Create sample AI context for evaluator
        self.sample_ai_context = {
            'event': {
                'title': 'Integration Test Meeting',
                'type': 'meeting',
                'priority': 'high',
                'location': 'Test Conference Room',
                'start_time': '2024-01-15T14:00:00Z',
                'end_time': '2024-01-15T15:00:00Z',
                'description': 'Integration test meeting for prompt systems'
            },
            'timing': {
                'time_until_start_hours': 2.0,
                'is_urgent': False,
                'is_soon': True
            },
            'recurrence': {
                'hint': 'weekly',
                'is_recurring': True,
                'pattern': 'Every Monday at 2 PM'
            },
            'processing': {
                'status': 'pending',
                'last_processed': '2024-01-08T14:00:00Z',
                'days_since_last_processed': 7
            }
        }

    def test_prompt_architecture_consistency(self):
        """Test that both prompt systems use consistent architecture."""
        # Test TaskExecutor prompt
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            executor_prompt = self.executor._create_ai_prompt(self.mock_task, context)
        
        # Test AIEvaluatorPrompts
        evaluator_prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Both should have consistent professional structure
        for prompt in [executor_prompt, evaluator_prompt]:
            assert "🎯" in prompt  # Professional emoji headers
            assert "📅" in prompt  # Time information
            assert "📋" in prompt  # Structured sections
            assert "🚨" in prompt  # Critical rules
            assert "💡" in prompt  # Guidance sections

    def test_metadata_integration_consistency(self):
        """Test that metadata integration is consistent across systems."""
        # Mock enhancements for TaskExecutor
        mock_enhancement = Mock()
        mock_enhancement.title = "Smart Time Parsing"
        mock_enhancement.ai_instructions = "Parse time expressions intelligently"
        
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[mock_enhancement]):
            executor_prompt = self.executor._create_ai_prompt(self.mock_task, context)
        
        # Both systems should handle metadata consistently
        assert "🎯 **AI GUIDANCE & ENHANCEMENTS**:" in executor_prompt
        assert "SMART TIME PARSING" in executor_prompt
        assert "Parse time expressions intelligently" in executor_prompt

    def test_professional_guidelines_consistency(self):
        """Test that professional guidelines are consistent across systems."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            executor_prompt = self.executor._create_ai_prompt(self.mock_task, context)
        
        evaluator_prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Both should have consistent professional guidelines structure
        for prompt in [executor_prompt, evaluator_prompt]:
            assert "🎯 **PROFESSIONAL" in prompt
            assert "🚨 **CRITICAL RULES**:" in prompt
            assert "💡 **" in prompt  # Quality guidelines
            assert "🔄 **" in prompt  # Process guidelines

    def test_response_format_consistency(self):
        """Test that response formats are consistent and professional."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            executor_prompt = self.executor._create_ai_prompt(self.mock_task, context)
        
        evaluator_prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Both should have clear response format guidance
        assert "RESPONSE FORMAT:" in executor_prompt or "RESPONSE QUALITY" in executor_prompt
        assert "📋 RESPONSE FORMAT:" in evaluator_prompt

    @pytest.mark.asyncio
    async def test_error_handling_consistency(self):
        """Test that error handling is consistent across systems."""
        # Test TaskExecutor error handling
        with patch('personal_assistant.tools.ai_scheduler.core.executor.AgentCore') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.run.side_effect = Exception("Test error")
            mock_agent_class.return_value = mock_agent
            
            result = await self.executor.execute_task(self.mock_task)
            
            assert result["success"] is False
            assert "Test error" in result["message"]
            assert "task_id" in result

    def test_context_utilization_consistency(self):
        """Test that context utilization is consistent across systems."""
        # Test TaskExecutor context utilization
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_run_at': '2024-01-14T09:00:00Z',
            'current_time': '2024-01-15T10:30:00Z',
            'notification_channels': ['sms', 'email']
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            executor_prompt = self.executor._create_ai_prompt(self.mock_task, context)
        
        # Should utilize all context elements
        assert "2024-01-15T10:30:00Z" in executor_prompt
        assert "2024-01-14T09:00:00Z" in executor_prompt
        assert "sms, email" in executor_prompt

    def test_quality_assessment_integration(self):
        """Test that quality assessment works across systems."""
        # Test high-quality response
        high_quality_response = """
        I acknowledge this important reminder about the project deadline.
        
        Here's what I understand:
        1. The project deadline is approaching
        2. We need to complete the final review
        3. All stakeholders should be notified
        
        I suggest we:
        • Schedule a final review meeting
        • Prepare the completion report
        • Notify all team members
        
        This is a critical milestone for our project success.
        """
        
        result = self.executor._process_ai_response(self.mock_task, high_quality_response)
        
        assert result["response_quality"]["is_high_quality"] is True
        assert result["response_quality"]["score"] >= 0.6
        assert "quality_indicators" in result

    def test_performance_consistency(self):
        """Test that performance is consistent across prompt systems."""
        import time
        
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Test TaskExecutor performance
        start_time = time.time()
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            for _ in range(50):
                self.executor._create_ai_prompt(self.mock_task, context)
        
        executor_time = time.time() - start_time
        
        # Test AIEvaluatorPrompts performance
        start_time = time.time()
        
        for _ in range(50):
            AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        evaluator_time = time.time() - start_time
        
        # Both should perform reasonably well
        assert executor_time < 2.0, f"TaskExecutor too slow: {executor_time:.2f}s"
        assert evaluator_time < 2.0, f"AIEvaluatorPrompts too slow: {evaluator_time:.2f}s"

    def test_memory_usage_consistency(self):
        """Test that memory usage is reasonable across systems."""
        import sys
        
        # Test TaskExecutor memory usage
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            prompts = []
            for _ in range(100):
                prompt = self.executor._create_ai_prompt(self.mock_task, context)
                prompts.append(prompt)
        
        # Test AIEvaluatorPrompts memory usage
        evaluator_prompts = []
        for _ in range(100):
            prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
            evaluator_prompts.append(prompt)
        
        # Should not consume excessive memory
        total_size = sys.getsizeof(prompts) + sys.getsizeof(evaluator_prompts)
        assert total_size < 10 * 1024 * 1024, f"Memory usage too high: {total_size / 1024 / 1024:.2f}MB"

    def test_concurrent_prompt_creation(self):
        """Test concurrent prompt creation across systems."""
        import asyncio
        import time
        
        async def create_executor_prompt():
            context = {
                'created_at': '2024-01-15T10:30:00Z',
                'current_time': '2024-01-15T10:30:00Z'
            }
            
            with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
                return self.executor._create_ai_prompt(self.mock_task, context)
        
        async def create_evaluator_prompt():
            return AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        async def run_concurrent_tests():
            start_time = time.time()
            
            # Run both systems concurrently
            tasks = []
            for _ in range(20):
                tasks.append(create_executor_prompt())
                tasks.append(create_evaluator_prompt())
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete in reasonable time
            assert execution_time < 5.0, f"Concurrent execution too slow: {execution_time:.2f}s"
            assert len(results) == 40  # 20 of each type
            
            return results
        
        # Run the concurrent test
        results = asyncio.run(run_concurrent_tests())
        
        # All results should be valid prompts
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 100
            assert "🎯" in result

    def test_prompt_customization_consistency(self):
        """Test that prompt customization is consistent across systems."""
        # Test different task types
        task_types = ["reminder", "periodic_task", "automated_task", "custom_task"]
        
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        for task_type in task_types:
            self.mock_task.task_type = task_type
            
            with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
                prompt = self.executor._create_ai_prompt(self.mock_task, context)
            
            # Each task type should have appropriate content
            assert "🎯 AI TASK EXECUTOR" in prompt
            assert task_type.upper() in prompt or task_type in prompt
            assert "🎯 **PROFESSIONAL EXECUTION GUIDELINES**:" in prompt

    def test_metadata_enhancement_integration(self):
        """Test integration with metadata enhancement system."""
        # Mock different enhancement types
        mock_enhancements = [
            Mock(title="Smart Time Parsing", ai_instructions="Parse time expressions intelligently"),
            Mock(title="Context Awareness", ai_instructions="Consider user context and preferences"),
            Mock(title="Workflow Guidance", ai_instructions="Provide step-by-step workflow guidance")
        ]
        
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=mock_enhancements):
            prompt = self.executor._create_ai_prompt(self.mock_task, context)
        
        # Should include all enhancements
        assert "🎯 **AI GUIDANCE & ENHANCEMENTS**:" in prompt
        assert "SMART TIME PARSING" in prompt
        assert "CONTEXT AWARENESS" in prompt
        assert "WORKFLOW GUIDANCE" in prompt
        assert "Parse time expressions intelligently" in prompt
        assert "Consider user context and preferences" in prompt
        assert "Provide step-by-step workflow guidance" in prompt

    def test_response_validation_integration(self):
        """Test response validation integration across systems."""
        # Test various response qualities
        test_responses = [
            ("High quality", """
            I acknowledge this important reminder.
            
            Here's my analysis:
            1. This is a critical task
            2. Immediate action is required
            3. I'll help you succeed
            
            Let's work together to complete this successfully.
            """),
            ("Medium quality", """
            I understand this reminder.
            
            Here are some suggestions:
            1. Review the requirements
            2. Plan your approach
            
            I'm here to help.
            """),
            ("Low quality", "ok")
        ]
        
        for quality_type, response in test_responses:
            result = self.executor._process_ai_response(self.mock_task, response)
            
            assert "response_quality" in result
            assert "extracted_info" in result
            assert "execution_status" in result
            
            if quality_type == "High quality":
                assert result["response_quality"]["is_high_quality"] is True
                assert "quality_indicators" in result
            elif quality_type == "Low quality":
                assert result["response_quality"]["is_high_quality"] is False

    def test_cross_system_prompt_compatibility(self):
        """Test that prompts from both systems are compatible with AgentCore."""
        # Test that both systems produce prompts that can be consumed by AgentCore
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            executor_prompt = self.executor._create_ai_prompt(self.mock_task, context)
        
        evaluator_prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        # Both prompts should be valid strings
        assert isinstance(executor_prompt, str)
        assert isinstance(evaluator_prompt, str)
        
        # Both should have reasonable length
        assert len(executor_prompt) > 500
        assert len(evaluator_prompt) > 500
        
        # Both should be properly formatted
        assert executor_prompt.strip() == executor_prompt
        assert evaluator_prompt.strip() == evaluator_prompt

    def test_system_initialization_consistency(self):
        """Test that both systems initialize consistently."""
        # Test TaskExecutor initialization
        assert hasattr(self.executor, 'metadata_manager')
        assert hasattr(self.executor, 'enhancement_manager')
        assert self.executor.metadata_manager is not None
        assert self.executor.enhancement_manager is not None
        
        # Test AIEvaluatorPrompts (static methods, no initialization needed)
        assert hasattr(AIEvaluatorPrompts, 'create_evaluation_prompt')
        assert hasattr(AIEvaluatorPrompts, 'create_recurrence_analysis_prompt')
        assert callable(AIEvaluatorPrompts.create_evaluation_prompt)
        assert callable(AIEvaluatorPrompts.create_recurrence_analysis_prompt)

    @pytest.mark.asyncio
    async def test_error_recovery_consistency(self):
        """Test that error recovery is consistent across systems."""
        # Test TaskExecutor error recovery
        with patch('personal_assistant.tools.ai_scheduler.core.executor.AgentCore') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.run.side_effect = Exception("Simulated error")
            mock_agent_class.return_value = mock_agent
            
            result = await self.executor.execute_task(self.mock_task)
            
            # Should handle error gracefully
            assert result["success"] is False
            assert "Simulated error" in result["message"]
            assert "task_id" in result
            assert result["task_id"] == self.mock_task.id

    def test_prompt_evolution_consistency(self):
        """Test that prompt evolution maintains consistency."""
        # Test that both systems can evolve while maintaining compatibility
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Test multiple iterations
        for iteration in range(5):
            with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
                executor_prompt = self.executor._create_ai_prompt(self.mock_task, context)
            
            evaluator_prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
            
            # Each iteration should produce consistent results
            assert "🎯 AI TASK EXECUTOR" in executor_prompt
            assert "🎯 AI CALENDAR EVENT EVALUATOR" in evaluator_prompt
            assert "🎯 **PROFESSIONAL" in executor_prompt
            assert "🎯 **PROFESSIONAL" in evaluator_prompt
