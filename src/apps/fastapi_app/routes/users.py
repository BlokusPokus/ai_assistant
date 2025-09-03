"""
User management API routes.

This module provides REST API endpoints for user management including
CRUD operations, profile updates, and preferences management.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.middleware.auth import get_current_user
from apps.fastapi_app.models.phone_management import (
    PhoneNumberCreate,
    PhoneNumberDeleteResponse,
    PhoneNumberListResponse,
    PhoneNumberResponse,
    PhoneNumberUpdate,
    PhoneNumberVerificationCode,
    PhoneNumberVerificationRequest,
    PhoneNumberVerificationResponse,
)
from apps.fastapi_app.models.users import (
    UserCreateRequest,
    UserDeleteRequest,
    UserListResponse,
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
    UserPublicResponse,
    UserResponse,
    UserUpdateRequest,
)
from apps.fastapi_app.services.phone_management_service import PhoneManagementService
from apps.fastapi_app.services.user_service import UserService
from personal_assistant.auth.decorators import require_permission
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal

# Create router
router = APIRouter(prefix="/api/v1/users", tags=["users"])

logger = logging.getLogger(__name__)


def get_default_preferences() -> Dict[str, Any]:
    """Get default preferences for new users."""
    return {
        "theme": "light",
        "language": "en",
        "notifications": True,
        "timezone": "UTC",
    }


def get_default_settings() -> Dict[str, Any]:
    """Get default settings for new users."""
    return {
        "privacy_level": "standard",
        "data_sharing": False,
        "auto_save": True,
        "session_timeout": 3600,
    }


def require_user_permission(resource_type: str, action: str):
    """Create a dependency that checks user permission."""

    async def _check_permission(
        current_user: User = Depends(get_current_user_db),
        db: AsyncSession = Depends(get_db),
    ) -> bool:
        """Check if current user has permission for specific resource and action."""
        try:
            from personal_assistant.auth.permission_service import PermissionService

            permission_service = PermissionService(db)
            has_permission = await permission_service.check_permission(
                user_id=current_user.id, resource_type=resource_type, action=action
            )

            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {resource_type}:{action}",
                )

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error checking permission {resource_type}:{action} for user {current_user.id}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Permission check failed",
            )

    return _check_permission


async def get_db():
    """Get database session."""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def get_current_user_db(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from database."""
    if not hasattr(request.state, "authenticated") or not request.state.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    user_id = request.state.user_id
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# Current user endpoints (user can access their own data)
@router.get("/me", response_model=UserPublicResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user_db)):
    """
    Get current user profile.

    Returns the profile information for the currently authenticated user.
    """
    try:
        return UserPublicResponse(
            id=current_user.id,
            email=current_user.email,
            phone_number=getattr(current_user, "phone_number", None),
            full_name=getattr(current_user, "full_name", None),
            is_active=getattr(current_user, "is_active", True),
            is_verified=getattr(current_user, "is_verified", False),
            last_login=getattr(current_user, "last_login", None),
            created_at=current_user.created_at,
            updated_at=getattr(current_user, "updated_at", current_user.created_at),
        )
    except Exception as e:
        logger.error(f"Error getting current user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile",
        )


@router.put("/me", response_model=UserPublicResponse)
async def update_current_user_profile(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_user_permission("user", "update")),
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
                detail="No valid data provided for update",
            )

        updated_user = await user_service.update_user(current_user.id, update_data)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile",
            )

        return UserPublicResponse.model_validate(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating current user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me/preferences", response_model=UserPreferencesResponse)
# @require_permission("user", "read")  # Disabled - doesn't work with FastAPI DI
async def get_user_preferences(
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_user_permission("user", "read")),
):
    """
    Get current user preferences.

    Returns the preferences for the currently authenticated user.
    """
    try:
        user_service = UserService(db)

        # Get preferences and settings with fallback to defaults
        try:
            preferences = await user_service.get_user_preferences(current_user.id)
            logger.info(
                f"Retrieved preferences for user {current_user.id}: {preferences}"
            )
        except Exception as e:
            logger.error(f"Error getting preferences: {e}")
            preferences = {}

        try:
            settings = await user_service.get_user_settings(current_user.id)
            logger.info(f"Retrieved settings for user {current_user.id}: {settings}")
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            settings = {}

        # Provide default preferences and settings for new users
        if not preferences:
            preferences = get_default_preferences()
            logger.info(f"Using default preferences for user {current_user.id}")

        if not settings:
            settings = get_default_settings()
            logger.info(f"Using default settings for user {current_user.id}")

        # Ensure we have valid datetime values
        created_at = getattr(current_user, "created_at", None)
        updated_at = getattr(current_user, "updated_at", None)

        if created_at is None:
            logger.warning(f"User {current_user.id} missing created_at")
            created_at = datetime.now(timezone.utc)
        if updated_at is None:
            logger.warning(f"User {current_user.id} missing updated_at")
            updated_at = datetime.now(timezone.utc)

        return UserPreferencesResponse(
            user_id=current_user.id,
            preferences=preferences,
            settings=settings,
            created_at=created_at,
            updated_at=updated_at,
        )
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user preferences: {str(e)}",
        )


