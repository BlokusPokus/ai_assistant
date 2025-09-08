"""
Performance tests for enhanced prompt engineering system.

This module tests the performance characteristics of the enhanced prompt systems including:
- Response time optimization
- Memory usage efficiency
- Concurrent processing capabilities
- Scalability testing
- Quality vs performance trade-offs
"""

import pytest
import time
import asyncio
import sys
import psutil
import os
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List

from personal_assistant.tools.ai_scheduler.core.executor import TaskExecutor
from personal_assistant.prompts.ai_evaluator_prompts import AIEvaluatorPrompts
from personal_assistant.database.models.ai_tasks import AITask


@pytest.mark.performance
class TestEnhancedPromptPerformance:
    """Test class for enhanced prompt system performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.executor = TaskExecutor()
        
        # Create mock AITask
        self.mock_task = Mock(spec=AITask)
        self.mock_task.id = 1
        self.mock_task.title = "Performance Test Reminder"
        self.mock_task.description = "Test reminder for performance testing"
        self.mock_task.task_type = "reminder"
        self.mock_task.schedule_type = "one_time"
        self.mock_task.schedule_config = None
        self.mock_task.user_id = 123
        self.mock_task.ai_context = "Performance test context"
        self.mock_task.created_at = datetime.utcnow()
        self.mock_task.last_run_at = None

        # Create sample AI context for evaluator
        self.sample_ai_context = {
            'event': {
                'title': 'Performance Test Meeting',
                'type': 'meeting',
                'priority': 'high',
                'location': 'Performance Test Room',
                'start_time': '2024-01-15T14:00:00Z',
                'end_time': '2024-01-15T15:00:00Z',
                'description': 'Performance test meeting for prompt systems'
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

    def test_single_prompt_creation_performance(self):
        """Test performance of single prompt creation."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Test TaskExecutor performance
        start_time = time.time()
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            executor_prompt = self.executor._create_ai_prompt(self.mock_task, context)
        
        executor_time = time.time() - start_time
        
        # Test AIEvaluatorPrompts performance
        start_time = time.time()
        
        evaluator_prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        evaluator_time = time.time() - start_time
        
        # Both should be fast for single prompt creation
        assert executor_time < 0.1, f"TaskExecutor too slow: {executor_time:.4f}s"
        assert evaluator_time < 0.1, f"AIEvaluatorPrompts too slow: {evaluator_time:.4f}s"
        
        # Both should produce substantial prompts
        assert len(executor_prompt) > 1000
        assert len(evaluator_prompt) > 1000

    def test_batch_prompt_creation_performance(self):
        """Test performance of batch prompt creation."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        batch_size = 100
        
        # Test TaskExecutor batch performance
        start_time = time.time()
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            executor_prompts = []
            for _ in range(batch_size):
                prompt = self.executor._create_ai_prompt(self.mock_task, context)
                executor_prompts.append(prompt)
        
        executor_time = time.time() - start_time
        
        # Test AIEvaluatorPrompts batch performance
        start_time = time.time()
        
        evaluator_prompts = []
        for _ in range(batch_size):
            prompt = AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
            evaluator_prompts.append(prompt)
        
        evaluator_time = time.time() - start_time
        
        # Both should handle batch creation efficiently
        assert executor_time < 2.0, f"TaskExecutor batch too slow: {executor_time:.2f}s"
        assert evaluator_time < 2.0, f"AIEvaluatorPrompts batch too slow: {evaluator_time:.2f}s"
        
        # Should maintain quality in batch
        assert len(executor_prompts) == batch_size
        assert len(evaluator_prompts) == batch_size
        
        for prompt in executor_prompts:
            assert len(prompt) > 1000
            assert "🎯 AI TASK EXECUTOR" in prompt
        
        for prompt in evaluator_prompts:
            assert len(prompt) > 1000
            assert "🎯 AI CALENDAR EVENT EVALUATOR" in prompt

    def test_memory_usage_efficiency(self):
        """Test memory usage efficiency of prompt creation."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create many prompts
        prompts = []
        for _ in range(1000):
            with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
                prompt = self.executor._create_ai_prompt(self.mock_task, context)
                prompts.append(prompt)
        
        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB for 1000 prompts)
        assert memory_increase < 50 * 1024 * 1024, f"Memory usage too high: {memory_increase / 1024 / 1024:.2f}MB"
        
        # Clean up
        del prompts

    def test_concurrent_prompt_creation_performance(self):
        """Test performance of concurrent prompt creation."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        async def create_executor_prompt():
            with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
                return self.executor._create_ai_prompt(self.mock_task, context)
        
        async def create_evaluator_prompt():
            return AIEvaluatorPrompts.create_evaluation_prompt(self.sample_ai_context)
        
        async def run_concurrent_test():
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = []
            for _ in range(50):
                tasks.append(create_executor_prompt())
                tasks.append(create_evaluator_prompt())
            
            # Run concurrently
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return results, execution_time
        
        # Run the concurrent test
        results, execution_time = asyncio.run(run_concurrent_test())
        
        # Should complete in reasonable time
        assert execution_time < 5.0, f"Concurrent execution too slow: {execution_time:.2f}s"
        assert len(results) == 100  # 50 of each type
        
        # All results should be valid
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 1000

    def test_response_quality_assessment_performance(self):
        """Test performance of response quality assessment."""
        # Create test responses of different lengths
        test_responses = [
            "Short response",
            "Medium length response with some content and structure",
            "Very long response with extensive content, multiple sections, detailed analysis, comprehensive suggestions, structured formatting, and professional quality indicators that should trigger all quality assessment criteria"
        ]
        
        for response in test_responses:
            start_time = time.time()
            
            # Test quality assessment performance
            for _ in range(1000):
                quality = self.executor._assess_response_quality(response)
                extracted = self.executor._extract_response_information(response)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should be very fast for quality assessment
            assert execution_time < 1.0, f"Quality assessment too slow: {execution_time:.4f}s"
            
            # Results should be valid
            assert "is_high_quality" in quality
            assert "score" in quality
            assert "indicators" in quality
            assert "has_acknowledgment" in extracted

    def test_metadata_integration_performance(self):
        """Test performance impact of metadata integration."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Test without metadata
        start_time = time.time()
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            prompt_without_metadata = self.executor._create_ai_prompt(self.mock_task, context)
        
        time_without_metadata = time.time() - start_time
        
        # Test with metadata
        mock_enhancements = [
            Mock(title=f"Enhancement {i}", ai_instructions=f"Instructions {i}")
            for i in range(10)  # 10 enhancements
        ]
        
        start_time = time.time()
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=mock_enhancements):
            prompt_with_metadata = self.executor._create_ai_prompt(self.mock_task, context)
        
        time_with_metadata = time.time() - start_time
        
        # Metadata integration should not significantly impact performance
        performance_ratio = time_with_metadata / time_without_metadata
        assert performance_ratio < 2.0, f"Metadata integration too slow: {performance_ratio:.2f}x"
        
        # Both prompts should be substantial
        assert len(prompt_without_metadata) > 1000
        assert len(prompt_with_metadata) > 1000
        
        # Metadata prompt should include enhancements
        assert "🎯 **AI GUIDANCE & ENHANCEMENTS**:" in prompt_with_metadata

    def test_scalability_with_large_contexts(self):
        """Test scalability with large context data."""
        # Create large context
        large_context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z',
            'notification_channels': ['sms', 'email', 'push', 'webhook'],
            'user_preferences': {
                'timezone': 'UTC',
                'language': 'en',
                'notifications': True,
                'reminders': True
            },
            'additional_data': {
                'key1': 'value1' * 100,  # Large string
                'key2': 'value2' * 100,
                'key3': 'value3' * 100
            }
        }
        
        start_time = time.time()
        
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            prompt = self.executor._create_ai_prompt(self.mock_task, large_context)
        
        execution_time = time.time() - start_time
        
        # Should handle large context efficiently
        assert execution_time < 0.5, f"Large context handling too slow: {execution_time:.4f}s"
        
        # Should still produce quality prompt
        assert len(prompt) > 1000
        assert "🎯 AI TASK EXECUTOR" in prompt

    def test_memory_leak_prevention(self):
        """Test that prompt creation doesn't cause memory leaks."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create and discard many prompts
        for iteration in range(10):
            prompts = []
            for _ in range(100):
                with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
                    prompt = self.executor._create_ai_prompt(self.mock_task, context)
                    prompts.append(prompt)
            
            # Discard prompts
            del prompts
            
            # Force garbage collection
            import gc
            gc.collect()
        
        # Get final memory
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 10MB)
        assert memory_increase < 10 * 1024 * 1024, f"Potential memory leak: {memory_increase / 1024 / 1024:.2f}MB"

    def test_cpu_usage_efficiency(self):
        """Test CPU usage efficiency during prompt creation."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Monitor CPU usage
        process = psutil.Process(os.getpid())
        
        start_time = time.time()
        start_cpu = process.cpu_percent()
        
        # Create many prompts
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            for _ in range(1000):
                prompt = self.executor._create_ai_prompt(self.mock_task, context)
                assert len(prompt) > 1000  # Ensure quality
        
        end_time = time.time()
        end_cpu = process.cpu_percent()
        
        execution_time = end_time - start_time
        avg_cpu = (start_cpu + end_cpu) / 2
        
        # Should complete efficiently
        assert execution_time < 5.0, f"CPU usage too high: {execution_time:.2f}s"
        
        # CPU usage should be reasonable
        assert avg_cpu < 50.0, f"CPU usage too high: {avg_cpu:.1f}%"

    def test_prompt_quality_vs_performance_tradeoff(self):
        """Test the tradeoff between prompt quality and performance."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Test different enhancement levels
        enhancement_levels = [0, 5, 10, 20]
        results = []
        
        for level in enhancement_levels:
            mock_enhancements = [
                Mock(title=f"Enhancement {i}", ai_instructions=f"Instructions {i}")
                for i in range(level)
            ]
            
            start_time = time.time()
            
            with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=mock_enhancements):
                prompt = self.executor._create_ai_prompt(self.mock_task, context)
            
            execution_time = time.time() - start_time
            prompt_length = len(prompt)
            
            results.append({
                'enhancement_level': level,
                'execution_time': execution_time,
                'prompt_length': prompt_length
            })
        
        # Performance should degrade gracefully with more enhancements
        for i in range(1, len(results)):
            prev_result = results[i-1]
            curr_result = results[i]
            
            # Execution time should increase reasonably
            time_ratio = curr_result['execution_time'] / prev_result['execution_time']
            assert time_ratio < 3.0, f"Performance degradation too steep: {time_ratio:.2f}x"
            
            # Prompt length should increase with more enhancements
            assert curr_result['prompt_length'] >= prev_result['prompt_length']

    def test_concurrent_quality_assessment_performance(self):
        """Test performance of concurrent quality assessment."""
        test_responses = [
            "High quality response with comprehensive analysis and actionable suggestions",
            "Medium quality response with some structure and helpful content",
            "Low quality response",
            "Very detailed response with extensive analysis, multiple sections, structured formatting, and professional quality indicators"
        ]
        
        async def assess_quality(response):
            return self.executor._assess_response_quality(response)
        
        async def run_concurrent_quality_test():
            start_time = time.time()
            
            # Create concurrent quality assessment tasks
            tasks = []
            for _ in range(100):  # 100 assessments per response type
                for response in test_responses:
                    tasks.append(assess_quality(response))
            
            # Run concurrently
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return results, execution_time
        
        # Run the concurrent quality test
        results, execution_time = asyncio.run(run_concurrent_quality_test())
        
        # Should complete efficiently
        assert execution_time < 2.0, f"Concurrent quality assessment too slow: {execution_time:.2f}s"
        assert len(results) == 400  # 100 * 4 response types
        
        # All results should be valid
        for result in results:
            assert "is_high_quality" in result
            assert "score" in result
            assert "indicators" in result

    def test_system_initialization_performance(self):
        """Test performance of system initialization."""
        start_time = time.time()
        
        # Initialize multiple executors
        executors = []
        for _ in range(10):
            executor = TaskExecutor()
            executors.append(executor)
        
        end_time = time.time()
        initialization_time = end_time - start_time
        
        # Should initialize efficiently
        assert initialization_time < 1.0, f"Initialization too slow: {initialization_time:.4f}s"
        
        # All executors should be properly initialized
        for executor in executors:
            assert executor.metadata_manager is not None
            assert executor.enhancement_manager is not None

    def test_prompt_caching_potential(self):
        """Test potential for prompt caching optimization."""
        context = {
            'created_at': '2024-01-15T10:30:00Z',
            'current_time': '2024-01-15T10:30:00Z'
        }
        
        # Test repeated prompt creation with same parameters
        with patch.object(self.executor.enhancement_manager, 'get_tool_enhancements', return_value=[]):
            start_time = time.time()
            
            prompts = []
            for _ in range(100):
                prompt = self.executor._create_ai_prompt(self.mock_task, context)
                prompts.append(prompt)
            
            end_time = time.time()
            execution_time = end_time - start_time
        
        # All prompts should be identical (good for caching)
        first_prompt = prompts[0]
        for prompt in prompts[1:]:
            assert prompt == first_prompt, "Prompts should be identical for same parameters"
        
        # Should be fast even without caching
        assert execution_time < 1.0, f"Repeated creation too slow: {execution_time:.4f}s"
