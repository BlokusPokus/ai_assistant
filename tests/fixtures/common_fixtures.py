"""
Common Test Fixtures

This module provides reusable pytest fixtures for common testing scenarios
including database sessions, mock services, test data, and environment setup.
"""

import asyncio
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from tests.mocks.database_mocks import get_async_session_mock, get_engine_mock, reset_all_database_mocks
from tests.mocks.external_api_mocks import (
    get_twilio_sms_mock, get_oauth_provider_mock, get_email_service_mock,
    get_file_storage_mock, reset_all_external_mocks
)
from tests.mocks.filesystem_mocks import get_filesystem_mock, reset_filesystem_mock
from tests.mocks.network_mocks import (
    get_aiohttp_session_mock, get_httpx_client_mock, get_websocket_server_mock,
    reset_network_mocks
)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_file(temp_directory):
    """Create a temporary file for testing."""
    temp_file_path = Path(temp_directory) / "test_file.txt"
    temp_file_path.write_text("test content")
    yield str(temp_file_path)
    temp_file_path.unlink(missing_ok=True)


@pytest.fixture
def mock_database_session():
    """Provide a mock database session."""
    session = get_async_session_mock()
    yield session
    reset_all_database_mocks()


@pytest.fixture
def mock_database_engine():
    """Provide a mock database engine."""
    engine = get_engine_mock()
    yield engine
    reset_all_database_mocks()


@pytest.fixture
def mock_twilio_sms():
    """Provide a mock Twilio SMS service."""
    twilio_mock = get_twilio_sms_mock()
    yield twilio_mock
    reset_all_external_mocks()


@pytest.fixture
def mock_oauth_provider():
    """Provide a mock OAuth provider."""
    oauth_mock = get_oauth_provider_mock("google")
    yield oauth_mock
    reset_all_external_mocks()


@pytest.fixture
def mock_email_service():
    """Provide a mock email service."""
    email_mock = get_email_service_mock()
    yield email_mock
    reset_all_external_mocks()


@pytest.fixture
def mock_file_storage():
    """Provide a mock file storage service."""
    storage_mock = get_file_storage_mock()
    yield storage_mock
    reset_all_external_mocks()


@pytest.fixture
def mock_filesystem():
    """Provide a mock file system."""
    fs_mock = get_filesystem_mock()
    yield fs_mock
    reset_filesystem_mock()


@pytest.fixture
def mock_aiohttp_session():
    """Provide a mock aiohttp session."""
    session_mock = get_aiohttp_session_mock()
    yield session_mock
    reset_network_mocks()


@pytest.fixture
def mock_httpx_client():
    """Provide a mock httpx client."""
    client_mock = get_httpx_client_mock()
    yield client_mock
    reset_network_mocks()


@pytest.fixture
def mock_websocket_server():
    """Provide a mock WebSocket server."""
    server_mock = get_websocket_server_mock()
    yield server_mock
    reset_network_mocks()


@pytest.fixture
def sample_user_data():
    """Provide sample user data for testing."""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_auth_data():
    """Provide sample authentication data for testing."""
    return {
        "access_token": "test_access_token_123",
        "refresh_token": "test_refresh_token_456",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "read write",
        "user_id": 1,
        "created_at": datetime.now()
    }


@pytest.fixture
def sample_api_request_data():
    """Provide sample API request data for testing."""
    return {
        "method": "POST",
        "url": "/api/v1/users",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token"
        },
        "body": {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepassword123"
        }
    }


@pytest.fixture
def sample_api_response_data():
    """Provide sample API response data for testing."""
    return {
        "status_code": 201,
        "headers": {
            "Content-Type": "application/json",
            "Location": "/api/v1/users/123"
        },
        "body": {
            "id": 123,
            "email": "newuser@example.com",
            "username": "newuser",
            "created_at": datetime.now().isoformat(),
            "message": "User created successfully"
        }
    }


@pytest.fixture
def sample_file_data():
    """Provide sample file data for testing."""
    return {
        "filename": "test_document.pdf",
        "content_type": "application/pdf",
        "size_bytes": 1024,
        "content": b"PDF file content here",
        "metadata": {
            "author": "Test Author",
            "title": "Test Document",
            "created_at": datetime.now().isoformat()
        }
    }


@pytest.fixture
def sample_sms_data():
    """Provide sample SMS data for testing."""
    return {
        "to": "+1234567890",
        "from_": "+0987654321",
        "body": "Test SMS message",
        "status": "queued",
        "sid": "SM1234567890abcdef",
        "created_at": datetime.now()
    }


