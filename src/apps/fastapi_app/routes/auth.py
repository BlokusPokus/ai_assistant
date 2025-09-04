"""
Authentication routes for user management.

This module provides endpoints for user registration, login,
logout, and token refresh operations.
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.auth.auth_utils import AuthUtils
from personal_assistant.auth.constants import TOKEN_TYPE_REFRESH
from personal_assistant.auth.decorators import require_permission
from personal_assistant.auth.jwt_service import jwt_service
from personal_assistant.auth.password_service import password_service
from personal_assistant.config.settings import settings
from personal_assistant.database.models.auth_tokens import AuthToken
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal

# Create router
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# Set up logging
logger = logging.getLogger(__name__)

# Pydantic models for request/response


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None

    @validator("phone_number")
    def validate_phone_number(cls, v):
        if v is not None:
            # Basic phone number validation - remove spaces and dashes
            v = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not v.startswith("+") and not v.isdigit():
                raise ValueError(
                    "Phone number must start with + or contain only digits"
                )
            if len(v) < 10 or len(v) > 15:
                raise ValueError("Phone number must be between 10 and 15 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # OAuth 2.0 standard token type  # nosec B106
    expires_in: int


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # OAuth 2.0 standard token type  # nosec B106
    expires_in: int
    user: UserResponse
    mfa_required: bool = False
    mfa_setup_required: bool = False


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str


class EmailVerification(BaseModel):
    token: str


# Dependency to get database session


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


# Dependency to get current user (for protected endpoints)


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User object if authenticated

    Raises:
        HTTPException: If not authenticated
    """
    if not hasattr(request.state, "authenticated") or not request.state.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    user_id = request.state.user_id
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    logger.info(f"Starting user registration for email: {user_data.email}")
    try:
        # Check if user already exists
        logger.debug("Checking if user already exists")
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(f"User with email {user_data.email} already exists")
            raise HTTPException(status_code=400, detail="Email already registered")

        # Validate password strength (this will raise HTTPException if invalid)
        logger.debug("Validating password strength")
        password_service._validate_password(user_data.password)

        # Hash password
        logger.debug("Hashing password")
        hashed_password = password_service.hash_password(user_data.password)

        # Generate verification token
        logger.debug("Generating verification token")
        verification_token = secrets.token_urlsafe(32)

        # Create new user
        logger.debug("Creating new user object")
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,  # Email verification required
            verification_token=verification_token,
            failed_login_attempts=0,
        )

        logger.debug("Adding user to database session")
        db.add(new_user)
        logger.debug("Committing user to database")
        await db.commit()
        logger.debug("Refreshing user from database")
        await db.refresh(new_user)

        # TODO: Send verification email
        # For now, return the verification token (in production, send via email)
        logger.info(f"Successfully registered user with ID: {new_user.id}")

        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            created_at=new_user.created_at.isoformat(),
        )

    except HTTPException as e:
        logger.warning(f"HTTPException during registration: {e.detail}")
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during user registration: {str(e)}", exc_info=True
        )
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to register user")


