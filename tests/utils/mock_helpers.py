"""
Mock helpers for the Personal Assistant test suite.

This module provides utilities for creating and managing mocks
across different test scenarios.
"""

import json
from typing import Dict, Any, List, Optional, Callable, Union
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from contextlib import contextmanager


class MockHelper:
    """Utility class for creating and managing mocks."""
    
    @staticmethod
    def create_mock_database():
        """Create a comprehensive mock database."""
        mock_db = Mock()
        mock_db.session = Mock()
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()
        mock_db.session.rollback = Mock()
        mock_db.session.close = Mock()
        mock_db.session.query = Mock()
        mock_db.session.execute = Mock()
        mock_db.session.get = Mock()
        mock_db.session.merge = Mock()
        mock_db.session.delete = Mock()
        mock_db.session.flush = Mock()
        return mock_db
    
    @staticmethod
    def create_mock_redis():
        """Create a comprehensive mock Redis client."""
        mock_redis = Mock()
        mock_redis.get = Mock(return_value=None)
        mock_redis.set = Mock(return_value=True)
        mock_redis.delete = Mock(return_value=True)
        mock_redis.exists = Mock(return_value=False)
        mock_redis.expire = Mock(return_value=True)
        mock_redis.hget = Mock(return_value=None)
        mock_redis.hset = Mock(return_value=True)
        mock_redis.hdel = Mock(return_value=True)
        mock_redis.hgetall = Mock(return_value={})
        mock_redis.lpush = Mock(return_value=True)
        mock_redis.rpop = Mock(return_value=None)
        mock_redis.llen = Mock(return_value=0)
        mock_redis.sadd = Mock(return_value=True)
        mock_redis.srem = Mock(return_value=True)
        mock_redis.smembers = Mock(return_value=set())
        mock_redis.ping = Mock(return_value=True)
        return mock_redis
    
    @staticmethod
    def create_mock_http_response(
        status_code: int = 200,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        text: Optional[str] = None
    ) -> Mock:
        """Create a mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.headers = headers or {}
        mock_response.text = text or json.dumps(data or {})
        mock_response.json.return_value = data or {}
        mock_response.raise_for_status = Mock()
        return mock_response
    
    @staticmethod
    def create_mock_file():
        """Create a mock file object."""
        mock_file = Mock()
        mock_file.read = Mock(return_value="")
        mock_file.write = Mock()
        mock_file.close = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        return mock_file
    
    @staticmethod
    def create_mock_logger():
        """Create a mock logger."""
        mock_logger = Mock()
        mock_logger.debug = Mock()
        mock_logger.info = Mock()
        mock_logger.warning = Mock()
        mock_logger.error = Mock()
        mock_logger.critical = Mock()
        mock_logger.exception = Mock()
        return mock_logger
    
    @staticmethod
    def create_mock_async_function(return_value: Any = None, side_effect: Any = None):
        """Create a mock async function."""
        async def mock_async(*args, **kwargs):
            if side_effect:
                if isinstance(side_effect, Exception):
                    raise side_effect
                return side_effect
            return return_value
        return mock_async


class DatabaseMockHelper:
    """Helper for database-related mocks."""
    
    @staticmethod
    @contextmanager
    def mock_database_session():
        """Context manager for mocking database session."""
        with patch('sqlalchemy.orm.Session') as mock_session:
            mock_session.return_value = MockHelper.create_mock_database().session
            yield mock_session
    
    @staticmethod
    @contextmanager
    def mock_database_query(model_class, return_value: Any = None):
        """Context manager for mocking database queries."""
        with patch(f'{model_class.__module__}.{model_class.__name__}.query') as mock_query:
            mock_query.return_value = return_value or Mock()
            yield mock_query
    
    @staticmethod
    @contextmanager
    def mock_database_commit():
        """Context manager for mocking database commit."""
        with patch('sqlalchemy.orm.Session.commit') as mock_commit:
            mock_commit.return_value = None
            yield mock_commit
    
    @staticmethod
    @contextmanager
    def mock_database_rollback():
        """Context manager for mocking database rollback."""
        with patch('sqlalchemy.orm.Session.rollback') as mock_rollback:
            mock_rollback.return_value = None
            yield mock_rollback


class APIMockHelper:
    """Helper for API-related mocks."""
    
    @staticmethod
    @contextmanager
    def mock_requests_get(url: str, response_data: Dict[str, Any] = None, status_code: int = 200):
        """Context manager for mocking GET requests."""
        with patch('requests.get') as mock_get:
            mock_response = MockHelper.create_mock_http_response(status_code, response_data)
            mock_get.return_value = mock_response
            yield mock_get
    
    @staticmethod
    @contextmanager
    def mock_requests_post(url: str, response_data: Dict[str, Any] = None, status_code: int = 201):
        """Context manager for mocking POST requests."""
        with patch('requests.post') as mock_post:
            mock_response = MockHelper.create_mock_http_response(status_code, response_data)
            mock_post.return_value = mock_response
            yield mock_post
    
    @staticmethod
    @contextmanager
    def mock_requests_put(url: str, response_data: Dict[str, Any] = None, status_code: int = 200):
        """Context manager for mocking PUT requests."""
        with patch('requests.put') as mock_put:
            mock_response = MockHelper.create_mock_http_response(status_code, response_data)
            mock_put.return_value = mock_response
            yield mock_put
    
    @staticmethod
    @contextmanager
    def mock_requests_delete(url: str, status_code: int = 204):
        """Context manager for mocking DELETE requests."""
        with patch('requests.delete') as mock_delete:
            mock_response = MockHelper.create_mock_http_response(status_code)
            mock_delete.return_value = mock_response
            yield mock_delete
    
    @staticmethod
    @contextmanager
    def mock_httpx_client():
        """Context manager for mocking httpx client."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.get = AsyncMock()
            mock_client_instance.post = AsyncMock()
            mock_client_instance.put = AsyncMock()
            mock_client_instance.delete = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            yield mock_client_instance


