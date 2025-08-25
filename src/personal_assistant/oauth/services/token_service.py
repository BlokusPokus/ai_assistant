"""
OAuth Token Service

This service handles OAuth token encryption, storage, and management
including token refresh, validation, and secure storage.
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from cryptography.fernet import Fernet

from personal_assistant.oauth.models.token import OAuthToken
from personal_assistant.oauth.models.integration import OAuthIntegration
from personal_assistant.oauth.exceptions import OAuthTokenError
from personal_assistant.config.settings import settings


class OAuthTokenService:
    """
    Service for managing OAuth tokens including encryption, storage, and refresh.
    """

    def __init__(self):
        """Initialize the token service with encryption key."""
        # In production, this should come from environment variables or secure storage
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)

    def encrypt_token(self, token: str) -> str:
        """
        Encrypt an OAuth token for secure storage.

        Args:
            token: Plain text token to encrypt

        Returns:
            Encrypted token string
        """
        try:
            encrypted_token = self.cipher_suite.encrypt(token.encode())
            return encrypted_token.decode()
        except Exception as e:
            raise OAuthTokenError(
                f"Failed to encrypt token: {e}", "unknown", "encrypt")

    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Decrypt an OAuth token for use.

        Args:
            encrypted_token: Encrypted token string

        Returns:
            Decrypted token string
        """
        try:
            decrypted_token = self.cipher_suite.decrypt(
                encrypted_token.encode())
            return decrypted_token.decode()
        except Exception as e:
            raise OAuthTokenError(
                f"Failed to decrypt token: {e}", "unknown", "decrypt")

    async def store_tokens(
        self,
        db: AsyncSession,
        integration_id: int,
        tokens: Dict[str, Any],
        **kwargs
    ) -> List[OAuthToken]:
        """
        Store OAuth tokens for an integration.

        Args:
            db: Database session
            integration_id: OAuth integration ID
            tokens: Dictionary containing tokens and metadata
            **kwargs: Additional token metadata

        Returns:
            List of stored OAuthToken objects
        """
        try:
            stored_tokens = []

            # Store access token
            if "access_token" in tokens:
                access_token = OAuthToken(
                    integration_id=integration_id,
                    token_type="access_token",
                    access_token=tokens["access_token"],
                    refresh_token=None,  # No refresh token for access token
                    expires_at=datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600)),
                    scope=" ".join(tokens.get("scope", "").split())
                    if tokens.get("scope") else None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(access_token)
                stored_tokens.append(access_token)

            # Store refresh token
            if "refresh_token" in tokens:
                refresh_token = OAuthToken(
                    integration_id=integration_id,
                    token_type="refresh_token",
                    # Put refresh token in access_token column (required)
                    access_token=tokens["refresh_token"],
                    refresh_token=None,  # Leave this as NULL since it's optional
                    # Refresh tokens expire in 1 year
                    expires_at=datetime.utcnow() + timedelta(days=365),
                    scope=" ".join(tokens.get("scope", "").split())
                    if tokens.get("scope") else None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(refresh_token)
                stored_tokens.append(refresh_token)

            await db.commit()

            # Don't refresh objects after commit to avoid greenlet_spawn issues
            # The objects will have their IDs set automatically by SQLAlchemy
            return stored_tokens

        except Exception as e:
            await db.rollback()
            raise OAuthTokenError(
                f"Failed to store tokens: {e}", "mixed", "store")

    async def get_valid_token(
        self,
        db: AsyncSession,
        integration_id: int,
        token_type: str = "access_token"
    ) -> Optional[OAuthToken]:
        """
        Get a valid token for an integration.

        Args:
            db: Database session
            integration_id: OAuth integration ID
            token_type: Type of token to retrieve

        Returns:
            Valid OAuthToken object or None
        """
        try:
            query = select(OAuthToken).where(
                OAuthToken.integration_id == integration_id,
                OAuthToken.token_type == token_type,
                (OAuthToken.expires_at.is_(None) |
                 (OAuthToken.expires_at > datetime.utcnow()))
            )

            result = await db.execute(query)
            token = result.scalar_one_or_none()

            return token

        except Exception as e:
            raise OAuthTokenError(
                f"Failed to retrieve token: {e}", token_type, "retrieve")

    async def refresh_access_token(
        self,
        db: AsyncSession,
        integration_id: int,
        provider
    ) -> Optional[str]:
        """
        Refresh an expired access token using a refresh token.

        Args:
            db: Database session
            integration_id: OAuth integration ID
            provider: OAuth provider instance

        Returns:
            New access token string or None
        """
        try:
            # Get refresh token
            refresh_token_obj = await self.get_valid_token(db, integration_id, "refresh_token")
            if not refresh_token_obj:
                return None

            # Use access_token directly (not encrypted)
            refresh_token = refresh_token_obj.access_token

            # Use provider to refresh token
            new_tokens = provider.refresh_access_token(refresh_token)

            # Store new tokens
            await self.store_tokens(db, integration_id, new_tokens)

            # Invalidate old access token
            await self.invalidate_token(db, integration_id, "access_token")

            return new_tokens.get("access_token")

        except Exception as e:
            raise OAuthTokenError(
                f"Failed to refresh access token: {e}", "access_token", "refresh")

    async def invalidate_token(
        self,
        db: AsyncSession,
        integration_id: int,
        token_type: str = "access_token"
    ) -> bool:
        """
        Invalidate a token for an integration.

        Args:
            db: Database session
            integration_id: OAuth integration ID
            token_type: Type of token to invalidate

        Returns:
            True if token was invalidated
        """
        try:
            query = update(OAuthToken).where(
                OAuthToken.integration_id == integration_id,
                OAuthToken.token_type == token_type
            ).values(updated_at=datetime.utcnow())

            await db.execute(query)
            await db.commit()

            return True

        except Exception as e:
            await db.rollback()
            raise OAuthTokenError(
                f"Failed to invalidate token: {e}", token_type, "invalidate")

    async def revoke_tokens(
        self,
        db: AsyncSession,
        integration_id: int
    ) -> bool:
        """
        Revoke all tokens for an integration.

        Args:
            db: Database session
            integration_id: OAuth integration ID

        Returns:
            True if tokens were revoked
        """
        try:
            query = delete(OAuthToken).where(
                OAuthToken.integration_id == integration_id
            )

            await db.execute(query)
            await db.commit()

            return True

        except Exception as e:
            await db.rollback()
            raise OAuthTokenError(
                f"Failed to revoke tokens: {e}", "mixed", "revoke")

    async def cleanup_expired_tokens(self, db: AsyncSession) -> int:
        """
        Clean up expired tokens.

        Args:
            db: Database session

        Returns:
            Number of tokens cleaned up
        """
        try:
            query = delete(OAuthToken).where(
                OAuthToken.expires_at < datetime.utcnow()
            )

            result = await db.execute(query)
            await db.commit()

            return result.rowcount

        except Exception as e:
            await db.rollback()
            raise OAuthTokenError(
                f"Failed to cleanup expired tokens: {e}", "mixed", "cleanup")

    def is_token_expired(self, token: OAuthToken) -> bool:
        """
        Check if a token is expired.

        Args:
            token: OAuthToken object to check

        Returns:
            True if token is expired
        """
        if not token.expires_at:
            return False  # No expiration (e.g., refresh tokens)

        return datetime.utcnow() > token.expires_at

    def get_token_expiry_time(self, token: OAuthToken) -> Optional[datetime]:
        """
        Get the expiry time for a token.

        Args:
            token: OAuthToken object

        Returns:
            Token expiry time or None
        """
        return token.expires_at
