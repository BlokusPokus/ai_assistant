"""
User management API routes.

This module provides REST API endpoints for user management including
CRUD operations, profile updates, and preferences management.
"""

import logging
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.database.models.users import User
from personal_assistant.auth.decorators import require_permission
from apps.fastapi_app.routes.auth import get_current_user
from apps.fastapi_app.models.users import (
    UserResponse, UserUpdateRequest, UserPreferencesResponse,
    UserPreferencesUpdateRequest, UserListResponse, UserCreateRequest,
    UserDeleteRequest
)
from apps.fastapi_app.services.user_service import UserService

# Create router
router = APIRouter(prefix="/api/v1/users", tags=["users"])

logger = logging.getLogger(__name__)


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


# Current user endpoints (user can access their own data)
@router.get("/me", response_model=UserResponse)
@require_permission("user", "read")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.

    Returns the profile information for the currently authenticated user.
    """
    try:
        return UserResponse.model_validate(current_user)
    except Exception as e:
        logger.error(f"Error getting current user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.put("/me", response_model=UserResponse)
@require_permission("user", "update")
async def update_current_user_profile(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile.

    Allows the authenticated user to update their own profile information.
    """
    try:
        user_service = UserService(db)

        # Convert Pydantic model to dict, excluding None values
        update_data = user_update.model_dump(exclude_unset=True)

        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid data provided for update"
            )

        updated_user = await user_service.update_user(
            current_user.id, update_data
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )

        return UserResponse.model_validate(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating current user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me/preferences", response_model=UserPreferencesResponse)
@require_permission("user", "read")
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user preferences.

    Returns the preferences for the currently authenticated user.
    """
    try:
        user_service = UserService(db)
        preferences = await user_service.get_user_preferences(current_user.id)
        settings = await user_service.get_user_settings(current_user.id)

        return UserPreferencesResponse(
            user_id=current_user.id,
            preferences=preferences,
            settings=settings,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user preferences"
        )


@router.put("/me/preferences", response_model=UserPreferencesResponse)
@require_permission("user", "update")
async def update_user_preferences(
    preferences: UserPreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user preferences.

    Allows the authenticated user to update their preferences and settings.
    """
    try:
        user_service = UserService(db)

        if preferences.preferences:
            success = await user_service.update_user_preferences(
                current_user.id, preferences.preferences
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update preferences"
                )

        if preferences.settings:
            success = await user_service.update_user_settings(
                current_user.id, preferences.settings
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update settings"
                )

        # Get updated preferences and settings
        updated_preferences = await user_service.get_user_preferences(current_user.id)
        updated_settings = await user_service.get_user_settings(current_user.id)

        return UserPreferencesResponse(
            user_id=current_user.id,
            preferences=updated_preferences,
            settings=updated_settings,
            created_at=current_user.created_at,
            updated_at=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me/settings", response_model=UserPreferencesResponse)
@require_permission("user", "read")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user settings.

    Returns the settings for the currently authenticated user.
    """
    try:
        user_service = UserService(db)
        settings = await user_service.get_user_settings(current_user.id)

        return UserPreferencesResponse(
            user_id=current_user.id,
            preferences={},  # Empty preferences for this endpoint
            settings=settings,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
    except Exception as e:
        logger.error(f"Error getting user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user settings"
        )


@router.put("/me/settings", response_model=UserPreferencesResponse)
@require_permission("user", "update")
async def update_user_settings(
    preferences: UserPreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user settings.

    Allows the authenticated user to update their settings.
    """
    try:
        user_service = UserService(db)

        if preferences.settings:
            success = await user_service.update_user_settings(
                current_user.id, preferences.settings
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update settings"
                )

        # Get updated settings
        updated_settings = await user_service.get_user_settings(current_user.id)

        return UserPreferencesResponse(
            user_id=current_user.id,
            preferences={},  # Empty preferences for this endpoint
            settings=updated_settings,
            created_at=current_user.created_at,
            updated_at=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Error updating user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Admin-only endpoints
@router.get("/", response_model=UserListResponse)
@require_permission("users", "read")
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Maximum number of users to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users (admin only).

    Returns a paginated list of users with total count.
    """
    try:
        user_service = UserService(db)
        users, total = await user_service.list_users(skip=skip, limit=limit)

        user_responses = [UserResponse.model_validate(user) for user in users]

        return UserListResponse(
            users=user_responses,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users list"
        )


@router.get("/{user_id}", response_model=UserResponse)
@require_permission("users", "read")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (admin only).

    Returns detailed information about a specific user.
    """
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{user_id}", response_model=UserResponse)
@require_permission("users", "update")
async def update_user(
    user_id: int,
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user by ID (admin only).

    Allows administrators to update any user's profile information.
    """
    try:
        user_service = UserService(db)

        # Check if user exists
        existing_user = await user_service.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Convert Pydantic model to dict, excluding None values
        update_data = user_update.model_dump(exclude_unset=True)
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid data provided for update"
            )

        updated_user = await user_service.update_user(user_id, update_data)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )

        return UserResponse.model_validate(updated_user)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{user_id}")
@require_permission("users", "delete")
async def deactivate_user(
    user_id: int,
    delete_request: UserDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate user account (admin only).

    Deactivates a user account instead of permanently deleting it.
    """
    try:
        user_service = UserService(db)

        # Check if user exists
        existing_user = await user_service.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent self-deactivation
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )

        success = await user_service.deactivate_user(
            user_id,
            reason=delete_request.deactivate_reason
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate user"
            )

        return {
            "message": "User deactivated successfully",
            "user_id": user_id,
            "deactivated_at": datetime.now(timezone.utc)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/", response_model=UserResponse)
@require_permission("users", "create")
async def create_user(
    user_create: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user (admin only).

    Allows administrators to create new user accounts.
    """
    try:
        user_service = UserService(db)

        # Check if user with email already exists
        existing_user = await user_service.get_user_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Create user data dictionary
        user_data = {
            'email': user_create.email,
            'full_name': user_create.full_name,
            'password': user_create.password,
            'is_active': user_create.is_active,
            'is_verified': user_create.is_verified
        }

        new_user = await user_service.create_user(user_data)

        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        return UserResponse.model_validate(new_user)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{user_id}/stats")
@require_permission("users", "read")
async def get_user_stats(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user statistics (admin only).

    Returns statistics and metadata about a specific user.
    """
    try:
        user_service = UserService(db)

        # Check if user exists
        existing_user = await user_service.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        stats = await user_service.get_user_stats(user_id)

        return {
            "user_id": user_id,
            "stats": stats,
            "retrieved_at": datetime.now(timezone.utc)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