@pytest.fixture
def sample_email_data():
    """Provide sample email data for testing."""
    return {
        "to": "recipient@example.com",
        "from_": "sender@example.com",
        "subject": "Test Email Subject",
        "html": "<h1>Test Email</h1><p>This is a test email.</p>",
        "text": "Test Email\n\nThis is a test email.",
        "status": "sent",
        "sent_at": datetime.now()
    }


@pytest.fixture
def sample_oauth_data():
    """Provide sample OAuth data for testing."""
    return {
        "provider": "google",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "redirect_uri": "http://localhost:8000/callback",
        "scopes": ["read", "write"],
        "state": "test_state_123",
        "code": "test_auth_code_456",
        "access_token": "test_access_token_789",
        "refresh_token": "test_refresh_token_012"
    }


@pytest.fixture
def sample_websocket_data():
    """Provide sample WebSocket data for testing."""
    return {
        "url": "ws://localhost:8765/ws",
        "message": "Hello, WebSocket!",
        "connection_id": "conn_123456",
        "user_id": 1,
        "room": "test_room",
        "timestamp": datetime.now()
    }


@pytest.fixture
def mock_user():
    """Provide a mock user object."""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    user.username = "testuser"
    user.first_name = "Test"
    user.last_name = "User"
    user.is_active = True
    user.is_verified = True
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    return user


@pytest.fixture
def mock_auth_token():
    """Provide a mock authentication token."""
    token = Mock()
    token.access_token = "test_access_token_123"
    token.refresh_token = "test_refresh_token_456"
    token.token_type = "Bearer"
    token.expires_in = 3600
    token.scope = "read write"
    token.user_id = 1
    token.created_at = datetime.now()
    return token


@pytest.fixture
def mock_api_client():
    """Provide a mock API client."""
    client = Mock()
    client.base_url = "http://localhost:8000"
    client.headers = {"Content-Type": "application/json"}
    client.timeout = 30
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    client.patch = AsyncMock()
    return client


@pytest.fixture
def mock_database_connection():
    """Provide a mock database connection."""
    connection = Mock()
    connection.is_connected = True
    connection.execute = AsyncMock()
    connection.commit = AsyncMock()
    connection.rollback = AsyncMock()
    connection.close = AsyncMock()
    return connection


@pytest.fixture
def mock_file_handler():
    """Provide a mock file handler."""
    handler = Mock()
    handler.filename = "test_file.txt"
    handler.content_type = "text/plain"
    handler.size = 1024
    handler.read = AsyncMock(return_value=b"test file content")
    handler.save = AsyncMock()
    handler.delete = AsyncMock()
    return handler


@pytest.fixture
def mock_sms_service():
    """Provide a mock SMS service."""
    service = Mock()
    service.send_sms = AsyncMock()
    service.get_message_status = AsyncMock()
    service.list_messages = AsyncMock()
    service.get_account_info = AsyncMock()
    return service


@pytest.fixture
def mock_email_service_provider():
    """Provide a mock email service provider."""
    provider = Mock()
    provider.send_email = AsyncMock()
    provider.send_template_email = AsyncMock()
    provider.get_sent_emails = AsyncMock()
    provider.get_email_status = AsyncMock()
    return provider


@pytest.fixture
def mock_oauth_service():
    """Provide a mock OAuth service."""
    service = Mock()
    service.get_authorization_url = AsyncMock()
    service.exchange_code_for_token = AsyncMock()
    service.refresh_token = AsyncMock()
    service.get_user_info = AsyncMock()
    service.revoke_token = AsyncMock()
    return service


@pytest.fixture
def mock_websocket_connection():
    """Provide a mock WebSocket connection."""
    connection = Mock()
    connection.url = "ws://localhost:8765/ws"
    connection.is_connected = True
    connection.send = AsyncMock()
    connection.recv = AsyncMock()
    connection.close = AsyncMock()
    connection.ping = AsyncMock()
    connection.pong = AsyncMock()
    return connection


@pytest.fixture
def mock_cache_service():
    """Provide a mock cache service."""
    cache = Mock()
    cache.get = AsyncMock()
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.exists = AsyncMock()
    cache.clear = AsyncMock()
    cache.get_ttl = AsyncMock()
    cache.set_ttl = AsyncMock()
    return cache


