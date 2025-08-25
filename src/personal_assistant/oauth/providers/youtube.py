"""
YouTube OAuth Provider Implementation

This module provides OAuth 2.0 integration with YouTube Data API for
accessing YouTube videos, channels, and playlists.
"""

import urllib.parse
import requests
from typing import Dict, List, Any
from .base import BaseOAuthProvider


class YouTubeOAuthProvider(BaseOAuthProvider):
    """
    YouTube OAuth 2.0 provider implementation.

    Supports YouTube Data API for accessing videos, channels, and playlists.
    Note: YouTube uses Google OAuth 2.0, so this is essentially a wrapper.
    """

    @property
    def provider_name(self) -> str:
        return "youtube"

    @property
    def authorization_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"

    @property
    def userinfo_url(self) -> str:
        return "https://www.googleapis.com/youtube/v3/channels"

    def get_authorization_url(
        self,
        state: str,
        scopes: List[str],
        **kwargs
    ) -> str:
        """
        Generate YouTube OAuth authorization URL.

        Args:
            state: CSRF protection state parameter
            scopes: List of requested OAuth scopes
            **kwargs: Additional parameters (access_type, prompt, etc.)

        Returns:
            Complete authorization URL
        """
        # YouTube uses Google OAuth, so we need YouTube-specific scopes
        youtube_scopes = [scope for scope in scopes if "youtube" in scope]
        if not youtube_scopes:
            youtube_scopes = [
                "https://www.googleapis.com/auth/youtube.readonly"]

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(youtube_scopes),
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
        self,
        authorization_code: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for YouTube OAuth tokens.

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
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(
                    f"YouTube OAuth token exchange failed: {response.status_code} - {response.text}")

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
                "provider_name": user_info.get("snippet", {}).get("title") if user_info.get("snippet") else None,
                "provider_email": None,  # YouTube doesn't provide email in channel info
                # Include the full response for debugging
                "raw_response": token_data
            }

        except Exception as e:
            raise Exception(
                f"Failed to exchange authorization code for tokens: {e}")

    def refresh_access_token(
        self,
        refresh_token: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Refresh YouTube OAuth access token.

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
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(
                    f"YouTube OAuth token refresh failed: {response.status_code} - {response.text}")

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

    def get_user_info(
        self,
        access_token: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get YouTube user information.

        Args:
            access_token: Valid access token
            **kwargs: Additional parameters

        Returns:
            Dictionary containing user information
        """
        try:
            # Make the HTTP GET request to YouTube Data API
            # We need to get the authenticated user's channel info
            params = {
                "part": "snippet,statistics",
                "mine": "true"  # Get the authenticated user's channel
            }

            response = requests.get(
                self.userinfo_url,
                params=params,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                },
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(
                    f"Failed to get user info: {response.status_code} - {response.text}")

            data = response.json()

            # YouTube API returns items array, get the first (and usually only) channel
            if data.get("items") and len(data["items"]) > 0:
                return data["items"][0]
            else:
                # Fallback to placeholder data if no channel found
                return {
                    "kind": "youtube#channel",
                    "id": "unknown",
                    "snippet": {
                        "title": "Unknown Channel",
                        "description": "No channel information available",
                        "customUrl": "@unknown",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "thumbnails": {
                            "default": {
                                "url": "https://example.com/placeholder.jpg",
                                "width": 88,
                                "height": 88
                            }
                        }
                    },
                    "statistics": {
                        "viewCount": "0",
                        "subscriberCount": "0",
                        "hiddenSubscriberCount": False,
                        "videoCount": "0"
                    }
                }

        except Exception as e:
            raise Exception(f"Failed to get user info: {e}")

    def validate_token(
        self,
        access_token: str,
        **kwargs
    ) -> bool:
        """
        Validate YouTube OAuth access token.

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
        Get available YouTube OAuth scopes.

        Returns:
            List of scope dictionaries with metadata
        """
        return [
            {
                "scope_name": "https://www.googleapis.com/auth/youtube.readonly",
                "display_name": "YouTube (Read Only)",
                "description": "View YouTube videos, channels, and playlists",
                "category": "youtube",
                "is_readonly": True,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/youtube",
                "display_name": "YouTube (Read/Write)",
                "description": "Manage YouTube videos, channels, and playlists",
                "category": "youtube",
                "is_readonly": False,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/youtube.upload",
                "display_name": "YouTube Upload",
                "description": "Upload videos to YouTube",
                "category": "youtube",
                "is_readonly": False,
                "is_required": False,
            },
            {
                "scope_name": "https://www.googleapis.com/auth/youtube.force-ssl",
                "display_name": "YouTube Force SSL",
                "description": "Force SSL for YouTube API calls",
                "category": "youtube",
                "is_readonly": True,
                "is_required": False,
            },
        ]

    def revoke_token(
        self,
        token: str,
        token_type: str = "access_token",
        **kwargs
    ) -> bool:
        """
        Revoke YouTube OAuth token.

        Args:
            token: Token to revoke
            token_type: Type of token (access_token, refresh_token)
            **kwargs: Additional parameters

        Returns:
            True if token was successfully revoked
        """
        try:
            # YouTube uses Google OAuth, so we can use Google's token revocation endpoint
            revoke_url = "https://oauth2.googleapis.com/revoke"

            # Make the HTTP POST request to Google's revoke endpoint
            response = requests.post(
                revoke_url,
                data={"token": token},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )

            # Google returns 200 for successful revocation
            if response.status_code == 200:
                return True
            else:
                print(
                    f"Warning: Token revocation returned status {response.status_code}")
                return False

        except Exception as e:
            print(f"Warning: Token revocation failed: {e}")
            return False

    def get_default_scopes(self) -> List[str]:
        """Get default YouTube OAuth scopes."""
        return [
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]

    def get_required_scopes(self) -> List[str]:
        """Get required YouTube OAuth scopes."""
        return []
