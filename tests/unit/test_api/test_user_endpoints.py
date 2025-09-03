"""
Unit tests for user management API endpoints.

This module tests the user management endpoints including:
- User profile management
- User preferences and settings
- Phone number management
- Admin user operations
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.routes.users import router as users_router
from apps.fastapi_app.models.users import (
    UserUpdateRequest,
    UserPreferencesUpdateRequest,
    UserCreateRequest,
    UserDeleteRequest,
)
from apps.fastapi_app.models.phone_management import (
    PhoneNumberCreate,
    PhoneNumberUpdate,
    PhoneNumberVerificationRequest,
    PhoneNumberVerificationCode,
)
from personal_assistant.database.models.users import User
from tests.utils.test_data_generators import UserDataGenerator, APIDataGenerator


class TestUserEndpoints:
    """Test class for user management API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.app.include_router(users_router)
        self.client = TestClient(self.app)
        
        # Test data generators
        self.user_generator = UserDataGenerator()
        self.api_generator = APIDataGenerator()
        
        # Sample test data
        self.test_user = self.user_generator.generate_user()
        self.test_user_update = {
            "full_name": "Updated User",
            "phone_number": "+1987654321"
        }
        self.test_preferences_update = {
            "preferences": {
                "theme": "dark",
                "language": "en"
            },
            "settings": {
                "privacy_level": "high"
            }
        }
        self.test_phone_create = {
            "phone_number": "+1987654321",
            "is_primary": False
        }

    @pytest.mark.asyncio
    async def test_get_current_user_profile_success(self):
        """Test successful retrieval of current user profile."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            mock_user.email = "test@example.com"
            mock_user.phone_number = "+1234567890"
            mock_user.full_name = "Test User"
            mock_user.is_active = True
            mock_user.is_verified = True
            mock_user.last_login = None
            mock_user.created_at = Mock()
            mock_user.updated_at = Mock()
            
            # Mock get_current_user_db dependency
            with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                response = self.client.get("/api/v1/users/me")
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["email"] == "test@example.com"
                assert data["full_name"] == "Test User"
                assert data["is_active"] is True
                assert data["is_verified"] is True

    @pytest.mark.asyncio
    async def test_get_current_user_profile_error(self):
        """Test error handling in get current user profile."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock get_current_user_db dependency to raise exception
            with patch('apps.fastapi_app.routes.users.get_current_user_db') as mock_get_user:
                mock_get_user.side_effect = Exception("Database error")
                
                response = self.client.get("/api/v1/users/me")
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert "Failed to retrieve user profile" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_current_user_profile_success(self):
        """Test successful update of current user profile."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock UserService
            with patch('apps.fastapi_app.routes.users.UserService') as mock_user_service_class:
                mock_user_service = Mock()
                mock_user_service_class.return_value = mock_user_service
                
                # Mock updated user
                mock_updated_user = Mock(spec=User)
                mock_updated_user.id = 1
                mock_updated_user.email = "updated@example.com"
                mock_updated_user.full_name = "Updated User"
                mock_updated_user.phone_number = "+1234567890"
                mock_updated_user.is_active = True
                mock_updated_user.is_verified = True
                mock_updated_user.last_login = None
                mock_updated_user.created_at = Mock()
                mock_updated_user.updated_at = Mock()
                
                mock_user_service.update_user.return_value = mock_updated_user
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    # Mock permission check
                    with patch('apps.fastapi_app.routes.users.require_user_permission') as mock_permission:
                        mock_permission.return_value = Mock(return_value=True)
                        
                        response = self.client.put(
                            "/api/v1/users/me",
                            json=self.test_user_update
                        )
                        
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert data["email"] == "updated@example.com"
                        assert data["full_name"] == "Updated User"

    @pytest.mark.asyncio
    async def test_update_current_user_profile_no_data(self):
        """Test update current user profile with no valid data."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock get_current_user_db dependency
            with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                # Mock permission check
                with patch('apps.fastapi_app.routes.users.require_user_permission') as mock_permission:
                    mock_permission.return_value = Mock(return_value=True)
                    
                    # Test with empty update data
                    response = self.client.put(
                        "/api/v1/users/me",
                        json={}
                    )
                    
                    assert response.status_code == status.HTTP_400_BAD_REQUEST
                    assert "No valid data provided for update" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_user_preferences_success(self):
        """Test successful retrieval of user preferences."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            mock_user.created_at = Mock()
            mock_user.updated_at = Mock()
            
            # Mock UserService
            with patch('apps.fastapi_app.routes.users.UserService') as mock_user_service_class:
                mock_user_service = Mock()
                mock_user_service_class.return_value = mock_user_service
                
                # Mock preferences and settings
                mock_user_service.get_user_preferences.return_value = {
                    "theme": "dark",
                    "language": "en",
                    "notifications": True
                }
                mock_user_service.get_user_settings.return_value = {
                    "privacy_level": "high",
                    "data_sharing": False
                }
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    # Mock permission check
                    with patch('apps.fastapi_app.routes.users.require_user_permission') as mock_permission:
                        mock_permission.return_value = Mock(return_value=True)
                        
                        response = self.client.get("/api/v1/users/me/preferences")
                        
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert data["user_id"] == 1
                        assert "preferences" in data
                        assert "settings" in data
                        assert data["preferences"]["theme"] == "dark"

    @pytest.mark.asyncio
    async def test_get_user_preferences_with_defaults(self):
        """Test retrieval of user preferences with default values."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            mock_user.created_at = Mock()
            mock_user.updated_at = Mock()
            
            # Mock UserService
            with patch('apps.fastapi_app.routes.users.UserService') as mock_user_service_class:
                mock_user_service = Mock()
                mock_user_service_class.return_value = mock_user_service
                
                # Mock empty preferences and settings (should use defaults)
                mock_user_service.get_user_preferences.return_value = {}
                mock_user_service.get_user_settings.return_value = {}
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    # Mock permission check
                    with patch('apps.fastapi_app.routes.users.require_user_permission') as mock_permission:
                        mock_permission.return_value = Mock(return_value=True)
                        
                        response = self.client.get("/api/v1/users/me/preferences")
                        
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert data["user_id"] == 1
                        assert "preferences" in data
                        assert "settings" in data
                        # Should have default values
                        assert data["preferences"]["theme"] == "light"
                        assert data["settings"]["privacy_level"] == "standard"

    @pytest.mark.asyncio
    async def test_update_user_preferences_success(self):
        """Test successful update of user preferences."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            mock_user.created_at = Mock()
            
            # Mock UserService
            with patch('apps.fastapi_app.routes.users.UserService') as mock_user_service_class:
                mock_user_service = Mock()
                mock_user_service_class.return_value = mock_user_service
                
                # Mock successful updates
                mock_user_service.update_user_preferences.return_value = True
                mock_user_service.update_user_settings.return_value = True
                
                # Mock updated preferences and settings
                mock_user_service.get_user_preferences.return_value = {
                    "theme": "dark",
                    "language": "en"
                }
                mock_user_service.get_user_settings.return_value = {
                    "privacy_level": "high"
                }
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    # Mock permission check
                    with patch('apps.fastapi_app.routes.users.require_user_permission') as mock_permission:
                        mock_permission.return_value = Mock(return_value=True)
                        
                        response = self.client.put(
                            "/api/v1/users/me/preferences",
                            json=self.test_preferences_update
                        )
                        
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert data["user_id"] == 1
                        assert "preferences" in data
                        assert "settings" in data

    @pytest.mark.asyncio
    async def test_get_user_phone_numbers_success(self):
        """Test successful retrieval of user phone numbers."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock PhoneManagementService
            with patch('apps.fastapi_app.routes.users.PhoneManagementService') as mock_phone_service_class:
                mock_phone_service = Mock()
                mock_phone_service_class.return_value = mock_phone_service
                
                # Mock phone numbers
                mock_phone_numbers = [
                    {
                        "id": 1,
                        "user_id": 1,
                        "phone_number": "+1234567890",
                        "is_primary": True,
                        "is_verified": True,
                        "verification_method": "sms",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ]
                mock_phone_service.get_user_phone_numbers.return_value = mock_phone_numbers
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.get("/api/v1/users/me/phone-numbers")
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert "phone_numbers" in data
                    assert len(data["phone_numbers"]) == 1
                    assert data["phone_numbers"][0]["phone_number"] == "+1234567890"
                    assert data["phone_numbers"][0]["is_primary"] is True

    @pytest.mark.asyncio
    async def test_add_user_phone_number_success(self):
        """Test successful addition of user phone number."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock PhoneManagementService
            with patch('apps.fastapi_app.routes.users.PhoneManagementService') as mock_phone_service_class:
                mock_phone_service = Mock()
                mock_phone_service_class.return_value = mock_phone_service
                
                # Mock successful phone number addition
                mock_new_phone = {
                    "id": 2,
                    "user_id": 1,
                    "phone_number": "+1987654321",
                    "is_primary": False,
                    "is_verified": False,
                    "verification_method": "sms",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
                mock_phone_service.add_user_phone_number.return_value = mock_new_phone
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.post(
                        "/api/v1/users/me/phone-numbers",
                        json=self.test_phone_create
                    )
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["phone_number"] == "+1987654321"
                    assert data["is_primary"] is False
                    assert data["is_verified"] is False

    @pytest.mark.asyncio
    async def test_add_user_phone_number_failure(self):
        """Test failure to add user phone number."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock PhoneManagementService
            with patch('apps.fastapi_app.routes.users.PhoneManagementService') as mock_phone_service_class:
                mock_phone_service = Mock()
                mock_phone_service_class.return_value = mock_phone_service
                
                # Mock failed phone number addition
                mock_phone_service.add_user_phone_number.return_value = None
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.post(
                        "/api/v1/users/me/phone-numbers",
                        json=self.test_phone_create
                    )
                    
                    assert response.status_code == status.HTTP_400_BAD_REQUEST
                    assert "Failed to add phone number" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_user_phone_number_success(self):
        """Test successful update of user phone number."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock PhoneManagementService
            with patch('apps.fastapi_app.routes.users.PhoneManagementService') as mock_phone_service_class:
                mock_phone_service = Mock()
                mock_phone_service_class.return_value = mock_phone_service
                
                # Mock successful phone number update
                mock_updated_phone = {
                    "id": 1,
                    "user_id": 1,
                    "phone_number": "+1234567890",
                    "is_primary": True,
                    "is_verified": True,
                    "verification_method": "sms",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
                mock_phone_service.update_user_phone_number.return_value = mock_updated_phone
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.put(
                        "/api/v1/users/me/phone-numbers/1",
                        json={"is_primary": True}
                    )
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["id"] == 1
                    assert data["is_primary"] is True

    @pytest.mark.asyncio
    async def test_update_user_phone_number_not_found(self):
        """Test update of non-existent phone number."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock PhoneManagementService
            with patch('apps.fastapi_app.routes.users.PhoneManagementService') as mock_phone_service_class:
                mock_phone_service = Mock()
                mock_phone_service_class.return_value = mock_phone_service
                
                # Mock phone number not found
                mock_phone_service.update_user_phone_number.return_value = None
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.put(
                        "/api/v1/users/me/phone-numbers/999",
                        json={"is_primary": True}
                    )
                    
                    assert response.status_code == status.HTTP_404_NOT_FOUND
                    assert "Phone number not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_user_phone_number_success(self):
        """Test successful deletion of user phone number."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock PhoneManagementService
            with patch('apps.fastapi_app.routes.users.PhoneManagementService') as mock_phone_service_class:
                mock_phone_service = Mock()
                mock_phone_service_class.return_value = mock_phone_service
                
                # Mock phone numbers before deletion
                mock_phone_numbers = [
                    {
                        "id": 1,
                        "user_id": 1,
                        "phone_number": "+1234567890",
                        "is_primary": True,
                        "is_verified": True,
                        "verification_method": "sms",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ]
                mock_phone_service.get_user_phone_numbers.return_value = mock_phone_numbers
                mock_phone_service.delete_user_phone_number.return_value = True
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.delete("/api/v1/users/me/phone-numbers/1")
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["success"] is True
                    assert "Phone number deleted successfully" in data["message"]
                    assert data["deleted_phone_number"] == "+1234567890"

    @pytest.mark.asyncio
    async def test_set_primary_phone_number_success(self):
        """Test successful setting of primary phone number."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock PhoneManagementService
            with patch('apps.fastapi_app.routes.users.PhoneManagementService') as mock_phone_service_class:
                mock_phone_service = Mock()
                mock_phone_service_class.return_value = mock_phone_service
                
                # Mock successful primary phone setting
                mock_phone_service.set_primary_phone_number.return_value = True
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.post("/api/v1/users/me/phone-numbers/1/set-primary")
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["success"] is True
                    assert "Primary phone number updated successfully" in data["message"]
                    assert data["phone_id"] == 1

    @pytest.mark.asyncio
    async def test_request_phone_verification_success(self):
        """Test successful phone verification request."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock PhoneManagementService
            with patch('apps.fastapi_app.routes.users.PhoneManagementService') as mock_phone_service_class:
                mock_phone_service = Mock()
                mock_phone_service_class.return_value = mock_phone_service
                
                # Mock phone numbers
                mock_phone_numbers = [
                    {
                        "id": 1,
                        "user_id": 1,
                        "phone_number": "+1234567890",
                        "is_primary": True,
                        "is_verified": False,
                        "verification_method": "sms",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ]
                mock_phone_service.get_user_phone_numbers.return_value = mock_phone_numbers
                mock_phone_service.send_verification_code.return_value = "123456"
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.post(
                        "/api/v1/users/me/phone-numbers/verify",
                        json={"phone_number": "+1234567890"}
                    )
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["success"] is True
                    assert "Verification code sent successfully" in data["message"]
                    assert data["phone_number"] == "+1234567890"
                    assert data["verification_status"] == "pending"

    @pytest.mark.asyncio
    async def test_verify_phone_number_code_success(self):
        """Test successful phone number verification."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock PhoneManagementService
            with patch('apps.fastapi_app.routes.users.PhoneManagementService') as mock_phone_service_class:
                mock_phone_service = Mock()
                mock_phone_service_class.return_value = mock_phone_service
                
                # Mock phone numbers
                mock_phone_numbers = [
                    {
                        "id": 1,
                        "user_id": 1,
                        "phone_number": "+1234567890",
                        "is_primary": True,
                        "is_verified": False,
                        "verification_method": "sms",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ]
                mock_phone_service.get_user_phone_numbers.return_value = mock_phone_numbers
                mock_phone_service.verify_phone_number.return_value = True
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.post(
                        "/api/v1/users/me/phone-numbers/verify-code",
                        json={
                            "phone_number": "+1234567890",
                            "verification_code": "123456"
                        }
                    )
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["success"] is True
                    assert "Phone number verified successfully" in data["message"]
                    assert data["phone_number"] == "+1234567890"
                    assert data["verification_status"] == "verified"

    def test_validation_errors(self):
        """Test various validation errors."""
        # Test invalid user update data
        response = self.client.put("/api/v1/users/me", json={"email": "invalid_email"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test invalid phone number format
        response = self.client.post(
            "/api/v1/users/me/phone-numbers",
            json={"phone_number": "invalid_phone", "is_primary": False}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test invalid verification code format
        response = self.client.post(
            "/api/v1/users/me/phone-numbers/verify-code",
            json={"phone_number": "+1234567890", "verification_code": "invalid"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_authentication_required(self):
        """Test that authentication is required for protected endpoints."""
        # Test without authentication
        response = self.client.get("/api/v1/users/me")
        # This would typically return 401, but depends on middleware implementation
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    @pytest.mark.asyncio
    async def test_permission_required(self):
        """Test that proper permissions are required for certain operations."""
        with patch('apps.fastapi_app.routes.users.get_db') as mock_get_db:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            # Mock current user
            mock_user = Mock(spec=User)
            mock_user.id = 1
            
            # Mock permission check failure
            with patch('apps.fastapi_app.routes.users.require_user_permission') as mock_permission:
                from fastapi import HTTPException
                mock_permission.return_value = Mock(side_effect=HTTPException(
                    status_code=403, detail="Insufficient permissions"
                ))
                
                # Mock get_current_user_db dependency
                with patch('apps.fastapi_app.routes.users.get_current_user_db', return_value=mock_user):
                    response = self.client.get("/api/v1/users/me/preferences")
                    
                    assert response.status_code == status.HTTP_403_FORBIDDEN
                    assert "Insufficient permissions" in response.json()["detail"]
