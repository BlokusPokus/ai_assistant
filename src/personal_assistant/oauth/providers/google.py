"""
Google OAuth Provider Implementation

This module provides OAuth 2.0 integration with Google APIs including
Google Calendar, Drive, Gmail, and YouTube Data API.
"""

import urllib.parse
from typing import Any, Dict, List

import requests

from .base import BaseOAuthProvider


class GoogleOAuthProvider(BaseOAuthProvider):
    """
    Google OAuth 2.0 provider implementation.

    Supports Google APIs including Calendar, Drive, Gmail, and YouTube Data API.
    """

    @property
    def provider_name(self) -> str:
        return "google"

    @property
    def authorization_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"

    @property
    def userinfo_url(self) -> str:
        return "https://www.googleapis.com/oauth2/v2/userinfo"

    def get_authorization_url(self, state: str, scopes: List[str], **kwargs) -> str:
        """
        Generate Google OAuth authorization URL.

        Args:
            state: CSRF protection state parameter
            scopes: List of requested OAuth scopes
            **kwargs: Additional parameters (access_type, prompt, etc.)

        Returns:
            Complete authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
            "access_type": kwargs.get("access_type", "offline"),
            "prompt": kwargs.get("prompt", "consent"),
        }

        # Add additional parameters if provided
        for key, value in kwargs.items():
            if key not in ["access_type", "prompt"]:
                params[key] = value

        query_string = urllib.parse.urlencode(params)
        return f"{self.authorization_url}?{query_string}"

    def exchange_code_for_tokens(
        self, authorization_code: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for Google OAuth tokens.

        Args:
            authorization_code: Authorization code from OAuth callback
            **kwargs: Additional parameters

        Returns:
            Dictionary containing tokens and metadata
        """
        try:
            # Prepare the token exchange request
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            }

            # Make the HTTP POST request to Google's token endpoint
            response = requests.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Google OAuth token exchange failed: {response.status_code} - {response.text}"
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
                "expires_in": token_data.get("expires_in", 604800),  # Default 7 days instead of 1 hour
                "scope": token_data.get("scope", ""),
                "provider_user_id": user_info.get("id"),
                "provider_email": user_info.get("email"),
                "provider_name": user_info.get("name"),
                # Include the full response for debugging
                "raw_response": token_data,
            }

        except Exception as e:
            raise Exception(f"Failed to exchange authorization code for tokens: {e}")

    def refresh_access_token(self, refresh_token: str, **kwargs) -> Dict[str, Any]:
        """
        Refresh Google OAuth access token.

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

            # Make the HTTP POST request to Google's token endpoint
            response = requests.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Google OAuth token refresh failed: {response.status_code} - {response.text}"
                )

            # Parse the response
            token_data = response.json()

            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": refresh_token,  # Keep the original refresh token
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": token_data.get("expires_in", 604800),  # Default 7 days instead of 1 hour
                "scope": token_data.get("scope", ""),
            }

        except Exception as e:
            raise Exception(f"Failed to refresh access token: {e}")

    def get_user_info(self, access_token: str, **kwargs) -> Dict[str, Any]:
        """
        Get Google user information.

        Args:
            access_token: Valid access token
            **kwargs: Additional parameters

        Returns:
            Dictionary containing user information
        """
        try:
            # Make the HTTP GET request to Google's userinfo endpoint
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
        Validate Google OAuth access token.

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
        Get available Google OAuth scopes.

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
                "scope_name": "https://www.googleapis.com/auth/userinfo.email",
                "display_name": "Email Address",
                "description": "Access to user's email address",
                "category": "identity",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/userinfo.profile",
                "display_name": "Profile Information",
                "description": "Access to user's basic profile information",
                "category": "identity",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/calendar.readonly",
                "display_name": "Calendar (Read Only)",
                "description": "View calendar events and settings",
                "category": "calendar",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/calendar.events",
                "display_name": "Calendar Events",
                "description": "View and manage calendar events",
                "category": "calendar",
                "is_readonly": False,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/drive.readonly",
                "display_name": "Google Drive (Read Only)",
                "description": "View files in Google Drive",
                "category": "drive",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/gmail.readonly",
                "display_name": "Gmail (Read Only)",
                "description": "View Gmail messages and settings",
                "category": "mail",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/gmail.send",
                "display_name": "Gmail Send",
                "description": "Send emails via Gmail",
                "category": "mail",
                "is_readonly": False,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/youtube.readonly",
                "display_name": "YouTube (Read Only)",
                "description": "View YouTube videos and channels",
                "category": "youtube",
                "is_readonly": True,
                "is_required": False,
            },
        ]

    def revoke_token(
        self, token: str, token_type: str = "access_token", **kwargs
    ) -> bool:
        """
        Revoke Google OAuth token.

        Args:
            token: Token to revoke
            token_type: Type of token (access_token, refresh_token)
            **kwargs: Additional parameters

        Returns:
            True if token was successfully revoked
        """
        # This is a placeholder implementation
        # In a real implementation, this would make an HTTP POST request to Google's revoke endpoint
        return True

    def get_default_scopes(self) -> List[str]:
        """Get default Google OAuth scopes."""
        return [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar.readonly",
        ]

    def get_required_scopes(self) -> List[str]:
        """Get required Google OAuth scopes."""
        return ["openid"]
