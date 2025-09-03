"""
Global pytest configuration and fixtures for the Personal Assistant test suite.

This module provides shared fixtures, configuration, and utilities used across
all test modules in the project.
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, Generator

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test configuration
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        "TEST_MODE": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/15",  # Use test database
        "SECRET_KEY": "test-secret-key",
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
    }


@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_database():
    """Mock database connection for testing."""
    mock_db = Mock()
    mock_db.session = Mock()
    mock_db.commit = Mock()
    mock_db.rollback = Mock()
    return mock_db


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    mock_redis = Mock()
    mock_redis.get = Mock(return_value=None)
    mock_redis.set = Mock(return_value=True)
    mock_redis.delete = Mock(return_value=True)
    mock_redis.exists = Mock(return_value=False)
    return mock_redis


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "phone_number": "+1234567890",
        "is_active": True,
        "is_verified": True,
    }


@pytest.fixture
def sample_auth_data():
    """Sample authentication data for testing."""
    return {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "token_type": "bearer",
        "expires_in": 3600,
    }


@pytest.fixture
def mock_external_apis():
    """Mock external API calls."""
    with patch("requests.get") as mock_get, \
         patch("requests.post") as mock_post, \
         patch("requests.put") as mock_put, \
         patch("requests.delete") as mock_delete:
        
        # Configure default responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "success"}
        
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": 1, "status": "created"}
        
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {"status": "updated"}
        
        mock_delete.return_value.status_code = 204
        
        yield {
            "get": mock_get,
            "post": mock_post,
            "put": mock_put,
            "delete": mock_delete,
        }


@pytest.fixture
def mock_file_system():
    """Mock file system operations."""
    with patch("builtins.open", create=True) as mock_open, \
         patch("os.path.exists") as mock_exists, \
         patch("os.makedirs") as mock_makedirs:
        
        mock_exists.return_value = True
        mock_makedirs.return_value = None
        
        yield {
            "open": mock_open,
            "exists": mock_exists,
            "makedirs": mock_makedirs,
        }


@pytest.fixture
def mock_logging():
    """Mock logging operations."""
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        yield mock_logger


@pytest.fixture(autouse=True)
def setup_test_environment(test_config):
    """Set up test environment variables."""
    for key, value in test_config.items():
        os.environ[key] = str(value)
    
    yield
    
    # Clean up environment variables
    for key in test_config.keys():
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_time():
    """Mock time operations for consistent testing."""
    with patch("time.time") as mock_time_func, \
         patch("datetime.datetime") as mock_datetime:
        
        mock_time_func.return_value = 1640995200.0  # 2022-01-01 00:00:00 UTC
        
        mock_now = Mock()
        mock_now.timestamp.return_value = 1640995200.0
        mock_now.isoformat.return_value = "2022-01-01T00:00:00"
        mock_datetime.now.return_value = mock_now
        mock_datetime.utcnow.return_value = mock_now
        
        yield {
            "time": mock_time_func,
            "datetime": mock_datetime,
        }


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.performance = pytest.mark.performance
pytest.mark.slow = pytest.mark.slow


# Test data generators
class TestDataGenerator:
    """Utility class for generating test data."""
    
    @staticmethod
    def generate_user_data(**kwargs) -> Dict[str, Any]:
        """Generate user data for testing."""
        default_data = {
            "id": 1,
            "email": "test@example.com",
            "full_name": "Test User",
            "phone_number": "+1234567890",
            "is_active": True,
            "is_verified": True,
            "created_at": "2022-01-01T00:00:00",
            "updated_at": "2022-01-01T00:00:00",
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def generate_auth_data(**kwargs) -> Dict[str, Any]:
        """Generate authentication data for testing."""
        default_data = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "scope": "read write",
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def generate_api_response(**kwargs) -> Dict[str, Any]:
        """Generate API response data for testing."""
        default_data = {
            "status": "success",
            "data": {},
            "message": "Operation completed successfully",
            "timestamp": "2022-01-01T00:00:00",
        }
        default_data.update(kwargs)
        return default_data


@pytest.fixture
def test_data_generator():
    """Test data generator fixture."""
    return TestDataGenerator()


# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Cleanup utilities
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Add cleanup logic here if needed
    pass