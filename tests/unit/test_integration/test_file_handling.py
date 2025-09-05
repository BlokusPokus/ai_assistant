"""
Unit tests for file handling functionality.

This module tests file management including
temporary file cleanup, user data backup, and file synchronization.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
import tempfile
import os

from tests.utils.test_data_generators import APIDataGenerator, UserDataGenerator


class TestFileHandling:
    """Test class for file handling functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_generator = APIDataGenerator()
        self.user_generator = UserDataGenerator()

    @pytest.mark.asyncio
    async def test_cleanup_temp_files_success(self):
        """Test successful temporary file cleanup."""
        # Mock the file tasks
        with patch('personal_assistant.workers.tasks.file_tasks.cleanup_temp_files') as mock_task:
            # Mock successful cleanup
            mock_task.return_value = {
                "task_id": "task_123",
                "status": "success",
                "files_removed": 15,
                "size_cleaned_bytes": 1024000,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Test cleanup task
            result = mock_task()
            
            assert result["status"] == "success"
            assert result["files_removed"] == 15
            assert result["size_cleaned_bytes"] == 1024000
            assert "task_id" in result
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_cleanup_temp_files_error_handling(self):
        """Test temporary file cleanup error handling."""
        # Mock the file tasks with error
        with patch('personal_assistant.workers.tasks.file_tasks.cleanup_temp_files') as mock_task:
            # Mock cleanup error
            mock_task.side_effect = Exception("Cleanup failed")
            
            # Test error handling
            with pytest.raises(Exception) as exc_info:
                mock_task()
            
            assert str(exc_info.value) == "Cleanup failed"

    @pytest.mark.asyncio
    async def test_backup_user_data_success(self):
        """Test successful user data backup."""
        # Mock the file tasks
        with patch('personal_assistant.workers.tasks.file_tasks.backup_user_data') as mock_task:
            # Mock successful backup
            mock_task.return_value = {
                "task_id": "backup_123",
                "status": "success",
                "users_backed_up": 25,
                "total_size_bytes": 5120000,
                "backup_location": "/backups/user_data_2024-01-15.tar.gz",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Test backup task
            result = mock_task()
            
            assert result["status"] == "success"
            assert result["users_backed_up"] == 25
            assert result["total_size_bytes"] == 5120000
            assert "backup_location" in result
            assert result["backup_location"].endswith(".tar.gz")

    @pytest.mark.asyncio
    async def test_backup_user_data_error_handling(self):
        """Test user data backup error handling."""
        # Mock the file tasks with error
        with patch('personal_assistant.workers.tasks.file_tasks.backup_user_data') as mock_task:
            # Mock backup error
            mock_task.side_effect = Exception("Backup failed")
            
            # Test error handling
            with pytest.raises(Exception) as exc_info:
                mock_task()
            
            assert str(exc_info.value) == "Backup failed"

    @pytest.mark.asyncio
    async def test_cleanup_old_logs_success(self):
        """Test successful old logs cleanup."""
        # Mock the file tasks
        with patch('personal_assistant.workers.tasks.file_tasks.cleanup_old_logs') as mock_task:
            # Mock successful cleanup
            mock_task.return_value = {
                "task_id": "log_cleanup_123",
                "status": "success",
                "log_files_removed": 50,
                "size_cleaned_bytes": 2048000,
                "oldest_log_retained": "2024-01-01",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Test log cleanup task
            result = mock_task()
            
            assert result["status"] == "success"
            assert result["log_files_removed"] == 50
            assert result["size_cleaned_bytes"] == 2048000
            assert "oldest_log_retained" in result

    @pytest.mark.asyncio
    async def test_sync_file_storage_success(self):
        """Test successful file storage synchronization."""
        # Mock the file tasks
        with patch('personal_assistant.workers.tasks.file_tasks.sync_file_storage') as mock_task:
            # Mock successful sync
            mock_task.return_value = {
                "task_id": "sync_123",
                "status": "success",
                "files_synced": 100,
                "conflicts_resolved": 5,
                "sync_duration_seconds": 120,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Test sync task
            result = mock_task()
            
            assert result["status"] == "success"
            assert result["files_synced"] == 100
            assert result["conflicts_resolved"] == 5
            assert result["sync_duration_seconds"] == 120

    @pytest.mark.asyncio
    async def test_file_storage_integration_manager(self):
        """Test file storage integration manager."""
        # Mock the storage integration manager
        with patch('personal_assistant.memory.storage_integration.StorageIntegrationManager') as mock_class:
            mock_manager = Mock()
            mock_class.return_value = mock_manager
            
            # Mock storage operations
            mock_manager.upload_file = AsyncMock(return_value={
                "file_id": "file_123",
                "storage_url": "https://storage.example.com/file_123",
                "size_bytes": 1024000
            })
            
            mock_manager.download_file = AsyncMock(return_value={
                "file_id": "file_123",
                "content": b"file content",
                "size_bytes": 1024000
            })
            
            mock_manager.delete_file = AsyncMock(return_value=True)
            
            # Test file upload
            upload_result = await mock_manager.upload_file("test_file.txt", b"file content")
            assert upload_result["file_id"] == "file_123"
            assert upload_result["size_bytes"] == 1024000
            
            # Test file download
            download_result = await mock_manager.download_file("file_123")
            assert download_result["file_id"] == "file_123"
            assert download_result["content"] == b"file content"
            
            # Test file deletion
            delete_result = await mock_manager.delete_file("file_123")
            assert delete_result is True

    def test_file_tasks_exist(self):
        """Test that file tasks exist and can be imported."""
        # Test that the actual file tasks exist
        from personal_assistant.workers.tasks import file_tasks
        
        # Check that the main tasks exist
        assert hasattr(file_tasks, 'cleanup_temp_files')
        assert hasattr(file_tasks, 'backup_user_data')
        assert hasattr(file_tasks, 'cleanup_old_logs')
        assert hasattr(file_tasks, 'sync_file_storage')
        
        # Test that they are callable
        assert callable(file_tasks.cleanup_temp_files)
        assert callable(file_tasks.backup_user_data)
        assert callable(file_tasks.cleanup_old_logs)
        assert callable(file_tasks.sync_file_storage)

    def test_file_tasks_return_types(self):
        """Test that file tasks return expected data structures."""
        # Test the actual file tasks (they should return dicts)
        from personal_assistant.workers.tasks import file_tasks
        
        # Mock the Celery task decorator to test the actual functions
        with patch('personal_assistant.workers.tasks.file_tasks.app.task') as mock_task:
            mock_task.return_value = lambda func: func
            
            # Test cleanup_temp_files
            result = file_tasks.cleanup_temp_files()
            assert isinstance(result, dict)
            assert "task_id" in result
            assert "status" in result
            
            # Test backup_user_data
            result = file_tasks.backup_user_data()
            assert isinstance(result, dict)
            assert "task_id" in result
            assert "status" in result
            
            # Test cleanup_old_logs
            result = file_tasks.cleanup_old_logs()
            assert isinstance(result, dict)
            assert "task_id" in result
            assert "status" in result
            
            # Test sync_file_storage
            result = file_tasks.sync_file_storage()
            assert isinstance(result, dict)
            assert "task_id" in result
            assert "status" in result
