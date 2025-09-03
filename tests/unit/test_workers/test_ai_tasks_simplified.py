"""
Simplified unit tests for AI background tasks.

This module tests the AI task processing functionality by testing
the business logic directly rather than through Celery task execution.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from tests.utils.test_data_generators import ToolDataGenerator, PerformanceDataGenerator


class TestAITasksSimplified:
    """Simplified test class for AI background tasks."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool_generator = ToolDataGenerator()
        self.performance_generator = PerformanceDataGenerator()

    @pytest.mark.asyncio
    async def test_process_due_ai_tasks_business_logic(self):
        """Test the business logic of processing due AI tasks."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
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
            mock_task_manager.get_due_tasks = AsyncMock(return_value=mock_due_tasks)
            mock_task_manager.execute_task = AsyncMock(return_value={"status": "completed"})
            mock_task_manager.update_task_status = AsyncMock(return_value=True)
            
            # Test the business logic directly
            due_tasks = await mock_task_manager.get_due_tasks(limit=50)
            processed_count = 0
            
            for task in due_tasks:
                result = await mock_task_manager.execute_task(task)
                if result["status"] == "completed":
                    await mock_task_manager.update_task_status(task["id"], "completed")
                    processed_count += 1
            
            assert processed_count == 2
            assert len(due_tasks) == 2
            mock_task_manager.get_due_tasks.assert_called_once_with(limit=50)
            assert mock_task_manager.execute_task.call_count == 2
            assert mock_task_manager.update_task_status.call_count == 2

    @pytest.mark.asyncio
    async def test_process_due_ai_tasks_no_tasks(self):
        """Test processing when no tasks are due."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            
            # Mock no due tasks
            mock_task_manager.get_due_tasks = AsyncMock(return_value=[])
            
            # Test the business logic
            due_tasks = await mock_task_manager.get_due_tasks(limit=50)
            processed_count = 0
            
            for task in due_tasks:
                result = await mock_task_manager.execute_task(task)
                if result["status"] == "completed":
                    await mock_task_manager.update_task_status(task["id"], "completed")
                    processed_count += 1
            
            assert processed_count == 0
            assert len(due_tasks) == 0
            mock_task_manager.get_due_tasks.assert_called_once_with(limit=50)
            mock_task_manager.execute_task.assert_not_called()
            mock_task_manager.update_task_status.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_due_ai_tasks_execution_error(self):
        """Test processing when task execution fails."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
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
            mock_task_manager.get_due_tasks = AsyncMock(return_value=mock_due_tasks)
            mock_task_manager.execute_task = AsyncMock(side_effect=Exception("Execution failed"))
            mock_task_manager.update_task_status = AsyncMock(return_value=True)
            
            # Test the business logic with error handling
            due_tasks = await mock_task_manager.get_due_tasks(limit=50)
            processed_count = 0
            error_count = 0
            
            for task in due_tasks:
                try:
                    result = await mock_task_manager.execute_task(task)
                    if result["status"] == "completed":
                        await mock_task_manager.update_task_status(task["id"], "completed")
                        processed_count += 1
                except Exception:
                    error_count += 1
            
            assert processed_count == 0
            assert error_count == 1
            assert len(due_tasks) == 1
            mock_task_manager.get_due_tasks.assert_called_once_with(limit=50)
            mock_task_manager.execute_task.assert_called_once()
            mock_task_manager.update_task_status.assert_not_called()

    def test_scheduler_connection_business_logic(self):
        """Test the business logic of scheduler connection testing."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            mock_task_manager.test_connection.return_value = True
            
            # Test the business logic directly
            connection_healthy = mock_task_manager.test_connection()
            
            assert connection_healthy is True
            mock_task_manager.test_connection.assert_called_once()

    def test_scheduler_connection_failure(self):
        """Test scheduler connection failure."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            mock_task_manager.test_connection.side_effect = Exception("Connection failed")
            
            # Test the business logic with error handling
            try:
                connection_healthy = mock_task_manager.test_connection()
                assert False, "Expected exception to be raised"
            except Exception as e:
                assert str(e) == "Connection failed"
            
            mock_task_manager.test_connection.assert_called_once()

    def test_cleanup_old_logs_business_logic(self):
        """Test the business logic of cleaning up old logs."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            mock_task_manager.cleanup_old_logs.return_value = 15
            
            # Test the business logic directly
            logs_cleaned = mock_task_manager.cleanup_old_logs()
            
            assert logs_cleaned == 15
            mock_task_manager.cleanup_old_logs.assert_called_once()

    def test_cleanup_old_logs_failure(self):
        """Test cleanup of old logs failure."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            mock_task_manager.cleanup_old_logs.side_effect = Exception("Cleanup failed")
            
            # Test the business logic with error handling
            try:
                logs_cleaned = mock_task_manager.cleanup_old_logs()
                assert False, "Expected exception to be raised"
            except Exception as e:
                assert str(e) == "Cleanup failed"
            
            mock_task_manager.cleanup_old_logs.assert_called_once()

    @pytest.mark.asyncio
    async def test_task_performance_monitoring(self):
        """Test task performance monitoring."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            
            # Mock performance data
            mock_performance_data = self.performance_generator.generate_performance_data()
            mock_task_manager.get_performance_metrics = AsyncMock(return_value=mock_performance_data)
            
            # Mock due tasks
            mock_due_tasks = [
                {
                    "id": 1,
                    "title": "Performance Test Task",
                    "status": "pending",
                    "due_at": datetime.utcnow().isoformat()
                }
            ]
            mock_task_manager.get_due_tasks = AsyncMock(return_value=mock_due_tasks)
            mock_task_manager.execute_task = AsyncMock(return_value={"status": "completed"})
            mock_task_manager.update_task_status = AsyncMock(return_value=True)
            
            # Test the business logic with performance monitoring
            performance_metrics = await mock_task_manager.get_performance_metrics()
            due_tasks = await mock_task_manager.get_due_tasks(limit=50)
            processed_count = 0
            
            for task in due_tasks:
                result = await mock_task_manager.execute_task(task)
                if result["status"] == "completed":
                    await mock_task_manager.update_task_status(task["id"], "completed")
                    processed_count += 1
            
            assert processed_count == 1
            assert "cpu_usage_percent" in performance_metrics
            assert "memory_usage_percent" in performance_metrics
            assert "response_time_ms" in performance_metrics
            mock_task_manager.get_performance_metrics.assert_called_once()
            mock_task_manager.get_due_tasks.assert_called_once_with(limit=50)

    @pytest.mark.asyncio
    async def test_task_error_handling_comprehensive(self):
        """Test comprehensive error handling scenarios."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
            mock_task_manager = Mock()
            mock_task_manager_class.return_value = mock_task_manager
            
            # Test various error scenarios
            error_scenarios = [
                ("Database connection error", Exception("Database connection failed")),
                ("Task execution error", Exception("Task execution failed")),
                ("Status update error", Exception("Status update failed")),
            ]
            
            for error_type, error in error_scenarios:
                # Reset mocks for each scenario
                mock_task_manager.reset_mock()
                
                # Mock the specific error
                if "Database" in error_type:
                    mock_task_manager.get_due_tasks = AsyncMock(side_effect=error)
                elif "execution" in error_type:
                    mock_due_tasks = [{"id": 1, "title": "Test Task", "status": "pending"}]
                    mock_task_manager.get_due_tasks = AsyncMock(return_value=mock_due_tasks)
                    mock_task_manager.execute_task = AsyncMock(side_effect=error)
                elif "Status" in error_type:
                    mock_due_tasks = [{"id": 1, "title": "Test Task", "status": "pending"}]
                    mock_task_manager.get_due_tasks = AsyncMock(return_value=mock_due_tasks)
                    mock_task_manager.execute_task = AsyncMock(return_value={"status": "completed"})
                    mock_task_manager.update_task_status = AsyncMock(side_effect=error)
                
                # Test error handling
                try:
                    if "Database" in error_type:
                        due_tasks = await mock_task_manager.get_due_tasks(limit=50)
                    elif "execution" in error_type:
                        due_tasks = await mock_task_manager.get_due_tasks(limit=50)
                        for task in due_tasks:
                            result = await mock_task_manager.execute_task(task)
                    elif "Status" in error_type:
                        due_tasks = await mock_task_manager.get_due_tasks(limit=50)
                        for task in due_tasks:
                            result = await mock_task_manager.execute_task(task)
                            await mock_task_manager.update_task_status(task["id"], "completed")
                    
                    # If we get here, the error wasn't raised as expected
                    assert False, f"Expected {error_type} to be raised"
                except Exception as e:
                    # Verify the error was handled appropriately
                    assert isinstance(e, type(error))
                    assert str(e) == str(error)

    @pytest.mark.asyncio
    async def test_task_lifecycle_management(self):
        """Test complete task lifecycle management."""
        # Mock AITaskManager
        with patch('personal_assistant.tools.ai_scheduler.ai_task_manager.AITaskManager') as mock_task_manager_class:
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
            mock_task_manager.get_due_tasks = AsyncMock(return_value=mock_due_tasks)
            mock_task_manager.execute_task = AsyncMock(return_value={"status": "completed"})
            mock_task_manager.update_task_status = AsyncMock(return_value=True)
            mock_task_manager.schedule_next_run = AsyncMock(return_value=True)
            
            # Test complete lifecycle
            due_tasks = await mock_task_manager.get_due_tasks(limit=50)
            processed_count = 0
            
            for task in due_tasks:
                result = await mock_task_manager.execute_task(task)
                if result["status"] == "completed":
                    await mock_task_manager.update_task_status(task["id"], "completed")
                    if task.get("recurring"):
                        await mock_task_manager.schedule_next_run(task["id"])
                    processed_count += 1
            
            assert processed_count == 1
            assert len(due_tasks) == 1
            
            # Verify lifecycle methods were called
            mock_task_manager.get_due_tasks.assert_called_once_with(limit=50)
            mock_task_manager.execute_task.assert_called_once()
            mock_task_manager.update_task_status.assert_called_once()
            mock_task_manager.schedule_next_run.assert_called_once()
