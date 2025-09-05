"""
Authentication-related test fixtures.

This module provides fixtures for testing authentication functionality
including user data, tokens, and authentication scenarios.
"""

import pytest
from typing import Dict, Any, List
from tests.utils.test_data_generators import UserDataGenerator, AuthDataGenerator


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return UserDataGenerator.generate_user(
        id=1,
        email="test@example.com",
        full_name="Test User",
        phone_number="+1234567890",
        is_active=True,
        is_verified=True
    )


@pytest.fixture
def sample_users():
    """Sample batch of users for testing."""
    return UserDataGenerator.generate_user_batch(5)


@pytest.fixture
def admin_user():
    """Admin user data for testing."""
    return UserDataGenerator.generate_user_with_roles(
        id=2,
        email="admin@example.com",
        full_name="Admin User",
        roles=["admin", "user"]
    )


@pytest.fixture
def inactive_user():
    """Inactive user data for testing."""
    return UserDataGenerator.generate_user(
        id=3,
        email="inactive@example.com",
        full_name="Inactive User",
        is_active=False,
        is_verified=False
    )


@pytest.fixture
def unverified_user():
    """Unverified user data for testing."""
    return UserDataGenerator.generate_user(
        id=4,
        email="unverified@example.com",
        full_name="Unverified User",
        is_active=True,
        is_verified=False
    )


@pytest.fixture
def access_token():
    """Sample access token for testing."""
    return AuthDataGenerator.generate_access_token(
        user_id=1,
        expires_in=3600,
        scope="read write"
    )


@pytest.fixture
def refresh_token():
    """Sample refresh token for testing."""
    return AuthDataGenerator.generate_refresh_token(
        user_id=1,
        expires_in=86400
    )


@pytest.fixture
def auth_tokens():
    """Complete authentication tokens for testing."""
    return AuthDataGenerator.generate_auth_pair(user_id=1)


@pytest.fixture
def expired_access_token():
    """Expired access token for testing."""
    return AuthDataGenerator.generate_access_token(
        user_id=1,
        expires_in=-3600,  # Expired
        scope="read write"
    )


@pytest.fixture
def invalid_token():
    """Invalid token for testing."""
    return {
        "access_token": "invalid_token",
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": "read write",
        "user_id": 1,
        "created_at": "2022-01-01T00:00:00",
    }


@pytest.fixture
def user_registration_data():
    """User registration data for testing."""
    return {
        "email": "newuser@example.com",
        "full_name": "New User",
        "phone_number": "+1987654321",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
    }


@pytest.fixture
def user_login_data():
    """User login data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
    }


@pytest.fixture
def invalid_login_data():
    """Invalid login data for testing."""
    return {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123!",
    }


@pytest.fixture
def password_reset_data():
    """Password reset data for testing."""
    return {
        "email": "test@example.com",
        "new_password": "NewPassword123!",
        "confirm_password": "NewPassword123!",
        "reset_token": "valid_reset_token",
    }


@pytest.fixture
def mfa_setup_data():
    """MFA setup data for testing."""
    return {
        "user_id": 1,
        "secret_key": "JBSWY3DPEHPK3PXP",
        "backup_codes": [
            "12345678",
            "87654321",
            "11223344",
            "44332211",
            "55667788",
        ],
    }


@pytest.fixture
def mfa_verification_data():
    """MFA verification data for testing."""
    return {
        "user_id": 1,
        "code": "123456",
        "backup_code": None,
    }


@pytest.fixture
def mfa_backup_code_data():
    """MFA backup code verification data for testing."""
    return {
        "user_id": 1,
        "code": None,
        "backup_code": "12345678",
    }


@pytest.fixture
def invalid_mfa_data():
    """Invalid MFA data for testing."""
    return {
        "user_id": 1,
        "code": "000000",
        "backup_code": None,
    }


@pytest.fixture
def user_permissions():
    """User permissions for testing."""
    return [
        "user:read",
        "user:write",
        "conversation:read",
        "conversation:write",
        "tools:use",
    ]


@pytest.fixture
def admin_permissions():
    """Admin permissions for testing."""
    return [
        "user:read",
        "user:write",
        "user:delete",
        "conversation:read",
        "conversation:write",
        "conversation:delete",
        "tools:use",
        "admin:manage",
        "system:configure",
    ]


@pytest.fixture
def user_roles():
    """User roles for testing."""
    return [
        {
            "id": 1,
            "name": "user",
            "description": "Standard user role",
            "permissions": ["user:read", "user:write", "conversation:read", "conversation:write"],
        },
        {
            "id": 2,
            "name": "admin",
            "description": "Administrator role",
            "permissions": ["user:read", "user:write", "user:delete", "admin:manage"],
        },
    ]


@pytest.fixture
def session_data():
    """Session data for testing."""
    return {
        "session_id": "test_session_123",
        "user_id": 1,
        "created_at": "2022-01-01T00:00:00",
        "expires_at": "2022-01-01T01:00:00",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0 (Test Browser)",
        "is_active": True,
    }


@pytest.fixture
def expired_session_data():
    """Expired session data for testing."""
    return {
        "session_id": "expired_session_123",
        "user_id": 1,
        "created_at": "2022-01-01T00:00:00",
        "expires_at": "2022-01-01T00:30:00",  # Expired
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0 (Test Browser)",
        "is_active": False,
    }


@pytest.fixture
def auth_headers():
    """Authentication headers for testing."""
    return {
        "Authorization": "Bearer test_access_token",
        "Content-Type": "application/json",
    }


@pytest.fixture
def invalid_auth_headers():
    """Invalid authentication headers for testing."""
    return {
        "Authorization": "Bearer invalid_token",
        "Content-Type": "application/json",
    }


@pytest.fixture
def missing_auth_headers():
    """Missing authentication headers for testing."""
    return {
        "Content-Type": "application/json",
    }


@pytest.fixture
def auth_scenarios():
    """Various authentication scenarios for testing."""
    return {
        "valid_user": {
            "user": UserDataGenerator.generate_user(is_active=True, is_verified=True),
            "tokens": AuthDataGenerator.generate_auth_pair(),
            "expected_result": "success",
        },
        "inactive_user": {
            "user": UserDataGenerator.generate_user(is_active=False, is_verified=True),
            "tokens": None,
            "expected_result": "account_inactive",
        },
        "unverified_user": {
            "user": UserDataGenerator.generate_user(is_active=True, is_verified=False),
            "tokens": AuthDataGenerator.generate_auth_pair(),
            "expected_result": "account_unverified",
        },
        "expired_token": {
            "user": UserDataGenerator.generate_user(is_active=True, is_verified=True),
            "tokens": AuthDataGenerator.generate_access_token(expires_in=-3600),
            "expected_result": "token_expired",
        },
        "invalid_token": {
            "user": UserDataGenerator.generate_user(is_active=True, is_verified=True),
            "tokens": {"access_token": "invalid_token"},
            "expected_result": "token_invalid",
        },
    }


@pytest.fixture
def rate_limit_scenarios():
    """Rate limiting scenarios for testing."""
    return {
        "normal_usage": {
            "requests_per_minute": 10,
            "expected_result": "allowed",
        },
        "moderate_usage": {
            "requests_per_minute": 50,
            "expected_result": "allowed",
        },
        "high_usage": {
            "requests_per_minute": 100,
            "expected_result": "rate_limited",
        },
        "excessive_usage": {
            "requests_per_minute": 200,
            "expected_result": "rate_limited",
        },
    }

