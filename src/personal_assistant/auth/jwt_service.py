"""
JWT Service for handling authentication tokens.

This service provides JWT token generation, validation, and refresh
capabilities with configurable expiration times and secure secret management.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from personal_assistant.config.settings import settings


class JWTService:
    """Service for JWT token operations."""

    def __init__(self):
        """Initialize JWT service with configuration."""
        self.secret_key = self._get_secret_key()
        self.algorithm = "HS256"
        self.access_token_expire_minutes = getattr(
            settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 15)
        self.refresh_token_expire_days = getattr(
            settings, 'REFRESH_TOKEN_EXPIRE_DAYS', 7)

    def _get_secret_key(self) -> str:
        """Get JWT secret key from environment or generate a secure one."""
        secret_key = getattr(settings, 'JWT_SECRET_KEY', None)
        if not secret_key:
            # In production, this should always be set via environment
            if getattr(settings, 'ENVIRONMENT', 'development') == 'production':
                raise ValueError(
                    "JWT_SECRET_KEY must be set in production environment")
            # For development, use a default (not secure for production)
            secret_key = "dev-secret-key-change-in-production"
        return secret_key

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create an access token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a refresh token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string to verify

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """
        Verify an access token specifically.

        Args:
            token: JWT access token string

        Returns:
            Decoded access token payload

        Raises:
            HTTPException: If token is not an access token or invalid
        """
        payload = self.verify_token(token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a refresh token specifically.

        Args:
            token: JWT refresh token string

        Returns:
            Decoded refresh token payload

        Raises:
            HTTPException: If token is not a refresh token or invalid
        """
        payload = self.verify_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Create a new access token using a valid refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token string
        """
        payload = self.verify_refresh_token(refresh_token)
        # Remove refresh-specific fields
        user_data = {k: v for k, v in payload.items()
                     if k not in ["exp", "type", "iat"]}
        return self.create_access_token(user_data)


# Global JWT service instance
jwt_service = JWTService()
