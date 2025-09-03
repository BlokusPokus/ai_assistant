"""
Base OAuth Provider Interface

This module defines the abstract base class that all OAuth providers
must implement. It provides a consistent interface for OAuth 2.0 flows
across different providers (Google, Microsoft, Notion, YouTube).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class BaseOAuthProvider(ABC):
    """
    Abstract base class for OAuth providers.

    This class defines the interface that all OAuth providers must implement
    to ensure consistent behavior across different services.
    """

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize the OAuth provider.

        Args:
            client_id: OAuth client ID from the provider
            client_secret: OAuth client secret from the provider
            redirect_uri: OAuth redirect URI for callbacks
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the OAuth provider."""

    @property
    @abstractmethod
    def authorization_url(self) -> str:
        """Return the OAuth authorization URL for this provider."""

    @property
    @abstractmethod
    def token_url(self) -> str:
        """Return the OAuth token exchange URL for this provider."""

    @property
    @abstractmethod
    def userinfo_url(self) -> str:
        """Return the user info URL for this provider."""

    @abstractmethod
    def get_authorization_url(self, state: str, scopes: List[str], **kwargs) -> str:
        """
        Generate the OAuth authorization URL.

        Args:
            state: CSRF protection state parameter
            scopes: List of requested OAuth scopes
            **kwargs: Additional provider-specific parameters

        Returns:
            Complete authorization URL
        """

    @abstractmethod
    def exchange_code_for_tokens(
        self, authorization_code: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            authorization_code: Authorization code from OAuth callback
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary containing tokens and metadata
        """

    @abstractmethod
    def refresh_access_token(self, refresh_token: str, **kwargs) -> Dict[str, Any]:
        """
        Refresh an expired access token using a refresh token.

        Args:
            refresh_token: Valid refresh token
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary containing new tokens and metadata
        """

    @abstractmethod
    def get_user_info(self, access_token: str, **kwargs) -> Dict[str, Any]:
        """
        Get user information using an access token.

        Args:
            access_token: Valid access token
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary containing user information
        """

    @abstractmethod
    def validate_token(self, access_token: str, **kwargs) -> bool:
        """
        Validate if an access token is still valid.

        Args:
            access_token: Access token to validate
            **kwargs: Additional provider-specific parameters

        Returns:
            True if token is valid, False otherwise
        """

    @abstractmethod
    def get_available_scopes(self) -> List[Dict[str, Any]]:
        """
        Get list of available OAuth scopes for this provider.

        Returns:
            List of scope dictionaries with metadata
        """

    @abstractmethod
    def revoke_token(
        self, token: str, token_type: str = "access_token", **kwargs
    ) -> bool:
        """
        Revoke an OAuth token.

        Args:
            token: Token to revoke
            token_type: Type of token (access_token, refresh_token)
            **kwargs: Additional provider-specific parameters

        Returns:
            True if token was successfully revoked
        """

    def get_default_scopes(self) -> List[str]:
        """
        Get default scopes for this provider.

        Returns:
            List of default scope strings
        """
        return []

    def get_required_scopes(self) -> List[str]:
        """
        Get required scopes for this provider.

        Returns:
            List of required scope strings
        """
        return []

    def validate_scopes(self, scopes: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate requested scopes against available scopes.

        Args:
            scopes: List of requested scopes

        Returns:
            Tuple of (is_valid, invalid_scopes)
        """
        available_scopes = [
            scope["scope_name"] for scope in self.get_available_scopes()
        ]
        invalid_scopes = [scope for scope in scopes if scope not in available_scopes]
        return len(invalid_scopes) == 0, invalid_scopes
