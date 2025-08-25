"""
OAuth Provider Implementations

This module provides OAuth provider implementations for various services
including Google, Microsoft, Notion, and YouTube.
"""

from .base import BaseOAuthProvider
from .google import GoogleOAuthProvider
from .microsoft import MicrosoftOAuthProvider
from .notion import NotionOAuthProvider
from .youtube import YouTubeOAuthProvider

__all__ = [
    "BaseOAuthProvider",
    "GoogleOAuthProvider",
    "MicrosoftOAuthProvider",
    "NotionOAuthProvider",
    "YouTubeOAuthProvider",
]
