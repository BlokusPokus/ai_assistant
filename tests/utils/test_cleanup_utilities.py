"""
Test Cleanup Utilities

This module provides utilities for cleaning up test data, temporary files,
mock objects, and other resources created during testing.
"""

import os
import shutil
import tempfile
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from unittest.mock import Mock, patch
from contextlib import contextmanager
import pytest


class TestCleanupManager:
    """Manager for test cleanup operations."""
    
    def __init__(self):
        self._cleanup_tasks = []
        self._temp_directories = []
        self._temp_files = []
        self._mock_objects = []
        self._patches = []
        self._database_records = []
        self._external_resources = []
    
    def add_cleanup_task(self, task: Callable, *args, **kwargs):
        """Add a cleanup task to be executed."""
        self._cleanup_tasks.append((task, args, kwargs))
    
    def add_temp_directory(self, temp_dir: str):
        """Add a temporary directory to be cleaned up."""
        self._temp_directories.append(temp_dir)
    
    def add_temp_file(self, temp_file: str):
        """Add a temporary file to be cleaned up."""
        self._temp_files.append(temp_file)
    
    def add_mock_object(self, mock_obj: Mock):
        """Add a mock object to be cleaned up."""
        self._mock_objects.append(mock_obj)
    
    def add_patch(self, patch_obj):
        """Add a patch object to be cleaned up."""
        self._patches.append(patch_obj)
    
    def add_database_record(self, session, model_class, record_id: Any):
        """Add a database record to be cleaned up."""
        self._database_records.append((session, model_class, record_id))
    
    def add_external_resource(self, resource_type: str, resource_id: str, cleanup_func: Callable):
        """Add an external resource to be cleaned up."""
        self._external_resources.append((resource_type, resource_id, cleanup_func))
    
    def cleanup_all(self):
        """Execute all cleanup tasks."""
        # Clean up external resources first
        for resource_type, resource_id, cleanup_func in self._external_resources:
            try:
                cleanup_func(resource_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup external resource {resource_type}:{resource_id}: {e}")
        
        # Clean up database records
        for session, model_class, record_id in self._database_records:
            try:
                record = session.query(model_class).get(record_id)
                if record:
                    session.delete(record)
                    session.commit()
            except Exception as e:
                print(f"Warning: Failed to cleanup database record {model_class.__name__}:{record_id}: {e}")
                try:
                    session.rollback()
                except Exception:
                    pass
        
        # Stop patches
        for patch_obj in self._patches:
            try:
                patch_obj.stop()
            except Exception as e:
                print(f"Warning: Failed to stop patch: {e}")
        
        # Reset mock objects
        for mock_obj in self._mock_objects:
            try:
                if hasattr(mock_obj, 'reset_mock'):
                    mock_obj.reset_mock()
                if hasattr(mock_obj, 'stop'):
                    mock_obj.stop()
            except Exception as e:
                print(f"Warning: Failed to reset mock object: {e}")
        
        # Remove temporary files
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Warning: Failed to remove temp file {temp_file}: {e}")
        
        # Remove temporary directories
        for temp_dir in self._temp_directories:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Failed to remove temp directory {temp_dir}: {e}")
        
        # Execute custom cleanup tasks
        for task, args, kwargs in self._cleanup_tasks:
            try:
                task(*args, **kwargs)
            except Exception as e:
                print(f"Warning: Failed to execute cleanup task {task.__name__}: {e}")
        
        # Clear all lists
        self._cleanup_tasks.clear()
        self._temp_directories.clear()
        self._temp_files.clear()
        self._mock_objects.clear()
        self._patches.clear()
        self._database_records.clear()
        self._external_resources.clear()


class FileCleanupUtilities:
    """Utilities for cleaning up files and directories."""
    
    @staticmethod
    def cleanup_temp_directory(temp_dir: str):
        """Clean up a temporary directory."""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Failed to cleanup temp directory {temp_dir}: {e}")
    
    @staticmethod
    def cleanup_temp_file(temp_file: str):
        """Clean up a temporary file."""
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except Exception as e:
            print(f"Warning: Failed to cleanup temp file {temp_file}: {e}")
    
    @staticmethod
    def cleanup_files_by_pattern(directory: str, pattern: str):
        """Clean up files matching a pattern in a directory."""
        try:
            import glob
            pattern_path = os.path.join(directory, pattern)
            for file_path in glob.glob(pattern_path):
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path, ignore_errors=True)
                except Exception as e:
                    print(f"Warning: Failed to cleanup file {file_path}: {e}")
        except Exception as e:
            print(f"Warning: Failed to cleanup files by pattern {pattern}: {e}")
    
    @staticmethod
    def cleanup_old_files(directory: str, max_age_hours: int = 24):
        """Clean up files older than specified hours."""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > max_age_seconds:
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Warning: Failed to cleanup old file {file_path}: {e}")
        except Exception as e:
            print(f"Warning: Failed to cleanup old files in {directory}: {e}")