@pytest.fixture
def mock_logger():
    """Provide a mock logger."""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    logger.exception = Mock()
    return logger


@pytest.fixture
def mock_metrics_service():
    """Provide a mock metrics service."""
    metrics = Mock()
    metrics.increment = Mock()
    metrics.decrement = Mock()
    metrics.gauge = Mock()
    metrics.histogram = Mock()
    metrics.timer = Mock()
    metrics.counter = Mock()
    return metrics


@pytest.fixture
def mock_config():
    """Provide a mock configuration object."""
    config = Mock()
    config.database_url = "sqlite:///test.db"
    config.redis_url = "redis://localhost:6379"
    config.secret_key = "test_secret_key"
    config.debug = True
    config.testing = True
    config.log_level = "DEBUG"
    return config


@pytest.fixture
def mock_environment():
    """Provide a mock environment setup."""
    env = Mock()
    env.database_url = "sqlite:///test.db"
    env.redis_url = "redis://localhost:6379"
    env.secret_key = "test_secret_key"
    env.debug = True
    env.testing = True
    env.log_level = "DEBUG"
    env.port = 8000
    env.host = "localhost"
    return env


@pytest.fixture
def async_test_runner():
    """Provide an async test runner for testing async functions."""
    def run_async_test(coro):
        """Run an async test function."""
        return asyncio.run(coro)
    return run_async_test


@pytest.fixture
def mock_time():
    """Provide a mock time for testing time-dependent functionality."""
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
        mock_dt.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
        yield mock_dt


@pytest.fixture
def mock_uuid():
    """Provide a mock UUID for testing."""
    with patch('uuid.uuid4') as mock_uuid:
        mock_uuid.return_value.hex = "1234567890abcdef1234567890abcdef"
        yield mock_uuid


@pytest.fixture
def mock_random():
    """Provide a mock random number generator for testing."""
    with patch('random.randint') as mock_randint:
        mock_randint.return_value = 42
        yield mock_randint


@pytest.fixture
def test_data_cleanup():
    """Provide test data cleanup functionality."""
    cleanup_items = []
    
    def add_cleanup(item):
        cleanup_items.append(item)
    
    def cleanup():
        for item in cleanup_items:
            if hasattr(item, 'delete'):
                try:
                    item.delete()
                except Exception:
                    pass
            elif hasattr(item, 'remove'):
                try:
                    item.remove()
                except Exception:
                    pass
            elif hasattr(item, 'unlink'):
                try:
                    item.unlink()
                except Exception:
                    pass
    
    yield add_cleanup
    cleanup()


@pytest.fixture
def mock_external_services():
    """Provide all external service mocks in one fixture."""
    services = {
        'twilio': get_twilio_sms_mock(),
        'oauth': get_oauth_provider_mock("google"),
        'email': get_email_service_mock(),
        'storage': get_file_storage_mock(),
        'aiohttp': get_aiohttp_session_mock(),
        'httpx': get_httpx_client_mock(),
        'websocket': get_websocket_server_mock()
    }
    
    yield services
    
    # Cleanup
    reset_all_external_mocks()
    reset_network_mocks()


@pytest.fixture
def mock_database_services():
    """Provide all database service mocks in one fixture."""
    services = {
        'session': get_async_session_mock(),
        'engine': get_engine_mock(),
        'connection': Mock()
    }
    
    yield services
    
    # Cleanup
    reset_all_database_mocks()


@pytest.fixture
def comprehensive_test_environment():
    """Provide a comprehensive test environment with all mocks and utilities."""
    env = {
        'temp_dir': tempfile.mkdtemp(),
        'database': {
            'session': get_async_session_mock(),
            'engine': get_engine_mock()
        },
        'external_apis': {
            'twilio': get_twilio_sms_mock(),
            'oauth': get_oauth_provider_mock("google"),
            'email': get_email_service_mock(),
            'storage': get_file_storage_mock()
        },
        'network': {
            'aiohttp': get_aiohttp_session_mock(),
            'httpx': get_httpx_client_mock(),
            'websocket': get_websocket_server_mock()
        },
        'filesystem': get_filesystem_mock(),
        'config': Mock(),
        'logger': Mock(),
        'metrics': Mock()
    }
    
    yield env
    
    # Cleanup
    shutil.rmtree(env['temp_dir'], ignore_errors=True)
    reset_all_database_mocks()
    reset_all_external_mocks()
    reset_network_mocks()
    reset_filesystem_mock()

