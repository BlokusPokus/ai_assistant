"""
Simple integration test for User Management API.

This test verifies that the API endpoints are properly registered and accessible.
"""

import pytest
from fastapi.testclient import TestClient

from apps.fastapi_app.main import app

client = TestClient(app)


def test_user_api_endpoints_registered():
    """Test that all expected user API endpoints are registered."""
    # Get all routes
    routes = [route for route in app.routes if hasattr(route, 'path')]

    # Expected user routes
    expected_user_routes = [
        "/api/v1/users/me",
        "/api/v1/users/me/preferences",
        "/api/v1/users/me/settings",
        "/api/v1/users/",
        "/api/v1/users/{user_id}",
        "/api/v1/users/{user_id}/stats"
    ]

    # Check that user routes exist
    user_routes = [r for r in routes if 'users' in str(r.path)]
    assert len(
        user_routes) >= 15, f"Expected at least 15 user routes, got {len(user_routes)}"

    # Check specific endpoints
    for expected_route in expected_user_routes:
        route_exists = any(
            expected_route.replace("{user_id}", "1") in str(r.path)
            or expected_route == str(r.path)
            for r in user_routes
        )
        assert route_exists, f"Route {expected_route} not found"


def test_user_api_requires_authentication():
    """Test that all user API endpoints require authentication."""
    endpoints = [
        "/api/v1/users/me",
        "/api/v1/users/me/preferences",
        "/api/v1/users/me/settings",
        "/api/v1/users/",
        "/api/v1/users/1",
        "/api/v1/users/1/stats"
    ]

    for endpoint in endpoints:
        # Test GET requests
        response = client.get(endpoint)
        assert response.status_code == 401, f"GET {endpoint} should require authentication"

        # Test POST requests (for endpoints that support it)
        if endpoint in ["/api/v1/users/", "/api/v1/users/me/preferences", "/api/v1/users/me/settings"]:
            response = client.post(endpoint, json={})
            assert response.status_code == 401, f"POST {endpoint} should require authentication"

        # Test PUT requests (for endpoints that support it)
        if endpoint in ["/api/v1/users/me", "/api/v1/users/1", "/api/v1/users/me/preferences", "/api/v1/users/me/settings"]:
            response = client.put(endpoint, json={})
            assert response.status_code == 401, f"PUT {endpoint} should require authentication"

        # Test DELETE requests (for endpoints that support it)
        if endpoint in ["/api/v1/users/1"]:
            response = client.delete(endpoint)
            assert response.status_code == 401, f"DELETE {endpoint} should require authentication"


def test_user_api_models_importable():
    """Test that all user API models can be imported."""
    try:
        from apps.fastapi_app.models.users import (
            UserResponse, UserUpdateRequest, UserPreferencesResponse,
            UserPreferencesUpdateRequest, UserListResponse, UserCreateRequest,
            UserDeleteRequest
        )
        assert True, "All user models imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import user models: {e}")


def test_user_service_importable():
    """Test that UserService can be imported."""
    try:
        from apps.fastapi_app.services.user_service import UserService
        assert True, "UserService imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import UserService: {e}")


def test_user_routes_importable():
    """Test that user routes can be imported."""
    try:
        from apps.fastapi_app.routes.users import router
        assert router is not None, "User router imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import user routes: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