class FileSystemMockHelper:
    """Helper for file system-related mocks."""
    
    @staticmethod
    @contextmanager
    def mock_file_open(file_path: str, content: str = ""):
        """Context manager for mocking file open."""
        with patch('builtins.open') as mock_open:
            mock_file = MockHelper.create_mock_file()
            mock_file.read.return_value = content
            mock_open.return_value = mock_file
            yield mock_open
    
    @staticmethod
    @contextmanager
    def mock_file_exists(file_path: str, exists: bool = True):
        """Context manager for mocking file existence."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = exists
            yield mock_exists
    
    @staticmethod
    @contextmanager
    def mock_file_makedirs():
        """Context manager for mocking directory creation."""
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.return_value = None
            yield mock_makedirs
    
    @staticmethod
    @contextmanager
    def mock_file_remove():
        """Context manager for mocking file removal."""
        with patch('os.remove') as mock_remove:
            mock_remove.return_value = None
            yield mock_remove


class LoggingMockHelper:
    """Helper for logging-related mocks."""
    
    @staticmethod
    @contextmanager
    def mock_logging_get_logger(logger_name: str = None):
        """Context manager for mocking logger creation."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MockHelper.create_mock_logger()
            mock_get_logger.return_value = mock_logger
            yield mock_logger
    
    @staticmethod
    @contextmanager
    def mock_logging_config():
        """Context manager for mocking logging configuration."""
        with patch('logging.basicConfig') as mock_config:
            mock_config.return_value = None
            yield mock_config


