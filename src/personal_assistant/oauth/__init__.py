"""
OAuth Manager Service for Personal Assistant

This module provides OAuth 2.0 integration capabilities for multiple providers
(Google, Microsoft, Notion, YouTube) with secure token management, user isolation,
and progressive feature activation.
"""

from .oauth_manager import OAuthManager
from .exceptions import OAuthError, OAuthValidationError, OAuthProviderError

# Import services and providers for OAuthManager functionality
from .services import (
    OAuthTokenService,
    OAuthConsentService,
    OAuthIntegrationService,
    OAuthSecurityService
)
from .providers.base import BaseOAuthProvider
from .providers.google import GoogleOAuthProvider
from .providers.microsoft import MicrosoftOAuthProvider
from .providers.notion import NotionOAuthProvider
from .providers.youtube import YouTubeOAuthProvider

# Models are imported separately when needed to avoid table conflicts
# from .models import (
#     OAuthIntegration,
#     OAuthToken,
#     OAuthScope,
#     OAuthConsent,
#     OAuthAuditLog,
#     OAuthState
# )

__version__ = "1.0.0"

__all__ = [
    # Core OAuth manager
    "OAuthManager",

    # Exceptions
    "OAuthError",
    "OAuthValidationError",
    "OAuthProviderError",

    # Services
    "OAuthTokenService",
    "OAuthConsentService",
    "OAuthIntegrationService",
    "OAuthSecurityService",

    # Provider base
    "BaseOAuthProvider",

    # Provider implementations
    "GoogleOAuthProvider",
    "MicrosoftOAuthProvider",
    "NotionOAuthProvider",
    "YouTubeOAuthProvider",
]
