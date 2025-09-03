"""
Test Data Generators

This module provides comprehensive test data generators for creating
realistic test data across all system components.
"""

import random
import string
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
from faker import Faker
import hashlib
import secrets


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


# Global generator instances
user_data_generator = UserDataGenerator()
auth_data_generator = AuthDataGenerator()
api_data_generator = APIDataGenerator()


def get_user_data_generator() -> UserDataGenerator:
    """Get the global user data generator."""
    return user_data_generator


def get_auth_data_generator() -> AuthDataGenerator:
    """Get the global auth data generator."""
    return auth_data_generator


def get_api_data_generator() -> APIDataGenerator:
    """Get the global API data generator."""
    return api_data_generator


def reset_all_generators():
    """Reset all global generators."""
    user_data_generator.reset()
    auth_data_generator.reset()
    api_data_generator.reset()