class ExternalServiceMockHelper:
    """Helper for external service mocks."""
    
    @staticmethod
    @contextmanager
    def mock_twilio_client():
        """Context manager for mocking Twilio client."""
        with patch('twilio.rest.Client') as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.messages.create = Mock()
            mock_client.return_value = mock_client_instance
            yield mock_client_instance
    
    @staticmethod
    @contextmanager
    def mock_openai_client():
        """Context manager for mocking OpenAI client."""
        with patch('openai.OpenAI') as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.chat.completions.create = Mock()
            mock_client.return_value = mock_client_instance
            yield mock_client_instance
    
    @staticmethod
    @contextmanager
    def mock_google_client():
        """Context manager for mocking Google API client."""
        with patch('google.oauth2.credentials.Credentials') as mock_credentials:
            mock_credentials.return_value = Mock()
            yield mock_credentials
    
    @staticmethod
    @contextmanager
    def mock_notion_client():
        """Context manager for mocking Notion client."""
        with patch('notion_client.Client') as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.pages.create = Mock()
            mock_client_instance.pages.retrieve = Mock()
            mock_client_instance.pages.update = Mock()
            mock_client_instance.pages.archive = Mock()
            mock_client.return_value = mock_client_instance
            yield mock_client_instance


class TimeMockHelper:
    """Helper for time-related mocks."""
    
    @staticmethod
    @contextmanager
    def mock_time(timestamp: float = 1640995200.0):
        """Context manager for mocking time.time()."""
        with patch('time.time') as mock_time:
            mock_time.return_value = timestamp
            yield mock_time
    
    @staticmethod
    @contextmanager
    def mock_datetime(fixed_datetime=None):
        """Context manager for mocking datetime."""
        if fixed_datetime is None:
            from datetime import datetime
            fixed_datetime = datetime(2022, 1, 1, 0, 0, 0)
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime
            mock_datetime.utcnow.return_value = fixed_datetime
            yield mock_datetime
    
    @staticmethod
    @contextmanager
    def mock_sleep():
        """Context manager for mocking time.sleep."""
        with patch('time.sleep') as mock_sleep:
            mock_sleep.return_value = None
            yield mock_sleep


class AsyncMockHelper:
    """Helper for async-related mocks."""
    
    @staticmethod
    def mock_async_function(return_value: Any = None, side_effect: Any = None):
        """Create a mock async function."""
        async def mock_async(*args, **kwargs):
            if side_effect:
                if isinstance(side_effect, Exception):
                    raise side_effect
                return side_effect
            return return_value
        return mock_async
    
    @staticmethod
    def mock_async_context_manager(return_value: Any = None):
        """Create a mock async context manager."""
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=return_value)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        return mock_context
    
    @staticmethod
    def mock_async_generator(values: List[Any]):
        """Create a mock async generator."""
        async def mock_async_gen():
            for value in values:
                yield value
        return mock_async_gen()


class CompositeMockHelper:
    """Helper for creating composite mocks."""
    
    @staticmethod
    def mock_database_and_redis():
        """Create mocks for both database and Redis."""
        return {
            'database': MockHelper.create_mock_database(),
            'redis': MockHelper.create_mock_redis(),
        }
    
    @staticmethod
    def mock_external_apis():
        """Create mocks for all external APIs."""
        return {
            'twilio': ExternalServiceMockHelper.mock_twilio_client(),
            'openai': ExternalServiceMockHelper.mock_openai_client(),
            'google': ExternalServiceMockHelper.mock_google_client(),
            'notion': ExternalServiceMockHelper.mock_notion_client(),
        }
    
    @staticmethod
    def mock_file_system():
        """Create mocks for file system operations."""
        return {
            'open': FileSystemMockHelper.mock_file_open,
            'exists': FileSystemMockHelper.mock_file_exists,
            'makedirs': FileSystemMockHelper.mock_file_makedirs,
            'remove': FileSystemMockHelper.mock_file_remove,
        }


# Export all helpers
__all__ = [
    'MockHelper',
    'DatabaseMockHelper',
    'APIMockHelper',
    'FileSystemMockHelper',
    'LoggingMockHelper',
    'ExternalServiceMockHelper',
    'TimeMockHelper',
    'AsyncMockHelper',
    'CompositeMockHelper',
]
