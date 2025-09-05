"""
Test Data Generators

This module provides comprehensive test data generators for creating
realistic test data across all system components.
"""

from typing import Any, Dict, List
from faker import Faker


class BaseDataGenerator:
    """Base class for all data generators."""
    
    def __init__(self, locale: str = 'en_US'):
        self.fake = Faker(locale)
        self._generated_data = []
    
    def reset(self):
        """Reset the generator state."""
        self._generated_data.clear()
    
    def get_generated_data(self) -> List[Any]:
        """Get all generated data."""
        return self._generated_data.copy()
    
    def clear_generated_data(self):
        """Clear all generated data."""
        self._generated_data.clear()


class UserDataGenerator(BaseDataGenerator):
    """Generator for user-related test data."""
    
    def generate_user(self, **overrides) -> Dict[str, Any]:
        """Generate a single user."""
        user = {
            "id": self.fake.random_int(min=1, max=10000),
            "email": self.fake.email(),
            "username": self.fake.user_name(),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "phone_number": self.fake.phone_number(),
            "date_of_birth": self.fake.date_of_birth(minimum_age=18, maximum_age=80),
            "is_active": self.fake.boolean(chance_of_getting_true=90),
            "is_verified": self.fake.boolean(chance_of_getting_true=80),
            "is_staff": self.fake.boolean(chance_of_getting_true=10),
            "is_superuser": self.fake.boolean(chance_of_getting_true=5),
            "created_at": self.fake.date_time_between(start_date='-2y', end_date='now'),
            "updated_at": self.fake.date_time_between(start_date='-1y', end_date='now'),
            "last_login": self.fake.date_time_between(start_date='-30d', end_date='now') if self.fake.boolean() else None,
            "timezone": self.fake.timezone(),
            "language": self.fake.language_code(),
            "country": self.fake.country_code(),
            "avatar_url": self.fake.image_url() if self.fake.boolean() else None,
            "bio": self.fake.text(max_nb_chars=200) if self.fake.boolean() else None,
            "website": self.fake.url() if self.fake.boolean() else None
        }
        
        # Apply overrides
        user.update(overrides)
        self._generated_data.append(user)
        return user
    
    def generate_users(self, count: int = 10, **overrides) -> List[Dict[str, Any]]:
        """Generate multiple users."""
        return [self.generate_user(**overrides) for _ in range(count)]


class AuthDataGenerator(BaseDataGenerator):
    """Generator for authentication-related test data."""
    
    def generate_access_token(self, user_id: int = None, **overrides) -> Dict[str, Any]:
        """Generate access token data."""
        token = {
            "access_token": self.fake.sha256(),
            "refresh_token": self.fake.sha256(),
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": " ".join(self.fake.words(nb=3)),
            "user_id": user_id or self.fake.random_int(min=1, max=10000),
            "client_id": self.fake.uuid4(),
            "created_at": self.fake.date_time_between(start_date='-1h', end_date='now'),
            "expires_at": self.fake.date_time_between(start_date='now', end_date='+1h')
        }
        
        token.update(overrides)
        self._generated_data.append(token)
        return token


class APIDataGenerator(BaseDataGenerator):
    """Generator for API-related test data."""
    
    def generate_api_request(self, **overrides) -> Dict[str, Any]:
        """Generate API request data."""
        request = {
            "method": self.fake.random_element(elements=("GET", "POST", "PUT", "DELETE", "PATCH")),
            "url": self.fake.url(),
            "path": "/" + "/".join(self.fake.words(nb=3)),
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.fake.sha256()}",
                "User-Agent": self.fake.user_agent(),
                "Accept": "application/json",
                "X-Request-ID": self.fake.uuid4()
            },
            "query_params": {
                "page": self.fake.random_int(min=1, max=100),
                "limit": self.fake.random_int(min=10, max=100),
                "sort": self.fake.random_element(elements=("created_at", "updated_at", "name", "email"))
            },
            "body": {
                "data": self.fake.text(max_nb_chars=500)
            },
            "client_ip": self.fake.ipv4(),
            "user_agent": self.fake.user_agent(),
            "timestamp": self.fake.date_time_between(start_date='-1h', end_date='now')
        }
        
        request.update(overrides)
        self._generated_data.append(request)
        return request
    
    def generate_api_response(self, status_code: int = None, **overrides) -> Dict[str, Any]:
        """Generate API response data."""
        status_code = status_code or self.fake.random_element(elements=(200, 201, 400, 401, 403, 404, 500))
        
        response = {
            "status_code": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Content-Length": str(self.fake.random_int(min=100, max=10000)),
                "X-Response-Time": f"{self.fake.random_number(digits=3)}ms",
                "X-Request-ID": self.fake.uuid4()
            },
            "body": {
                "success": status_code < 400,
                "message": self.fake.text(max_nb_chars=200),
                "data": self.fake.text(max_nb_chars=1000) if status_code < 400 else None,
                "error": self.fake.text(max_nb_chars=200) if status_code >= 400 else None
            },
            "response_time": self.fake.random_number(digits=3) / 1000,  # milliseconds
            "timestamp": self.fake.date_time_between(start_date='-1h', end_date='now')
        }
        
        response.update(overrides)
        self._generated_data.append(response)
        return response