class DatabaseCleanupUtilities:
    """Utilities for cleaning up database records."""
    
    @staticmethod
    def cleanup_user_records(session, user_ids: List[int]):
        """Clean up user records by IDs."""
        try:
            from src.personal_assistant.database.models.users import User
            for user_id in user_ids:
                user = session.query(User).get(user_id)
                if user:
                    session.delete(user)
            session.commit()
        except Exception as e:
            print(f"Warning: Failed to cleanup user records: {e}")
            try:
                session.rollback()
            except Exception:
                pass
    
    @staticmethod
    def cleanup_test_data(session, table_name: str, test_prefix: str = "test_"):
        """Clean up test data from a specific table."""
        try:
            # This would be implemented based on your specific database models
            # For now, it's a placeholder
            pass
        except Exception as e:
            print(f"Warning: Failed to cleanup test data from {table_name}: {e}")
            try:
                session.rollback()
            except Exception:
                pass
    
    @staticmethod
    def cleanup_all_test_data(session):
        """Clean up all test data from the database."""
        try:
            # This would be implemented based on your specific database models
            # For now, it's a placeholder
            pass
        except Exception as e:
            print(f"Warning: Failed to cleanup all test data: {e}")
            try:
                session.rollback()
            except Exception:
                pass
    
    @staticmethod
    def reset_database_sequences(session):
        """Reset database sequences to start from 1."""
        try:
            # This would be implemented based on your specific database
            # For now, it's a placeholder
            pass
        except Exception as e:
            print(f"Warning: Failed to reset database sequences: {e}")


class MockCleanupUtilities:
    """Utilities for cleaning up mock objects."""
    
    @staticmethod
    def cleanup_mock_objects(*mock_objects):
        """Clean up multiple mock objects."""
        for mock_obj in mock_objects:
            try:
                if hasattr(mock_obj, 'reset_mock'):
                    mock_obj.reset_mock()
                if hasattr(mock_obj, 'stop'):
                    mock_obj.stop()
            except Exception as e:
                print(f"Warning: Failed to cleanup mock object: {e}")
    
    @staticmethod
    def cleanup_patches(*patches):
        """Clean up multiple patch objects."""
        for patch_obj in patches:
            try:
                patch_obj.stop()
            except Exception as e:
                print(f"Warning: Failed to stop patch: {e}")
    
    @staticmethod
    def cleanup_all_mocks():
        """Clean up all active mocks and patches."""
        try:
            # This would clean up all active mocks
            # For now, it's a placeholder
            pass
        except Exception as e:
            print(f"Warning: Failed to cleanup all mocks: {e}")


