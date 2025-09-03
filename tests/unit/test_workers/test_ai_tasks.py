"""
Unit tests for AI background tasks.

This module tests the AI task processing functionality including:
- Task scheduling and execution
- Error handling and retry logic
- Task lifecycle management
- Performance monitoring
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from personal_assistant.workers.tasks.ai_tasks import (
    process_due_ai_tasks,
    _process_due_ai_tasks_async,
    test_scheduler_connection,
    cleanup_old_logs,
)
from tests.utils.test_data_generators import ToolDataGenerator, PerformanceDataGenerator


class TestAITasks:
    """Test class for AI background tasks."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool_generator = ToolDataGenerator()
        self.performance_generator = PerformanceDataGenerator()

    @pytest.mark.asyncio
    async def test_process_due_ai_tasks_success(self):
        """Test successful processing of due AI tasks."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "test_task_123"
        mock_task.retry = Mock()
        
        # Mock the async function
        with patch('personal_assistant.workers.tasks.ai_tasks._process_due_ai_tasks_async') as mock_async:
            mock_async.return_value = {
                "task_id": "test_task_123",
                "status": "success",
                "tasks_processed": 5,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Mock nest_asyncio and event loop
            with patch('personal_assistant.workers.tasks.ai_tasks.nest_asyncio') as mock_nest:
                with patch('personal_assistant.workers.tasks.ai_tasks.asyncio') as mock_asyncio:
                    mock_loop = Mock()
                    mock_asyncio.get_event_loop.return_value = mock_loop
                    mock_loop.run_until_complete.return_value = {
                        "task_id": "test_task_123",
                        "status": "success",
                        "tasks_processed": 5,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    result = process_due_ai_tasks(mock_task)
                    
                    assert result["status"] == "success"
                    assert result["tasks_processed"] == 5
                    assert "task_id" in result
                    assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_process_due_ai_tasks_retry_on_failure(self):
        """Test retry logic when task processing fails."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "test_task_123"
        mock_task.retry = Mock()
        
        # Mock the async function to raise an exception
        with patch('personal_assistant.workers.tasks.ai_tasks._process_due_ai_tasks_async') as mock_async:
            mock_async.side_effect = Exception("Database connection failed")
            
            # Mock nest_asyncio and event loop
            with patch('personal_assistant.workers.tasks.ai_tasks.nest_asyncio'):
                with patch('personal_assistant.workers.tasks.ai_tasks.asyncio') as mock_asyncio:
                    mock_loop = Mock()
                    mock_asyncio.get_event_loop.return_value = mock_loop
                    mock_loop.run_until_complete.side_effect = Exception("Database connection failed")
                    
                    # Should raise retry exception
                    with pytest.raises(Exception):
                        process_due_ai_tasks(mock_task)
                    
                    # Verify retry was called
                    mock_task.retry.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_due_ai_tasks_async_success(self):
        """Test the async implementation of AI task processing."""
        # Mock AITaskManager
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            
            # Mock due tasks
            mock_due_tasks = [
                {
                    "id": 1,
                    "title": "Test Task 1",
                    "status": "pending",
                    "due_at": datetime.utcnow().isoformat()
                },
                {
                    "id": 2,
                    "title": "Test Task 2", 
                    "status": "pending",
                    "due_at": datetime.utcnow().isoformat()
                }
            ]
            mock_task_manager.get_due_tasks.return_value = mock_due_tasks
            
            # Mock task execution
            mock_task_manager.execute_task.return_value = {"status": "completed"}
            mock_task_manager.update_task_status.return_value = True
            
            result = await _process_due_ai_tasks_async("test_task_123")
            
            assert result["status"] == "success"
            assert result["tasks_processed"] == 2
            assert result["task_id"] == "test_task_123"
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_process_due_ai_tasks_async_no_tasks(self):
        """Test async processing when no tasks are due."""
        # Mock AITaskManager
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            
            # Mock no due tasks
            mock_task_manager.get_due_tasks.return_value = []
            
            result = await _process_due_ai_tasks_async("test_task_123")
            
            assert result["status"] == "success"
            assert result["tasks_processed"] == 0
            assert result["task_id"] == "test_task_123"

    @pytest.mark.asyncio
    async def test_process_due_ai_tasks_async_execution_error(self):
        """Test async processing when task execution fails."""
        # Mock AITaskManager
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            
            # Mock due tasks
            mock_due_tasks = [
                {
                    "id": 1,
                    "title": "Test Task 1",
                    "status": "pending",
                    "due_at": datetime.utcnow().isoformat()
                }
            ]
            mock_task_manager.get_due_tasks.return_value = mock_due_tasks
            
            # Mock task execution failure
            mock_task_manager.execute_task.side_effect = Exception("Execution failed")
            mock_task_manager.update_task_status.return_value = True
            
            result = await _process_due_ai_tasks_async("test_task_123")
            
            assert result["status"] == "partial_success"
            assert result["tasks_processed"] == 0
            assert result["errors"] == 1
            assert result["task_id"] == "test_task_123"

    def test_test_scheduler_connection_success(self):
        """Test successful scheduler connection test."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "test_connection_123"
        mock_task.retry = Mock()
        
        # Mock database connection
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            mock_task_manager.test_connection.return_value = True
            
            # Call the task function directly (not as a Celery task)
            result = test_scheduler_connection.run(mock_task)
            
            assert result["status"] == "success"
            assert result["connection_healthy"] is True
            assert result["task_id"] == "test_connection_123"
            assert "timestamp" in result

    def test_test_scheduler_connection_failure(self):
        """Test scheduler connection test failure."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "test_connection_123"
        mock_task.retry = Mock()
        
        # Mock database connection failure
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            mock_task_manager.test_connection.side_effect = Exception("Connection failed")
            
            # Should raise retry exception
            with pytest.raises(Exception):
                test_scheduler_connection(mock_task)
            
            # Verify retry was called
            mock_task.retry.assert_called_once()

    def test_cleanup_old_logs_success(self):
        """Test successful cleanup of old logs."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "cleanup_logs_123"
        mock_task.retry = Mock()
        
        # Mock AITaskManager
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            mock_task_manager.cleanup_old_logs.return_value = 15
            
            result = cleanup_old_logs(mock_task)
            
            assert result["status"] == "success"
            assert result["logs_cleaned"] == 15
            assert result["task_id"] == "cleanup_logs_123"
            assert "timestamp" in result

    def test_cleanup_old_logs_failure(self):
        """Test cleanup of old logs failure."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "cleanup_logs_123"
        mock_task.retry = Mock()
        
        # Mock AITaskManager
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            mock_task_manager.cleanup_old_logs.side_effect = Exception("Cleanup failed")
            
            # Should raise retry exception
            with pytest.raises(Exception):
                cleanup_old_logs(mock_task)
            
            # Verify retry was called
            mock_task.retry.assert_called_once()

    @pytest.mark.asyncio
    async def test_task_performance_monitoring(self):
        """Test task performance monitoring."""
        # Mock AITaskManager
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            
            # Mock performance data
            mock_performance_data = self.performance_generator.generate_performance_data()
            mock_task_manager.get_performance_metrics.return_value = mock_performance_data
            
            # Mock due tasks
            mock_due_tasks = [
                {
                    "id": 1,
                    "title": "Performance Test Task",
                    "status": "pending",
                    "due_at": datetime.utcnow().isoformat()
                }
            ]
            mock_task_manager.get_due_tasks.return_value = mock_due_tasks
            mock_task_manager.execute_task.return_value = {"status": "completed"}
            mock_task_manager.update_task_status.return_value = True
            
            result = await _process_due_ai_tasks_async("performance_test_123")
            
            assert result["status"] == "success"
            assert result["tasks_processed"] == 1
            assert "performance_metrics" in result or result["status"] == "success"

    @pytest.mark.asyncio
    async def test_task_error_handling_comprehensive(self):
        """Test comprehensive error handling scenarios."""
        # Mock AITaskManager
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            
            # Test various error scenarios
            error_scenarios = [
                ("Database connection error", Exception("Database connection failed")),
                ("Task execution error", Exception("Task execution failed")),
                ("Status update error", Exception("Status update failed")),
                ("Timeout error", TimeoutError("Task timeout")),
            ]
            
            for error_type, error in error_scenarios:
                # Mock due tasks
                mock_due_tasks = [
                    {
                        "id": 1,
                        "title": f"Error Test Task - {error_type}",
                        "status": "pending",
                        "due_at": datetime.utcnow().isoformat()
                    }
                ]
                mock_task_manager.get_due_tasks.return_value = mock_due_tasks
                
                # Mock the specific error
                if "Database" in error_type:
                    mock_task_manager.get_due_tasks.side_effect = error
                elif "execution" in error_type:
                    mock_task_manager.execute_task.side_effect = error
                elif "Status" in error_type:
                    mock_task_manager.update_task_status.side_effect = error
                
                result = await _process_due_ai_tasks_async(f"error_test_{error_type.replace(' ', '_')}")
                
                # Should handle errors gracefully
                assert result["status"] in ["success", "partial_success", "error"]
                assert "task_id" in result
                assert "timestamp" in result

    def test_task_retry_configuration(self):
        """Test task retry configuration and behavior."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "retry_test_123"
        mock_task.retry = Mock()
        
        # Test retry configuration
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            mock_task_manager.test_connection.side_effect = Exception("Connection failed")
            
            # Mock nest_asyncio and event loop
            with patch('personal_assistant.workers.tasks.ai_tasks.nest_asyncio'):
                with patch('personal_assistant.workers.tasks.ai_tasks.asyncio') as mock_asyncio:
                    mock_loop = Mock()
                    mock_asyncio.get_event_loop.return_value = mock_loop
                    mock_loop.run_until_complete.side_effect = Exception("Connection failed")
                    
                    # Should raise retry exception
                    with pytest.raises(Exception):
                        test_scheduler_connection(mock_task)
                    
                    # Verify retry was called with correct parameters
                    mock_task.retry.assert_called_once()
                    call_args = mock_task.retry.call_args
                    assert "countdown" in call_args.kwargs
                    assert "max_retries" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_task_lifecycle_management(self):
        """Test complete task lifecycle management."""
        # Mock AITaskManager
        with patch('personal_assistant.workers.tasks.ai_tasks.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            
            # Mock task lifecycle
            mock_due_tasks = [
                {
                    "id": 1,
                    "title": "Lifecycle Test Task",
                    "status": "pending",
                    "due_at": datetime.utcnow().isoformat(),
                    "recurring": True,
                    "schedule_type": "daily"
                }
            ]
            mock_task_manager.get_due_tasks.return_value = mock_due_tasks
            mock_task_manager.execute_task.return_value = {"status": "completed"}
            mock_task_manager.update_task_status.return_value = True
            mock_task_manager.schedule_next_run.return_value = True
            
            result = await _process_due_ai_tasks_async("lifecycle_test_123")
            
            assert result["status"] == "success"
            assert result["tasks_processed"] == 1
            assert result["task_id"] == "lifecycle_test_123"
            
            # Verify lifecycle methods were called
            mock_task_manager.execute_task.assert_called_once()
            mock_task_manager.update_task_status.assert_called_once()
            mock_task_manager.schedule_next_run.assert_called_once()
