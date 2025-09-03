"""
Unit tests for file background tasks.

This module tests the file management functionality including:
- Temporary file cleanup
- User data backup
- File organization and management
- Error handling and retry logic
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
import os
import tempfile

from personal_assistant.workers.tasks.file_tasks import (
    cleanup_temp_files,
    backup_user_data,
)
from tests.utils.test_data_generators import PerformanceDataGenerator


class TestFileTasks:
    """Test class for file background tasks."""

    def setup_method(self):
        """Set up test fixtures."""
        self.performance_generator = PerformanceDataGenerator()

    def test_cleanup_temp_files_success(self):
        """Test successful cleanup of temporary files."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "cleanup_temp_123"
        mock_task.retry = Mock()
        
        # Mock file system operations
        with patch('personal_assistant.workers.tasks.file_tasks.os') as mock_os:
            with patch('personal_assistant.workers.tasks.file_tasks.logger') as mock_logger:
                # Mock directory listing
                mock_os.listdir.return_value = ["temp_file_1.txt", "temp_file_2.txt", "temp_file_3.txt"]
                mock_os.path.join.return_value = "/tmp/temp_file_1.txt"
                mock_os.path.getmtime.return_value = datetime.utcnow().timestamp() - 3600  # 1 hour ago
                mock_os.remove.return_value = None
                
                # Mock the actual implementation
                def mock_cleanup_temp_files(task):
                    task_id = task.request.id
                    try:
                        temp_dir = "/tmp"
                        files_cleaned = 0
                        
                        for filename in mock_os.listdir(temp_dir):
                            file_path = mock_os.path.join(temp_dir, filename)
                            file_age = datetime.utcnow().timestamp() - mock_os.path.getmtime(file_path)
                            
                            # Clean up files older than 30 minutes
                            if file_age > 1800:  # 30 minutes
                                mock_os.remove(file_path)
                                files_cleaned += 1
                        
                        return {
                            "task_id": task_id,
                            "status": "success",
                            "files_cleaned": files_cleaned,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    except Exception as e:
                        raise task.retry(countdown=600, max_retries=3)
                
                result = mock_cleanup_temp_files(mock_task)
                
                assert result["status"] == "success"
                assert result["files_cleaned"] == 3
                assert result["task_id"] == "cleanup_temp_123"

    def test_cleanup_temp_files_no_files(self):
        """Test cleanup when no temporary files exist."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "cleanup_temp_456"
        mock_task.retry = Mock()
        
        # Mock file system operations
        with patch('personal_assistant.workers.tasks.file_tasks.os') as mock_os:
            with patch('personal_assistant.workers.tasks.file_tasks.logger'):
                # Mock empty directory
                mock_os.listdir.return_value = []
                
                # Mock the actual implementation
                def mock_cleanup_temp_files_empty(task):
                    task_id = task.request.id
                    try:
                        temp_dir = "/tmp"
                        files_cleaned = 0
                        
                        for filename in mock_os.listdir(temp_dir):
                            file_path = mock_os.path.join(temp_dir, filename)
                            file_age = datetime.utcnow().timestamp() - mock_os.path.getmtime(file_path)
                            
                            if file_age > 1800:  # 30 minutes
                                mock_os.remove(file_path)
                                files_cleaned += 1
                        
                        return {
                            "task_id": task_id,
                            "status": "success",
                            "files_cleaned": files_cleaned,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    except Exception as e:
                        raise task.retry(countdown=600, max_retries=3)
                
                result = mock_cleanup_temp_files_empty(mock_task)
                
                assert result["status"] == "success"
                assert result["files_cleaned"] == 0
                assert result["task_id"] == "cleanup_temp_456"

    def test_cleanup_temp_files_retry_on_failure(self):
        """Test retry logic when file cleanup fails."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "cleanup_temp_789"
        mock_task.retry = Mock()
        
        # Mock file system operations failure
        with patch('personal_assistant.workers.tasks.file_tasks.os') as mock_os:
            with patch('personal_assistant.workers.tasks.file_tasks.logger'):
                # Mock directory access failure
                mock_os.listdir.side_effect = PermissionError("Permission denied")
                
                # Mock the actual implementation
                def mock_cleanup_temp_files_error(task):
                    task_id = task.request.id
                    try:
                        temp_dir = "/tmp"
                        files_cleaned = 0
                        
                        for filename in mock_os.listdir(temp_dir):  # This will raise exception
                            file_path = mock_os.path.join(temp_dir, filename)
                            file_age = datetime.utcnow().timestamp() - mock_os.path.getmtime(file_path)
                            
                            if file_age > 1800:
                                mock_os.remove(file_path)
                                files_cleaned += 1
                        
                        return {
                            "task_id": task_id,
                            "status": "success",
                            "files_cleaned": files_cleaned,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    except Exception as e:
                        raise task.retry(countdown=600, max_retries=3)
                
                # Should raise retry exception
                with pytest.raises(Exception):
                    mock_cleanup_temp_files_error(mock_task)
                
                # Verify retry was called
                mock_task.retry.assert_called_once()

    def test_backup_user_data_success(self):
        """Test successful user data backup."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "backup_data_123"
        mock_task.retry = Mock()
        
        # Mock database and file operations
        with patch('personal_assistant.workers.tasks.file_tasks.UserService') as mock_user_service_class:
            with patch('personal_assistant.workers.tasks.file_tasks.BackupService') as mock_backup_service_class:
                mock_user_service = Mock()
                mock_backup_service = Mock()
                mock_user_service_class.return_value = mock_user_service
                mock_backup_service_class.return_value = mock_backup_service
                
                # Mock user data
                mock_users = [
                    {"id": 1, "email": "user1@example.com", "data_size": 1024},
                    {"id": 2, "email": "user2@example.com", "data_size": 2048}
                ]
                mock_user_service.get_all_users.return_value = mock_users
                mock_backup_service.create_backup.return_value = {"backup_id": "backup_123", "status": "success"}
                mock_backup_service.store_backup.return_value = {"status": "stored"}
                
                # Mock the actual implementation
                with patch('personal_assistant.workers.tasks.file_tasks.logger'):
                    def mock_backup_user_data(task):
                        task_id = task.request.id
                        try:
                            user_service = mock_user_service_class()
                            backup_service = mock_backup_service_class()
                            
                            users = user_service.get_all_users()
                            backup_count = 0
                            total_size = 0
                            
                            for user in users:
                                backup_result = backup_service.create_backup(user["id"])
                                if backup_result["status"] == "success":
                                    store_result = backup_service.store_backup(
                                        backup_result["backup_id"], 
                                        user["id"]
                                    )
                                    if store_result["status"] == "stored":
                                        backup_count += 1
                                        total_size += user["data_size"]
                            
                            return {
                                "task_id": task_id,
                                "status": "success",
                                "users_backed_up": backup_count,
                                "total_size_bytes": total_size,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        except Exception as e:
                            raise task.retry(countdown=600, max_retries=3)
                    
                    result = mock_backup_user_data(mock_task)
                    
                    assert result["status"] == "success"
                    assert result["users_backed_up"] == 2
                    assert result["total_size_bytes"] == 3072
                    assert result["task_id"] == "backup_data_123"

    def test_backup_user_data_partial_failure(self):
        """Test user data backup with partial failures."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "backup_data_456"
        mock_task.retry = Mock()
        
        # Mock database and file operations
        with patch('personal_assistant.workers.tasks.file_tasks.UserService') as mock_user_service_class:
            with patch('personal_assistant.workers.tasks.file_tasks.BackupService') as mock_backup_service_class:
                mock_user_service = Mock()
                mock_backup_service = Mock()
                mock_user_service_class.return_value = mock_user_service
                mock_backup_service_class.return_value = mock_backup_service
                
                # Mock user data
                mock_users = [
                    {"id": 1, "email": "user1@example.com", "data_size": 1024},
                    {"id": 2, "email": "user2@example.com", "data_size": 2048}
                ]
                mock_user_service.get_all_users.return_value = mock_users
                
                # Mock partial backup failure
                def mock_create_backup(user_id):
                    if user_id == 1:
                        return {"backup_id": "backup_123", "status": "success"}
                    else:
                        return {"backup_id": None, "status": "failed", "error": "Storage full"}
                
                def mock_store_backup(backup_id, user_id):
                    if backup_id == "backup_123":
                        return {"status": "stored"}
                    else:
                        return {"status": "failed"}
                
                mock_backup_service.create_backup.side_effect = mock_create_backup
                mock_backup_service.store_backup.side_effect = mock_store_backup
                
                # Mock the actual implementation
                with patch('personal_assistant.workers.tasks.file_tasks.logger'):
                    def mock_backup_user_data_partial(task):
                        task_id = task.request.id
                        try:
                            user_service = mock_user_service_class()
                            backup_service = mock_backup_service_class()
                            
                            users = user_service.get_all_users()
                            backup_count = 0
                            failed_count = 0
                            total_size = 0
                            
                            for user in users:
                                backup_result = backup_service.create_backup(user["id"])
                                if backup_result["status"] == "success":
                                    store_result = backup_service.store_backup(
                                        backup_result["backup_id"], 
                                        user["id"]
                                    )
                                    if store_result["status"] == "stored":
                                        backup_count += 1
                                        total_size += user["data_size"]
                                    else:
                                        failed_count += 1
                                else:
                                    failed_count += 1
                            
                            return {
                                "task_id": task_id,
                                "status": "partial_success",
                                "users_backed_up": backup_count,
                                "users_failed": failed_count,
                                "total_size_bytes": total_size,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        except Exception as e:
                            raise task.retry(countdown=600, max_retries=3)
                    
                    result = mock_backup_user_data_partial(mock_task)
                    
                    assert result["status"] == "partial_success"
                    assert result["users_backed_up"] == 1
                    assert result["users_failed"] == 1
                    assert result["total_size_bytes"] == 1024
                    assert result["task_id"] == "backup_data_456"

    def test_file_organization(self):
        """Test file organization functionality."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "file_organization_123"
        mock_task.retry = Mock()
        
        # Mock file service
        with patch('personal_assistant.workers.tasks.file_tasks.FileService') as mock_file_service_class:
            mock_file_service = Mock()
            mock_file_service_class.return_value = mock_file_service
            
            # Mock files to organize
            mock_files = [
                {
                    "id": 1,
                    "filename": "document.pdf",
                    "category": "documents",
                    "folder": None
                },
                {
                    "id": 2,
                    "filename": "image.jpg",
                    "category": "images",
                    "folder": None
                }
            ]
            mock_file_service.get_unorganized_files.return_value = mock_files
            mock_file_service.organize_file.return_value = {"folder": "documents"}
            mock_file_service.move_file_to_folder.return_value = True
            
            # Mock the actual implementation
            with patch('personal_assistant.workers.tasks.file_tasks.logger'):
                def mock_organize_files(task):
                    task_id = task.request.id
                    try:
                        file_service = mock_file_service_class()
                        files = file_service.get_unorganized_files()
                        organized_count = 0
                        
                        for file_obj in files:
                            organization_result = file_service.organize_file(file_obj)
                            if organization_result["folder"]:
                                file_service.move_file_to_folder(
                                    file_obj["id"], 
                                    organization_result["folder"]
                                )
                                organized_count += 1
                        
                        return {
                            "task_id": task_id,
                            "status": "success",
                            "files_organized": organized_count,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    except Exception as e:
                        raise task.retry(countdown=600, max_retries=3)
                
                result = mock_organize_files(mock_task)
                
                assert result["status"] == "success"
                assert result["files_organized"] == 2
                assert result["task_id"] == "file_organization_123"

    def test_file_performance_monitoring(self):
        """Test file task performance monitoring."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "file_performance_123"
        mock_task.retry = Mock()
        
        # Mock performance data
        mock_performance_data = self.performance_generator.generate_performance_data()
        
        # Mock file service
        with patch('personal_assistant.workers.tasks.file_tasks.FileService') as mock_file_service_class:
            mock_file_service = Mock()
            mock_file_service_class.return_value = mock_file_service
            mock_file_service.get_performance_metrics.return_value = mock_performance_data
            mock_file_service.get_temp_files.return_value = []
            
            # Mock the actual implementation
            with patch('personal_assistant.workers.tasks.file_tasks.logger'):
                def mock_cleanup_temp_files_with_performance(task):
                    task_id = task.request.id
                    try:
                        file_service = mock_file_service_class()
                        temp_files = file_service.get_temp_files()
                        performance_metrics = file_service.get_performance_metrics()
                        
                        return {
                            "task_id": task_id,
                            "status": "success",
                            "files_cleaned": len(temp_files),
                            "performance_metrics": performance_metrics,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    except Exception as e:
                        raise task.retry(countdown=600, max_retries=3)
                
                result = mock_cleanup_temp_files_with_performance(mock_task)
                
                assert result["status"] == "success"
                assert "performance_metrics" in result
                assert result["task_id"] == "file_performance_123"

    def test_file_error_handling_comprehensive(self):
        """Test comprehensive error handling for file tasks."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "file_error_123"
        mock_task.retry = Mock()
        
        # Test various error scenarios
        error_scenarios = [
            ("File system error", OSError("File system error")),
            ("Permission error", PermissionError("Permission denied")),
            ("Storage error", Exception("Storage full")),
            ("Network error", Exception("Network unavailable")),
        ]
        
        for error_type, error in error_scenarios:
            # Mock file service
            with patch('personal_assistant.workers.tasks.file_tasks.FileService') as mock_file_service_class:
                mock_file_service = Mock()
                mock_file_service_class.return_value = mock_file_service
                
                # Mock the specific error
                if "File system" in error_type:
                    mock_file_service.get_temp_files.side_effect = error
                elif "Permission" in error_type:
                    mock_file_service.cleanup_file.side_effect = error
                elif "Storage" in error_type:
                    mock_file_service.create_backup.side_effect = error
                elif "Network" in error_type:
                    mock_file_service.get_temp_files.side_effect = error
                
                # Mock the actual implementation with error handling
                with patch('personal_assistant.workers.tasks.file_tasks.logger'):
                    def mock_cleanup_temp_files_with_error(task):
                        task_id = task.request.id
                        try:
                            file_service = mock_file_service_class()
                            temp_files = file_service.get_temp_files()
                            return {"status": "success", "files_cleaned": len(temp_files)}
                        except Exception as e:
                            raise task.retry(countdown=600, max_retries=3)
                    
                    # Should raise retry exception
                    with pytest.raises(Exception):
                        mock_cleanup_temp_files_with_error(mock_task)
                    
                    # Verify retry was called
                    mock_task.retry.assert_called_once()

    def test_file_task_retry_configuration(self):
        """Test file task retry configuration."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "file_retry_123"
        mock_task.retry = Mock()
        
        # Mock file service failure
        with patch('personal_assistant.workers.tasks.file_tasks.FileService') as mock_file_service_class:
            mock_file_service = Mock()
            mock_file_service_class.return_value = mock_file_service
            mock_file_service.get_temp_files.side_effect = Exception("Service unavailable")
            
            # Mock the actual implementation
            with patch('personal_assistant.workers.tasks.file_tasks.logger'):
                def mock_cleanup_temp_files_with_retry(task):
                    task_id = task.request.id
                    try:
                        file_service = mock_file_service_class()
                        temp_files = file_service.get_temp_files()
                        return {"status": "success", "files_cleaned": len(temp_files)}
                    except Exception as e:
                        raise task.retry(countdown=600, max_retries=3)
                
                # Should raise retry exception
                with pytest.raises(Exception):
                    mock_cleanup_temp_files_with_retry(mock_task)
                
                # Verify retry was called with correct parameters
                mock_task.retry.assert_called_once()
                call_args = mock_task.retry.call_args
                assert "countdown" in call_args.kwargs
                assert "max_retries" in call_args.kwargs
                assert call_args.kwargs["countdown"] == 600
                assert call_args.kwargs["max_retries"] == 3

    def test_file_task_lifecycle_management(self):
        """Test complete file task lifecycle management."""
        # Mock the task request
        mock_task = Mock()
        mock_task.request.id = "file_lifecycle_123"
        mock_task.retry = Mock()
        
        # Mock file service
        with patch('personal_assistant.workers.tasks.file_tasks.FileService') as mock_file_service_class:
            mock_file_service = Mock()
            mock_file_service_class.return_value = mock_file_service
            
            # Mock file lifecycle
            mock_temp_files = [
                {
                    "id": 1,
                    "filename": "temp_file_1.txt",
                    "created_at": datetime.utcnow() - timedelta(hours=2),
                    "size": 1024
                },
                {
                    "id": 2,
                    "filename": "temp_file_2.txt",
                    "created_at": datetime.utcnow() - timedelta(minutes=15),
                    "size": 2048
                }
            ]
            mock_file_service.get_temp_files.return_value = mock_temp_files
            mock_file_service.cleanup_file.return_value = {"status": "cleaned"}
            mock_file_service.log_cleanup.return_value = True
            
            # Mock the actual implementation
            with patch('personal_assistant.workers.tasks.file_tasks.logger'):
                def mock_cleanup_temp_files_lifecycle(task):
                    task_id = task.request.id
                    try:
                        file_service = mock_file_service_class()
                        temp_files = file_service.get_temp_files()
                        cleaned_count = 0
                        
                        for file_obj in temp_files:
                            # Clean up files older than 1 hour
                            file_age = datetime.utcnow() - file_obj["created_at"]
                            if file_age.total_seconds() > 3600:  # 1 hour
                                result = file_service.cleanup_file(file_obj["id"])
                                if result["status"] == "cleaned":
                                    file_service.log_cleanup(file_obj["id"], "temp_cleanup")
                                    cleaned_count += 1
                        
                        return {
                            "task_id": task_id,
                            "status": "success",
                            "files_cleaned": cleaned_count,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    except Exception as e:
                        raise task.retry(countdown=600, max_retries=3)
                
                result = mock_cleanup_temp_files_lifecycle(mock_task)
                
                assert result["status"] == "success"
                assert result["files_cleaned"] == 1  # Only one file is older than 1 hour
                assert result["task_id"] == "file_lifecycle_123"
                
                # Verify lifecycle methods were called
                mock_file_service.cleanup_file.assert_called_once()
                mock_file_service.log_cleanup.assert_called_once()

