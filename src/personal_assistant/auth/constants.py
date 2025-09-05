"""
Authentication constants for the Personal Assistant TDAH application.

This module contains constants used throughout the authentication system
to avoid hardcoded strings and improve maintainability.
"""

# Token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
TOKEN_TYPE_RESET = "reset"
TOKEN_TYPE_VERIFICATION = "verification"

# Note: OAuth 2.0 standard token types like "bearer" are defined by RFC 6750
# and don't need constants as they're universal standards

# Token expiration defaults (in days)
DEFAULT_ACCESS_TOKEN_EXPIRE_DAYS = 1
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 30
DEFAULT_RESET_TOKEN_EXPIRE_DAYS = 1
DEFAULT_VERIFICATION_TOKEN_EXPIRE_DAYS = 1

# Permission constants
PERMISSION_READ = "read"
PERMISSION_WRITE = "write"
PERMISSION_DELETE = "delete"
PERMISSION_ADMIN = "admin"

# Role constants
ROLE_USER = "user"
ROLE_ADMIN = "admin"
ROLE_MODERATOR = "moderator"

# Authentication status
AUTH_STATUS_ACTIVE = "active"
AUTH_STATUS_INACTIVE = "inactive"
AUTH_STATUS_SUSPENDED = "suspended"
AUTH_STATUS_PENDING = "pending"
