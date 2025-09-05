"""
Common Test Utilities

This module provides common utilities and helper functions for testing
including assertions, context managers, and test helpers.
"""

import asyncio
import functools
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch
import pytest
import tempfile
import shutil
from pathlib import Path


class TestAssertions:
    """Custom test assertions for common testing scenarios."""
    
    @staticmethod
    def assert_dict_contains(dict_obj: Dict[str, Any], expected_keys: List[str]):
        """Assert that a dictionary contains all expected keys."""
        missing_keys = [key for key in expected_keys if key not in dict_obj]
        assert not missing_keys, f"Dictionary missing keys: {missing_keys}"
    
    @staticmethod
    def assert_dict_has_values(dict_obj: Dict[str, Any], expected_values: Dict[str, Any]):
        """Assert that a dictionary has the expected values for given keys."""
        for key, expected_value in expected_values.items():
            assert key in dict_obj, f"Key '{key}' not found in dictionary"
            assert dict_obj[key] == expected_value, f"Value for key '{key}' is {dict_obj[key]}, expected {expected_value}"
    
    @staticmethod
    def assert_response_success(response: Dict[str, Any], expected_status: int = 200):
        """Assert that an API response indicates success."""
        assert "status_code" in response, "Response missing status_code"
        assert response["status_code"] == expected_status, f"Expected status {expected_status}, got {response['status_code']}"
        
        if "body" in response and isinstance(response["body"], dict):
            assert "success" in response["body"], "Response body missing success field"
            assert response["body"]["success"] is True, "Response indicates failure"
    
    @staticmethod
    def assert_response_error(response: Dict[str, Any], expected_status: int = 400):
        """Assert that an API response indicates an error."""
        assert "status_code" in response, "Response missing status_code"
        assert response["status_code"] == expected_status, f"Expected status {expected_status}, got {response['status_code']}"
        
        if "body" in response and isinstance(response["body"], dict):
            assert "success" in response["body"], "Response body missing success field"
            assert response["body"]["success"] is False, "Response indicates success when error expected"
    
    @staticmethod
    def assert_datetime_recent(dt: datetime, max_age_seconds: int = 60):
        """Assert that a datetime is recent (within max_age_seconds)."""
        now = datetime.now()
        age = (now - dt).total_seconds()
        assert age <= max_age_seconds, f"Datetime is {age} seconds old, expected <= {max_age_seconds}"
    
    @staticmethod
    def assert_list_not_empty(lst: List[Any], message: str = "List should not be empty"):
        """Assert that a list is not empty."""
        assert len(lst) > 0, message
    
    @staticmethod
    def assert_list_contains(lst: List[Any], item: Any, message: str = None):
        """Assert that a list contains a specific item."""
        if message is None:
            message = f"List should contain {item}"
        assert item in lst, message
    
    @staticmethod
    def assert_string_not_empty(s: str, message: str = "String should not be empty"):
        """Assert that a string is not empty."""
        assert s and len(s.strip()) > 0, message
    
    @staticmethod
    def assert_email_format(email: str, message: str = "Invalid email format"):
        """Assert that a string is a valid email format."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert re.match(email_pattern, email), message
    
    @staticmethod
    def assert_uuid_format(uuid_str: str, message: str = "Invalid UUID format"):
        """Assert that a string is a valid UUID format."""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, uuid_str, re.IGNORECASE), message


class TestContextManagers:
    """Context managers for common testing scenarios."""
    
    @staticmethod
    @contextmanager
    def temp_directory():
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @staticmethod
    @contextmanager
    def temp_file(content: str = "test content", suffix: str = ".txt"):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            temp_file_path = f.name
        
        try:
            yield temp_file_path
        finally:
            Path(temp_file_path).unlink(missing_ok=True)
    
    @staticmethod
    @contextmanager
    def mock_time(fixed_time: datetime = None):
        """Mock the current time for testing."""
        if fixed_time is None:
            fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        
        with patch('datetime.datetime') as mock_dt:
            mock_dt.now.return_value = fixed_time
            mock_dt.utcnow.return_value = fixed_time
            yield mock_dt
    
    @staticmethod
    @contextmanager
    def mock_uuid(fixed_uuid: str = "12345678-1234-1234-1234-123456789012"):
        """Mock UUID generation for testing."""
        with patch('uuid.uuid4') as mock_uuid_func:
            mock_uuid_func.return_value.hex = fixed_uuid.replace('-', '')
            yield mock_uuid_func
    
    @staticmethod
    @contextmanager
    def mock_random(fixed_value: int = 42):
        """Mock random number generation for testing."""
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = fixed_value
            yield mock_randint
    
    @staticmethod
    @asynccontextmanager
    async def async_timeout(timeout_seconds: float = 5.0):
        """Async context manager for timeout testing."""
        try:
            yield
        except asyncio.TimeoutError:
            pytest.fail(f"Operation timed out after {timeout_seconds} seconds")
    
    @staticmethod
    @contextmanager
    def capture_logs(logger_name: str = None):
        """Capture log messages for testing."""
        import logging
        from io import StringIO
        
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            yield log_capture
        finally:
            logger.removeHandler(handler)


class TestHelpers:
    """Helper functions for common testing operations."""
    
    @staticmethod
    def create_mock_user(**overrides) -> Mock:
        """Create a mock user object."""
        user = Mock()
        user.id = overrides.get('id', 1)
        user.email = overrides.get('email', 'test@example.com')
        user.username = overrides.get('username', 'testuser')
        user.first_name = overrides.get('first_name', 'Test')
        user.last_name = overrides.get('last_name', 'User')
        user.is_active = overrides.get('is_active', True)
        user.is_verified = overrides.get('is_verified', True)
        user.created_at = overrides.get('created_at', datetime.now())
        user.updated_at = overrides.get('updated_at', datetime.now())
        return user
    
    @staticmethod
    def create_mock_token(**overrides) -> Mock:
        """Create a mock authentication token."""
        token = Mock()
        token.access_token = overrides.get('access_token', 'test_access_token')
        token.refresh_token = overrides.get('refresh_token', 'test_refresh_token')
        token.token_type = overrides.get('token_type', 'Bearer')
        token.expires_in = overrides.get('expires_in', 3600)
        token.scope = overrides.get('scope', 'read write')
        token.user_id = overrides.get('user_id', 1)
        token.created_at = overrides.get('created_at', datetime.now())
        return token
    
    @staticmethod
    def create_mock_api_response(status_code: int = 200, **overrides) -> Dict[str, Any]:
        """Create a mock API response."""
        response = {
            "status_code": status_code,
            "headers": {
                "Content-Type": "application/json",
                "X-Request-ID": "test-request-id"
            },
            "body": {
                "success": status_code < 400,
                "message": "Test response",
                "data": {"test": "data"} if status_code < 400 else None,
                "error": "Test error" if status_code >= 400 else None
            },
            "response_time": 0.1
        }
        response.update(overrides)
        return response
    
    @staticmethod
    def create_mock_database_session():
        """Create a mock database session."""
        session = Mock()
        session.add = AsyncMock()
        session.add_all = AsyncMock()
        session.delete = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.merge = AsyncMock()
        session.execute = AsyncMock()
        session.scalar = AsyncMock()
        session.scalars = AsyncMock()
        session.query = Mock()
        session.get = Mock()
        session.begin = Mock()
        session.begin_nested = Mock()
        session.close = AsyncMock()
        return session
    
    @staticmethod
    def create_mock_http_client():
        """Create a mock HTTP client."""
        client = Mock()
        client.get = AsyncMock()
        client.post = AsyncMock()
        client.put = AsyncMock()
        client.delete = AsyncMock()
        client.patch = AsyncMock()
        client.close = AsyncMock()
        return client
    
    @staticmethod
    def create_mock_file_handler():
        """Create a mock file handler."""
        handler = Mock()
        handler.filename = "test_file.txt"
        handler.content_type = "text/plain"
        handler.size = 1024
        handler.read = AsyncMock(return_value=b"test file content")
        handler.save = AsyncMock()
        handler.delete = AsyncMock()
        return handler


class PerformanceTestHelpers:
    """Helpers for performance testing."""
    
    @staticmethod
    def measure_execution_time(func: Callable) -> Callable:
        """Decorator to measure function execution time."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            return result
        return wrapper
    
    @staticmethod
    async def measure_async_execution_time(func: Callable) -> Callable:
        """Decorator to measure async function execution time."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Async function {func.__name__} executed in {execution_time:.4f} seconds")
            return result
        return wrapper
    
    @staticmethod
    def assert_execution_time_under(func: Callable, max_seconds: float):
        """Assert that a function executes within a specified time limit."""
        start_time = time.time()
        result = func()
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time <= max_seconds, f"Function executed in {execution_time:.4f} seconds, expected <= {max_seconds}"
        return result
    
    @staticmethod
    async def assert_async_execution_time_under(func: Callable, max_seconds: float):
        """Assert that an async function executes within a specified time limit."""
        start_time = time.time()
        result = await func()
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time <= max_seconds, f"Async function executed in {execution_time:.4f} seconds, expected <= {max_seconds}"
        return result


class TestDataHelpers:
    """Helpers for test data management."""
    
    @staticmethod
    def generate_test_email() -> str:
        """Generate a test email address."""
        import random
        import string
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = random.choice(['example.com', 'test.com', 'demo.org'])
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_test_phone() -> str:
        """Generate a test phone number."""
        import random
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        return f"+1{area_code}{exchange}{number}"
    
    @staticmethod
    def generate_test_uuid() -> str:
        """Generate a test UUID."""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_test_password(length: int = 12) -> str:
        """Generate a test password."""
        import random
        import string
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(characters, k=length))
    
    @staticmethod
    def generate_test_json_data() -> Dict[str, Any]:
        """Generate test JSON data."""
        import random
        return {
            "id": random.randint(1, 1000),
            "name": f"Test Item {random.randint(1, 100)}",
            "description": "This is a test item",
            "active": random.choice([True, False]),
            "created_at": datetime.now().isoformat(),
            "tags": [f"tag{i}" for i in range(random.randint(1, 5))],
            "metadata": {
                "version": f"1.{random.randint(0, 9)}",
                "category": random.choice(["A", "B", "C"]),
                "priority": random.randint(1, 5)
            }
        }


class TestCleanupHelpers:
    """Helpers for test cleanup operations."""
    
    @staticmethod
    def cleanup_temp_files(temp_dir: str):
        """Clean up temporary files in a directory."""
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
    
    @staticmethod
    def cleanup_mock_objects(*mock_objects):
        """Clean up mock objects."""
        for mock_obj in mock_objects:
            if hasattr(mock_obj, 'reset_mock'):
                mock_obj.reset_mock()
            if hasattr(mock_obj, 'stop'):
                try:
                    mock_obj.stop()
                except Exception:
                    pass
    
    @staticmethod
    def cleanup_database_records(session, model_class, **filters):
        """Clean up database records created during testing."""
        try:
            records = session.query(model_class).filter_by(**filters).all()
            for record in records:
                session.delete(record)
            session.commit()
        except Exception:
            session.rollback()
    
    @staticmethod
    def cleanup_external_resources():
        """Clean up external resources used in testing."""
        # This would be implemented based on specific external services
        # For now, it's a placeholder
        pass


# Global instances for easy access
test_assertions = TestAssertions()
test_context_managers = TestContextManagers()
test_helpers = TestHelpers()
performance_helpers = PerformanceTestHelpers()
test_data_helpers = TestDataHelpers()
test_cleanup_helpers = TestCleanupHelpers()


def get_test_assertions() -> TestAssertions:
    """Get the test assertions instance."""
    return test_assertions


def get_test_context_managers() -> TestContextManagers:
    """Get the test context managers instance."""
    return test_context_managers


def get_test_helpers() -> TestHelpers:
    """Get the test helpers instance."""
    return test_helpers


def get_performance_helpers() -> PerformanceTestHelpers:
    """Get the performance helpers instance."""
    return performance_helpers


def get_test_data_helpers() -> TestDataHelpers:
    """Get the test data helpers instance."""
    return test_data_helpers


def get_test_cleanup_helpers() -> TestCleanupHelpers:
    """Get the test cleanup helpers instance."""
    return test_cleanup_helpers
