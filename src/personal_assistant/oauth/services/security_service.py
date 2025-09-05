"""
OAuth Security Service

This service handles OAuth security measures including state validation,
CSRF protection, scope validation, and security audit logging.
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.oauth.exceptions import OAuthSecurityError, OAuthStateError
from personal_assistant.oauth.models.audit_log import OAuthAuditLog
from personal_assistant.oauth.models.state import OAuthState


class OAuthSecurityService:
    """
    Service for OAuth security measures and audit logging.
    """

    def __init__(self):
        """Initialize the security service."""
        self.state_expiry_hours = 1  # State tokens expire after 1 hour

    def generate_state_token(self) -> str:
        """
        Generate a secure state token for CSRF protection.

        Returns:
            Secure random state token
        """
        try:
            return secrets.token_urlsafe(32)
        except Exception as e:
            raise OAuthSecurityError(
                f"Failed to generate state token: {e}", "token_generation"
            )

    async def create_state(
        self,
        db: AsyncSession,
        provider: str,
        user_id: Optional[int] = None,
        redirect_uri: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OAuthState:
        """
        Create a new OAuth state for CSRF protection.

        Args:
            db: Database session
            provider: OAuth provider name
            user_id: Optional user ID if known
            redirect_uri: Intended redirect URI
            scopes: Requested scopes
            metadata: Additional state metadata

        Returns:
            Created OAuthState object
        """
        try:
            state = OAuthState(
                state_token=self.generate_state_token(),
                provider=provider,
                user_id=user_id,
                redirect_uri=redirect_uri,
                scopes=scopes if scopes else None,  # Store as array, not string
                metadata=metadata or {},
                is_used=False,
                expires_at=datetime.utcnow() + timedelta(hours=self.state_expiry_hours),
            )

            db.add(state)
            await db.commit()
            await db.refresh(state)

            return state

        except Exception as e:
            await db.rollback()
            raise OAuthSecurityError(f"Failed to create state: {e}", "state_creation")

    async def get_state_by_token(
        self, db: AsyncSession, state_token: str
    ) -> Optional[OAuthState]:
        """
        Get OAuth state by token without validation.

        Args:
            db: Database session
            state_token: State token to retrieve

        Returns:
            OAuthState object or None if not found
        """
        try:
            query = select(OAuthState).where(OAuthState.state_token == state_token)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise OAuthSecurityError(
                f"Failed to get state by token: {e}", "state_retrieval"
            )

    async def validate_state(
        self, db: AsyncSession, state_token: str, provider: str, mark_used: bool = True
    ) -> OAuthState:
        """
        Validate an OAuth state token.

        Args:
            db: Database session
            state_token: State token to validate
            provider: Expected provider
            mark_used: Whether to mark the state as used

        Returns:
            Valid OAuthState object

        Raises:
            OAuthStateError: If state is invalid, expired, or already used
        """
        try:
            # Find the state
            query = select(OAuthState).where(
                OAuthState.state_token == state_token, OAuthState.provider == provider
            )

            result = await db.execute(query)
            state = result.scalar_one_or_none()

            if not state:
                raise OAuthStateError("Invalid state token")

            if state.is_used:
                raise OAuthStateError("State token already used")

            if state.expires_at < datetime.utcnow():
                raise OAuthStateError("State token expired")

            # Mark as used if requested
            if mark_used:
                await self.mark_state_used(db, state.id)

            return state

        except OAuthStateError:
            raise
        except Exception as e:
            raise OAuthSecurityError(
                f"Failed to validate state: {e}", "state_validation"
            )

    async def mark_state_used(self, db: AsyncSession, state_id: int) -> bool:
        """
        Mark a state token as used.

        Args:
            db: Database session
            state_id: State ID to mark as used

        Returns:
            True if state was marked as used
        """
        try:
            query = (
                update(OAuthState).where(OAuthState.id == state_id).values(is_used=True)
            )

            await db.execute(query)
            await db.commit()
            return True

        except Exception as e:
            await db.rollback()
            raise OAuthSecurityError(
                f"Failed to mark state as used: {e}", "state_mark_used"
            )

    async def cleanup_expired_states(self, db: AsyncSession) -> int:
        """
        Clean up expired state tokens.

        Args:
            db: Database session

        Returns:
            Number of states cleaned up
        """
        try:
            query = delete(OAuthState).where(OAuthState.expires_at < datetime.utcnow())

            result = await db.execute(query)
            await db.commit()

            return result.rowcount

        except Exception as e:
            await db.rollback()
            raise OAuthSecurityError(
                f"Failed to cleanup expired states: {e}", "state_cleanup"
            )

    def validate_redirect_uri(self, redirect_uri: str, allowed_uris: List[str]) -> bool:
        """
        Validate a redirect URI against allowed URIs.

        Args:
            redirect_uri: Redirect URI to validate
            allowed_uris: List of allowed redirect URIs

        Returns:
            True if redirect URI is allowed
        """
        try:
            # Basic validation - check if URI is in allowed list
            return redirect_uri in allowed_uris
        except Exception as e:
            raise OAuthSecurityError(
                f"Failed to validate redirect URI: {e}", "redirect_uri_validation"
            )

    def validate_scopes(
        self,
        requested_scopes: List[str],
        allowed_scopes: List[str],
        required_scopes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Validate requested OAuth scopes.

        Args:
            requested_scopes: List of requested scopes
            allowed_scopes: List of allowed scopes
            required_scopes: List of required scopes

        Returns:
            Dictionary containing validation results
        """
        try:
            result: dict[str, Any] = {
                "is_valid": True,
                "invalid_scopes": [],
                "missing_required": [],
                "valid_scopes": [],
            }

            # Check for invalid scopes
            for scope in requested_scopes:
                if scope in allowed_scopes:
                    result["valid_scopes"].append(scope)
                else:
                    result["invalid_scopes"].append(scope)
                    result["is_valid"] = False

            # Check for missing required scopes
            if required_scopes:
                for scope in required_scopes:
                    if scope not in requested_scopes:
                        result["missing_required"].append(scope)
                        result["is_valid"] = False

            return result

        except Exception as e:
            raise OAuthSecurityError(
                f"Failed to validate scopes: {e}", "scope_validation"
            )

    async def log_security_event(
        self,
        db: AsyncSession,
        user_id: int,
        action: str,
        status: str,
        provider: str,
        integration_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> OAuthAuditLog:
        """
        Log a security event for audit purposes.

        Args:
            db: Database session
            user_id: User ID
            action: Security action performed
            status: Status of the action (success, failure, etc.)
            provider: OAuth provider name
            integration_id: Optional integration ID
            ip_address: IP address of the action
            user_agent: User agent of the action
            details: Additional action details
            error_message: Error message if action failed

        Returns:
            Created OAuthAuditLog object
        """
        try:
            audit_log = OAuthAuditLog(
                integration_id=integration_id,
                user_id=user_id,
                action=action,
                status=status,
                # Calculate success based on status
                success=(status == "success"),
                provider=provider,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
                error_message=error_message,
            )

            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)

            return audit_log

        except Exception as e:
            await db.rollback()
            raise OAuthSecurityError(
                f"Failed to log security event: {e}", "security_logging"
            )

    async def get_security_events(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        provider: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[OAuthAuditLog]:
        """
        Get security events with optional filtering.

        Args:
            db: Database session
            user_id: Optional user ID filter
            provider: Optional provider filter
            action: Optional action filter
            status: Optional status filter
            limit: Maximum number of events to return

        Returns:
            List of OAuthAuditLog objects
        """
        try:
            query = select(OAuthAuditLog)

            if user_id:
                query = query.where(OAuthAuditLog.user_id == user_id)

            if provider:
                query = query.where(OAuthAuditLog.provider == provider)

            if action:
                query = query.where(OAuthAuditLog.action == action)

            if status:
                query = query.where(OAuthAuditLog.status == status)

            # Order by creation time (newest first)
            query = query.order_by(OAuthAuditLog.created_at.desc()).limit(limit)

            result = await db.execute(query)
            events = result.scalars().all()

            return list(events)

        except Exception as e:
            raise OAuthSecurityError(
                f"Failed to retrieve security events: {e}", "security_retrieval"
            )

    def generate_csrf_token(self) -> str:
        """
        Generate a CSRF token for additional protection.

        Returns:
            CSRF token string
        """
        try:
            return secrets.token_urlsafe(32)
        except Exception as e:
            raise OAuthSecurityError(
                f"Failed to generate CSRF token: {e}", "csrf_token_generation"
            )

    def validate_csrf_token(self, token: str, expected_token: str) -> bool:
        """
        Validate a CSRF token.

        Args:
            token: Token to validate
            expected_token: Expected token value

        Returns:
            True if tokens match
        """
        try:
            # Use constant-time comparison to prevent timing attacks
            return secrets.compare_digest(token, expected_token)
        except Exception as e:
            raise OAuthSecurityError(
                f"Failed to validate CSRF token: {e}", "csrf_token_validation"
            )

    async def cleanup_old_audit_logs(self, db: AsyncSession, days: int = 90) -> int:
        """
        Clean up old audit logs (for compliance and performance).

        Args:
            db: Database session
            days: Number of days to keep logs

        Returns:
            Number of logs cleaned up
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            query = delete(OAuthAuditLog).where(OAuthAuditLog.created_at < cutoff_date)

            result = await db.execute(query)
            await db.commit()

            return result.rowcount

        except Exception as e:
            await db.rollback()
            raise OAuthSecurityError(
                f"Failed to cleanup old audit logs: {e}", "audit_log_cleanup"
            )
