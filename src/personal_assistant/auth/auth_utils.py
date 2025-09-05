"""
Authentication utilities for common operations.

This module provides utility functions for token extraction,
user context management, and other authentication helpers.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer


class AuthUtils:
    """Utility functions for authentication operations."""

    @staticmethod
    def extract_token_from_header(request: Request) -> Optional[str]:
        """
        Extract JWT token from Authorization header.

        Args:
            request: FastAPI request object

        Returns:
            JWT token string if found, None otherwise
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        # Check if it's a Bearer token
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix

        return None

    @staticmethod
    def extract_token_from_cookie(
        request: Request, cookie_name: str = "access_token"
    ) -> Optional[str]:
        """
        Extract JWT token from cookies.

        Args:
            request: FastAPI request object
            cookie_name: Name of the cookie containing the token

        Returns:
            JWT token string if found, None otherwise
        """
        return request.cookies.get(cookie_name)

    @staticmethod
    def get_user_id_from_token(token_payload: Dict[str, Any]) -> Optional[int]:
        """
        Extract user ID from JWT token payload.

        Args:
            token_payload: Decoded JWT token payload

        Returns:
            User ID if found, None otherwise
        """
        return token_payload.get("user_id")

    @staticmethod
    def get_user_email_from_token(token_payload: Dict[str, Any]) -> Optional[str]:
        """
        Extract user email from JWT token payload.

        Args:
            token_payload: Decoded JWT token payload

        Returns:
            User email if found, None otherwise
        """
        return token_payload.get("email")

    @staticmethod
    def validate_user_context(user_id: int, token_user_id: int) -> None:
        """
        Validate that the token user ID matches the requested user ID.

        Args:
            user_id: Requested user ID
            token_user_id: User ID from token

        Raises:
            HTTPException: If user IDs don't match
        """
        if user_id != token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own data",
            )

    @staticmethod
    def create_user_context(user_id: int, email: str, full_name: str) -> Dict[str, Any]:
        """
        Create a user context dictionary for JWT tokens.

        Args:
            user_id: User's unique identifier
            email: User's email address
            full_name: User's full name

        Returns:
            Dictionary containing user context
        """
        return {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "sub": str(user_id),  # JWT standard subject claim
            "iat": None,  # Will be set by JWT service
            "exp": None,  # Will be set by JWT service
            "type": None,  # Will be set by JWT service
        }


# HTTP Bearer scheme for OpenAPI documentation
security = HTTPBearer(auto_error=False)
