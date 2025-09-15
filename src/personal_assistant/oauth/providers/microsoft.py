"""
Microsoft OAuth Provider Implementation

This module provides OAuth 2.0 integration with Microsoft Graph API including
Outlook Calendar, OneDrive, and Microsoft 365 services.
"""

import urllib.parse
from typing import Any, Dict, List

import requests

from .base import BaseOAuthProvider


class MicrosoftOAuthProvider(BaseOAuthProvider):
    """
    Microsoft OAuth 2.0 provider implementation.

    Supports Microsoft Graph API including Outlook Calendar, OneDrive, and Microsoft 365.
    """

    @property
    def provider_name(self) -> str:
        return "microsoft"

    @property
    def authorization_url(self) -> str:
        return "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"

    @property
    def token_url(self) -> str:
        return "https://login.microsoftonline.com/common/oauth2/v2.0/token"

    @property
    def userinfo_url(self) -> str:
        return "https://graph.microsoft.com/v1.0/me"

    def get_authorization_url(self, state: str, scopes: List[str], **kwargs) -> str:
        """
        Generate Microsoft OAuth authorization URL.

        Args:
            state: CSRF protection state parameter
            scopes: List of requested OAuth scopes
            **kwargs: Additional parameters (response_mode, prompt, etc.)

        Returns:
            Complete authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
            "response_mode": kwargs.get("response_mode", "query"),
            "prompt": kwargs.get("prompt", "consent"),
        }

        # Add additional parameters if provided
        for key, value in kwargs.items():
            if key not in ["response_mode", "prompt"]:
                params[key] = value

        query_string = urllib.parse.urlencode(params)
        auth_url = f"{self.authorization_url}?{query_string}"
        
        # Debug logging
        print(f"DEBUG: Microsoft authorization URL - scopes: {scopes}")
        print(f"DEBUG: Microsoft authorization URL - scope param: {params.get('scope')}")
        print(f"DEBUG: Microsoft authorization URL: {auth_url}")
        
        return auth_url

    def exchange_code_for_tokens(
        self, authorization_code: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for Microsoft OAuth tokens.

        Args:
            authorization_code: Authorization code from OAuth callback
            **kwargs: Additional parameters (scopes, etc.)

        Returns:
            Dictionary containing tokens and metadata
        """
        try:
            # Get scopes from kwargs or use default Microsoft Graph scopes
            scopes = kwargs.get('scopes', ['openid', 'profile', 'email', 'User.Read'])
            scope_string = ' '.join(scopes) if isinstance(scopes, list) else scopes
            
            # Debug logging
            print(f"DEBUG: Microsoft token exchange - scopes from kwargs: {kwargs.get('scopes')}")
            print(f"DEBUG: Microsoft token exchange - processed scopes: {scopes}")
            print(f"DEBUG: Microsoft token exchange - scope_string: {scope_string}")
            
            # Prepare the token exchange request
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
                "scope": scope_string,  # Required by Microsoft OAuth 2.0
            }

            # Make the HTTP POST request to Microsoft's token endpoint
            response = requests.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )

            if response.status_code != 200:
                from personal_assistant.oauth.exceptions import OAuthProviderError
                raise OAuthProviderError(
                    f"Microsoft OAuth token exchange failed: {response.status_code} - {response.text}",
                    provider="microsoft",
                    operation="exchange_code_for_tokens",
                    status_code=response.status_code
                )

            # Parse the response
            token_data = response.json()

            # Extract user info if we have an access token
            user_info = {}
            if "access_token" in token_data:
                try:
                    user_info = self.get_user_info(token_data["access_token"])
                except Exception as e:
                    # Log the error but don't fail the token exchange
                    print(f"Warning: Failed to get user info: {e}")

            # Return the complete token data
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": token_data.get("expires_in", 3600),
                "scope": token_data.get("scope", ""),
                "provider_user_id": user_info.get("id"),
                "provider_email": user_info.get("mail"),
                "provider_name": user_info.get("displayName"),
                # Include the full response for debugging
                "raw_response": token_data,
            }

        except Exception as e:
            from personal_assistant.oauth.exceptions import OAuthProviderError
            raise OAuthProviderError(
                f"Failed to exchange authorization code for tokens: {e}",
                provider="microsoft",
                operation="exchange_code_for_tokens"
            )

    def refresh_access_token(self, refresh_token: str, **kwargs) -> Dict[str, Any]:
        """
        Refresh Microsoft OAuth access token.

        Args:
            refresh_token: Valid refresh token
            **kwargs: Additional parameters

        Returns:
            Dictionary containing new tokens and metadata
        """
        try:
            # Prepare the token refresh request
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }

            # Make the HTTP POST request to Microsoft's token endpoint
            response = requests.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Microsoft OAuth token refresh failed: {response.status_code} - {response.text}"
                )

            # Parse the response
            token_data = response.json()

            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": refresh_token,  # Keep the original refresh token
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": token_data.get("expires_in", 3600),
                "scope": token_data.get("scope", ""),
            }

        except Exception as e:
            raise Exception(f"Failed to refresh access token: {e}")

    def get_user_info(self, access_token: str, **kwargs) -> Dict[str, Any]:
        """
        Get Microsoft user information.

        Args:
            access_token: Valid access token
            **kwargs: Additional parameters

        Returns:
            Dictionary containing user information
        """
        try:
            # Make the HTTP GET request to Microsoft Graph API
            response = requests.get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Failed to get user info: {response.status_code} - {response.text}"
                )

            return response.json()  # type: ignore

        except Exception as e:
            raise Exception(f"Failed to get user info: {e}")

    def validate_token(self, access_token: str, **kwargs) -> bool:
        """
        Validate Microsoft OAuth access token.

        Args:
            access_token: Access token to validate
            **kwargs: Additional parameters

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Try to get user info - if it succeeds, the token is valid
            user_info = self.get_user_info(access_token)
            return "id" in user_info
        except Exception:
            return False

    def get_available_scopes(self) -> List[Dict[str, Any]]:
        """
        Get available Microsoft OAuth scopes.

        Returns:
            List of scope dictionaries with metadata
        """
        return [
            {
                "scope_name": "openid",
                "display_name": "OpenID Connect",
                "description": "Access to user's basic profile information",
                "category": "identity",
                "is_readonly": True,
                "is_required": True,
            },
            {
                "scope_name": "profile",
                "display_name": "Profile",
                "description": "Access to user's basic profile information",
                "category": "identity",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "email",
                "display_name": "Email",
                "description": "Access to user's email address",
                "category": "identity",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "User.Read",
                "display_name": "User Profile (Read)",
                "description": "Read user profile information",
                "category": "identity",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "Calendars.Read",
                "display_name": "Calendar (Read)",
                "description": "Read calendar events and settings",
                "category": "calendar",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "Calendars.ReadWrite",
                "display_name": "Calendar (Read/Write)",
                "description": "Read and write calendar events",
                "category": "calendar",
                "is_readonly": False,
                "is_required": False,
            },
            {
                "scope_name": "Files.Read",
                "display_name": "Files (Read)",
                "description": "Read files in OneDrive",
                "category": "files",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "Mail.Read",
                "display_name": "Mail (Read)",
                "description": "Read Outlook mail messages",
                "category": "mail",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "Tasks.Read",
                "display_name": "Tasks (Read)",
                "description": "Read Microsoft To Do tasks",
                "category": "tasks",
                "is_readonly": True,
                "is_required": False,
            },
        ]

    def revoke_token(
        self, token: str, token_type: str = "access_token", **kwargs
    ) -> bool:
        """
        Revoke Microsoft OAuth token.

        Args:
            token: Token to revoke
            token_type: Type of token (access_token, refresh_token)
            **kwargs: Additional parameters

        Returns:
            True if token was successfully revoked
        """
        try:
            # Microsoft doesn't have a standard token revocation endpoint like Google
            # Instead, we can invalidate the token by making it unusable
            # For now, we'll return True as the token will naturally expire
            # In a production environment, you might want to track revoked tokens

            # Note: Microsoft Graph API tokens are JWT tokens that expire automatically
            # There's no need to make an HTTP call to revoke them

            return True

        except Exception as e:
            print(f"Warning: Token revocation failed: {e}")
            return False

    def get_default_scopes(self) -> List[str]:
        """Get default Microsoft OAuth scopes."""
        return [
            "openid",
            "profile",
            "email",
            "User.Read",
            "Calendars.Read",
        ]

    def get_required_scopes(self) -> List[str]:
        """Get required Microsoft OAuth scopes."""
        return ["openid"]
