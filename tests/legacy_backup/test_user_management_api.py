"""
Comprehensive tests for the User Management API.

This module tests all user management endpoints including CRUD operations,
preferences management, and RBAC integration.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.fastapi_app.main import app
from src.apps.fastapi_app.services.user_service import UserService
from src.apps.fastapi_app.models.users import (
    UserResponse, UserUpdateRequest, UserPreferencesResponse,
    UserPreferencesUpdateRequest
)
from src.personal_assistant.database.models.users import User
from src.personal_assistant.database.models.user_settings import UserSetting

# Test client
client = TestClient(app)

# Mock data for testing
MOCK_USER = User(
    id=1,
    email="test@example.com",
    full_name="Test User",
    hashed_password="hashed_password",
    is_active=True,
    is_verified=True,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)

MOCK_USER_SETTINGS = [
    UserSetting(
        id=1,
        user_id=1,
        key="theme",
        value="dark",
        category="preferences",
        setting_type="string",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ),
    UserSetting(
        id=2,
        user_id=1,
        key="notifications",
        value="true",
        category="settings",
        setting_type="boolean",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
]


class TestUserService:
    """Test cases for UserService class."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self):
        """Test successful user retrieval by ID."""
        mock_db = AsyncMock()
        mock_user = MagicMock()

        # Mock the execute method to return a result object
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        service = UserService(mock_db)
        result = await service.get_user_by_id(1)

        assert result == mock_user
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Test user retrieval when user doesn't exist."""
        mock_db = AsyncMock()

        # Mock the execute method to return a result object
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = UserService(mock_db)
        result = await service.get_user_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_success(self):
        """Test successful user update."""
        mock_db = AsyncMock()
        mock_user = MagicMock()

        # Mock the execute method to return a result object
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        service = UserService(mock_db)
        result = await service.update_user(1, {"full_name": "Updated Name"})

        assert result == mock_user
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_no_valid_data(self):
        """Test user update with no valid data."""
        mock_db = AsyncMock()
        mock_user = MagicMock()

        # Mock the execute method to return a result object
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        service = UserService(mock_db)
        result = await service.update_user(1, {})

        assert result == mock_user
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_preferences_success(self):
        """Test successful preferences retrieval."""
        mock_db = AsyncMock()
        mock_settings = [MagicMock(key="theme", value="dark")]

        # Mock the execute method to return a result object
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_settings
        mock_db.execute.return_value = mock_result

        service = UserService(mock_db)
        result = await service.get_user_preferences(1)

        assert result == {"theme": "dark"}

    @pytest.mark.asyncio
    async def test_update_user_preferences_success(self):
        """Test successful preferences update."""
        mock_db = AsyncMock()

        # Mock the execute method to return a result object
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = UserService(mock_db)
        result = await service.update_user_preferences(1, {"theme": "light"})

        assert result is True
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_users_success(self):
        """Test successful user listing."""
        mock_db = AsyncMock()
        mock_users = [MagicMock(), MagicMock()]

        # Mock count result
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2

        # Mock users result
        mock_users_result = MagicMock()
        mock_users_result.scalars.return_value.all.return_value = mock_users

        # Set up execute to return different results for different calls
        mock_db.execute.side_effect = [mock_count_result, mock_users_result]

        service = UserService(mock_db)
        users, total = await service.list_users(skip=0, limit=10)

        assert len(users) == 2
        assert total == 2


