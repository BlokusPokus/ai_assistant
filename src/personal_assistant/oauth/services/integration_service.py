"""
OAuth Integration Service

This service manages OAuth integrations, including creation, updates,
status management, and integration lifecycle operations.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from personal_assistant.monitoring import get_metrics_service
from personal_assistant.oauth.exceptions import OAuthIntegrationError
from personal_assistant.oauth.models.consent import OAuthConsent
from personal_assistant.oauth.models.integration import OAuthIntegration
from personal_assistant.oauth.models.token import OAuthToken
from personal_assistant.oauth.providers.base import BaseOAuthProvider

logger = logging.getLogger(__name__)


class OAuthIntegrationService:
    """
    Service for managing OAuth integrations and their lifecycle.
    """

    async def create_integration(
        self,
        db: AsyncSession,
        user_id: int,
        provider: str,
        provider_user_id: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        provider_metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> OAuthIntegration:
        """
        Create a new OAuth integration.

        Args:
            db: Database session
            user_id: User ID
            provider: OAuth provider name
            provider_user_id: User ID from the provider
            scopes: List of granted scopes
            provider_metadata: Provider-specific metadata
            **kwargs: Additional integration data

        Returns:
            Created OAuthIntegration object
        """
        try:
            integration = OAuthIntegration(
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                scopes=scopes or [],
                provider_metadata=provider_metadata or {},
                status="pending",
                **kwargs,
            )

            db.add(integration)
            await db.commit()
            await db.refresh(integration)

            return integration

        except Exception as e:
            await db.rollback()
            raise OAuthIntegrationError(f"Failed to create integration: {e}")

    async def get_user_integrations(
        self,
        db: AsyncSession,
        user_id: int,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        active_only: bool = True,
    ) -> List[OAuthIntegration]:
        """
        Get OAuth integrations for a user.

        Args:
            db: Database session
            user_id: User ID
            provider: Optional provider filter
            status: Optional status filter
            active_only: Whether to return only active integrations

        Returns:
            List of OAuthIntegration objects
        """
        try:
            query = select(OAuthIntegration).where(OAuthIntegration.user_id == user_id)

            if provider:
                query = query.where(OAuthIntegration.provider == provider)

            if status:
                query = query.where(OAuthIntegration.status == status)

            if active_only:
                # Since is_active field doesn't exist, we'll filter by status instead
                query = query.where(OAuthIntegration.status.in_(["pending", "active"]))

            # Include related data
            query = query.options(
                joinedload(OAuthIntegration.tokens),
                joinedload(OAuthIntegration.consents),
            )

            result = await db.execute(query)
            integrations = result.unique().scalars().all()

            return integrations

        except Exception as e:
            raise OAuthIntegrationError(f"Failed to retrieve user integrations: {e}")

    async def get_integration_by_user_and_provider(
        self, db: AsyncSession, user_id: int, provider: str
    ) -> Optional[OAuthIntegration]:
        """
        Get OAuth integration for a specific user and provider.

        Args:
            db: Database session
            user_id: User ID
            provider: OAuth provider name

        Returns:
            OAuthIntegration object if found, None otherwise
        """
        try:
            query = select(OAuthIntegration).where(
                OAuthIntegration.user_id == user_id,
                OAuthIntegration.provider == provider,
            )

            result = await db.execute(query)
            integration = result.scalar_one_or_none()

            return integration

        except Exception as e:
            raise OAuthIntegrationError(
                f"Failed to get integration by user and provider: {e}"
            )

    async def get_integration(
        self, db: AsyncSession, integration_id: int, include_related: bool = True
    ) -> Optional[OAuthIntegration]:
        """
        Get a specific OAuth integration.

        Args:
            db: Database session
            integration_id: Integration ID
            include_related: Whether to include related data

        Returns:
            OAuthIntegration object or None
        """
        try:
            query = select(OAuthIntegration).where(
                OAuthIntegration.id == integration_id
            )

            if include_related:
                query = query.options(
                    joinedload(OAuthIntegration.tokens),
                    joinedload(OAuthIntegration.consents),
                    joinedload(OAuthIntegration.audit_logs),
                )

            result = await db.execute(query)
            integration = result.unique().scalar_one_or_none()

            return integration

        except Exception as e:
            raise OAuthIntegrationError(f"Failed to retrieve integration: {e}")

    async def update_integration(
        self, db: AsyncSession, integration_id: int, **kwargs
    ) -> OAuthIntegration:
        """
        Update an OAuth integration.

        Args:
            db: Database session
            integration_id: Integration ID
            **kwargs: Fields to update

        Returns:
            Updated OAuthIntegration object
        """
        try:
            print(f"🔍 DEBUG: Starting update_integration for ID: {integration_id}")
            print(f"🔍 DEBUG: Update fields: {list(kwargs.keys())}")

            # Add updated_at timestamp
            kwargs["updated_at"] = datetime.utcnow()

            # Filter out problematic fields that might cause SQLAlchemy issues
            safe_fields = {}
            json_fields = {}

            for key, value in kwargs.items():
                if key in ["provider_metadata", "scopes"]:
                    # Handle JSON/ARRAY fields separately
                    json_fields[key] = value
                else:
                    safe_fields[key] = value

            # Update safe fields first
            if safe_fields:
                query = (
                    update(OAuthIntegration)
                    .where(OAuthIntegration.id == integration_id)
                    .values(**safe_fields)
                )

                print(f"🔍 DEBUG: Executing update query for safe fields")
                await db.execute(query)

            # Handle JSON fields separately if needed
            if json_fields:
                # Get the current integration to update JSON fields
                integration = await self.get_integration(db, integration_id)
                if integration:
                    for key, value in json_fields.items():
                        setattr(integration, key, value)
                    print(f"🔍 DEBUG: Updated JSON fields directly")

            print(f"🔍 DEBUG: Update completed, committing")
            await db.commit()
            print(f"🔍 DEBUG: Commit successful")

            # Return the updated integration
            return await self.get_integration(db, integration_id)

        except Exception as e:
            print(f"🔍 ERROR: Failed to update integration: {e}")
            print(f"🔍 ERROR Type: {type(e)}")
            import traceback

            print(f"🔍 ERROR Traceback: {traceback.format_exc()}")
            await db.rollback()
            raise OAuthIntegrationError(f"Failed to update integration: {e}")

    async def activate_integration(
        self,
        db: AsyncSession,
        integration_id: int,
        provider_user_id: Optional[str] = None,
        **kwargs,
    ) -> OAuthIntegration:
        """
        Activate an OAuth integration.

        Args:
            db: Database session
            integration_id: Integration ID
            provider_user_id: User ID from provider
            **kwargs: Additional data to update

        Returns:
            Updated OAuthIntegration object
        """
        try:
            update_data = {
                "status": "active",
                "last_sync_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            if provider_user_id:
                update_data["provider_user_id"] = provider_user_id

            # Add any additional data
            update_data.update(kwargs)

            return await self.update_integration(db, integration_id, **update_data)

        except Exception as e:
            raise OAuthIntegrationError(f"Failed to activate integration: {e}")

    async def deactivate_integration(
        self, db: AsyncSession, integration_id: int, reason: Optional[str] = None
    ) -> OAuthIntegration:
        """
        Deactivate an OAuth integration.

        Args:
            db: Database session
            integration_id: Integration ID
            reason: Reason for deactivation

        Returns:
            Updated OAuthIntegration object
        """
        try:
            update_data = {"status": "inactive", "updated_at": datetime.utcnow()}

            if reason:
                update_data["provider_metadata"] = {"deactivation_reason": reason}

            return await self.update_integration(db, integration_id, **update_data)

        except Exception as e:
            raise OAuthIntegrationError(f"Failed to deactivate integration: {e}")

    async def revoke_integration(
        self, db: AsyncSession, integration_id: int, reason: Optional[str] = None
    ) -> bool:
        """
        Revoke an OAuth integration and all associated tokens/consents.

        Args:
            db: Database session
            integration_id: Integration ID
            reason: Reason for revocation

        Returns:
            True if integration was revoked
        """
        try:
            print(f"🔍 DEBUG: Starting revoke_integration for ID: {integration_id}")

            # Update integration status
            print(f"🔍 DEBUG: Updating integration status to revoked")
            await self.update_integration(
                db,
                integration_id,
                status="revoked",
                provider_metadata={"revocation_reason": reason} if reason else None,
            )
            print(f"🔍 DEBUG: Integration status updated successfully")

            # Revoke all tokens
            print(f"🔍 DEBUG: Revoking all tokens for integration {integration_id}")
            from personal_assistant.oauth.services.token_service import (
                OAuthTokenService,
            )

            token_service = OAuthTokenService()
            await token_service.revoke_all_tokens(db, integration_id)
            print(f"🔍 DEBUG: All tokens revoked successfully")

            # Revoke all consents
            print(f"🔍 DEBUG: Revoking all consents for integration {integration_id}")
            from personal_assistant.oauth.services.consent_service import (
                OAuthConsentService,
            )

            consent_service = OAuthConsentService()
            await consent_service.revoke_all_user_consents(
                db,
                user_id=None,  # Will be filtered by integration_id
                integration_id=integration_id,
                reason=reason,
            )
            print(f"🔍 DEBUG: All consents revoked successfully")

            print(f"🔍 DEBUG: Integration {integration_id} revoked successfully")
            return True

        except Exception as e:
            print(f"❌ DEBUG: Error in revoke_integration: {e}")
            print(f"❌ DEBUG: Error type: {type(e)}")
            import traceback

            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            raise OAuthIntegrationError(f"Failed to revoke integration: {e}")

    async def sync_integration(
        self, db: AsyncSession, integration_id: int, provider: BaseOAuthProvider
    ) -> bool:
        """
        Sync an OAuth integration with the provider.

        Args:
            db: Database session
            integration_id: Integration ID
            provider: OAuth provider instance

        Returns:
            True if sync was successful
        """
        try:
            integration = await self.get_integration(db, integration_id)
            if not integration:
                return False

            # Get valid access token
            from personal_assistant.oauth.services.token_service import (
                OAuthTokenService,
            )

            token_service = OAuthTokenService()
            token = await token_service.get_valid_token(
                db, integration_id, "access_token"
            )

            if not token:
                # Try to refresh token
                new_token = await token_service.refresh_access_token(
                    db, integration_id, provider
                )
                if not new_token:
                    return False
                token = await token_service.get_valid_token(
                    db, integration_id, "access_token"
                )

            if token:
                # Get user info from provider
                user_info = provider.get_user_info(
                    token.access_token
                )  # Use access_token instead of encrypted_token

                # Update integration with latest info
                await self.update_integration(
                    db,
                    integration_id,
                    provider_user_id=user_info.get("id"),
                    provider_email=user_info.get("email") or user_info.get("mail"),
                    provider_name=user_info.get("name") or user_info.get("displayName"),
                    last_sync_at=datetime.utcnow(),
                )

                return True

            return False

        except Exception as e:
            raise OAuthIntegrationError(f"Failed to sync integration: {e}")

    async def get_integration_status(
        self, db: AsyncSession, user_id: int
    ) -> Dict[str, Any]:
        """
        Get integration status summary for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary containing integration status summary
        """
        try:
            integrations = await self.get_user_integrations(
                db, user_id, active_only=False
            )

            summary = {
                "total_integrations": len(integrations),
                "active_integrations": len(
                    [i for i in integrations if i.status == "active"]
                ),
                "pending_integrations": len(
                    [i for i in integrations if i.status == "pending"]
                ),
                "inactive_integrations": len(
                    [
                        i
                        for i in integrations
                        if i.status in ["inactive", "revoked", "expired"]
                    ]
                ),
                "providers": {},
            }

            # Group by provider
            for integration in integrations:
                provider = integration.provider
                if provider not in summary["providers"]:
                    summary["providers"][provider] = {
                        "total": 0,
                        "active": 0,
                        "pending": 0,
                        "inactive": 0,
                    }

                summary["providers"][provider]["total"] += 1
                if integration.status == "active":
                    summary["providers"][provider]["active"] += 1
                elif integration.status == "pending":
                    summary["providers"][provider]["pending"] += 1
                else:
                    summary["providers"][provider]["inactive"] += 1

            # Update Prometheus metrics
            try:
                metrics_service = get_metrics_service()

                # Update OAuth integration counts by provider
                for provider, stats in summary["providers"].items():
                    metrics_service.oauth_integrations_active.labels(
                        provider=provider
                    ).set(stats["active"])

            except Exception as metrics_error:
                logger.warning(
                    f"Failed to update Prometheus OAuth metrics: {metrics_error}"
                )

            return summary

        except Exception as e:
            raise OAuthIntegrationError(f"Failed to get integration status: {e}")

    async def cleanup_inactive_integrations(self, db: AsyncSession) -> int:
        """
        Clean up inactive integrations (for maintenance purposes).

        Args:
            db: Database session

        Returns:
            Number of integrations cleaned up
        """
        try:
            # This is a placeholder implementation
            # In a real implementation, you might want to archive old integrations
            # rather than delete them for compliance reasons
            return 0

        except Exception as e:
            raise OAuthIntegrationError(f"Failed to cleanup inactive integrations: {e}")