class ToolDataGenerator(BaseDataGenerator):
    """Generator for tool-related test data."""
    
    def generate_tool_data(self, **overrides) -> Dict[str, Any]:
        """Generate tool data for testing."""
        tool_data = {
            "name": self.fake.word(),
            "description": self.fake.sentence(),
            "category": self.fake.random_element(elements=("utility", "communication", "productivity", "entertainment")),
            "version": f"{self.fake.random_int(min=1, max=10)}.{self.fake.random_int(min=0, max=9)}.{self.fake.random_int(min=0, max=9)}",
            "author": self.fake.name(),
            "is_active": self.fake.boolean(chance_of_getting_true=90),
            "created_at": self.fake.date_time_between(start_date='-1y', end_date='now'),
            "updated_at": self.fake.date_time_between(start_date='-30d', end_date='now'),
            "usage_count": self.fake.random_int(min=0, max=10000),
            "rating": round(self.fake.random.uniform(1.0, 5.0), 1),
            "tags": [self.fake.word() for _ in range(self.fake.random_int(min=1, max=5))],
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": self.fake.sentence()
                    },
                    "param2": {
                        "type": "integer",
                        "description": self.fake.sentence()
                    }
                }
            }
        }
        
        tool_data.update(overrides)
        self._generated_data.append(tool_data)
        return tool_data
    
    def generate_tool_execution_data(self, **overrides) -> Dict[str, Any]:
        """Generate tool execution data for testing."""
        execution_data = {
            "tool_name": self.fake.word(),
            "user_id": self.fake.random_int(min=1, max=1000),
            "execution_time": self.fake.random.uniform(0.1, 5.0),
            "status": self.fake.random_element(elements=("success", "error", "timeout")),
            "input_parameters": {
                "param1": self.fake.word(),
                "param2": self.fake.random_int(min=1, max=100)
            },
            "output": self.fake.text(max_nb_chars=500),
            "error_message": self.fake.sentence() if self.fake.boolean() else None,
            "timestamp": self.fake.date_time_between(start_date='-1h', end_date='now')
        }
        
        execution_data.update(overrides)
        self._generated_data.append(execution_data)
        return execution_data


class PerformanceDataGenerator(BaseDataGenerator):
    """Generator for performance-related test data."""
    
    def generate_performance_metrics(self, **overrides) -> Dict[str, Any]:
        """Generate performance metrics for testing."""
        metrics = {
            "execution_time": self.fake.random.uniform(0.1, 10.0),
            "memory_usage": self.fake.random.uniform(10.0, 1000.0),
            "cpu_usage": self.fake.random.uniform(1.0, 100.0),
            "response_time": self.fake.random.uniform(0.05, 2.0),
            "throughput": self.fake.random.uniform(10.0, 1000.0),
            "error_rate": self.fake.random.uniform(0.0, 0.1),
            "timestamp": self.fake.date_time_between(start_date='-1h', end_date='now')
        }
        
        metrics.update(overrides)
        self._generated_data.append(metrics)
        return metrics


class DatabaseDataGenerator(BaseDataGenerator):
    """Generator for database-related test data."""
    
    def generate_database_record(self, **overrides) -> Dict[str, Any]:
        """Generate database record data for testing."""
        record = {
            "id": self.fake.random_int(min=1, max=10000),
            "created_at": self.fake.date_time_between(start_date='-1y', end_date='now'),
            "updated_at": self.fake.date_time_between(start_date='-30d', end_date='now'),
            "is_active": self.fake.boolean(chance_of_getting_true=90),
            "metadata": {
                "source": self.fake.word(),
                "version": f"{self.fake.random_int(min=1, max=10)}.{self.fake.random_int(min=0, max=9)}",
                "tags": [self.fake.word() for _ in range(self.fake.random_int(min=1, max=3))]
            }
        }
        
        record.update(overrides)
        self._generated_data.append(record)
        return record
    
    def generate_conversation_state(self, **overrides) -> Dict[str, Any]:
        """Generate conversation state data for testing."""
        state = {
            "id": self.fake.random_int(min=1, max=10000),
            "user_id": self.fake.random_int(min=1, max=1000),
            "session_id": self.fake.uuid4(),
            "context": {
                "current_topic": self.fake.word(),
                "previous_messages": [self.fake.sentence() for _ in range(self.fake.random_int(min=1, max=5))],
                "user_preferences": {
                    "language": self.fake.language_code(),
                    "timezone": self.fake.timezone()
                }
            },
            "state_data": {
                "active_tools": [self.fake.word() for _ in range(self.fake.random_int(min=0, max=3))],
                "pending_actions": [self.fake.word() for _ in range(self.fake.random_int(min=0, max=2))]
            },
            "created_at": self.fake.date_time_between(start_date='-1h', end_date='now'),
            "updated_at": self.fake.date_time_between(start_date='-30m', end_date='now')
        }
        
        state.update(overrides)
        self._generated_data.append(state)
        return state


# Global generator instances
user_data_generator = UserDataGenerator()
auth_data_generator = AuthDataGenerator()
api_data_generator = APIDataGenerator()
tool_data_generator = ToolDataGenerator()
performance_data_generator = PerformanceDataGenerator()
database_data_generator = DatabaseDataGenerator()


def get_user_data_generator() -> UserDataGenerator:
    """Get the global user data generator."""
    return user_data_generator


def get_auth_data_generator() -> AuthDataGenerator:
    """Get the global auth data generator."""
    return auth_data_generator


def get_tool_data_generator() -> ToolDataGenerator:
    """Get the global tool data generator."""
    return tool_data_generator


def get_performance_data_generator() -> PerformanceDataGenerator:
    """Get the global performance data generator."""
    return performance_data_generator


def get_database_data_generator() -> DatabaseDataGenerator:
    """Get the global database data generator."""
    return database_data_generator


def get_api_data_generator() -> APIDataGenerator:
    """Get the global API data generator."""
    return api_data_generator


def reset_all_generators():
    """Reset all global generators."""
    user_data_generator.reset()
    auth_data_generator.reset()
    api_data_generator.reset()