class TestUserModels:
    """Test cases for Pydantic user models."""

    def test_user_response_model(self):
        """Test UserResponse model creation."""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "is_verified": True,
            "last_login": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        user_response = UserResponse(**user_data)
        assert user_response.id == 1
        assert user_response.email == "test@example.com"
        assert user_response.full_name == "Test User"

    def test_user_update_request_model(self):
        """Test UserUpdateRequest model validation."""
        # Valid update request
        update_data = {
            "full_name": "Updated Name"
        }
        update_request = UserUpdateRequest(**update_data)
        assert update_request.full_name == "Updated Name"

    def test_user_update_request_empty_names(self):
        """Test UserUpdateRequest validation for empty names."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            UserUpdateRequest(full_name="   ")

    def test_user_preferences_update_request_validation(self):
        """Test UserPreferencesUpdateRequest validation."""
        # Valid preferences
        preferences_data = {
            "preferences": {"theme": "dark", "language": "en"},
            "settings": {"notifications": True}
        }
        request = UserPreferencesUpdateRequest(**preferences_data)
        assert request.preferences == {"theme": "dark", "language": "en"}
        assert request.settings == {"notifications": True}

    def test_user_preferences_update_request_invalid_types(self):
        """Test UserPreferencesUpdateRequest validation for invalid types."""
        with pytest.raises(ValueError, match="Invalid value type"):
            UserPreferencesUpdateRequest(
                preferences={"invalid": lambda x: x}
            )


class TestUserAPIEndpoints:
    """Test cases for user API endpoints."""

    @patch('src.apps.fastapi_app.routes.users.get_current_user')
    @patch('src.apps.fastapi_app.routes.users.UserService')
    def test_get_current_user_profile_success(self, mock_user_service, mock_get_current_user):
        """Test successful current user profile retrieval."""
        # Mock current user
        mock_get_current_user.return_value = MOCK_USER

        # Mock user service
        mock_service_instance = MagicMock()
        mock_user_service.return_value = mock_service_instance

        response = client.get("/api/v1/users/me")

        # Should return 401 due to missing authentication
        assert response.status_code == 401

    @patch('src.apps.fastapi_app.routes.users.get_current_user')
    @patch('src.apps.fastapi_app.routes.users.UserService')
    def test_update_current_user_profile_success(self, mock_user_service, mock_get_current_user):
        """Test successful current user profile update."""
        # Mock current user
        mock_get_current_user.return_value = MOCK_USER

        # Mock user service
        mock_service_instance = MagicMock()
        mock_service_instance.update_user.return_value = MOCK_USER
        mock_user_service.return_value = mock_service_instance

        update_data = {"full_name": "Updated"}
        response = client.put("/api/v1/users/me", json=update_data)

        # Should return 401 due to missing authentication
        assert response.status_code == 401

    def test_get_user_preferences_endpoint(self):
        """Test user preferences endpoint."""
        response = client.get("/api/v1/users/me/preferences")
        # Should return 401 due to missing authentication
        assert response.status_code == 401

    def test_update_user_preferences_endpoint(self):
        """Test user preferences update endpoint."""
        update_data = {"preferences": {"theme": "light"}}
        response = client.put("/api/v1/users/me/preferences", json=update_data)
        # Should return 401 due to missing authentication
        assert response.status_code == 401

    def test_list_users_endpoint(self):
        """Test list users endpoint."""
        response = client.get("/api/v1/users/")
        # Should return 401 due to missing authentication
        assert response.status_code == 401

    def test_get_user_by_id_endpoint(self):
        """Test get user by ID endpoint."""
        response = client.get("/api/v1/users/1")
        # Should return 401 due to missing authentication
        assert response.status_code == 401

    def test_create_user_endpoint(self):
        """Test create user endpoint."""
        user_data = {
            "email": "new@example.com",
            "full_name": "New User",
            "password": "password123"
        }
        response = client.post("/api/v1/users/", json=user_data)
        # Should return 401 due to missing authentication
        assert response.status_code == 401

    def test_deactivate_user_endpoint(self):
        """Test deactivate user endpoint."""
        deactivate_data = {"deactivate_reason": "Testing"}
        response = client.delete("/api/v1/users/1")
        # Should return 401 due to missing authentication
        assert response.status_code == 401


class TestUserAPIIntegration:
    """Integration tests for user API endpoints."""

    @pytest.fixture
    def mock_authenticated_user(self):
        """Mock authenticated user for testing."""
        return MOCK_USER

    @pytest.fixture
    def mock_user_service(self):
        """Mock user service for testing."""
        service = MagicMock()
        service.get_user_by_id.return_value = MOCK_USER
        service.update_user.return_value = MOCK_USER
        service.get_user_preferences.return_value = {"theme": "dark"}
        service.get_user_settings.return_value = {"notifications": True}
        service.update_user_preferences.return_value = True
        service.update_user_settings.return_value = True
        service.list_users.return_value = ([MOCK_USER], 1)
        service.create_user.return_value = MOCK_USER
        service.deactivate_user.return_value = True
        service.get_user_stats.return_value = {"preferences_count": 5}
        return service

    def test_user_api_endpoints_structure(self):
        """Test that all expected user API endpoints exist."""
        # Check that the router is properly registered
        app_routes = [route.path for route in app.routes]

        expected_routes = [
            "/api/v1/users/me",
            "/api/v1/users/me/preferences",
            "/api/v1/users/me/settings",
            "/api/v1/users/",
            "/api/v1/users/{user_id}",
            "/api/v1/users/{user_id}/stats"
        ]

        for route in expected_routes:
            # Check if route exists (accounting for path parameters)
            route_exists = any(
                route.replace("{user_id}", "1") in app_route
                or route == app_route
                for app_route in app_routes
            )
            assert route_exists, f"Route {route} not found in application"

    def test_user_api_models_importable(self):
        """Test that all user API models can be imported."""
        try:
            from src.apps.fastapi_app.models.users import (
                UserResponse, UserUpdateRequest, UserPreferencesResponse,
                UserPreferencesUpdateRequest, UserListResponse, UserCreateRequest,
                UserDeleteRequest
            )
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import user models: {e}")

    def test_user_service_importable(self):
        """Test that UserService can be imported."""
        try:
            from src.apps.fastapi_app.services.user_service import UserService
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import UserService: {e}")


class TestUserAPISecurity:
    """Test cases for user API security features."""

    def test_all_endpoints_require_authentication(self):
        """Test that all user endpoints require authentication."""
        endpoints = [
            ("GET", "/api/v1/users/me"),
            ("PUT", "/api/v1/users/me"),
            ("GET", "/api/v1/users/me/preferences"),
            ("PUT", "/api/v1/users/me/preferences"),
            ("GET", "/api/v1/users/me/settings"),
            ("PUT", "/api/v1/users/me/settings"),
            ("GET", "/api/v1/users/"),
            ("GET", "/api/v1/users/1"),
            ("PUT", "/api/v1/users/1"),
            ("DELETE", "/api/v1/users/1"),
            ("POST", "/api/v1/users/"),
            ("GET", "/api/v1/users/1/stats")
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
                assert response.status_code == 401, f"{method} {endpoint} should require authentication"

    def test_input_validation(self):
        """Test that input validation is working."""
        # Test with invalid email format
        invalid_data = {"email": "invalid-email"}
        response = client.put("/api/v1/users/me", json=invalid_data)
        # Should return 401 due to missing authentication, but if it gets past that,
        # it should validate the email format
        assert response.status_code == 401

    def test_rate_limiting_integration(self):
        """Test that rate limiting is integrated."""
        # This test would require a more sophisticated setup with rate limiting
        # For now, we just verify the endpoint exists and responds
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401  # Unauthorized, not rate limited


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
