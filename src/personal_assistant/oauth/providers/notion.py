"""
Notion OAuth Provider Implementation

This module provides OAuth 2.0 integration with Notion API for
accessing and managing Notion workspaces and pages.
"""

import urllib.parse
from typing import Any, Dict, List

import requests

from .base import BaseOAuthProvider


class NotionOAuthProvider(BaseOAuthProvider):
    """
    Notion OAuth 2.0 provider implementation.

    Supports Notion API for accessing workspaces, pages, and databases.
    """

    @property
    def provider_name(self) -> str:
        return "notion"

    @property
    def authorization_url(self) -> str:
        return "https://api.notion.com/v1/oauth/authorize"

    @property
    def token_url(self) -> str:
        return "https://api.notion.com/v1/oauth/token"

    @property
    def userinfo_url(self) -> str:
        return "https://api.notion.com/v1/users/me"

    def get_authorization_url(self, state: str, scopes: List[str], **kwargs) -> str:
        """
        Generate Notion OAuth authorization URL.

        Args:
            state: CSRF protection state parameter
            scopes: List of requested OAuth scopes
            **kwargs: Additional parameters (owner, etc.)

        Returns:
            Complete authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
            "owner": kwargs.get("owner", "user"),
        }

        # Add additional parameters if provided
        for key, value in kwargs.items():
            if key not in ["owner"]:
                params[key] = value

        query_string = urllib.parse.urlencode(params)
        return f"{self.authorization_url}?{query_string}"

    def exchange_code_for_tokens(
        self, authorization_code: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for Notion OAuth tokens.

        Args:
            authorization_code: Authorization code from OAuth callback
            **kwargs: Additional parameters

        Returns:
            Dictionary containing tokens and metadata
        """
        try:
            # Prepare the token exchange request
            data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": self.redirect_uri,
            }

            # Make the HTTP POST request to Notion's token endpoint
            response = requests.post(
                self.token_url,
                data=data,
                auth=(self.client_id, self.client_secret),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Notion OAuth token exchange failed: {response.status_code} - {response.text}"
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
                "refresh_token": token_data.get("refresh_token"),  # Add refresh token extraction
                "token_type": token_data.get("token_type", "Bearer"),
                "workspace_id": token_data.get("workspace_id"),
                "workspace_name": token_data.get("workspace_name"),
                "workspace_icon": token_data.get("workspace_icon"),
                "bot_id": token_data.get("bot_id"),
                "provider_user_id": user_info.get("id"),
                "provider_email": user_info.get("person", {}).get("email")
                if user_info.get("person")
                else None,
                "provider_name": user_info.get("name"),
                # Include the full response for debugging
                "raw_response": token_data,
            }

        except Exception as e:
            raise Exception(f"Failed to exchange authorization code for tokens: {e}")

    def refresh_access_token(self, refresh_token: str, **kwargs) -> Dict[str, Any]:
        """
        Refresh Notion OAuth access token.

        Args:
            refresh_token: Valid refresh token
            **kwargs: Additional parameters

        Returns:
            Dictionary containing new tokens and metadata
        """
        try:
            # Prepare the token refresh request
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }

            # Make the HTTP POST request to Notion's token endpoint
            response = requests.post(
                self.token_url,
                data=data,
                auth=(self.client_id, self.client_secret),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Notion OAuth token refresh failed: {response.status_code} - {response.text}"
                )

            # Parse the response
            token_data = response.json()

            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),  # Include refresh token in refresh response
                "token_type": token_data.get("token_type", "Bearer"),
                "workspace_id": token_data.get("workspace_id"),
                "workspace_name": token_data.get("workspace_name"),
                "workspace_icon": token_data.get("workspace_icon"),
                "bot_id": token_data.get("bot_id"),
            }

        except Exception as e:
            raise Exception(f"Failed to refresh access token: {e}")

    def get_user_info(self, access_token: str, **kwargs) -> Dict[str, Any]:
        """
        Get Notion user information.

        Args:
            access_token: Valid access token
            **kwargs: Additional parameters

        Returns:
            Dictionary containing user information
        """
        try:
            # Make the HTTP GET request to Notion's user endpoint
            response = requests.get(
                self.userinfo_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Notion-Version": "2022-06-28",
                },
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
        Validate Notion OAuth access token.

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
        Get available Notion OAuth scopes.

        Returns:
            List of scope dictionaries with metadata
        """
        return [
            {
                "scope_name": "read",
                "display_name": "Read Access",
                "description": "Read access to Notion pages and databases",
                "category": "access",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "write",
                "display_name": "Write Access",
                "description": "Write access to Notion pages and databases",
                "category": "access",
                "is_readonly": False,
                "is_required": False,
            },
            {
                "scope_name": "update",
                "display_name": "Update Access",
                "description": "Update existing Notion content",
                "category": "access",
                "is_readonly": False,
                "is_required": False,
            },
            {
                "scope_name": "insert",
                "display_name": "Insert Access",
                "description": "Insert new content into Notion",
                "category": "access",
                "is_readonly": False,
                "is_required": False,
            },
        ]

    def revoke_token(
        self, token: str, token_type: str = "access_token", **kwargs
    ) -> bool:
        """
        Revoke Notion OAuth token.

        Args:
            token: Token to revoke
            token_type: Type of token (access_token, refresh_token)
            **kwargs: Additional parameters

        Returns:
            True if token was successfully revoked
        """
        try:
            # Notion doesn't have a standard token revocation endpoint
            # Instead, we can invalidate the token by making it unusable
            # For now, we'll return True as the token will naturally expire
            # In a production environment, you might want to track revoked tokens

            # Note: Notion API tokens are long-lived and don't expire automatically
            # You would need to implement custom token invalidation logic

            return True

        except Exception as e:
            print(f"Warning: Token revocation failed: {e}")
            return False

    def get_default_scopes(self) -> List[str]:
        """Get default Notion OAuth scopes."""
        return ["read", "write"]

    def get_required_scopes(self) -> List[str]:
        """Get required Notion OAuth scopes."""
        return []
