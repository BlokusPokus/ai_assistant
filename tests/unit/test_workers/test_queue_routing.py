"""
Unit tests for Celery queue routing configuration.

These tests ensure that queue routing is properly configured and prevent
regression of the queue routing issues that were fixed in Task 070.
"""

import pytest
import redis
from unittest.mock import patch, MagicMock
from personal_assistant.workers.celery_app import app


class TestQueueRouting:
    """Test queue routing configuration."""

    def test_task_routes_configuration(self):
        """Test that task routes are configured correctly."""
        routes = app.conf.task_routes

        # Test AI tasks routing
        assert 'personal_assistant.workers.tasks.ai_tasks.*' in routes
        assert routes['personal_assistant.workers.tasks.ai_tasks.*']['queue'] == 'ai_tasks'
        assert routes['personal_assistant.workers.tasks.ai_tasks.*']['priority'] == 10





    def test_queue_declarations(self):
        """Test that queues are properly declared."""
        queues = app.conf.task_queues
        queue_names = [q.name for q in queues]

        expected_queues = ['ai_tasks']
        for queue in expected_queues:
            assert queue in queue_names

    def test_default_queue_configuration(self):
        """Test default queue configuration."""
        assert app.conf.task_default_queue == 'ai_tasks'
        assert app.conf.task_default_exchange == 'ai_tasks'
        assert app.conf.task_default_exchange_type == 'direct'
        assert app.conf.task_default_routing_key == 'ai_tasks'

    def test_beat_schedule_configuration(self):
        """Test beat schedule configuration."""
        schedule = app.conf.beat_schedule

        # Test AI tasks schedule
        assert 'process-due-ai-tasks' in schedule
        assert schedule['process-due-ai-tasks']['task'] == 'personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks'
        assert schedule['process-due-ai-tasks']['options']['priority'] == 10



    def test_queue_routing_consistency(self):
        """Test that queue routing is consistent across configuration."""
        routes = app.conf.task_routes
        queues = app.conf.task_queues
        queue_names = [q.name for q in queues]

        # Ensure all routed queues are declared
        for pattern, config in routes.items():
            queue_name = config['queue']
            assert queue_name in queue_names, f"Queue '{queue_name}' from route '{pattern}' is not declared"

    def test_priority_ordering(self):
        """Test that task priorities are properly ordered."""
        routes = app.conf.task_routes

        # AI tasks should have highest priority
        ai_priority = routes['personal_assistant.workers.tasks.ai_tasks.*']['priority']
        assert ai_priority == 10




    def test_redis_connection_configuration(self):
        """Test Redis connection configuration."""
        broker_url = app.conf.broker_url
        result_backend = app.conf.result_backend

        # Both should use Redis
        assert 'redis://' in broker_url
        assert 'redis://' in result_backend

        # Should use same Redis instance
        assert broker_url == result_backend

    @pytest.mark.integration
    def test_queue_names_are_clean(self):
        """Test that Redis queue names don't have special characters."""
        # This test requires Redis to be running
        try:
            r = redis.from_url(app.conf.broker_url)
            
            # Get all keys
            keys = r.keys('*')
            
            # Check for problematic queue names with special characters
            problematic_queues = []
            for key in keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                if any(char in key_str for char in ['\x06', '\x169', '\x163', '\x166']):
                    problematic_queues.append(key_str)
            
            assert len(problematic_queues) == 0, f"Found problematic queue names: {problematic_queues}"
            
        except redis.ConnectionError:
            pytest.skip("Redis not available for integration test")

    @pytest.mark.integration
    def test_no_accumulated_tasks_in_suffixed_queues(self):
        """Test that there are no accumulated tasks in suffixed queues."""
        try:
            r = redis.from_url(app.conf.broker_url)
            
            # Check for suffixed queues (like ai_tasks9, etc.)
            keys = r.keys('*')
            suffixed_queues = []
            
            for key in keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                if any(queue in key_str for queue in ['ai_tasks']):
                    if key_str not in ['ai_tasks']:
                        # Check if it's a list (queue) and has tasks
                        if r.type(key_str) == 'list':
                            length = r.llen(key_str)
                            if length > 0:
                                suffixed_queues.append((key_str, length))
            
            assert len(suffixed_queues) == 0, f"Found accumulated tasks in suffixed queues: {suffixed_queues}"
            
        except redis.ConnectionError:
            pytest.skip("Redis not available for integration test")


class TestQueueRoutingRegression:
    """Test to prevent regression of the original queue routing issue."""

    def test_worker_listens_to_correct_queues(self):
        """Test that worker configuration includes all required queues."""
        # This test verifies the Docker configuration would include the correct queues
        expected_queues = ['ai_tasks']
        
        # The worker command should include all these queues
        # This is verified by checking that all queues are declared in Celery config
        declared_queues = [q.name for q in app.conf.task_queues]
        
        for queue in expected_queues:
            assert queue in declared_queues, f"Queue '{queue}' is not declared in Celery configuration"

    def test_beat_sends_to_correct_queues(self):
        """Test that Beat scheduler sends tasks to correct queues."""
        schedule = app.conf.beat_schedule
        
        # Check that scheduled tasks are routed to correct queues
        for schedule_name, config in schedule.items():
            task_name = config['task']
            
            # Determine expected queue based on task name
            if 'ai_tasks' in task_name:
                expected_queue = 'ai_tasks'
            else:
                expected_queue = 'ai_tasks'  # default
            
            # Check that task routing matches expected queue
            task_routes = app.conf.task_routes
            task_pattern = f"{task_name.split('.')[:-1]}.*"  # Get pattern like "personal_assistant.workers.tasks.ai_tasks.*"
            task_pattern = '.'.join(task_name.split('.')[:-1]) + '.*'
            
            if task_pattern in task_routes:
                actual_queue = task_routes[task_pattern]['queue']
                assert actual_queue == expected_queue, f"Task '{task_name}' routes to '{actual_queue}' but should route to '{expected_queue}'"

    def test_no_default_celery_queue_conflicts(self):
        """Test that we don't have conflicts with default Celery queue."""
        # Ensure our tasks don't accidentally route to the default 'celery' queue
        routes = app.conf.task_routes
        
        for pattern, config in routes.items():
            queue_name = config['queue']
            assert queue_name != 'celery', f"Task pattern '{pattern}' routes to default 'celery' queue instead of specific queue"

    def test_queue_naming_consistency(self):
        """Test that queue names are consistent and don't have special characters."""
        queues = app.conf.task_queues
        
        for queue in queues:
            queue_name = queue.name
            
            # Queue names should be clean (no special characters)
            assert all(c.isalnum() or c in '_-' for c in queue_name), f"Queue name '{queue_name}' contains invalid characters"
            
            # Queue names should not have numeric suffixes
            assert not queue_name[-1].isdigit(), f"Queue name '{queue_name}' has numeric suffix, indicating potential naming conflict"
            
            # Routing key should match queue name
            assert queue.routing_key == queue_name, f"Routing key '{queue.routing_key}' doesn't match queue name '{queue_name}'"


if __name__ == "__main__":
    pytest.main([__file__])
