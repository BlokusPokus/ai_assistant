"""
OAuth Consent Service

This service manages user consent for OAuth scopes, tracking consent
decisions and maintaining an audit trail for compliance purposes.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from personal_assistant.oauth.exceptions import OAuthConsentError
from personal_assistant.oauth.models.consent import OAuthConsent
from personal_assistant.oauth.models.scope import OAuthScope


class OAuthConsentService:
    """
    Service for managing OAuth user consent and scope permissions.
    """

    async def record_consent(
        self,
        db: AsyncSession,
        user_id: int,
        integration_id: int,
        scope_id: int,
        consent_status: str = "granted",
        consent_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs,
    ) -> OAuthConsent:
        """
        Record user consent for an OAuth scope.

        Args:
            db: Database session
            user_id: User ID
            integration_id: OAuth integration ID
            scope_id: OAuth scope ID
            consent_status: Status of consent (granted, denied, revoked)
            consent_reason: Reason for consent decision
            ip_address: IP address when consent was given
            user_agent: User agent when consent was given
            **kwargs: Additional consent metadata

        Returns:
            Created OAuthConsent object
        """
        try:
            consent = OAuthConsent(
                integration_id=integration_id,
                scope_id=scope_id,
                user_id=user_id,
                consent_status=consent_status,
                consent_granted_at=datetime.utcnow()
                if consent_status == "granted"
                else None,
                consent_revoked_at=datetime.utcnow()
                if consent_status == "revoked"
                else None,
                consent_reason=consent_reason,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=kwargs,
            )

            db.add(consent)
            await db.commit()
            await db.refresh(consent)

            return consent

        except Exception as e:
            await db.rollback()
            raise OAuthConsentError(f"Failed to record consent: {e}")

    async def get_user_consents(
        self,
        db: AsyncSession,
        user_id: int,
        integration_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[OAuthConsent]:
        """
        Get user consents with optional filtering.

        Args:
            db: Database session
            user_id: User ID (not used directly, but kept for API compatibility)
            integration_id: Optional integration ID filter
            status: Optional consent status filter

        Returns:
            List of OAuthConsent objects
        """
        try:
            # Start with base query - we can't filter by user_id directly since OAuthConsent doesn't have it
            # We'll need to filter through the integration relationship
            query = select(OAuthConsent)

            if integration_id:
                query = query.where(OAuthConsent.integration_id == integration_id)

            if status:
                # Map status to is_revoked field
                if status == "revoked":
                    query = query.where(OAuthConsent.is_revoked.is_(True))
                elif status == "active":
                    query = query.where(OAuthConsent.is_revoked.is_(False))

            # Include related data
            query = query.options(joinedload(OAuthConsent.integration))

            result = await db.execute(query)
            consents = result.unique().scalars().all()

            return list(consents)

        except Exception as e:
            raise OAuthConsentError(f"Failed to retrieve user consents: {e}")

    async def get_integration_consents(
        self, db: AsyncSession, integration_id: int, status: Optional[str] = None
    ) -> List[OAuthConsent]:
        """
        Get consents for a specific integration.

        Args:
            db: Database session
            integration_id: OAuth integration ID
            status: Optional consent status filter

        Returns:
            List of OAuthConsent objects
        """
        try:
            query = select(OAuthConsent).where(
                OAuthConsent.integration_id == integration_id
            )

            if status:
                # Map status to is_revoked field
                if status == "revoked":
                    query = query.where(OAuthConsent.is_revoked.is_(True))
                elif status == "active":
                    query = query.where(OAuthConsent.is_revoked.is_(False))

            # Include related data
            query = query.options(joinedload(OAuthConsent.integration))

            result = await db.execute(query)
            consents = result.unique().scalars().all()

            return list(consents)

        except Exception as e:
            raise OAuthConsentError(f"Failed to retrieve integration consents: {e}")

    async def revoke_consent(
        self, db: AsyncSession, consent_id: int, reason: Optional[str] = None
    ) -> bool:
        """
        Revoke a user's consent for an OAuth scope.

        Args:
            db: Database session
            consent_id: Consent ID to revoke
            reason: Reason for revocation

        Returns:
            True if consent was revoked
        """
        try:
            query = (
                update(OAuthConsent)
                .where(OAuthConsent.id == consent_id)
                .values(
                    is_revoked=True, revoked_at=datetime.utcnow(), revoked_reason=reason
                )
            )

            await db.execute(query)
            await db.commit()
            return True

        except Exception as e:
            await db.rollback()
            raise OAuthConsentError(f"Failed to revoke consent: {e}")

    async def revoke_all_user_consents(
        self,
        db: AsyncSession,
        user_id: int,
        integration_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> int:
        """
        Revoke all consents for a user (or specific integration).

        Args:
            db: Database session
            user_id: User ID
            integration_id: Optional integration ID filter
            reason: Reason for revocation

        Returns:
            Number of consents revoked
        """
        try:
            # Import OAuthIntegration to join with it
            from personal_assistant.oauth.models.integration import OAuthIntegration
            
            query = update(OAuthConsent).where(
                OAuthConsent.integration_id.in_(
                    select(OAuthIntegration.id).where(OAuthIntegration.user_id == user_id)
                ),
                OAuthConsent.is_revoked == False,
            )

            if integration_id:
                query = query.where(OAuthConsent.integration_id == integration_id)

            query = query.values(
                is_revoked=True,
                revoked_at=datetime.utcnow(),
                revoked_reason=reason,
            )

            result = await db.execute(query)
            await db.commit()

            return result.rowcount

        except Exception as e:
            await db.rollback()
            raise OAuthConsentError(f"Failed to revoke user consents: {e}")

    async def check_scope_consent(
        self, db: AsyncSession, user_id: int, integration_id: int, scope_name: str
    ) -> bool:
        """
        Check if a user has consented to a specific scope.

        Args:
            db: Database session
            user_id: User ID
            integration_id: OAuth integration ID
            scope_name: Scope name to check

        Returns:
            True if user has consented to the scope
        """
        try:
            # First get the scope ID
            scope_query = select(OAuthScope.id).where(
                OAuthScope.scope_name == scope_name
            )
            scope_result = await db.execute(scope_query)
            scope_id = scope_result.scalar_one_or_none()

            if not scope_id:
                return False

            # Check if user has granted consent
            consent_query = select(OAuthConsent).where(
                OAuthConsent.user_id == user_id,
                OAuthConsent.integration_id == integration_id,
                OAuthConsent.scope_id == scope_id,
                OAuthConsent.consent_status == "granted",
            )

            consent_result = await db.execute(consent_query)
            consent = consent_result.scalar_one_or_none()

            return consent is not None

        except Exception as e:
            raise OAuthConsentError(f"Failed to check scope consent: {e}")

    async def get_consent_summary(
        self, db: AsyncSession, user_id: int
    ) -> Dict[str, Any]:
        """
        Get a summary of user's OAuth consents.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary containing consent summary
        """
        try:
            consents = await self.get_user_consents(db, user_id)

            summary: dict[str, Any] = {
                "total_consents": len(consents),
                "granted_consents": len(
                    [c for c in consents if c.consent_status == "granted"]
                ),
                "denied_consents": len(
                    [c for c in consents if c.consent_status == "denied"]
                ),
                "revoked_consents": len(
                    [c for c in consents if c.consent_status == "revoked"]
                ),
                "integrations": {},
            }

            # Group by integration
            for consent in consents:
                integration_id = consent.integration_id
                if integration_id not in summary["integrations"]:
                    summary["integrations"][integration_id] = {
                        "total_scopes": 0,
                        "granted_scopes": 0,
                        "denied_scopes": 0,
                        "revoked_scopes": 0,
                    }

                summary["integrations"][integration_id]["total_scopes"] += 1
                summary["integrations"][integration_id][
                    f"{consent.consent_status}_scopes"
                ] += 1

            return summary

        except Exception as e:
            raise OAuthConsentError(f"Failed to get consent summary: {e}")

    async def cleanup_expired_consents(self, db: AsyncSession) -> int:
        """
        Clean up old consent records (for compliance purposes).

        Args:
            db: Database session

        Returns:
            Number of consents cleaned up
        """
        try:
            # This is a placeholder implementation
            # In a real implementation, you might want to archive old consents
            # rather than delete them for compliance reasons
            return 0

        except Exception as e:
            raise OAuthConsentError(f"Failed to cleanup expired consents: {e}")
