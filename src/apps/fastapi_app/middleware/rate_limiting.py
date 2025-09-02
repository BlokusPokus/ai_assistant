"""
Rate limiting middleware for FastAPI.

This middleware provides rate limiting for authentication endpoints
and other sensitive operations to prevent abuse.
"""

import time
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from personal_assistant.config.settings import settings


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting sensitive operations."""

    def __init__(self, app):
        """Initialize rate limiting middleware."""
        super().__init__(app)
        self.rate_limits = {
            "login": {
                "max_attempts": getattr(settings, 'RATE_LIMIT_LOGIN_ATTEMPTS', 5),
                "window_minutes": getattr(settings, 'RATE_LIMIT_LOGIN_WINDOW_MINUTES', 15),
                "attempts": {}  # IP -> [(timestamp, count), ...]
            },
            "token_refresh": {
                "max_attempts": getattr(settings, 'RATE_LIMIT_TOKEN_REFRESH_PER_HOUR', 10),
                "window_minutes": 60,
                "attempts": {}  # user_id -> [(timestamp, count), ...]
            },
            "registration": {
                "max_attempts": getattr(settings, 'RATE_LIMIT_REGISTRATION_PER_HOUR', 3),
                "window_minutes": 60,
                "attempts": {}  # IP -> [(timestamp, count), ...]
            }
        }

    async def dispatch(self, request: Request, call_next):
        """
        Process the request through rate limiting middleware.

        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint function

        Returns:
            Response from the next middleware or endpoint
        """
        # Check rate limits based on endpoint
        if request.url.path == "/api/v1/auth/login":
            if not self._check_rate_limit("login", self._get_client_ip(request)):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many login attempts. Please try again later.",
                        "retry_after": self._get_retry_after("login", self._get_client_ip(request))
                    }
                )

        elif request.url.path == "/api/v1/auth/refresh":
            # For refresh, we need user ID from the request
            user_id = self._extract_user_id_from_refresh_request(request)
            if user_id and not self._check_rate_limit("token_refresh", str(user_id)):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many token refresh attempts. Please try again later.",
                        "retry_after": self._get_retry_after("token_refresh", str(user_id))
                    }
                )

        elif request.url.path == "/api/v1/auth/register":
            if not self._check_rate_limit("registration", self._get_client_ip(request)):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many registration attempts. Please try again later.",
                        "retry_after": self._get_retry_after("registration", self._get_client_ip(request))
                    }
                )

        # Process the request
        response = await call_next(request)

        # Record successful attempts for rate limiting
        if request.url.path == "/api/v1/auth/login" and response.status_code == 200:
            self._record_successful_attempt(
                "login", self._get_client_ip(request))
        elif request.url.path == "/api/v1/auth/refresh" and response.status_code == 200:
            user_id = self._extract_user_id_from_refresh_request(request)
            if user_id:
                self._record_successful_attempt("token_refresh", str(user_id))
        elif request.url.path == "/api/v1/auth/register" and response.status_code == 201:
            self._record_successful_attempt(
                "registration", self._get_client_ip(request))

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address string
        """
        # Check for forwarded IP (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to client host
        return request.client.host if request.client else "unknown"

    def _extract_user_id_from_refresh_request(self, request: Request) -> Optional[int]:
        """
        Extract user ID from refresh token request.

        Args:
            request: FastAPI request object

        Returns:
            User ID if found, None otherwise
        """
        try:
            # Try to get user ID from request body
            body = request.body()
            if body:
                import json
                data = json.loads(body)
                return data.get("user_id")
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            # Ignore JSON parsing errors and missing attributes
            pass
        return None

    def _check_rate_limit(self, limit_type: str, identifier: str) -> bool:
        """
        Check if a rate limit has been exceeded.

        Args:
            limit_type: Type of rate limit to check
            identifier: Unique identifier (IP or user ID)

        Returns:
            True if within limits, False if exceeded
        """
        if limit_type not in self.rate_limits:
            return True

        limit_config = self.rate_limits[limit_type]
        current_time = time.time()
        window_seconds = limit_config["window_minutes"] * 60

        # Clean old attempts
        if identifier in limit_config["attempts"]:
            limit_config["attempts"][identifier] = [
                (timestamp, count) for timestamp, count in limit_config["attempts"][identifier]
                if current_time - timestamp < window_seconds
            ]

        # Count recent attempts
        recent_attempts = limit_config["attempts"].get(identifier, [])
        total_attempts = sum(count for _, count in recent_attempts)

        return total_attempts < limit_config["max_attempts"]

    def _record_successful_attempt(self, limit_type: str, identifier: str) -> None:
        """
        Record a successful attempt for rate limiting.

        Args:
            limit_type: Type of rate limit
            identifier: Unique identifier (IP or user ID)
        """
        if limit_type not in self.rate_limits:
            return

        current_time = time.time()

        if identifier not in self.rate_limits[limit_type]["attempts"]:
            self.rate_limits[limit_type]["attempts"][identifier] = []

        # Add successful attempt
        self.rate_limits[limit_type]["attempts"][identifier].append(
            (current_time, 1))

    def _get_retry_after(self, limit_type: str, identifier: str) -> int:
        """
        Get retry after time in seconds.

        Args:
            limit_type: Type of rate limit
            identifier: Unique identifier

        Returns:
            Seconds to wait before retry
        """
        if limit_type not in self.rate_limits:
            return 60

        limit_config = self.rate_limits[limit_type]
        current_time = time.time()
        window_seconds = limit_config["window_minutes"] * 60

        if identifier in limit_config["attempts"]:
            attempts = limit_config["attempts"][identifier]
            if attempts:
                oldest_attempt = min(timestamp for timestamp, _ in attempts)
                return max(0, int(oldest_attempt + window_seconds - current_time))

        return 60  # Default 1 minute
