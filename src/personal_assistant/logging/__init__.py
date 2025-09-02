"""
Structured logging utilities for the personal assistant framework.

📁 logging/__init__.py
Provides structured JSON logging, correlation IDs, and enhanced logging utilities.
"""

from .structured_formatter import (
    StructuredJSONFormatter,
    CorrelationContext,
    correlation_context,
    get_correlation_id,
    set_correlation_id,
    generate_correlation_id,
    log_with_context
)

from .oauth_audit import (
    OAuthAuditLogger,
    oauth_audit_logger,
    log_oauth_authorization_request,
    log_oauth_authorization_granted,
    log_oauth_authorization_denied,
    log_oauth_token_refresh,
    log_oauth_token_revocation,
    log_oauth_security_event
)

__all__ = [
    "StructuredJSONFormatter",
    "CorrelationContext",
    "correlation_context",
    "get_correlation_id",
    "set_correlation_id",
    "generate_correlation_id",
    "log_with_context",
    "OAuthAuditLogger",
    "oauth_audit_logger",
    "log_oauth_authorization_request",
    "log_oauth_authorization_granted",
    "log_oauth_authorization_denied",
    "log_oauth_token_refresh",
    "log_oauth_token_revocation",
    "log_oauth_security_event"
]
