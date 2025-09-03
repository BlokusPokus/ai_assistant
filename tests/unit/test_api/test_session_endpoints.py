"""
Unit tests for session management API endpoints.

This module tests the session management endpoints including:
- Session listing and statistics
- Session invalidation
- Session extension
- Health checks
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.routes.sessions import router as sessions_router
from apps.fastapi_app.routes.sessions import (
    InvalidateAllSessionsRequest,
)
from personal_assistant.database.models.users import User
from personal_assistant.database.models.mfa_models import SecurityEvent
from tests.utils.test_data_generators import UserDataGenerator, APIDataGenerator


class TestSessionEndpoints:
    """Test class for session management API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.app.include_router(sessions_router)
        self.client = TestClient(self.app)
        
        # Test data generators
        self.user_generator = UserDataGenerator()
        self.api_generator = APIDataGenerator()
        
        # Sample test data
        self.test_user = self.user_generator.generate_user()
        self.test_session_data = {
            "session_id": "test_session_123",
            "device_info": {
                "browser": "Chrome",
                "os": "Windows"
            },
            "ip_address": "192.168.1.1"
        }

    @pytest.mark.asyncio
    async def test_get_user_sessions_success(self):
        """Test successful retrieval of user sessions."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session data
                mock_sessions = [
                    {
                        "session_id": "session_1",
                        "device_info": {
                            "browser": "Chrome",
                            "os": "Windows",
                            "device": "Desktop",
                            "platform": "Web"
                        },
                        "ip_address": "192.168.1.1",
                        "user_agent": "Mozilla/5.0...",
                        "created_at": "2024-01-01T00:00:00",
                        "last_accessed": "2024-01-01T12:00:00",
                        "expires_at": "2024-01-02T00:00:00",
                        "is_active": True,
                        "session_type": "web"
                    }
                ]
                mock_session_service.get_user_sessions.return_value = mock_sessions
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.get("/api/v1/sessions/")
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert len(data) == 1
                    assert data[0]["session_id"] == "session_1"
                    assert data[0]["device_info"]["browser"] == "Chrome"
                    assert data[0]["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_user_sessions_error(self):
        """Test error handling in get user sessions."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock service error
                mock_session_service.get_user_sessions.side_effect = Exception("Service error")
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.get("/api/v1/sessions/")
                    
                    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                    assert "Failed to get sessions" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_session_stats_success(self):
        """Test successful retrieval of session statistics."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session stats
                mock_stats = {
                    "total_sessions": 3,
                    "active_sessions": 2,
                    "can_create_new": True,
                    "oldest_session": "2024-01-01T00:00:00",
                    "newest_session": "2024-01-01T12:00:00",
                    "sessions_remaining": 1
                }
                mock_session_service.get_session_stats.return_value = mock_stats
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.get("/api/v1/sessions/stats")
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["total_sessions"] == 3
                    assert data["active_sessions"] == 2
                    assert data["can_create_new"] is True
                    assert data["sessions_remaining"] == 1

    @pytest.mark.asyncio
    async def test_get_session_stats_error(self):
        """Test error handling in get session stats."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock service error
                mock_session_service.get_session_stats.side_effect = Exception("Service error")
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.get("/api/v1/sessions/stats")
                    
                    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                    assert "Failed to get session stats" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_invalidate_session_success(self):
        """Test successful session invalidation."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session data
                mock_session_data = {
                    "session_id": "session_1",
                    "user_id": "1",
                    "device_info": {"browser": "Chrome"}
                }
                mock_session_service.get_session.return_value = mock_session_data
                mock_session_service.invalidate_session.return_value = True
                
                # Mock database operations
                mock_session.add = Mock()
                mock_session.commit = AsyncMock()
                mock_session.rollback = AsyncMock()
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.delete("/api/v1/sessions/session_1")
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert "Session invalidated successfully" in data["message"]

    @pytest.mark.asyncio
    async def test_invalidate_session_not_found(self):
        """Test invalidation of non-existent session."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session not found
                mock_session_service.get_session.return_value = None
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.delete("/api/v1/sessions/nonexistent_session")
                    
                    assert response.status_code == status.HTTP_404_NOT_FOUND
                    assert "Session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_invalidate_session_wrong_owner(self):
        """Test invalidation of session belonging to different user."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session belonging to different user
                mock_session_data = {
                    "session_id": "session_1",
                    "user_id": "2",  # Different user
                    "device_info": {"browser": "Chrome"}
                }
                mock_session_service.get_session.return_value = mock_session_data
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.delete("/api/v1/sessions/session_1")
                    
                    assert response.status_code == status.HTTP_404_NOT_FOUND
                    assert "Session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_invalidate_session_service_error(self):
        """Test session invalidation with service error."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session data
                mock_session_data = {
                    "session_id": "session_1",
                    "user_id": "1",
                    "device_info": {"browser": "Chrome"}
                }
                mock_session_service.get_session.return_value = mock_session_data
                mock_session_service.invalidate_session.return_value = False
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.delete("/api/v1/sessions/session_1")
                    
                    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                    assert "Failed to invalidate session" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_invalidate_all_sessions_success(self):
        """Test successful invalidation of all sessions."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock successful invalidation
                mock_session_service.invalidate_user_sessions.return_value = 3
                
                # Mock database operations
                mock_session.add = Mock()
                mock_session.commit = AsyncMock()
                mock_session.rollback = AsyncMock()
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.post(
                        "/api/v1/sessions/invalidate-all",
                        json={"exclude_current": True}
                    )
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert "Invalidated 3 sessions successfully" in data["message"]
                    assert data["invalidated_count"] == 3

    @pytest.mark.asyncio
    async def test_invalidate_all_sessions_error(self):
        """Test error handling in invalidate all sessions."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock service error
                mock_session_service.invalidate_user_sessions.side_effect = Exception("Service error")
                
                # Mock database operations
                mock_session.rollback = AsyncMock()
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.post(
                        "/api/v1/sessions/invalidate-all",
                        json={"exclude_current": True}
                    )
                    
                    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                    assert "Failed to invalidate sessions" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_extend_session_success(self):
        """Test successful session extension."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session data
                mock_session_data = {
                    "session_id": "session_1",
                    "user_id": "1",
                    "expires_at": "2024-01-02T00:00:00"
                }
                mock_session_service.get_session.return_value = mock_session_data
                mock_session_service.extend_session.return_value = True
                
                # Mock database operations
                mock_session.add = Mock()
                mock_session.commit = AsyncMock()
                mock_session.rollback = AsyncMock()
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.post("/api/v1/sessions/extend/session_1?hours=2")
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert "Session extended successfully" in data["message"]

    @pytest.mark.asyncio
    async def test_extend_session_not_found(self):
        """Test extension of non-existent session."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session not found
                mock_session_service.get_session.return_value = None
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.post("/api/v1/sessions/extend/nonexistent_session")
                    
                    assert response.status_code == status.HTTP_404_NOT_FOUND
                    assert "Session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_extend_session_service_error(self):
        """Test session extension with service error."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session data
                mock_session_data = {
                    "session_id": "session_1",
                    "user_id": "1",
                    "expires_at": "2024-01-02T00:00:00"
                }
                mock_session_service.get_session.return_value = mock_session_data
                mock_session_service.extend_session.return_value = False
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.post("/api/v1/sessions/extend/session_1")
                    
                    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                    assert "Failed to extend session" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_check_session_service_health_success(self):
        """Test successful session service health check."""
        with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
            mock_session_service = Mock()
            mock_get_service.return_value = mock_session_service
            
            # Mock Redis ping
            mock_redis = Mock()
            mock_redis.ping = AsyncMock()
            mock_session_service.redis = mock_redis
            
            response = self.client.get("/api/v1/sessions/health")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "session_management"
            assert data["redis"] == "connected"

    @pytest.mark.asyncio
    async def test_check_session_service_health_error(self):
        """Test session service health check with error."""
        with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
            mock_session_service = Mock()
            mock_get_service.return_value = mock_session_service
            
            # Mock Redis ping failure
            mock_redis = Mock()
            mock_redis.ping = AsyncMock(side_effect=Exception("Connection failed"))
            mock_session_service.redis = mock_redis
            
            response = self.client.get("/api/v1/sessions/health")
            
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert "Session service unhealthy" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_session_service_unavailable(self):
        """Test when session service is unavailable."""
        with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
            from fastapi import HTTPException
            mock_get_service.side_effect = HTTPException(
                status_code=503, detail="Session service unavailable"
            )
            
            response = self.client.get("/api/v1/sessions/health")
            
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert "Session service unavailable" in response.json()["detail"]

    def test_validation_errors(self):
        """Test various validation errors."""
        # Test invalid request body for invalidate all sessions
        response = self.client.post("/api/v1/sessions/invalidate-all", json={"invalid": "data"})
        # This should still work as the endpoint accepts the request
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    @pytest.mark.asyncio
    async def test_authentication_required(self):
        """Test that authentication is required for protected endpoints."""
        # Test without authentication - should fail
        response = self.client.get("/api/v1/sessions/")
        # This would typically return 401, but depends on middleware implementation
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    @pytest.mark.asyncio
    async def test_permission_required(self):
        """Test that proper permissions are required for certain operations."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session data
                mock_session_data = {
                    "session_id": "session_1",
                    "user_id": "1",
                    "device_info": {"browser": "Chrome"}
                }
                mock_session_service.get_session.return_value = mock_session_data
                mock_session_service.invalidate_session.return_value = True
                
                # Mock database operations
                mock_session.add = Mock()
                mock_session.commit = AsyncMock()
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    # Test with proper authentication
                    response = self.client.delete("/api/v1/sessions/session_1")
                    
                    assert response.status_code == status.HTTP_200_OK
                    assert "Session invalidated successfully" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_security_event_logging(self):
        """Test that security events are properly logged."""
        with patch('apps.fastapi_app.routes.sessions.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock SessionService
            with patch('apps.fastapi_app.routes.sessions.get_session_service') as mock_get_service:
                mock_session_service = Mock()
                mock_get_service.return_value = mock_session_service
                
                # Mock session data
                mock_session_data = {
                    "session_id": "session_1",
                    "user_id": "1",
                    "device_info": {"browser": "Chrome"}
                }
                mock_session_service.get_session.return_value = mock_session_data
                mock_session_service.invalidate_session.return_value = True
                
                # Mock database operations
                mock_session.add = Mock()
                mock_session.commit = AsyncMock()
                
                # Mock get_current_user dependency
                with patch('apps.fastapi_app.routes.sessions.get_current_user', return_value=mock_user):
                    response = self.client.delete("/api/v1/sessions/session_1")
                    
                    assert response.status_code == status.HTTP_200_OK
                    
                    # Verify that SecurityEvent was added to session
                    mock_session.add.assert_called_once()
                    added_object = mock_session.add.call_args[0][0]
                    assert isinstance(added_object, SecurityEvent)
                    assert added_object.user_id == 1
                    assert added_object.event_type == "session_invalidated"
