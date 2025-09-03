"""
OAuth-specific exceptions for the Personal Assistant OAuth Manager Service.
"""

from typing import Any, Dict, Optional


class OAuthError(Exception):
    """Base exception for OAuth-related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class OAuthValidationError(OAuthError):
    """Exception raised when OAuth validation fails."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None
    ):
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})


class OAuthProviderError(OAuthError):
    """Exception raised when OAuth provider operations fail."""

    def __init__(
        self,
        message: str,
        provider: str,
        operation: str,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            message,
            "PROVIDER_ERROR",
            {"provider": provider, "operation": operation, "status_code": status_code},
        )


class OAuthTokenError(OAuthError):
    """Exception raised when OAuth token operations fail."""

    def __init__(self, message: str, token_type: str, operation: str):
        super().__init__(
            message, "TOKEN_ERROR", {"token_type": token_type, "operation": operation}
        )


class OAuthConsentError(OAuthError):
    """Exception raised when OAuth consent operations fail."""

    def __init__(
        self,
        message: str,
        consent_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ):
        super().__init__(
            message, "CONSENT_ERROR", {"consent_id": consent_id, "user_id": user_id}
        )


class OAuthIntegrationError(OAuthError):
    """Exception raised when OAuth integration operations fail."""

    def __init__(
        self,
        message: str,
        integration_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ):
        super().__init__(
            message,
            "INTEGRATION_ERROR",
            {"integration_id": integration_id, "user_id": user_id},
        )


class OAuthSecurityError(OAuthError):
    """Exception raised when OAuth security checks fail."""

    def __init__(
        self, message: str, security_check: str, ip_address: Optional[str] = None
    ):
        super().__init__(
            message,
            "SECURITY_ERROR",
            {"security_check": security_check, "ip_address": ip_address},
        )


class OAuthRateLimitError(OAuthError):
    """Exception raised when OAuth rate limits are exceeded."""

    def __init__(
        self, message: str, rate_limit_type: str, retry_after: Optional[int] = None
    ):
        super().__init__(
            message,
            "RATE_LIMIT_ERROR",
            {"rate_limit_type": rate_limit_type, "retry_after": retry_after},
        )


class OAuthScopeError(OAuthError):
    """Exception raised when OAuth scope validation fails."""

    def __init__(
        self,
        message: str,
        requested_scopes: Optional[list] = None,
        allowed_scopes: Optional[list] = None,
    ):
        super().__init__(
            message,
            "SCOPE_ERROR",
            {"requested_scopes": requested_scopes, "allowed_scopes": allowed_scopes},
        )


class OAuthStateError(OAuthError):
    """Exception raised when OAuth state parameter validation fails."""

    def __init__(
        self,
        message: str,
        state: Optional[str] = None,
        expected_state: Optional[str] = None,
    ):
        super().__init__(
            message, "STATE_ERROR", {"state": state, "expected_state": expected_state}
        )
