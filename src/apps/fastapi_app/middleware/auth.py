"""
Authentication middleware for FastAPI.

This middleware validates JWT tokens and injects user context
into requests for protected endpoints.
"""

import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from personal_assistant.auth.jwt_service import jwt_service
from personal_assistant.auth.auth_utils import AuthUtils


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication and user context injection."""

    def __init__(self, app, exclude_paths: Optional[list] = None):
        """
        Initialize authentication middleware.

        Args:
            app: FastAPI application instance
            exclude_paths: List of paths to exclude from authentication
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/webhook/twilio",  # Keep Twilio webhook accessible
            "/twilio/sms",      # Keep Twilio SMS webhook accessible
            "/sms-router/webhook/sms",  # SMS Router webhook for Twilio
            "/sms-router/webhook/health",  # SMS Router health check
        ]

    async def dispatch(self, request: Request, call_next):
        """
        Process the request through authentication middleware.

        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint function

        Returns:
            Response from the next middleware or endpoint
        """
        # Check if path should be excluded from authentication
        if self._should_exclude_path(request.url.path):
            return await call_next(request)

        # Extract token from request
        token = self._extract_token(request)

        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"},
                headers={"WWW-Authenticate": "Bearer"}
            )

        try:
            # Validate token and get user context
            payload = jwt_service.verify_access_token(token)
            user_id = AuthUtils.get_user_id_from_token(payload)
            email = AuthUtils.get_user_email_from_token(payload)
            full_name = payload.get("full_name")

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user information"
                )

            # Inject user context into request state
            request.state.user_id = user_id
            request.state.user_email = email
            request.state.user_full_name = full_name
            request.state.authenticated = True

            # Add user info to request headers for downstream services
            request.headers.__dict__["_list"].extend([
                (b"x-user-id", str(user_id).encode()),
                (b"x-user-email", email.encode() if email else b""),
                (b"x-user-full-name", full_name.encode() if full_name else b""),
                (b"x-authenticated", b"true")
            ])

            # Process the request
            response = await call_next(request)
            return response

        except HTTPException:
            # Re-raise HTTP exceptions (like token expired)
            raise
        except Exception as e:
            # Handle other authentication errors
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication failed"},
                headers={"WWW-Authenticate": "Bearer"}
            )

    def _should_exclude_path(self, path: str) -> bool:
        """
        Check if a path should be excluded from authentication.

        Args:
            path: Request path

        Returns:
            True if path should be excluded, False otherwise
        """
        for exclude_path in self.exclude_paths:
            if path == exclude_path or path.startswith(exclude_path + "/"):
                return True
        return False

    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from request headers or cookies.

        Args:
            request: FastAPI request object

        Returns:
            JWT token string if found, None otherwise
        """
        # Try to get token from Authorization header
        token = AuthUtils.extract_token_from_header(request)
        if token:
            return token

        # Try to get token from cookies
        token = AuthUtils.extract_token_from_cookie(request)
        if token:
            return token

        return None


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Get current authenticated user from request state.

    Args:
        request: FastAPI request object

    Returns:
        Dictionary containing user information

    Raises:
        HTTPException: If user is not authenticated
    """
    if not hasattr(request.state, 'authenticated') or not request.state.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return {
        "user_id": request.state.user_id,
        "email": request.state.user_email,
        "full_name": request.state.user_full_name
    }
