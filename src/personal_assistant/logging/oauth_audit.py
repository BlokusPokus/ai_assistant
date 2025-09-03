"""
OAuth audit logging for security and compliance.

📁 logging/oauth_audit.py
Provides comprehensive OAuth event logging for security audit trails and compliance.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Request

from .structured_formatter import get_correlation_id


class OAuthAuditLogger:
    """
    Dedicated logger for OAuth security events and audit trails.

    Provides structured logging for all OAuth-related events including:
    - Authorization requests and grants
    - Token refresh and revocation
    - Scope changes and permission updates
    - Security events and failed attempts
    - Integration status changes
    """

    def __init__(self):
        """Initialize the OAuth audit logger."""
        self.logger = logging.getLogger("personal_assistant.oauth_audit")
        self.logger.setLevel(logging.INFO)

        # Ensure this logger doesn't propagate to avoid duplicate logs
        self.logger.propagate = False

    def _log_oauth_event(
        self,
        event_type: str,
        user_id: int,
        provider: str,
        level: str = "info",
        **kwargs,
    ) -> None:
        """
        Log an OAuth event with structured metadata.

        Args:
            event_type: Type of OAuth event
            user_id: User ID associated with the event
            provider: OAuth provider (google, microsoft, notion, etc.)
            level: Log level (info, warning, error)
            **kwargs: Additional event metadata
        """
        # Extract request context if available
        request = kwargs.get("request")
        ip_address = None
        user_agent = None

        if request and isinstance(request, Request):
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        # Build structured log entry
        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "provider": provider,
            "security_level": "audit",
            "correlation_id": get_correlation_id(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "ip_address": ip_address,
                "user_agent": user_agent,
                **{k: v for k, v in kwargs.items() if k != "request"},
            },
        }

        # Log with appropriate level
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(
            f"OAuth {event_type} for user {user_id} with {provider}", extra=log_data
        )

    def log_authorization_request(
        self,
        user_id: int,
        provider: str,
        scopes: List[str],
        request: Optional[Request] = None,
        **kwargs,
    ) -> None:
        """
        Log OAuth authorization request.

        Args:
            user_id: User requesting authorization
            provider: OAuth provider
            scopes: Requested scopes
            request: FastAPI request object
            **kwargs: Additional metadata
        """
        self._log_oauth_event(
            "authorization_request",
            user_id,
            provider,
            request=request,
            scopes=scopes,
            **kwargs,
        )

    def log_authorization_granted(
        self,
        user_id: int,
        provider: str,
        scopes: List[str],
        integration_id: Optional[str] = None,
        request: Optional[Request] = None,
        **kwargs,
    ) -> None:
        """
        Log successful OAuth authorization grant.

        Args:
            user_id: User who granted authorization
            provider: OAuth provider
            scopes: Granted scopes
            integration_id: Integration ID if available
            request: FastAPI request object
            **kwargs: Additional metadata
        """
        self._log_oauth_event(
            "authorization_granted",
            user_id,
            provider,
            request=request,
            scopes=scopes,
            integration_id=integration_id,
            **kwargs,
        )

    def log_authorization_denied(
        self,
        user_id: int,
        provider: str,
        reason: str,
        request: Optional[Request] = None,
        **kwargs,
    ) -> None:
        """
        Log denied OAuth authorization.

        Args:
            user_id: User who denied authorization
            provider: OAuth provider
            reason: Reason for denial
            request: FastAPI request object
            **kwargs: Additional metadata
        """
        self._log_oauth_event(
            "authorization_denied",
            user_id,
            provider,
            level="warning",
            request=request,
            reason=reason,
            **kwargs,
        )

    def log_token_refresh(
        self,
        user_id: int,
        provider: str,
        success: bool,
        integration_id: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Log OAuth token refresh attempt.

        Args:
            user_id: User whose token is being refreshed
            provider: OAuth provider
            success: Whether refresh was successful
            integration_id: Integration ID if available
            error: Error message if refresh failed
            **kwargs: Additional metadata
        """
        level = "info" if success else "warning"
        self._log_oauth_event(
            "token_refresh",
            user_id,
            provider,
            level=level,
            success=success,
            integration_id=integration_id,
            error=error,
            **kwargs,
        )

    def log_token_revocation(
        self,
        user_id: int,
        provider: str,
        integration_id: Optional[str] = None,
        request: Optional[Request] = None,
        **kwargs,
    ) -> None:
        """
        Log OAuth token revocation.

        Args:
            user_id: User revoking token
            provider: OAuth provider
            integration_id: Integration ID if available
            request: FastAPI request object
            **kwargs: Additional metadata
        """
        self._log_oauth_event(
            "token_revocation",
            user_id,
            provider,
            request=request,
            integration_id=integration_id,
            **kwargs,
        )

    def log_scope_change(
        self,
        user_id: int,
        provider: str,
        old_scopes: List[str],
        new_scopes: List[str],
        integration_id: Optional[str] = None,
        request: Optional[Request] = None,
        **kwargs,
    ) -> None:
        """
        Log OAuth scope changes.

        Args:
            user_id: User changing scopes
            provider: OAuth provider
            old_scopes: Previous scopes
            new_scopes: New scopes
            integration_id: Integration ID if available
            request: FastAPI request object
            **kwargs: Additional metadata
        """
        self._log_oauth_event(
            "scope_change",
            user_id,
            provider,
            request=request,
            integration_id=integration_id,
            old_scopes=old_scopes,
            new_scopes=new_scopes,
            **kwargs,
        )

    def log_integration_status_change(
        self,
        user_id: int,
        provider: str,
        old_status: str,
        new_status: str,
        integration_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Log OAuth integration status changes.

        Args:
            user_id: User whose integration status changed
            provider: OAuth provider
            old_status: Previous status
            new_status: New status
            integration_id: Integration ID if available
            **kwargs: Additional metadata
        """
        self._log_oauth_event(
            "integration_status_change",
            user_id,
            provider,
            integration_id=integration_id,
            old_status=old_status,
            new_status=new_status,
            **kwargs,
        )

    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[int],
        provider: str,
        severity: str = "warning",
        description: str = "",
        request: Optional[Request] = None,
        **kwargs,
    ) -> None:
        """
        Log OAuth security events.

        Args:
            event_type: Type of security event
            user_id: User ID if available
            provider: OAuth provider
            severity: Event severity (info, warning, error, critical)
            description: Event description
            request: FastAPI request object
            **kwargs: Additional metadata
        """
        self._log_oauth_event(
            f"security_{event_type}",
            user_id or 0,  # Use 0 for unknown user
            provider,
            level=severity,
            request=request,
            description=description,
            **kwargs,
        )

    def log_api_access(
        self,
        user_id: int,
        provider: str,
        endpoint: str,
        method: str,
        success: bool,
        response_code: Optional[int] = None,
        request: Optional[Request] = None,
        **kwargs,
    ) -> None:
        """
        Log OAuth API access attempts.

        Args:
            user_id: User accessing API
            provider: OAuth provider
            endpoint: API endpoint accessed
            method: HTTP method
            success: Whether access was successful
            response_code: HTTP response code
            request: FastAPI request object
            **kwargs: Additional metadata
        """
        level = "info" if success else "warning"
        self._log_oauth_event(
            "api_access",
            user_id,
            provider,
            level=level,
            request=request,
            endpoint=endpoint,
            method=method,
            success=success,
            response_code=response_code,
            **kwargs,
        )


# Global OAuth audit logger instance
oauth_audit_logger = OAuthAuditLogger()


# Convenience functions for easy access
def log_oauth_authorization_request(
    user_id: int,
    provider: str,
    scopes: List[str],
    request: Optional[Request] = None,
    **kwargs,
) -> None:
    """Log OAuth authorization request."""
    oauth_audit_logger.log_authorization_request(
        user_id, provider, scopes, request, **kwargs
    )


def log_oauth_authorization_granted(
    user_id: int,
    provider: str,
    scopes: List[str],
    integration_id: Optional[str] = None,
    request: Optional[Request] = None,
    **kwargs,
) -> None:
    """Log successful OAuth authorization grant."""
    oauth_audit_logger.log_authorization_granted(
        user_id, provider, scopes, integration_id, request, **kwargs
    )


def log_oauth_authorization_denied(
    user_id: int,
    provider: str,
    reason: str,
    request: Optional[Request] = None,
    **kwargs,
) -> None:
    """Log denied OAuth authorization."""
    oauth_audit_logger.log_authorization_denied(
        user_id, provider, reason, request, **kwargs
    )


def log_oauth_token_refresh(
    user_id: int,
    provider: str,
    success: bool,
    integration_id: Optional[str] = None,
    error: Optional[str] = None,
    **kwargs,
) -> None:
    """Log OAuth token refresh attempt."""
    oauth_audit_logger.log_token_refresh(
        user_id, provider, success, integration_id, error, **kwargs
    )


def log_oauth_token_revocation(
    user_id: int,
    provider: str,
    integration_id: Optional[str] = None,
    request: Optional[Request] = None,
    **kwargs,
) -> None:
    """Log OAuth token revocation."""
    oauth_audit_logger.log_token_revocation(
        user_id, provider, integration_id, request, **kwargs
    )


def log_oauth_security_event(
    event_type: str,
    user_id: Optional[int],
    provider: str,
    severity: str = "warning",
    description: str = "",
    request: Optional[Request] = None,
    **kwargs,
) -> None:
    """Log OAuth security event."""
    oauth_audit_logger.log_security_event(
        event_type, user_id, provider, severity, description, request, **kwargs
    )
