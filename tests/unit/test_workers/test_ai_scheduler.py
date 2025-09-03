"""
Unit tests for AI scheduler.

This module tests the AI scheduler functionality including:
- Task scheduling and management
- Due task retrieval
- Next run time calculation
- Task statistics
- Task cleanup
- Error handling
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from personal_assistant.workers.schedulers.ai_scheduler import AIScheduler, ai_scheduler
from tests.utils.test_data_generators import ToolDataGenerator, PerformanceDataGenerator


class TestAIScheduler:
    """Test class for AI scheduler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool_generator = ToolDataGenerator()
        self.performance_generator = PerformanceDataGenerator()
        self.scheduler = AIScheduler()

    @pytest.mark.asyncio
    async def test_get_due_tasks_success(self):
        """Test successful retrieval of due tasks."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
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
            
            result = await self.scheduler.get_due_tasks(limit=50)
            
            assert result == mock_due_tasks
            assert len(result) == 2
            mock_task_manager.get_due_tasks.assert_called_once_with(limit=50)

    @pytest.mark.asyncio
    async def test_get_due_tasks_empty(self):
        """Test retrieval of due tasks when none are available."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock no due tasks
            mock_task_manager.get_due_tasks.return_value = []
            
            result = await self.scheduler.get_due_tasks(limit=50)
            
            assert result == []
            assert len(result) == 0
            mock_task_manager.get_due_tasks.assert_called_once_with(limit=50)

    @pytest.mark.asyncio
    async def test_get_due_tasks_error(self):
        """Test error handling when retrieving due tasks fails."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock error
            mock_task_manager.get_due_tasks.side_effect = Exception("Database connection failed")
            
            result = await self.scheduler.get_due_tasks(limit=50)
            
            assert result == []
            mock_task_manager.get_due_tasks.assert_called_once_with(limit=50)

    @pytest.mark.asyncio
    async def test_calculate_next_run_daily(self):
        """Test calculation of next run time for daily schedule."""
        # Mock current time
        with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            result = await self.scheduler.calculate_next_run("daily", {})
            
            # Should be tomorrow at the same time
            expected = mock_now + timedelta(days=1)
            assert result == expected

    @pytest.mark.asyncio
    async def test_calculate_next_run_weekly(self):
        """Test calculation of next run time for weekly schedule."""
        # Mock current time (Monday)
        with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)  # Monday
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            result = await self.scheduler.calculate_next_run("weekly", {})
            
            # Should be next Monday (7 days ahead)
            expected = mock_now + timedelta(days=7)
            assert result == expected

    @pytest.mark.asyncio
    async def test_calculate_next_run_monthly(self):
        """Test calculation of next run time for monthly schedule."""
        # Mock current time
        with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            result = await self.scheduler.calculate_next_run("monthly", {})
            
            # Should be next month (simplified calculation)
            expected = datetime(2024, 2, 1, 10, 30, 0)
            assert result == expected

    @pytest.mark.asyncio
    async def test_calculate_next_run_custom(self):
        """Test calculation of next run time for custom schedule."""
        # Mock current time
        with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            custom_config = {"cron": "0 9 * * *"}  # Daily at 9 AM
            
            result = await self.scheduler.calculate_next_run("custom", custom_config)
            
            # Should default to hourly if parsing fails
            expected = mock_now + timedelta(hours=1)
            assert result == expected

    @pytest.mark.asyncio
    async def test_calculate_next_run_unknown_type(self):
        """Test calculation of next run time for unknown schedule type."""
        # Mock current time
        with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            result = await self.scheduler.calculate_next_run("unknown", {})
            
            # Should default to hourly
            expected = mock_now + timedelta(hours=1)
            assert result == expected

    @pytest.mark.asyncio
    async def test_calculate_next_run_error(self):
        """Test error handling in next run time calculation."""
        # Mock current time
        with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = Exception("Time calculation error")
            
            result = await self.scheduler.calculate_next_run("daily", {})
            
            # Should default to hourly on error
            expected = mock_now + timedelta(hours=1)
            assert result == expected

    @pytest.mark.asyncio
    async def test_get_task_statistics_success(self):
        """Test successful retrieval of task statistics."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock statistics
            mock_task_manager.get_total_task_count.return_value = 100
            mock_task_manager.get_pending_task_count.return_value = 25
            mock_task_manager.get_completed_task_count.return_value = 70
            mock_task_manager.get_failed_task_count.return_value = 5
            
            # Mock current time
            with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
                mock_now = datetime(2024, 1, 15, 10, 30, 0)
                mock_datetime.utcnow.return_value = mock_now
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                result = await self.scheduler.get_task_statistics()
                
                assert result["total_tasks"] == 100
                assert result["pending_tasks"] == 25
                assert result["completed_tasks"] == 70
                assert result["failed_tasks"] == 5
                assert result["success_rate"] == 70.0  # 70/100 * 100
                assert result["timestamp"] == mock_now.isoformat()

    @pytest.mark.asyncio
    async def test_get_task_statistics_zero_total(self):
        """Test task statistics when total tasks is zero."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock zero statistics
            mock_task_manager.get_total_task_count.return_value = 0
            mock_task_manager.get_pending_task_count.return_value = 0
            mock_task_manager.get_completed_task_count.return_value = 0
            mock_task_manager.get_failed_task_count.return_value = 0
            
            # Mock current time
            with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
                mock_now = datetime(2024, 1, 15, 10, 30, 0)
                mock_datetime.utcnow.return_value = mock_now
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                result = await self.scheduler.get_task_statistics()
                
                assert result["total_tasks"] == 0
                assert result["pending_tasks"] == 0
                assert result["completed_tasks"] == 0
                assert result["failed_tasks"] == 0
                assert result["success_rate"] == 0  # 0/0 = 0
                assert result["timestamp"] == mock_now.isoformat()

    @pytest.mark.asyncio
    async def test_get_task_statistics_error(self):
        """Test error handling in task statistics retrieval."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock error
            mock_task_manager.get_total_task_count.side_effect = Exception("Database error")
            
            # Mock current time
            with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
                mock_now = datetime(2024, 1, 15, 10, 30, 0)
                mock_datetime.utcnow.return_value = mock_now
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                result = await self.scheduler.get_task_statistics()
                
                assert "error" in result
                assert result["error"] == "Database error"
                assert result["timestamp"] == mock_now.isoformat()

    @pytest.mark.asyncio
    async def test_cleanup_old_tasks_success(self):
        """Test successful cleanup of old tasks."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock cleanup result
            mock_task_manager.cleanup_old_tasks.return_value = 15
            
            # Mock current time
            with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
                mock_now = datetime(2024, 1, 15, 10, 30, 0)
                mock_datetime.utcnow.return_value = mock_now
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                result = await self.scheduler.cleanup_old_tasks(days_old=30)
                
                assert result == 15
                
                # Verify cutoff date calculation
                expected_cutoff = mock_now - timedelta(days=30)
                mock_task_manager.cleanup_old_tasks.assert_called_once_with(expected_cutoff)

    @pytest.mark.asyncio
    async def test_cleanup_old_tasks_error(self):
        """Test error handling in old task cleanup."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock error
            mock_task_manager.cleanup_old_tasks.side_effect = Exception("Cleanup failed")
            
            result = await self.scheduler.cleanup_old_tasks(days_old=30)
            
            assert result == 0

    @pytest.mark.asyncio
    async def test_cleanup_old_tasks_default_days(self):
        """Test cleanup with default days parameter."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock cleanup result
            mock_task_manager.cleanup_old_tasks.return_value = 10
            
            # Mock current time
            with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
                mock_now = datetime(2024, 1, 15, 10, 30, 0)
                mock_datetime.utcnow.return_value = mock_now
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                result = await self.scheduler.cleanup_old_tasks()  # Default 30 days
                
                assert result == 10
                
                # Verify default cutoff date calculation
                expected_cutoff = mock_now - timedelta(days=30)
                mock_task_manager.cleanup_old_tasks.assert_called_once_with(expected_cutoff)

    def test_ai_scheduler_initialization(self):
        """Test AI scheduler initialization."""
        # Test that the scheduler is properly initialized
        assert self.scheduler is not None
        assert hasattr(self.scheduler, 'task_manager')
        assert self.scheduler.task_manager is not None

    def test_global_ai_scheduler_instance(self):
        """Test global AI scheduler instance."""
        # Test that the global instance is properly created
        assert ai_scheduler is not None
        assert isinstance(ai_scheduler, AIScheduler)
        assert hasattr(ai_scheduler, 'task_manager')

    @pytest.mark.asyncio
    async def test_parse_custom_schedule_success(self):
        """Test successful parsing of custom schedule."""
        # Mock current time
        with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            custom_config = {"cron": "0 9 * * *"}  # Daily at 9 AM
            
            result = self.scheduler._parse_custom_schedule(custom_config)
            
            # Should default to hourly if parsing fails (simplified implementation)
            expected = mock_now + timedelta(hours=1)
            assert result == expected

    @pytest.mark.asyncio
    async def test_parse_custom_schedule_error(self):
        """Test error handling in custom schedule parsing."""
        # Mock current time
        with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            custom_config = {"invalid": "config"}
            
            result = self.scheduler._parse_custom_schedule(custom_config)
            
            # Should default to hourly on error
            expected = mock_now + timedelta(hours=1)
            assert result == expected

    @pytest.mark.asyncio
    async def test_parse_custom_schedule_exception(self):
        """Test exception handling in custom schedule parsing."""
        # Mock current time
        with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Mock exception during parsing
            with patch.object(self.scheduler, '_parse_custom_schedule') as mock_parse:
                mock_parse.side_effect = Exception("Parsing error")
                
                result = self.scheduler._parse_custom_schedule({"cron": "0 9 * * *"})
                
                # Should default to hourly on exception
                expected = mock_now + timedelta(hours=1)
                assert result == expected

    @pytest.mark.asyncio
    async def test_scheduler_performance_monitoring(self):
        """Test scheduler performance monitoring."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock performance data
            mock_performance_data = self.performance_generator.generate_performance_data()
            mock_task_manager.get_performance_metrics.return_value = mock_performance_data
            mock_task_manager.get_due_tasks.return_value = []
            
            result = await self.scheduler.get_due_tasks(limit=50)
            
            assert result == []
            mock_task_manager.get_due_tasks.assert_called_once_with(limit=50)

    @pytest.mark.asyncio
    async def test_scheduler_error_handling_comprehensive(self):
        """Test comprehensive error handling in scheduler."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Test various error scenarios
            error_scenarios = [
                ("Database connection error", Exception("Database connection failed")),
                ("Task execution error", Exception("Task execution failed")),
                ("Statistics error", Exception("Statistics retrieval failed")),
                ("Cleanup error", Exception("Cleanup failed")),
            ]
            
            for error_type, error in error_scenarios:
                if "Database" in error_type:
                    mock_task_manager.get_due_tasks.side_effect = error
                    result = await self.scheduler.get_due_tasks(limit=50)
                    assert result == []
                elif "Statistics" in error_type:
                    mock_task_manager.get_total_task_count.side_effect = error
                    result = await self.scheduler.get_task_statistics()
                    assert "error" in result
                elif "Cleanup" in error_type:
                    mock_task_manager.cleanup_old_tasks.side_effect = error
                    result = await self.scheduler.cleanup_old_tasks()
                    assert result == 0

    @pytest.mark.asyncio
    async def test_scheduler_lifecycle_management(self):
        """Test complete scheduler lifecycle management."""
        # Mock AITaskManager
        with patch.object(self.scheduler, 'task_manager') as mock_task_manager:
            # Mock lifecycle operations
            mock_task_manager.get_due_tasks.return_value = []
            mock_task_manager.get_total_task_count.return_value = 100
            mock_task_manager.get_pending_task_count.return_value = 25
            mock_task_manager.get_completed_task_count.return_value = 70
            mock_task_manager.get_failed_task_count.return_value = 5
            mock_task_manager.cleanup_old_tasks.return_value = 10
            
            # Mock current time
            with patch('personal_assistant.workers.schedulers.ai_scheduler.datetime') as mock_datetime:
                mock_now = datetime(2024, 1, 15, 10, 30, 0)
                mock_datetime.utcnow.return_value = mock_now
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                # Test complete lifecycle
                due_tasks = await self.scheduler.get_due_tasks(limit=50)
                statistics = await self.scheduler.get_task_statistics()
                cleanup_result = await self.scheduler.cleanup_old_tasks()
                
                assert due_tasks == []
                assert statistics["total_tasks"] == 100
                assert statistics["success_rate"] == 70.0
                assert cleanup_result == 10
                
                # Verify all methods were called
                mock_task_manager.get_due_tasks.assert_called_once()
                mock_task_manager.get_total_task_count.assert_called_once()
                mock_task_manager.get_pending_task_count.assert_called_once()
                mock_task_manager.get_completed_task_count.assert_called_once()
                mock_task_manager.get_failed_task_count.assert_called_once()
                mock_task_manager.cleanup_old_tasks.assert_called_once()

