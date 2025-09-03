"""
Test helper utilities for the Personal Assistant test suite.

This module provides common utilities and helper functions used across
multiple test modules.
"""

import json
import hashlib
import random
import string
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


class TestHelper:
    """Utility class for common test operations."""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """Generate a random string of specified length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_email() -> str:
        """Generate a random email address."""
        username = TestHelper.generate_random_string(8)
        domain = random.choice(['example.com', 'test.com', 'demo.org'])
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_random_phone() -> str:
        """Generate a random phone number."""
        return f"+1{random.randint(1000000000, 9999999999)}"
    
    @staticmethod
    def generate_random_id() -> int:
        """Generate a random ID."""
        return random.randint(1, 10000)
    
    @staticmethod
    def generate_timestamp(days_offset: int = 0) -> str:
        """Generate a timestamp with optional offset."""
        base_time = datetime.now()
        if days_offset != 0:
            base_time += timedelta(days=days_offset)
        return base_time.isoformat()
    
    @staticmethod
    def create_mock_response(
        status_code: int = 200,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Mock:
        """Create a mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = data or {}
        mock_response.headers = headers or {}
        mock_response.text = json.dumps(data or {})
        return mock_response
    
    @staticmethod
    def create_mock_database_session():
        """Create a mock database session."""
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        mock_session.query = Mock()
        mock_session.execute = Mock()
        mock_session.close = Mock()
        return mock_session
    
    @staticmethod
    def create_mock_redis_client():
        """Create a mock Redis client."""
        mock_redis = Mock()
        mock_redis.get = Mock(return_value=None)
        mock_redis.set = Mock(return_value=True)
        mock_redis.delete = Mock(return_value=True)
        mock_redis.exists = Mock(return_value=False)
        mock_redis.expire = Mock(return_value=True)
        mock_redis.hget = Mock(return_value=None)
        mock_redis.hset = Mock(return_value=True)
        mock_redis.hdel = Mock(return_value=True)
        return mock_redis
    
    @staticmethod
    def assert_dict_contains(expected: Dict[str, Any], actual: Dict[str, Any]) -> None:
        """Assert that actual dict contains all keys from expected dict."""
        for key, expected_value in expected.items():
            assert key in actual, f"Key '{key}' not found in actual dict"
            assert actual[key] == expected_value, f"Value for key '{key}' mismatch"
    
    @staticmethod
    def assert_list_contains(expected_items: List[Any], actual_list: List[Any]) -> None:
        """Assert that actual list contains all expected items."""
        for expected_item in expected_items:
            assert expected_item in actual_list, f"Item {expected_item} not found in actual list"
    
    @staticmethod
    def mock_external_api_call(
        url: str,
        method: str = "GET",
        response_data: Optional[Dict[str, Any]] = None,
        status_code: int = 200
    ):
        """Context manager for mocking external API calls."""
        from contextlib import contextmanager
        
        @contextmanager
        def _mock_api():
            with patch('requests.request') as mock_request:
                mock_response = TestHelper.create_mock_response(status_code, response_data)
                mock_request.return_value = mock_response
                yield mock_request
        
        return _mock_api()
    
    @staticmethod
    def mock_database_operation(operation: str, return_value: Any = None):
        """Context manager for mocking database operations."""
        from contextlib import contextmanager
        
        @contextmanager
        def _mock_db():
            if operation == "query":
                with patch('sqlalchemy.orm.Session.query') as mock_query:
                    mock_query.return_value = return_value or Mock()
                    yield mock_query
            elif operation == "commit":
                with patch('sqlalchemy.orm.Session.commit') as mock_commit:
                    mock_commit.return_value = return_value
                    yield mock_commit
            elif operation == "rollback":
                with patch('sqlalchemy.orm.Session.rollback') as mock_rollback:
                    mock_rollback.return_value = return_value
                    yield mock_rollback
        
        return _mock_db()
    
    @staticmethod
    def mock_file_operation(operation: str, return_value: Any = None):
        """Context manager for mocking file operations."""
        from contextlib import contextmanager
        
        @contextmanager
        def _mock_file():
            if operation == "open":
                with patch('builtins.open') as mock_open:
                    mock_file = Mock()
                    mock_file.read.return_value = return_value or ""
                    mock_file.write = Mock()
                    mock_file.close = Mock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    yield mock_open
            elif operation == "exists":
                with patch('os.path.exists') as mock_exists:
                    mock_exists.return_value = return_value or True
                    yield mock_exists
            elif operation == "makedirs":
                with patch('os.makedirs') as mock_makedirs:
                    mock_makedirs.return_value = return_value
                    yield mock_makedirs
        
        return _mock_file()
    
    @staticmethod
    def mock_logging_operation(level: str = "INFO"):
        """Context manager for mocking logging operations."""
        from contextlib import contextmanager
        
        @contextmanager
        def _mock_logging():
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                yield mock_logger
        
        return _mock_logging()
    
    @staticmethod
    def create_test_user_data(**kwargs) -> Dict[str, Any]:
        """Create test user data with defaults."""
        default_data = {
            "id": TestHelper.generate_random_id(),
            "email": TestHelper.generate_random_email(),
            "full_name": f"Test User {TestHelper.generate_random_string(5)}",
            "phone_number": TestHelper.generate_random_phone(),
            "is_active": True,
            "is_verified": True,
            "created_at": TestHelper.generate_timestamp(),
            "updated_at": TestHelper.generate_timestamp(),
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_test_auth_data(**kwargs) -> Dict[str, Any]:
        """Create test authentication data with defaults."""
        default_data = {
            "access_token": f"access_{TestHelper.generate_random_string(32)}",
            "refresh_token": f"refresh_{TestHelper.generate_random_string(32)}",
            "token_type": "bearer",
            "expires_in": 3600,
            "scope": "read write",
            "created_at": TestHelper.generate_timestamp(),
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_test_api_response(**kwargs) -> Dict[str, Any]:
        """Create test API response data with defaults."""
        default_data = {
            "status": "success",
            "data": {},
            "message": "Operation completed successfully",
            "timestamp": TestHelper.generate_timestamp(),
            "request_id": TestHelper.generate_random_string(16),
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for testing using bcrypt."""
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def generate_jwt_payload(**kwargs) -> Dict[str, Any]:
        """Generate JWT payload for testing."""
        default_payload = {
            "sub": TestHelper.generate_random_email(),
            "user_id": TestHelper.generate_random_id(),
            "exp": int(datetime.now().timestamp()) + 3600,
            "iat": int(datetime.now().timestamp()),
            "iss": "test-issuer",
            "aud": "test-audience",
        }
        default_payload.update(kwargs)
        return default_payload
    
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
    def assert_async_called_with(mock_async, *args, **kwargs):
        """Assert that an async mock was called with specific arguments."""
        # This is a simplified version - in practice, you'd need more sophisticated
        # async mocking depending on your testing framework
        assert mock_async.called
        if args:
            assert mock_async.call_args[0] == args
        if kwargs:
            assert mock_async.call_args[1] == kwargs


class TestDataFactory:
    """Factory class for creating test data objects."""
    
    @staticmethod
    def create_user(**kwargs) -> Dict[str, Any]:
        """Create a user object for testing."""
        return TestHelper.create_test_user_data(**kwargs)
    
    @staticmethod
    def create_auth_token(**kwargs) -> Dict[str, Any]:
        """Create an auth token object for testing."""
        return TestHelper.create_test_auth_data(**kwargs)
    
    @staticmethod
    def create_api_response(**kwargs) -> Dict[str, Any]:
        """Create an API response object for testing."""
        return TestHelper.create_test_api_response(**kwargs)
    
    @staticmethod
    def create_error_response(error_code: str, message: str) -> Dict[str, Any]:
        """Create an error response object for testing."""
        return {
            "status": "error",
            "error_code": error_code,
            "message": message,
            "timestamp": TestHelper.generate_timestamp(),
            "request_id": TestHelper.generate_random_string(16),
        }
    
    @staticmethod
    def create_pagination_response(
        data: List[Dict[str, Any]],
        page: int = 1,
        per_page: int = 10,
        total: int = None
    ) -> Dict[str, Any]:
        """Create a paginated response object for testing."""
        if total is None:
            total = len(data)
        
        return {
            "status": "success",
            "data": data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1,
            },
            "timestamp": TestHelper.generate_timestamp(),
        }


# Export commonly used utilities
__all__ = [
    'TestHelper',
    'TestDataFactory',
]