@router.put("/me/preferences", response_model=UserPreferencesResponse)
# @require_permission("user", "update")  # Disabled - doesn't work with FastAPI DI
async def update_user_preferences(
    preferences: UserPreferencesUpdateRequest,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_user_permission("user", "update")),
):
    """
    Update current user preferences.

    Allows the authenticated user to update their preferences and settings.
    """
    try:
        user_service = UserService(db)

        if preferences.preferences:
            try:
                success = await user_service.update_user_preferences(
                    current_user.id, preferences.preferences
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update preferences",
                    )
                logger.info(
                    f"Updated preferences for user {current_user.id}: {preferences.preferences}"
                )
            except Exception as e:
                logger.error(f"Error updating preferences: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update preferences: {str(e)}",
                )

        if preferences.settings:
            try:
                success = await user_service.update_user_settings(
                    current_user.id, preferences.settings
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update settings",
                    )
                logger.info(
                    f"Updated settings for user {current_user.id}: {preferences.settings}"
                )
            except Exception as e:
                logger.error(f"Error updating settings: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update settings: {str(e)}",
                )

        # Get updated preferences and settings
        try:
            updated_preferences = await user_service.get_user_preferences(
                current_user.id
            )
            updated_settings = await user_service.get_user_settings(current_user.id)
        except Exception as e:
            logger.error(f"Error getting updated data: {e}")
            updated_preferences = {}
            updated_settings = {}

        # Check if user has required attributes
        created_at = getattr(current_user, "created_at", None)
        if created_at is None:
            created_at = datetime.now(timezone.utc)

        return UserPreferencesResponse(
            user_id=current_user.id,
            preferences=updated_preferences,
            settings=updated_settings,
            created_at=created_at,
            updated_at=datetime.now(timezone.utc),
        )
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/me/settings", response_model=UserPreferencesResponse)
@require_permission("user", "read")
async def get_user_settings(
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user settings.

    Returns the settings for the currently authenticated user.
    """
    try:
        user_service = UserService(db)

        try:
            settings = await user_service.get_user_settings(current_user.id)
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            settings = {}

        # Provide default settings for new users
        if not settings:
            settings = get_default_settings()
            logger.info(f"Using default settings for user {current_user.id}")

        # Ensure we have valid datetime values
        created_at = getattr(current_user, "created_at", None)
        updated_at = getattr(current_user, "updated_at", None)

        if created_at is None:
            created_at = datetime.now(timezone.utc)
        if updated_at is None:
            updated_at = datetime.now(timezone.utc)

        return UserPreferencesResponse(
            user_id=current_user.id,
            preferences={},  # Empty preferences for this endpoint
            settings=settings,
            created_at=created_at,
            updated_at=updated_at,
        )
    except Exception as e:
        logger.error(f"Error getting user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user settings",
        )


@router.put("/me/settings", response_model=UserPreferencesResponse)
@require_permission("user", "update")
async def update_user_settings(
    preferences: UserPreferencesUpdateRequest,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
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
                    detail="Failed to update settings",
                )

        # Get updated settings
        updated_settings = await user_service.get_user_settings(current_user.id)

        return UserPreferencesResponse(
            user_id=current_user.id,
            preferences={},  # Empty preferences for this endpoint
            settings=updated_settings,
            created_at=current_user.created_at,
            updated_at=datetime.now(timezone.utc),
        )
    except Exception as e:
        logger.error(f"Error updating user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Admin-only endpoints
@router.get("/", response_model=UserListResponse)
@require_permission("users", "read")
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of users to return"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
            users=user_responses, total=total, skip=skip, limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users list",
        )


@router.get("/{user_id}", response_model=UserResponse)
@require_permission("users", "read")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{user_id}", response_model=UserResponse)
@require_permission("users", "update")
async def update_user(
    user_id: int,
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Convert Pydantic model to dict, excluding None values
        update_data = user_update.model_dump(exclude_unset=True)
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid data provided for update",
            )

        updated_user = await user_service.update_user(user_id, update_data)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile",
            )

        return UserResponse.model_validate(updated_user)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{user_id}")
@require_permission("users", "delete")
async def deactivate_user(
    user_id: int,
    delete_request: UserDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Prevent self-deactivation
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account",
            )

        success = await user_service.deactivate_user(
            user_id, reason=delete_request.deactivate_reason
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate user",
            )

        return {
            "message": "User deactivated successfully",
            "user_id": user_id,
            "deactivated_at": datetime.now(timezone.utc),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/", response_model=UserResponse)
@require_permission("users", "create")
async def create_user(
    user_create: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
                detail="User with this email already exists",
            )

        # Create user data dictionary
        user_data = {
            "email": user_create.email,
            "full_name": user_create.full_name,
            "password": user_create.password,
            "is_active": user_create.is_active,
            "is_verified": user_create.is_verified,
        }

        new_user = await user_service.create_user(user_data)

        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            )

        return UserResponse.model_validate(new_user)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{user_id}/stats")
@require_permission("users", "read")
async def get_user_stats(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        stats = await user_service.get_user_stats(user_id)

        return {
            "user_id": user_id,
            "stats": stats,
            "retrieved_at": datetime.now(timezone.utc),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Phone Management Routes
@router.get("/me/phone-numbers", response_model=PhoneNumberListResponse)
async def get_user_phone_numbers(
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's phone numbers.

    Returns all phone numbers associated with the authenticated user.
    """
    try:
        phone_service = PhoneManagementService(db)
        phone_numbers = await phone_service.get_user_phone_numbers(current_user.id)

        # Find primary phone ID
        primary_phone_id = None
        for phone in phone_numbers:
            if phone["is_primary"]:
                # If ID is 0, it means it's the primary phone from users table
                # We'll set primary_phone_id to None since it doesn't have a mapping record
                if phone["id"] != 0:
                    primary_phone_id = phone["id"]
                break

        return PhoneNumberListResponse(
            phone_numbers=[
                PhoneNumberResponse(
                    # ID is already 0 for primary phone from users table
                    id=phone["id"],
                    user_id=phone["user_id"],
                    phone_number=phone["phone_number"],
                    is_primary=phone["is_primary"],
                    is_verified=phone["is_verified"],
                    verification_method=phone["verification_method"],
                    created_at=phone["created_at"],
                    updated_at=phone["updated_at"],
                )
                for phone in phone_numbers
            ],
            total_count=len(phone_numbers),
            primary_phone_id=primary_phone_id,
        )
    except Exception as e:
        logger.error(f"Error getting phone numbers for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve phone numbers",
        )


@router.post("/me/phone-numbers", response_model=PhoneNumberResponse)
async def add_user_phone_number(
    phone_data: PhoneNumberCreate,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new phone number for current user.

    Allows the authenticated user to add a new phone number to their profile.
    """
    try:
        phone_service = PhoneManagementService(db)

        new_phone = await phone_service.add_user_phone_number(
            user_id=current_user.id,
            phone_number=phone_data.phone_number,
            is_primary=phone_data.is_primary,
            verification_method="sms",
        )

        if not new_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add phone number. It may already exist or be invalid.",
            )

        return PhoneNumberResponse(
            id=new_phone["id"],
            user_id=new_phone["user_id"],
            phone_number=new_phone["phone_number"],
            is_primary=new_phone["is_primary"],
            is_verified=new_phone["is_verified"],
            verification_method=new_phone["verification_method"],
            created_at=new_phone["created_at"],
            updated_at=new_phone["updated_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding phone number for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add phone number",
        )


@router.put("/me/phone-numbers/{phone_id}", response_model=PhoneNumberResponse)
async def update_user_phone_number(
    phone_id: int,
    phone_data: PhoneNumberUpdate,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user's phone number.

    Allows the authenticated user to update their phone number information.
    """
    try:
        phone_service = PhoneManagementService(db)

        # Convert Pydantic model to dict, excluding None values
        update_data = phone_data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid data provided for update",
            )

        updated_phone = await phone_service.update_user_phone_number(
            user_id=current_user.id, phone_id=phone_id, updates=update_data
        )

        if not updated_phone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found or you don't have permission to update it",
            )

        return PhoneNumberResponse(
            id=updated_phone["id"],
            user_id=updated_phone["user_id"],
            phone_number=updated_phone["phone_number"],
            is_primary=updated_phone["is_primary"],
            is_verified=updated_phone["is_verified"],
            verification_method=updated_phone["verification_method"],
            created_at=updated_phone["created_at"],
            updated_at=updated_phone["updated_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating phone number {phone_id} for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update phone number",
        )


@router.delete("/me/phone-numbers/{phone_id}", response_model=PhoneNumberDeleteResponse)
async def delete_user_phone_number(
    phone_id: int,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user's phone number.

    Allows the authenticated user to remove a phone number from their profile.
    """
    try:
        phone_service = PhoneManagementService(db)

        # Get phone number before deletion for response
        phone_numbers = await phone_service.get_user_phone_numbers(current_user.id)
        phone_to_delete = next((p for p in phone_numbers if p["id"] == phone_id), None)

        if not phone_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found or you don't have permission to delete it",
            )

        success = await phone_service.delete_user_phone_number(
            user_id=current_user.id, phone_id=phone_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete phone number",
            )

        # Get remaining phone count
        remaining_phones = await phone_service.get_user_phone_numbers(current_user.id)

        return PhoneNumberDeleteResponse(
            success=True,
            message="Phone number deleted successfully",
            deleted_phone_number=phone_to_delete["phone_number"],
            remaining_phone_count=len(remaining_phones),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting phone number {phone_id} for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete phone number",
        )


@router.post("/me/phone-numbers/{phone_id}/set-primary")
async def set_primary_phone_number(
    phone_id: int,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
):
    """
    Set a phone number as primary for current user.

    Allows the authenticated user to set a phone number as their primary contact.
    """
    try:
        phone_service = PhoneManagementService(db)

        success = await phone_service.set_primary_phone_number(
            user_id=current_user.id, phone_id=phone_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found or you don't have permission to modify it",
            )

        return {
            "success": True,
            "message": "Primary phone number updated successfully",
            "phone_id": phone_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error setting primary phone {phone_id} for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set primary phone number",
        )


@router.post("/me/phone-numbers/verify", response_model=PhoneNumberVerificationResponse)
async def request_phone_verification(
    verification_request: PhoneNumberVerificationRequest,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
):
    """
    Request verification code for a phone number.

    Sends a verification code via SMS to the specified phone number.
    """
    try:
        phone_service = PhoneManagementService(db)

        # Check if phone number belongs to user
        phone_numbers = await phone_service.get_user_phone_numbers(current_user.id)
        phone_exists = any(
            p["phone_number"] == verification_request.phone_number
            for p in phone_numbers
        )

        if not phone_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found in your profile",
            )

        # Send verification code
        verification_code = await phone_service.send_verification_code(
            user_id=current_user.id, phone_number=verification_request.phone_number
        )

        if not verification_code:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification code",
            )

        return PhoneNumberVerificationResponse(
            success=True,
            message="Verification code sent successfully",
            phone_number=verification_request.phone_number,
            verification_status="pending",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting verification for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request verification",
        )


@router.post(
    "/me/phone-numbers/verify-code", response_model=PhoneNumberVerificationResponse
)
async def verify_phone_number_code(
    verification_code: PhoneNumberVerificationCode,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify phone number with verification code.

    Verifies a phone number using the provided verification code.
    """
    try:
        phone_service = PhoneManagementService(db)

        # Check if phone number belongs to user
        phone_numbers = await phone_service.get_user_phone_numbers(current_user.id)
        phone_exists = any(
            p["phone_number"] == verification_code.phone_number for p in phone_numbers
        )

        if not phone_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found in your profile",
            )

        # Verify the code
        success = await phone_service.verify_phone_number(
            user_id=current_user.id,
            phone_number=verification_code.phone_number,
            verification_code=verification_code.verification_code,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code or verification failed",
            )

        return PhoneNumberVerificationResponse(
            success=True,
            message="Phone number verified successfully",
            phone_number=verification_code.phone_number,
            verification_status="verified",
            expires_at=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying phone number for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify phone number",
        )
