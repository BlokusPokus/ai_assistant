"""
Test OAuth routes functionality.

This module tests the OAuth FastAPI routes to ensure they work correctly
with the OAuth models and services.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Import the FastAPI app with OAuth routes
from src.apps.fastapi_app.main import app


class TestOAuthRoutes:
    """Test OAuth route functionality."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_oauth_providers_endpoint_requires_auth(self):
        """Test that OAuth providers endpoint requires authentication."""
        # This endpoint should require authentication
        response = self.client.get("/api/v1/oauth/providers")

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_oauth_status_endpoint_requires_auth(self):
        """Test that OAuth status endpoint requires authentication."""
        # This endpoint should require authentication
        response = self.client.get("/api/v1/oauth/status")

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_oauth_integrations_endpoint_requires_auth(self):
        """Test that OAuth integrations endpoint requires authentication."""
        # This endpoint should require authentication
        response = self.client.get("/api/v1/oauth/integrations")

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_oauth_initiate_endpoint_requires_auth(self):
        """Test that OAuth initiate endpoint requires authentication."""
        # This endpoint should require authentication
        response = self.client.post("/api/v1/oauth/initiate", json={
            "provider": "google",
            "scopes": ["openid", "email"],
            "redirect_uri": "https://example.com/callback"
        })

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_oauth_callback_endpoint_requires_auth(self):
        """Test that OAuth callback endpoint requires authentication."""
        # This endpoint should require authentication for security
        response = self.client.get(
            "/api/v1/oauth/callback?state=test_state&code=test_code&provider=google")

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_oauth_routes_exist(self):
        """Test that all expected OAuth routes exist."""
        # Get all routes from the app
        routes = [route.path for route in app.routes]

        # Expected OAuth routes (with correct prefix)
        expected_routes = [
            "/api/v1/oauth/providers",
            "/api/v1/oauth/initiate",
            "/api/v1/oauth/callback",
            "/api/v1/oauth/integrations",
            "/api/v1/oauth/status"
        ]

        # Check that all expected routes exist
        for route in expected_routes:
            assert route in routes, f"Route {route} not found"


if __name__ == "__main__":
    pytest.main([__file__])
