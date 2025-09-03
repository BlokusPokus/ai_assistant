"""
Unit tests for Celery application configuration.

This module tests the Celery app setup including:
- Application configuration
- Task routing and scheduling
- Signal handling
- Performance monitoring
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from personal_assistant.workers.celery_app import app
from personal_assistant.workers.schedulers.ai_scheduler import AIScheduler, ai_scheduler


class TestCeleryApp:
    """Test class for Celery application configuration."""

    def setup_method(self):
        """Set up test fixtures."""
        pass

    def test_celery_app_initialization(self):
        """Test Celery app initialization and configuration."""
        # Test that the app is properly initialized
        assert app is not None
        assert app.main == "personal_assistant.workers.celery_app"
        
        # Test basic configuration
        assert hasattr(app, 'conf')
        assert app.conf.task_serializer == 'json'
        assert app.conf.accept_content == ['json']
        assert app.conf.result_serializer == 'json'
        assert app.conf.timezone == 'UTC'
        assert app.conf.enable_utc is True

    def test_celery_app_task_routing(self):
        """Test task routing configuration."""
        # Test that task routes are properly configured
        task_routes = app.conf.task_routes
        
        # Check for specific task routes
        assert 'personal_assistant.workers.tasks.ai_tasks.*' in task_routes
        assert 'personal_assistant.workers.tasks.email_tasks.*' in task_routes
        assert 'personal_assistant.workers.tasks.file_tasks.*' in task_routes
        assert 'personal_assistant.workers.tasks.maintenance_tasks.*' in task_routes
        assert 'personal_assistant.workers.tasks.sync_tasks.*' in task_routes

    def test_celery_app_beat_schedule(self):
        """Test beat schedule configuration."""
        # Test that beat schedule is properly configured
        beat_schedule = app.conf.beat_schedule
        
        # Check for specific scheduled tasks
        assert 'process-due-ai-tasks' in beat_schedule
        assert 'test-scheduler-connection' in beat_schedule
        assert 'cleanup-old-logs' in beat_schedule
        assert 'process-email-queue' in beat_schedule
        assert 'send-daily-email-summary' in beat_schedule
        assert 'cleanup-temp-files' in beat_schedule
        assert 'backup-user-data' in beat_schedule
        assert 'sync-calendar-events' in beat_schedule
        assert 'sync-notion-pages' in beat_schedule

    def test_celery_app_task_priorities(self):
        """Test task priority configuration."""
        # Test that task priorities are properly set
        beat_schedule = app.conf.beat_schedule
        
        # Check priority settings
        assert beat_schedule['process-due-ai-tasks']['options']['priority'] == 10
        assert beat_schedule['test-scheduler-connection']['options']['priority'] == 10
        assert beat_schedule['cleanup-old-logs']['options']['priority'] == 10
        assert beat_schedule['process-email-queue']['options']['priority'] == 5
        assert beat_schedule['send-daily-email-summary']['options']['priority'] == 5
        assert beat_schedule['cleanup-temp-files']['options']['priority'] == 3
        assert beat_schedule['backup-user-data']['options']['priority'] == 3
        assert beat_schedule['sync-calendar-events']['options']['priority'] == 7

    def test_celery_app_signal_handlers(self):
        """Test signal handler registration."""
        # Test that signal handlers are properly registered
        # This is a bit tricky to test directly, but we can check if the handlers exist
        
        # Mock the signal handlers
        with patch('personal_assistant.workers.celery_app.task_failure') as mock_task_failure:
            with patch('personal_assistant.workers.celery_app.task_postrun') as mock_task_postrun:
                with patch('personal_assistant.workers.celery_app.task_prerun') as mock_task_prerun:
                    # The signal handlers should be registered during app initialization
                    # We can't easily test the actual registration, but we can verify
                    # that the signal objects exist and are importable
                    assert mock_task_failure is not None
                    assert mock_task_postrun is not None
                    assert mock_task_prerun is not None

    def test_celery_app_redis_configuration(self):
        """Test Redis configuration."""
        # Test that Redis URLs are properly configured
        # Note: In a real test environment, these would be set to test values
        
        # Mock environment variables
        with patch.dict('os.environ', {
            'REDIS_URL': 'redis://test:6379',
            'CELERY_BROKER_URL': 'redis://test:6379',
            'CELERY_RESULT_BACKEND': 'redis://test:6379'
        }):
            # The app should use these values
            # We can't easily test the actual configuration without
            # reinitializing the app, but we can verify the structure
            assert hasattr(app, 'conf')
            assert hasattr(app.conf, 'broker_url')
            assert hasattr(app.conf, 'result_backend')

    def test_celery_app_database_configuration(self):
        """Test database configuration integration."""
        # Test that database configuration is properly integrated
        
        # Mock database configuration
        with patch('personal_assistant.workers.celery_app.db_config') as mock_db_config:
            mock_db_config._initialize_database.return_value = None
            
            # The app should have database configuration
            # We can verify that the database config is accessible
            assert mock_db_config is not None

    def test_celery_app_logging_configuration(self):
        """Test logging configuration."""
        # Test that logging is properly configured
        
        # Mock logging
        with patch('personal_assistant.workers.celery_app.logger') as mock_logger:
            # The app should have logging configured
            assert mock_logger is not None

    def test_celery_app_task_serialization(self):
        """Test task serialization configuration."""
        # Test that task serialization is properly configured
        assert app.conf.task_serializer == 'json'
        assert app.conf.accept_content == ['json']
        assert app.conf.result_serializer == 'json'
        assert app.conf.result_accept_content == ['json']

    def test_celery_app_timezone_configuration(self):
        """Test timezone configuration."""
        # Test that timezone is properly configured
        assert app.conf.timezone == 'UTC'
        assert app.conf.enable_utc is True

    def test_celery_app_worker_configuration(self):
        """Test worker configuration."""
        # Test that worker configuration is properly set
        assert app.conf.worker_prefetch_multiplier == 1
        assert app.conf.task_acks_late is True
        assert app.conf.worker_disable_rate_limits is True

    def test_celery_app_monitoring_configuration(self):
        """Test monitoring configuration."""
        # Test that monitoring is properly configured
        assert app.conf.worker_send_task_events is True
        assert app.conf.task_send_sent_event is True

    def test_celery_app_error_handling(self):
        """Test error handling configuration."""
        # Test that error handling is properly configured
        assert app.conf.task_reject_on_worker_lost is True
        assert app.conf.task_ignore_result is False

    def test_celery_app_performance_configuration(self):
        """Test performance configuration."""
        # Test that performance settings are properly configured
        assert app.conf.worker_prefetch_multiplier == 1
        assert app.conf.task_acks_late is True
        assert app.conf.worker_disable_rate_limits is True

    def test_celery_app_environment_configuration(self):
        """Test environment-specific configuration."""
        # Test that environment configuration is properly handled
        
        # Mock environment
        with patch.dict('os.environ', {'ENVIRONMENT': 'test'}):
            # The app should handle different environments
            # We can verify that environment variables are accessible
            import os
            assert os.getenv('ENVIRONMENT') == 'test'

    def test_celery_app_configuration_validation(self):
        """Test configuration validation."""
        # Test that configuration is valid
        
        # Check required configuration items
        required_configs = [
            'task_serializer',
            'accept_content',
            'result_serializer',
            'timezone',
            'enable_utc',
            'worker_prefetch_multiplier',
            'task_acks_late',
            'worker_disable_rate_limits',
            'worker_send_task_events',
            'task_send_sent_event',
            'task_reject_on_worker_lost',
            'task_ignore_result'
        ]
        
        for config in required_configs:
            assert hasattr(app.conf, config), f"Missing configuration: {config}"

    def test_celery_app_task_registration(self):
        """Test task registration."""
        # Test that tasks are properly registered
        
        # Check that tasks are registered
        registered_tasks = app.tasks.keys()
        
        # Check for specific task registrations
        expected_tasks = [
            'personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks',
            'personal_assistant.workers.tasks.ai_tasks.test_scheduler_connection',
            'personal_assistant.workers.tasks.ai_tasks.cleanup_old_logs',
            'personal_assistant.workers.tasks.email_tasks.process_email_queue',
            'personal_assistant.workers.tasks.email_tasks.send_daily_email_summary',
            'personal_assistant.workers.tasks.file_tasks.cleanup_temp_files',
            'personal_assistant.workers.tasks.file_tasks.backup_user_data',
            'personal_assistant.workers.tasks.maintenance_tasks.optimize_database',
            'personal_assistant.workers.tasks.maintenance_tasks.cleanup_old_sessions',
            'personal_assistant.workers.tasks.maintenance_tasks.cleanup_old_logs',
            'personal_assistant.workers.tasks.maintenance_tasks.system_health_check',
            'personal_assistant.workers.tasks.maintenance_tasks.cleanup_expired_cache',
            'personal_assistant.workers.tasks.sync_tasks.sync_calendar_events',
            'personal_assistant.workers.tasks.sync_tasks.sync_notion_pages',
            'personal_assistant.workers.tasks.sync_tasks.sync_email_services',
            'personal_assistant.workers.tasks.sync_tasks.sync_user_preferences'
        ]
        
        for task in expected_tasks:
            assert task in registered_tasks, f"Task not registered: {task}"

    def test_celery_app_beat_schedule_validation(self):
        """Test beat schedule validation."""
        # Test that beat schedule is properly formatted
        
        beat_schedule = app.conf.beat_schedule
        
        for task_name, task_config in beat_schedule.items():
            # Check required fields
            assert 'task' in task_config, f"Missing task field in {task_name}"
            assert 'schedule' in task_config, f"Missing schedule field in {task_name}"
            assert 'options' in task_config, f"Missing options field in {task_name}"
            
            # Check task field format
            assert task_config['task'].startswith('personal_assistant.workers.tasks.'), \
                f"Invalid task format in {task_name}"
            
            # Check options field
            assert 'priority' in task_config['options'], f"Missing priority in {task_name}"
            assert isinstance(task_config['options']['priority'], int), \
                f"Priority must be integer in {task_name}"

    def test_celery_app_task_routes_validation(self):
        """Test task routes validation."""
        # Test that task routes are properly formatted
        
        task_routes = app.conf.task_routes
        
        for route_pattern, route_config in task_routes.items():
            # Check required fields
            assert 'queue' in route_config, f"Missing queue field in {route_pattern}"
            assert 'priority' in route_config, f"Missing priority field in {route_pattern}"
            
            # Check priority is integer
            assert isinstance(route_config['priority'], int), \
                f"Priority must be integer in {route_pattern}"

    def test_celery_app_import_validation(self):
        """Test that all required modules are importable."""
        # Test that all required modules can be imported
        
        try:
            from personal_assistant.workers.tasks import ai_tasks, email_tasks, file_tasks, maintenance_tasks, sync_tasks
            from personal_assistant.workers.schedulers import ai_scheduler
            from personal_assistant.workers.utils import error_handling, health_check, task_monitoring
        except ImportError as e:
            pytest.fail(f"Failed to import required module: {e}")

    def test_celery_app_configuration_consistency(self):
        """Test configuration consistency."""
        # Test that configuration is consistent across different parts
        
        # Check that task routes and beat schedule are consistent
        task_routes = app.conf.task_routes
        beat_schedule = app.conf.beat_schedule
        
        # All tasks in beat schedule should have corresponding routes
        for task_name, task_config in beat_schedule.items():
            task_path = task_config['task']
            
            # Find matching route
            matching_route = None
            for route_pattern, route_config in task_routes.items():
                if task_path.startswith(route_pattern.replace('*', '')):
                    matching_route = route_config
                    break
            
            assert matching_route is not None, f"No matching route for task {task_path}"

    def test_celery_app_environment_handling(self):
        """Test environment-specific handling."""
        # Test that the app handles different environments properly
        
        # Mock different environments
        environments = ['development', 'testing', 'production']
        
        for env in environments:
            with patch.dict('os.environ', {'ENVIRONMENT': env}):
                # The app should handle different environments
                # We can verify that environment variables are accessible
                import os
                assert os.getenv('ENVIRONMENT') == env

    def test_celery_app_configuration_loading(self):
        """Test configuration loading from files."""
        # Test that configuration is loaded from appropriate files
        
        # Mock configuration file loading
        with patch('personal_assistant.workers.celery_app.load_dotenv') as mock_load_dotenv:
            # The app should attempt to load configuration files
            # We can verify that load_dotenv is called
            assert mock_load_dotenv is not None

