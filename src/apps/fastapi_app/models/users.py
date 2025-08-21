"""
User management API models.

This module provides Pydantic models for user management API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, validator, ConfigDict


class UserResponse(BaseModel):
    """Response model for user information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserUpdateRequest(BaseModel):
    """Request model for updating user profile."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            # Basic email validation is handled by EmailStr
            pass
        return v

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Name cannot be empty")
            if len(v) > 100:
                raise ValueError("Name too long (max 100 characters)")
        return v.strip() if v else v


class UserPreferencesResponse(BaseModel):
    """Response model for user preferences."""
    user_id: int
    preferences: Dict[str, Any]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class UserPreferencesUpdateRequest(BaseModel):
    """Request model for updating user preferences."""
    preferences: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None

    @validator('preferences', 'settings')
    def validate_dict_values(cls, v):
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError("Must be a dictionary")
            # Validate that values are JSON serializable
            for key, value in v.items():
                if not isinstance(key, str):
                    raise ValueError("All keys must be strings")
                # Basic validation for common types
                if not isinstance(value, (str, int, float, bool, type(None))):
                    if isinstance(value, (list, dict)):
                        # Recursively validate nested structures
                        if isinstance(value, list):
                            for item in value:
                                if not isinstance(item, (str, int, float, bool, type(None))):
                                    raise ValueError(
                                        f"Invalid value type in list: {type(item)}")
                        else:  # dict
                            for k, val in value.items():
                                if not isinstance(k, str):
                                    raise ValueError(
                                        "All nested keys must be strings")
                                if not isinstance(val, (str, int, float, bool, type(None))):
                                    raise ValueError(
                                        f"Invalid nested value type: {type(val)}")
                    else:
                        raise ValueError(f"Invalid value type: {type(value)}")
        return v


class UserListResponse(BaseModel):
    """Response model for user list."""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class UserCreateRequest(BaseModel):
    """Request model for creating a new user (admin only)."""
    email: EmailStr
    full_name: str
    password: str
    is_active: bool = True
    is_verified: bool = False

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password too long (max 128 characters)")
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Full name cannot be empty")
        if len(v) > 100:
            raise ValueError("Full name too long (max 100 characters)")
        return v.strip()


class UserDeleteRequest(BaseModel):
    """Request model for deactivating a user."""
    deactivate_reason: Optional[str] = None
    transfer_data_to: Optional[int] = None  # User ID to transfer data to
