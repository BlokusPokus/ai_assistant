"""
Test Environment Setup

This module provides utilities for setting up and managing test environments
including database setup, configuration, and environment variables.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, patch
import pytest
from contextlib import contextmanager


class TestEnvironmentManager:
    """Manager for test environment setup and teardown."""
    
    def __init__(self):
        self._temp_directories = []
        self._environment_vars = {}
        self._original_env = {}
        self._patches = []
    
    def setup_temp_directory(self, prefix: str = "test_") -> str:
        """Set up a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        self._temp_directories.append(temp_dir)
        return temp_dir
    
    def setup_environment_variable(self, key: str, value: str):
        """Set up an environment variable for testing."""
        self._original_env[key] = os.environ.get(key)
        os.environ[key] = value
        self._environment_vars[key] = value
    
    def setup_test_config(self, config_overrides: Dict[str, Any] = None) -> Mock:
        """Set up test configuration."""
        config = Mock()
        config.database_url = "sqlite:///test.db"
        config.redis_url = "redis://localhost:6379"
        config.secret_key = "test_secret_key_12345"
        config.debug = True
        config.testing = True
        config.log_level = "DEBUG"
        config.port = 8000
        config.host = "localhost"
        config.cors_origins = ["http://localhost:3000"]
        config.rate_limit_enabled = True
        config.rate_limit_requests = 100
        config.rate_limit_window = 60
        
        if config_overrides:
            for key, value in config_overrides.items():
                setattr(config, key, value)
        
        return config
    
    def setup_database_config(self, database_url: str = None) -> Dict[str, Any]:
        """Set up database configuration for testing."""
        return {
            "url": database_url or "sqlite:///test.db",
            "echo": False,
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "pool_pre_ping": True,
            "connect_args": {
                "check_same_thread": False
            }
        }
    
    def setup_redis_config(self, redis_url: str = None) -> Dict[str, Any]:
        """Set up Redis configuration for testing."""
        return {
            "url": redis_url or "redis://localhost:6379",
            "db": 1,  # Use test database
            "decode_responses": True,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
    
    def setup_logging_config(self) -> Dict[str, Any]:
        """Set up logging configuration for testing."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "test": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "test",
                    "stream": "ext://sys.stdout"
                }
            },
            "loggers": {
                "": {
                    "level": "DEBUG",
                    "handlers": ["console"],
                    "propagate": False
                }
            }
        }
    
    def setup_mock_services(self) -> Dict[str, Mock]:
        """Set up mock services for testing."""
        services = {
            "database": Mock(),
            "redis": Mock(),
            "email": Mock(),
            "sms": Mock(),
            "storage": Mock(),
            "cache": Mock(),
            "metrics": Mock(),
            "logger": Mock()
        }
        
        # Configure mock database service
        services["database"].connect = Mock()
        services["database"].disconnect = Mock()
        services["database"].execute = Mock()
        services["database"].commit = Mock()
        services["database"].rollback = Mock()
        
        # Configure mock Redis service
        services["redis"].get = Mock()
        services["redis"].set = Mock()
        services["redis"].delete = Mock()
        services["redis"].exists = Mock()
        services["redis"].expire = Mock()
        
        # Configure mock email service
        services["email"].send = Mock()
        services["email"].send_template = Mock()
        services["email"].get_status = Mock()
        
        # Configure mock SMS service
        services["sms"].send = Mock()
        services["sms"].get_status = Mock()
        services["sms"].get_balance = Mock()
        
        # Configure mock storage service
        services["storage"].upload = Mock()
        services["storage"].download = Mock()
        services["storage"].delete = Mock()
        services["storage"].list = Mock()
        
        # Configure mock cache service
        services["cache"].get = Mock()
        services["cache"].set = Mock()
        services["cache"].delete = Mock()
        services["cache"].clear = Mock()
        
        # Configure mock metrics service
        services["metrics"].increment = Mock()
        services["metrics"].decrement = Mock()
        services["metrics"].gauge = Mock()
        services["metrics"].histogram = Mock()
        services["metrics"].timer = Mock()
        
        # Configure mock logger
        services["logger"].debug = Mock()
        services["logger"].info = Mock()
        services["logger"].warning = Mock()
        services["logger"].error = Mock()
        services["logger"].critical = Mock()
        
        return services
    
    def setup_test_data(self) -> Dict[str, Any]:
        """Set up test data for testing."""
        return {
            "users": [
                {
                    "id": 1,
                    "email": "test1@example.com",
                    "username": "testuser1",
                    "is_active": True,
                    "is_verified": True
                },
                {
                    "id": 2,
                    "email": "test2@example.com",
                    "username": "testuser2",
                    "is_active": True,
                    "is_verified": False
                }
            ],
            "tokens": [
                {
                    "access_token": "test_access_token_1",
                    "refresh_token": "test_refresh_token_1",
                    "user_id": 1,
                    "expires_at": "2024-12-31T23:59:59Z"
                }
            ],
            "configs": [
                {
                    "key": "test_config_1",
                    "value": "test_value_1",
                    "description": "Test configuration 1"
                }
            ]
        }
    
    def cleanup(self):
        """Clean up test environment."""
        # Clean up temporary directories
        for temp_dir in self._temp_directories:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
        
        # Restore original environment variables
        for key, original_value in self._original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value
        
        # Stop all patches
        for patch_obj in self._patches:
            try:
                patch_obj.stop()
            except Exception:
                pass
        
        # Clear internal state
        self._temp_directories.clear()
        self._environment_vars.clear()
        self._original_env.clear()
        self._patches.clear()


class TestDatabaseSetup:
    """Utilities for setting up test databases."""
    
    @staticmethod
    def create_test_database_url(temp_dir: str = None) -> str:
        """Create a test database URL."""
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()
        
        db_path = Path(temp_dir) / "test.db"
        return f"sqlite:///{db_path}"
    
    @staticmethod
    def setup_in_memory_database() -> str:
        """Set up an in-memory SQLite database for testing."""
        return "sqlite:///:memory:"
    
    @staticmethod
    def create_test_tables(session):
        """Create test tables in the database."""
        # This would be implemented based on your specific database models
        # For now, it's a placeholder
        pass
    
    @staticmethod
    def populate_test_data(session, test_data: Dict[str, Any]):
        """Populate the database with test data."""
        # This would be implemented based on your specific database models
        # For now, it's a placeholder
        pass
    
    @staticmethod
    def cleanup_test_data(session):
        """Clean up test data from the database."""
        # This would be implemented based on your specific database models
        # For now, it's a placeholder
        pass


class TestConfigurationSetup:
    """Utilities for setting up test configurations."""
    
    @staticmethod
    def create_test_config_file(temp_dir: str, config_data: Dict[str, Any]) -> str:
        """Create a test configuration file."""
        config_file = Path(temp_dir) / "test_config.json"
        
        import json
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return str(config_file)
    
    @staticmethod
    def create_test_env_file(temp_dir: str, env_data: Dict[str, str]) -> str:
        """Create a test environment file."""
        env_file = Path(temp_dir) / ".env.test"
        
        with open(env_file, 'w') as f:
            for key, value in env_data.items():
                f.write(f"{key}={value}\n")
        
        return str(env_file)
    
    @staticmethod
    def setup_test_settings(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """Set up test settings."""
        settings = {
            "DEBUG": True,
            "TESTING": True,
            "SECRET_KEY": "test_secret_key_12345",
            "DATABASE_URL": "sqlite:///test.db",
            "REDIS_URL": "redis://localhost:6379",
            "LOG_LEVEL": "DEBUG",
            "CORS_ORIGINS": ["http://localhost:3000"],
            "RATE_LIMIT_ENABLED": True,
            "RATE_LIMIT_REQUESTS": 100,
            "RATE_LIMIT_WINDOW": 60,
            "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
            "SMS_BACKEND": "test.backends.SMSBackend",
            "STORAGE_BACKEND": "test.backends.StorageBackend"
        }
        
        if overrides:
            settings.update(overrides)
        
        return settings


class TestServiceSetup:
    """Utilities for setting up test services."""
    
    @staticmethod
    def setup_mock_database_service():
        """Set up a mock database service."""
        service = Mock()
        service.connect = Mock()
        service.disconnect = Mock()
        service.execute = Mock()
        service.commit = Mock()
        service.rollback = Mock()
        service.query = Mock()
        service.get = Mock()
        service.create = Mock()
        service.update = Mock()
        service.delete = Mock()
        return service
    
    @staticmethod
    def setup_mock_cache_service():
        """Set up a mock cache service."""
        service = Mock()
        service.get = Mock()
        service.set = Mock()
        service.delete = Mock()
        service.exists = Mock()
        service.clear = Mock()
        service.get_ttl = Mock()
        service.set_ttl = Mock()
        return service
    
    @staticmethod
    def setup_mock_external_services():
        """Set up mock external services."""
        services = {
            "email": Mock(),
            "sms": Mock(),
            "storage": Mock(),
            "payment": Mock(),
            "analytics": Mock()
        }
        
        # Configure email service
        services["email"].send = Mock()
        services["email"].send_template = Mock()
        services["email"].get_status = Mock()
        
        # Configure SMS service
        services["sms"].send = Mock()
        services["sms"].get_status = Mock()
        services["sms"].get_balance = Mock()
        
        # Configure storage service
        services["storage"].upload = Mock()
        services["storage"].download = Mock()
        services["storage"].delete = Mock()
        services["storage"].list = Mock()
        
        # Configure payment service
        services["payment"].create_payment = Mock()
        services["payment"].process_payment = Mock()
        services["payment"].refund_payment = Mock()
        services["payment"].get_payment_status = Mock()
        
        # Configure analytics service
        services["analytics"].track_event = Mock()
        services["analytics"].track_page_view = Mock()
        services["analytics"].get_metrics = Mock()
        
        return services


# Global test environment manager
test_env_manager = TestEnvironmentManager()


@contextmanager
def test_environment(env_vars: Dict[str, str] = None, temp_dir: str = None):
    """Context manager for test environment setup."""
    manager = TestEnvironmentManager()
    
    try:
        # Set up temporary directory
        if temp_dir:
            manager.setup_temp_directory()
        
        # Set up environment variables
        if env_vars:
            for key, value in env_vars.items():
                manager.setup_environment_variable(key, value)
        
        yield manager
    finally:
        manager.cleanup()


@pytest.fixture
def test_env():
    """Pytest fixture for test environment."""
    manager = TestEnvironmentManager()
    yield manager
    manager.cleanup()


@pytest.fixture
def test_config():
    """Pytest fixture for test configuration."""
    return TestConfigurationSetup.setup_test_settings()


@pytest.fixture
def test_database_url():
    """Pytest fixture for test database URL."""
    return TestDatabaseSetup.setup_in_memory_database()


@pytest.fixture
def test_services():
    """Pytest fixture for test services."""
    return TestServiceSetup.setup_mock_external_services()


def get_test_environment_manager() -> TestEnvironmentManager:
    """Get the global test environment manager."""
    return test_env_manager


def setup_test_environment(env_vars: Dict[str, str] = None, temp_dir: str = None) -> TestEnvironmentManager:
    """Set up a test environment."""
    manager = TestEnvironmentManager()
    
    if temp_dir:
        manager.setup_temp_directory()
    
    if env_vars:
        for key, value in env_vars.items():
            manager.setup_environment_variable(key, value)
    
    return manager


def cleanup_test_environment(manager: TestEnvironmentManager):
    """Clean up a test environment."""
    manager.cleanup()

