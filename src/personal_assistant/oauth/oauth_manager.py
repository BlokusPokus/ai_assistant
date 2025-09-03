"""
OAuth Manager

This is the main OAuth manager class that orchestrates all OAuth operations
including provider management, integration lifecycle, and security measures.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.config.settings import settings
from personal_assistant.monitoring import get_metrics_service
from personal_assistant.oauth.exceptions import OAuthError, OAuthProviderError
from personal_assistant.oauth.providers.base import BaseOAuthProvider
from personal_assistant.oauth.providers.google import GoogleOAuthProvider
from personal_assistant.oauth.providers.microsoft import MicrosoftOAuthProvider
from personal_assistant.oauth.providers.notion import NotionOAuthProvider
from personal_assistant.oauth.providers.youtube import YouTubeOAuthProvider
from personal_assistant.oauth.services.consent_service import OAuthConsentService
from personal_assistant.oauth.services.integration_service import (
    OAuthIntegrationService,
)
from personal_assistant.oauth.services.security_service import OAuthSecurityService
from personal_assistant.oauth.services.token_service import OAuthTokenService

logger = logging.getLogger(__name__)


class OAuthManager:
    """
    Main OAuth manager that orchestrates all OAuth operations.

    This class provides a unified interface for OAuth operations across
    different providers and manages the complete OAuth lifecycle.
    """

    def __init__(self):
        """Initialize the OAuth manager with all services."""
        self.token_service = OAuthTokenService()
        self.consent_service = OAuthConsentService()
        self.integration_service = OAuthIntegrationService()
        self.security_service = OAuthSecurityService()

        # Provider registry
        self.providers: Dict[str, Type[BaseOAuthProvider]] = {
            "google": GoogleOAuthProvider,
            "microsoft": MicrosoftOAuthProvider,
            "notion": NotionOAuthProvider,
            "youtube": YouTubeOAuthProvider,
        }

        # Provider configurations (should come from environment variables in production)
        self.provider_configs = {
            "google": {
                "client_id": getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", ""),
                "client_secret": getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", ""),
                "redirect_uri": getattr(settings, "GOOGLE_OAUTH_REDIRECT_URI", ""),
            },
            "microsoft": {
                "client_id": getattr(settings, "MICROSOFT_OAUTH_CLIENT_ID", ""),
                "client_secret": getattr(settings, "MICROSOFT_OAUTH_CLIENT_SECRET", ""),
                "redirect_uri": getattr(settings, "MICROSOFT_OAUTH_REDIRECT_URI", ""),
            },
            "notion": {
                "client_id": getattr(settings, "NOTION_OAUTH_CLIENT_ID", ""),
                "client_secret": getattr(settings, "NOTION_OAUTH_CLIENT_SECRET", ""),
                "redirect_uri": getattr(settings, "NOTION_OAUTH_REDIRECT_URI", ""),
            },
            "youtube": {
                "client_id": getattr(settings, "YOUTUBE_OAUTH_CLIENT_ID", ""),
                "client_secret": getattr(settings, "YOUTUBE_OAUTH_CLIENT_SECRET", ""),
                "redirect_uri": getattr(settings, "YOUTUBE_OAUTH_REDIRECT_URI", ""),
            },
        }

    def get_provider(self, provider_name: str) -> BaseOAuthProvider:
        """
        Get an OAuth provider instance.

        Args:
            provider_name: Name of the provider

        Returns:
            OAuth provider instance

        Raises:
            OAuthProviderError: If provider is not supported or credentials are missing
        """
        if provider_name not in self.providers:
            raise OAuthProviderError(f"Unsupported provider: {provider_name}")

        provider_class = self.providers[provider_name]
        config = self.provider_configs[provider_name]

        # Validate that required credentials are present
        if not config["client_id"] or not config["client_secret"]:
            raise OAuthProviderError(
                f"OAuth credentials not configured for {provider_name}. "
                f"Please set {provider_name.upper()}_OAUTH_CLIENT_ID and "
                f"{provider_name.upper()}_OAUTH_CLIENT_SECRET environment variables."
            )

        return provider_class(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config["redirect_uri"],
        )

    def get_supported_providers(self) -> List[str]:
        """
        Get list of supported OAuth providers.

        Returns:
            List of supported provider names
        """
        return list(self.providers.keys())

    def get_provider_scopes(self, provider_name: str) -> List[Dict[str, Any]]:
        """
        Get available scopes for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            List of scope dictionaries
        """
        provider = self.get_provider(provider_name)
        return provider.get_available_scopes()

    async def initiate_oauth_flow(
        self,
        db: AsyncSession,
        user_id: int,
        provider_name: str,
        scopes: List[str],
        redirect_uri: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Initiate an OAuth flow for a user.

        Args:
            db: Database session
            user_id: User ID
            provider_name: OAuth provider name
            scopes: Requested OAuth scopes
            redirect_uri: Custom redirect URI
            **kwargs: Additional parameters

        Returns:
            Dictionary containing authorization URL and state
        """
        try:
            # Get provider
            provider = self.get_provider(provider_name)

            # Validate scopes
            scope_validation = provider.validate_scopes(scopes)
            if not scope_validation[0]:
                raise OAuthError(f"Invalid scopes: {scope_validation[1]}")

            # Create OAuth state for CSRF protection
            state = await self.security_service.create_state(
                db=db,
                provider=provider_name,
                user_id=user_id,
                redirect_uri=redirect_uri or provider.redirect_uri,
                scopes=scopes,
                metadata=kwargs,
            )

            # Generate authorization URL
            auth_url = provider.get_authorization_url(
                state=state.state_token, scopes=scopes, **kwargs
            )

            # Log security event
            await self.security_service.log_security_event(
                db=db,
                user_id=user_id,
                action="connect",  # Use valid action from database constraint
                status="success",
                provider=provider_name,
                details={"scopes": scopes, "state_id": state.id},
            )

            return {
                "authorization_url": auth_url,
                "state_token": state.state_token,
                "provider": provider_name,
                "scopes": scopes,
            }

        except Exception as e:
            # Log security event
            await self.security_service.log_security_event(
                db=db,
                user_id=user_id,
                action="connect",  # Use standard OAuth action
                status="failure",
                provider=provider_name,
                error_message=str(e),
                details={"scopes": scopes},
            )
            raise

    async def handle_oauth_callback(
        self,
        db: AsyncSession,
        state_token: str,
        authorization_code: str,
        provider_name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback and complete the flow.

        Args:
            db: Database session
            state_token: State token from callback
            authorization_code: Authorization code from callback
            provider_name: OAuth provider name
            **kwargs: Additional callback parameters

        Returns:
            Dictionary containing integration details
        """
        try:
            # Validate state token (don't mark as used yet)
            state = await self.security_service.validate_state(
                db=db,
                state_token=state_token,
                provider=provider_name,
                mark_used=False,  # Don't mark as used until flow completes
            )

            # Get provider
            provider = self.get_provider(provider_name)

            # Exchange code for tokens
            tokens = provider.exchange_code_for_tokens(authorization_code, **kwargs)

            # Check if integration already exists
            existing_integration = (
                await self.integration_service.get_integration_by_user_and_provider(
                    db=db, user_id=state.user_id, provider=provider_name
                )
            )

            if existing_integration:
                # Update existing integration
                integration = await self.integration_service.update_integration(
                    db=db,
                    integration_id=existing_integration.id,
                    provider_user_id=tokens.get("provider_user_id"),
                    scopes=state.scopes if state.scopes else [],
                    provider_metadata=tokens,
                    status="pending",
                )
            else:
                # Create new integration
                integration = await self.integration_service.create_integration(
                    db=db,
                    user_id=state.user_id,
                    provider=provider_name,
                    provider_user_id=tokens.get("provider_user_id"),
                    scopes=state.scopes if state.scopes else [],
                    provider_metadata=tokens,
                )

            # Store tokens
            try:
                stored_tokens = await self.token_service.store_tokens(
                    db=db, integration_id=integration.id, tokens=tokens
                )
            except Exception as token_error:
                raise

            # Record consents for requested scopes
            if state.scopes:
                scope_list = state.scopes
                for scope_name in scope_list:
                    # Get scope ID (this would need to be implemented based on your scope model)
                    # For now, we'll skip scope-specific consent recording
                    pass

            # Activate integration
            try:
                await self.integration_service.activate_integration(
                    db=db,
                    integration_id=integration.id,
                    provider_user_id=tokens.get("provider_user_id"),
                )
            except Exception as activation_error:
                raise

            # Log security event
            await self.security_service.log_security_event(
                db=db,
                user_id=state.user_id,
                action="connect",  # Use valid action from database constraint
                status="success",
                provider=provider_name,
                integration_id=integration.id,
                details={"scopes": state.scopes},
            )

            # Mark state as used after successful completion
            await self.security_service.mark_state_used(db, state.id)

            return {
                "integration_id": integration.id,
                "provider": provider_name,
                "status": "active",
                "scopes": state.scopes if state.scopes else [],
            }

        except Exception as e:
            # Log security event
            if "state" in locals() and state.user_id:
                await self.security_service.log_security_event(
                    db=db,
                    user_id=state.user_id,
                    action="error",  # Use valid action from database constraint
                    status="failure",
                    provider=provider_name,
                    error_message=str(e),
                )
            raise

    async def refresh_integration_tokens(
        self, db: AsyncSession, integration_id: int
    ) -> bool:
        """
        Refresh tokens for an OAuth integration.

        Args:
            db: Database session
            integration_id: Integration ID

        Returns:
            True if tokens were refreshed successfully
        """
        try:
            # Get integration
            integration = await self.integration_service.get_integration(
                db, integration_id
            )
            if not integration:
                print(f"⚠️  DEBUG: Integration {integration_id} not found")
                return False

            print(
                f"🔍 DEBUG: Found integration {integration_id} for provider {integration.provider}"
            )

            # Get provider
            try:
                provider = self.get_provider(integration.provider)
                print(f"🔍 DEBUG: Got provider for {integration.provider}")
            except Exception as e:
                print(f"❌ DEBUG: Error getting provider: {e}")
                raise

            # Check if refresh token exists
            from personal_assistant.oauth.services.token_service import (
                OAuthTokenService,
            )

            token_service = OAuthTokenService()
            refresh_token = await token_service.get_valid_token(
                db, integration_id, "refresh_token"
            )

            if not refresh_token:
                # No refresh token available - this integration cannot be refreshed
                print(
                    f"⚠️  No refresh token available for integration {integration_id} ({integration.provider})"
                )
                print(f"🔍 DEBUG: About to return False")
                return False

            print(f"🔍 DEBUG: Found refresh token, proceeding with refresh")

            # Refresh tokens
            start_time = datetime.now()
            new_token = await token_service.refresh_access_token(
                db=db, integration_id=integration_id, provider=provider
            )
            duration = (datetime.now() - start_time).total_seconds()

            if new_token:
                print(f"🔍 DEBUG: Token refresh successful")

                # Update Prometheus metrics
                try:
                    metrics_service = get_metrics_service()
                    metrics_service.oauth_token_refresh_total.labels(
                        provider=integration.provider, status="success"
                    ).inc()
                    metrics_service.oauth_operation_duration_seconds.labels(
                        provider=integration.provider, operation="refresh"
                    ).observe(duration)
                except Exception as metrics_error:
                    logger.warning(
                        f"Failed to update Prometheus OAuth metrics: {metrics_error}"
                    )

                # Update integration
                await self.integration_service.update_integration(
                    db=db, integration_id=integration_id, last_sync_at=datetime.utcnow()
                )

                # Log security event
                await self.security_service.log_security_event(
                    db=db,
                    user_id=integration.user_id,
                    action="refresh",  # Use valid action from database constraint
                    status="success",
                    provider=integration.provider,
                    integration_id=integration_id,
                )

                return True

            print(f"⚠️  DEBUG: Token refresh returned no new token")

            # Update Prometheus metrics for failure
            try:
                metrics_service = get_metrics_service()
                metrics_service.oauth_token_refresh_total.labels(
                    provider=integration.provider, status="failure"
                ).inc()
                metrics_service.oauth_errors_total.labels(
                    provider=integration.provider, error_type="refresh_failed"
                ).inc()
            except Exception as metrics_error:
                logger.warning(
                    f"Failed to update Prometheus OAuth metrics: {metrics_error}"
                )
            return False

        except Exception as e:
            print(f"❌ DEBUG: Exception in refresh_integration_tokens: {e}")
            print(f"❌ DEBUG: Exception type: {type(e)}")
            import traceback

            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")

            # Log security event
            if "integration" in locals():
                try:
                    await self.security_service.log_security_event(
                        db=db,
                        user_id=integration.user_id,
                        action="error",  # Use valid action from database constraint
                        status="failure",
                        provider=integration.provider,
                        integration_id=integration_id,
                        error_message=str(e),
                    )
                    print(f"🔍 DEBUG: Security event logged successfully")
                except Exception as log_error:
                    print(f"❌ DEBUG: Failed to log security event: {log_error}")
            raise

    async def revoke_integration(
        self, db: AsyncSession, integration_id: int, reason: Optional[str] = None
    ) -> bool:
        """
        Revoke an OAuth integration.

        Args:
            db: Database session
            integration_id: Integration ID
            reason: Reason for revocation

        Returns:
            True if integration was revoked
        """
        try:
            # Get integration for logging
            integration = await self.integration_service.get_integration(
                db, integration_id
            )

            # Revoke integration
            success = await self.integration_service.revoke_integration(
                db=db, integration_id=integration_id, reason=reason
            )

            if success and integration:
                # Log security event
                await self.security_service.log_security_event(
                    db=db,
                    user_id=integration.user_id,
                    action="revoke",  # Use valid action from database constraint
                    status="success",
                    provider=integration.provider,
                    integration_id=integration_id,
                    details={"reason": reason},
                )

            return success

        except Exception as e:
            # Log security event
            if "integration" in locals():
                await self.security_service.log_security_event(
                    db=db,
                    user_id=integration.user_id,
                    action="error",  # Use valid action from database constraint
                    status="failure",
                    provider=integration.provider,
                    integration_id=integration_id,
                    error_message=str(e),
                )
            raise

    async def get_user_integrations(
        self,
        db: AsyncSession,
        user_id: int,
        provider: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get OAuth integrations for a user.

        Args:
            db: Database session
            user_id: User ID
            provider: Optional provider filter
            active_only: Whether to return only active integrations

        Returns:
            List of integration dictionaries
        """
        try:
            integrations = await self.integration_service.get_user_integrations(
                db=db, user_id=user_id, provider=provider, active_only=active_only
            )

            result = []
            for integration in integrations:
                integration_data = {
                    "id": integration.id,
                    "provider": integration.provider,
                    "status": integration.status,
                    # Compute based on status
                    "is_active": integration.status in ["pending", "active"],
                    "scopes": integration.scopes,
                    "created_at": integration.created_at.isoformat(),
                    "last_sync_at": integration.last_sync_at.isoformat()
                    if integration.last_sync_at
                    else None,
                }

                # Add provider-specific metadata
                if integration.provider_metadata:
                    integration_data["metadata"] = integration.provider_metadata

                result.append(integration_data)

            return result

        except Exception as e:
            raise OAuthError(f"Failed to get user integrations: {e}")

    async def sync_all_integrations(
        self, db: AsyncSession, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sync all OAuth integrations (or for a specific user).

        Args:
            db: Database session
            user_id: Optional user ID filter

        Returns:
            Dictionary containing sync results
        """
        try:
            # Get integrations to sync
            if user_id:
                integrations = await self.integration_service.get_user_integrations(
                    db=db, user_id=user_id, active_only=True
                )
            else:
                # This would need to be implemented to get all active integrations
                integrations = []

            sync_results = {
                "total_integrations": len(integrations),
                "successful_syncs": 0,
                "failed_syncs": 0,
                "errors": [],
            }

            for integration in integrations:
                try:
                    provider = self.get_provider(integration.provider)
                    success = await self.integration_service.sync_integration(
                        db=db, integration_id=integration.id, provider=provider
                    )

                    if success:
                        sync_results["successful_syncs"] += 1
                    else:
                        sync_results["failed_syncs"] += 1
                        sync_results["errors"].append(
                            {
                                "integration_id": integration.id,
                                "provider": integration.provider,
                                "error": "Sync failed",
                            }
                        )

                except Exception as e:
                    sync_results["failed_syncs"] += 1
                    sync_results["errors"].append(
                        {
                            "integration_id": integration.id,
                            "provider": integration.provider,
                            "error": str(e),
                        }
                    )

            return sync_results

        except Exception as e:
            raise OAuthError(f"Failed to sync integrations: {e}")

    async def cleanup_expired_data(self, db: AsyncSession) -> Dict[str, int]:
        """
        Clean up expired OAuth data.

        Args:
            db: Database session

        Returns:
            Dictionary containing cleanup results
        """
        try:
            cleanup_results = {}

            # Clean up expired tokens
            expired_tokens = await self.token_service.cleanup_expired_tokens(db)
            cleanup_results["expired_tokens"] = expired_tokens

            # Clean up expired states
            expired_states = await self.security_service.cleanup_expired_states(db)
            cleanup_results["expired_states"] = expired_states

            # Clean up old audit logs
            old_audit_logs = await self.security_service.cleanup_old_audit_logs(db)
            cleanup_results["old_audit_logs"] = old_audit_logs

            return cleanup_results

        except Exception as e:
            raise OAuthError(f"Failed to cleanup expired data: {e}")
