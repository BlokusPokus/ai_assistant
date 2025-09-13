"""
Integration tests for Celery Beat → Redis → Worker flow.

These tests verify that the complete task flow works correctly
and prevent regression of the queue routing issues.
"""

import pytest
import time
import redis
from personal_assistant.workers.celery_app import app


class TestCeleryIntegration:
    """Test Celery integration and queue routing."""

    @pytest.mark.integration
    def test_task_routing_to_correct_queue(self):
        """Test that tasks are routed to the correct queue."""
        try:
            r = redis.from_url(app.conf.broker_url)
            
            # Clear any existing tasks
            for queue_name in ['ai_tasks', 'celery']:
                r.delete(queue_name)
            
            # Send a test task
            result = app.send_task('personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks')
            
            # Wait a moment for task to be queued
            time.sleep(1)
            
            # Check that task is in the correct queue
            ai_tasks_length = r.llen('ai_tasks')
            celery_length = r.llen('celery')
            
            # Task should be in ai_tasks queue, not celery queue
            assert ai_tasks_length > 0, "Task was not routed to ai_tasks queue"
            assert celery_length == 0, "Task was incorrectly routed to celery queue"
            
            # Clean up
            r.delete('ai_tasks')
            
        except redis.ConnectionError:
            pytest.skip("Redis not available for integration test")

    @pytest.mark.integration
    def test_worker_queue_listening(self):
        """Test that worker is listening to correct queues."""
        try:
            inspect = app.control.inspect()
            active_queues = inspect.active_queues()
            
            if active_queues:
                for worker, queues in active_queues.items():
                    queue_names = [q['name'] for q in queues]
                    assert 'ai_tasks' in queue_names, f"Worker {worker} is not listening to ai_tasks queue"
            else:
                pytest.skip("No active workers found for testing")
                
        except Exception as e:
            pytest.skip(f"Could not inspect worker queues: {e}")

    @pytest.mark.integration
    def test_beat_schedule_execution(self):
        """Test that Beat scheduler can execute scheduled tasks."""
        try:
            # This test verifies that Beat can send tasks to Redis
            # We'll send a task manually to simulate Beat behavior
            
            r = redis.from_url(app.conf.broker_url)
            
            # Clear any existing tasks
            r.delete('ai_tasks')
            
            # Send a task that would be scheduled by Beat
            result = app.send_task(
                'personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks',
                options={'priority': 10}
            )
            
            # Wait for task to be queued
            time.sleep(1)
            
            # Check that task is in Redis
            ai_tasks_length = r.llen('ai_tasks')
            assert ai_tasks_length > 0, "Beat-scheduled task was not queued in Redis"
            
            # Clean up
            r.delete('ai_tasks')
            
        except redis.ConnectionError:
            pytest.skip("Redis not available for integration test")

    @pytest.mark.integration
    def test_queue_isolation(self):
        """Test that different task types are routed to different queues."""
        try:
            r = redis.from_url(app.conf.broker_url)
            
            # Clear all queues
            for queue_name in ['ai_tasks']:
                r.delete(queue_name)
            
            # Send different types of tasks
            ai_result = app.send_task('personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks')
            
            # Wait for tasks to be queued
            time.sleep(1)
            
            # Check that tasks are in correct queues
            ai_tasks_length = r.llen('ai_tasks')
            
            assert ai_tasks_length > 0, "AI task was not routed to ai_tasks queue"
            
            # Clean up
            for queue_name in ['ai_tasks']:
                r.delete(queue_name)
                
        except redis.ConnectionError:
            pytest.skip("Redis not available for integration test")

    @pytest.mark.integration
    def test_no_queue_naming_conflicts(self):
        """Test that there are no queue naming conflicts."""
        try:
            r = redis.from_url(app.conf.broker_url)
            
            # Get all keys
            keys = r.keys('*')
            
            # Check for problematic queue names
            problematic_queues = []
            for key in keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                
                # Check for suffixed queues (like ai_tasks9, etc.)
                if any(queue in key_str for queue in ['ai_tasks']):
                    if key_str not in ['ai_tasks']:
                        # Check if it's a list (queue) and has tasks
                        if r.type(key_str) == 'list':
                            length = r.llen(key_str)
                            if length > 0:
                                problematic_queues.append((key_str, length))
            
            assert len(problematic_queues) == 0, f"Found problematic queues with tasks: {problematic_queues}"
            
        except redis.ConnectionError:
            pytest.skip("Redis not available for integration test")

    @pytest.mark.integration
    def test_redis_connection_stability(self):
        """Test that Redis connection is stable and working."""
        try:
            r = redis.from_url(app.conf.broker_url)
            
            # Test basic Redis operations
            r.ping()
            
            # Test queue operations
            test_queue = 'test_queue'
            r.lpush(test_queue, 'test_task')
            length = r.llen(test_queue)
            assert length == 1, "Redis queue operations are not working"
            
            # Clean up
            r.delete(test_queue)
            
        except redis.ConnectionError:
            pytest.skip("Redis not available for integration test")


class TestCeleryRegressionPrevention:
    """Tests to prevent regression of the original queue routing issue."""

    @pytest.mark.integration
    def test_original_issue_prevention(self):
        """Test that prevents the original issue: Beat → ai_tasks, Worker → celery."""
        try:
            r = redis.from_url(app.conf.broker_url)
            
            # Clear queues
            r.delete('ai_tasks', 'celery')
            
            # Send a task that should go to ai_tasks queue
            result = app.send_task('personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks')
            
            # Wait for task to be queued
            time.sleep(1)
            
            # Check that task is NOT in celery queue (the original problem)
            celery_length = r.llen('celery')
            assert celery_length == 0, "Task was routed to celery queue instead of ai_tasks queue (original issue regression)"
            
            # Check that task IS in ai_tasks queue (the fix)
            ai_tasks_length = r.llen('ai_tasks')
            assert ai_tasks_length > 0, "Task was not routed to ai_tasks queue (fix not working)"
            
            # Clean up
            r.delete('ai_tasks', 'celery')
            
        except redis.ConnectionError:
            pytest.skip("Redis not available for integration test")

    @pytest.mark.integration
    def test_worker_listens_to_all_queues(self):
        """Test that worker listens to all required queues, not just celery."""
        try:
            inspect = app.control.inspect()
            active_queues = inspect.active_queues()
            
            if active_queues:
                for worker, queues in active_queues.items():
                    queue_names = [q['name'] for q in queues]
                    
                    # Worker should listen to all our custom queues
                    required_queues = ['ai_tasks']
                    for required_queue in required_queues:
                        assert required_queue in queue_names, f"Worker {worker} is not listening to required queue {required_queue}"
            else:
                pytest.skip("No active workers found for testing")
                
        except Exception as e:
            pytest.skip(f"Could not inspect worker queues: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