class ExternalResourceCleanupUtilities:
    """Utilities for cleaning up external resources."""
    
    @staticmethod
    def cleanup_redis_keys(redis_client, key_pattern: str = "test_*"):
        """Clean up Redis keys matching a pattern."""
        try:
            keys = redis_client.keys(key_pattern)
            if keys:
                redis_client.delete(*keys)
        except Exception as e:
            print(f"Warning: Failed to cleanup Redis keys {key_pattern}: {e}")
    
    @staticmethod
    def cleanup_s3_objects(s3_client, bucket: str, prefix: str = "test/"):
        """Clean up S3 objects with a specific prefix."""
        try:
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if 'Contents' in response:
                objects = [{'Key': obj['Key']} for obj in response['Contents']]
                if objects:
                    s3_client.delete_objects(Bucket=bucket, Delete={'Objects': objects})
        except Exception as e:
            print(f"Warning: Failed to cleanup S3 objects {prefix}: {e}")
    
    @staticmethod
    def cleanup_email_queue(email_service, queue_name: str = "test_queue"):
        """Clean up email queue."""
        try:
            # This would be implemented based on your specific email service
            # For now, it's a placeholder
            pass
        except Exception as e:
            print(f"Warning: Failed to cleanup email queue {queue_name}: {e}")
    
    @staticmethod
    def cleanup_sms_queue(sms_service, queue_name: str = "test_queue"):
        """Clean up SMS queue."""
        try:
            # This would be implemented based on your specific SMS service
            # For now, it's a placeholder
            pass
        except Exception as e:
            print(f"Warning: Failed to cleanup SMS queue {queue_name}: {e}")


class AsyncCleanupUtilities:
    """Utilities for cleaning up async resources."""
    
    @staticmethod
    async def cleanup_async_resources(*cleanup_funcs):
        """Clean up multiple async resources."""
        for cleanup_func in cleanup_funcs:
            try:
                if asyncio.iscoroutinefunction(cleanup_func):
                    await cleanup_func()
                else:
                    cleanup_func()
            except Exception as e:
                print(f"Warning: Failed to cleanup async resource: {e}")
    
    @staticmethod
    async def cleanup_async_database_connections(connections: List[Any]):
        """Clean up async database connections."""
        for connection in connections:
            try:
                if hasattr(connection, 'close'):
                    if asyncio.iscoroutinefunction(connection.close):
                        await connection.close()
                    else:
                        connection.close()
            except Exception as e:
                print(f"Warning: Failed to cleanup async database connection: {e}")
    
    @staticmethod
    async def cleanup_async_http_clients(clients: List[Any]):
        """Clean up async HTTP clients."""
        for client in clients:
            try:
                if hasattr(client, 'close'):
                    if asyncio.iscoroutinefunction(client.close):
                        await client.close()
                    else:
                        client.close()
            except Exception as e:
                print(f"Warning: Failed to cleanup async HTTP client: {e}")


# Global cleanup manager
cleanup_manager = TestCleanupManager()


@contextmanager
def test_cleanup():
    """Context manager for test cleanup."""
    manager = TestCleanupManager()
    try:
        yield manager
    finally:
        manager.cleanup_all()


@pytest.fixture
def test_cleanup_manager():
    """Pytest fixture for test cleanup manager."""
    manager = TestCleanupManager()
    yield manager
    manager.cleanup_all()


@pytest.fixture
def temp_directory_cleanup():
    """Pytest fixture for temporary directory cleanup."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    FileCleanupUtilities.cleanup_temp_directory(temp_dir)


@pytest.fixture
def temp_file_cleanup():
    """Pytest fixture for temporary file cleanup."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_file = f.name
    yield temp_file
    FileCleanupUtilities.cleanup_temp_file(temp_file)


def get_cleanup_manager() -> TestCleanupManager:
    """Get the global cleanup manager."""
    return cleanup_manager


def register_cleanup_task(task: Callable, *args, **kwargs):
    """Register a cleanup task with the global manager."""
    cleanup_manager.add_cleanup_task(task, *args, **kwargs)


def register_temp_directory(temp_dir: str):
    """Register a temporary directory for cleanup."""
    cleanup_manager.add_temp_directory(temp_dir)


def register_temp_file(temp_file: str):
    """Register a temporary file for cleanup."""
    cleanup_manager.add_temp_file(temp_file)


def register_mock_object(mock_obj: Mock):
    """Register a mock object for cleanup."""
    cleanup_manager.add_mock_object(mock_obj)


def register_patch(patch_obj):
    """Register a patch object for cleanup."""
    cleanup_manager.add_patch(patch_obj)


def execute_cleanup():
    """Execute all registered cleanup tasks."""
    cleanup_manager.cleanup_all()