@router.post("/login", response_model=AuthResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT tokens."""
    try:
        # Find user by email
        result = await db.execute(select(User).where(User.email == user_data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Check if account is active
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account is deactivated")

        # Check if email is verified (optional for now)
        if not user.is_verified:
            # Allow login but warn about verification
            pass

        # Verify password
        if not password_service.verify_password(
            user_data.password, user.hashed_password
        ):
            # Increment failed login attempts
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            user.updated_at = datetime.utcnow()

            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                await db.commit()
                raise HTTPException(
                    status_code=401,
                    detail="Account locked due to too many failed attempts. Try again in 30 minutes.",
                )

            await db.commit()
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()

        # Generate tokens
        access_token = jwt_service.create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            }
        )
        refresh_token = jwt_service.create_refresh_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            }
        )

        # Store refresh token in database
        auth_token = AuthToken(
            user_id=user.id,
            token=refresh_token,
            token_type=TOKEN_TYPE_REFRESH,
            expires_at=datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            is_revoked=False,
        )

        db.add(auth_token)
        await db.commit()

        # Set tokens in cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",  # OAuth 2.0 standard token type  # nosec B106
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at.isoformat(),
            ),
            mfa_required=False,
            mfa_setup_required=False,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh, response: Response, db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Args:
        token_data: Refresh token data
        response: FastAPI response object for cookies
        db: Database session

    Returns:
        New JWT access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        # Verify refresh token
        payload = jwt_service.verify_refresh_token(token_data.refresh_token)
        user_id = AuthUtils.get_user_id_from_token(payload)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Check if refresh token exists in database
        stored_token = await db.execute(
            select(AuthToken).where(
                AuthToken.user_id == user_id,
                AuthToken.token == token_data.refresh_token,
            )
        )
        stored_token = stored_token.scalar_one_or_none()

        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Get user information
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        # Create new access token
        user_context = AuthUtils.create_user_context(
            user_id=user.id, email=user.email, full_name=user.full_name
        )

        new_access_token = jwt_service.create_access_token(user_context)

        # Update cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=jwt_service.access_token_expire_minutes * 60,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=token_data.refresh_token,
            expires_in=jwt_service.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user and invalidate tokens.

    Args:
        response: FastAPI response object for cookies
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    # Remove refresh token from database
    await db.execute(delete(AuthToken).where(AuthToken.user_id == current_user.id))
    await db.commit()

    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
@require_permission("user", "read")
async def get_current_user_info(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at.isoformat(),
    )


@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    request: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    """Request a password reset for a user."""
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal if email exists or not
            return {
                "message": "If the email exists, a password reset link has been sent"
            }

        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.utcnow() + timedelta(hours=24)

        # Update user with reset token
        user.password_reset_token = reset_token
        user.password_reset_expires = reset_expires
        user.updated_at = datetime.utcnow()

        await db.commit()

        # TODO: Send email with reset link
        # For now, just return the token (in production, send via email)
        return {
            "message": "Password reset link sent to your email",
            "reset_token": reset_token,  # Remove this in production
            "expires_at": reset_expires.isoformat(),
        }

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to process password reset request"
        )


@router.post("/reset-password", response_model=dict)
async def reset_password(request: PasswordReset, db: AsyncSession = Depends(get_db)):
    """Reset password using reset token."""
    try:
        # Find user with valid reset token
        result = await db.execute(
            select(User).where(
                User.password_reset_token == request.token,
                User.password_reset_expires > datetime.utcnow(),
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )

        # Validate new password (this will raise HTTPException if invalid)
        password_service._validate_password(request.new_password)

        # Hash new password and clear reset token
        user.hashed_password = password_service.hash_password(request.new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.updated_at = datetime.utcnow()

        await db.commit()

        return {"message": "Password reset successfully"}

    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to reset password")


@router.post("/verify-email", response_model=dict)
async def verify_email(request: EmailVerification, db: AsyncSession = Depends(get_db)):
    """Verify user email using verification token."""
    try:
        # Find user with verification token
        result = await db.execute(
            select(User).where(User.verification_token == request.token)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=400, detail="Invalid verification token")

        if user.is_verified:
            return {"message": "Email already verified"}

        # Mark email as verified and clear token
        user.is_verified = True
        user.verification_token = None
        user.updated_at = datetime.utcnow()

        await db.commit()

        return {"message": "Email verified successfully"}

    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to verify email")


@router.post("/resend-verification", response_model=dict)
async def resend_verification(
    request: PasswordResetRequest,  # Reuse email model
    db: AsyncSession = Depends(get_db),
):
    """Resend email verification token."""
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, a verification link has been sent"}

        if user.is_verified:
            return {"message": "Email is already verified"}

        # Generate new verification token
        verification_token = secrets.token_urlsafe(32)
        user.verification_token = verification_token
        user.updated_at = datetime.utcnow()

        await db.commit()

        # TODO: Send email with verification link
        # For now, just return the token (in production, send via email)
        return {
            "message": "Verification link sent to your email",
            "verification_token": verification_token,  # Remove this in production
        }

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to resend verification")
