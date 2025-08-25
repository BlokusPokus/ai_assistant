"""
Microsoft OAuth Provider Implementation

This module provides OAuth 2.0 integration with Microsoft Graph API including
Outlook Calendar, OneDrive, and Microsoft 365 services.
"""

import urllib.parse
from typing import Dict, List, Any
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

    def get_authorization_url(
        self, 
        state: str, 
        scopes: List[str],
        **kwargs
    ) -> str:
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
        return f"{self.authorization_url}?{query_string}"

    def exchange_code_for_tokens(
        self, 
        authorization_code: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for Microsoft OAuth tokens.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing tokens and metadata
        """
        # This is a placeholder implementation
        # In a real implementation, this would make an HTTP POST request to Microsoft's token endpoint
        return {
            "access_token": "placeholder_access_token",
            "refresh_token": "placeholder_refresh_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": kwargs.get("scope", ""),
        }

    def refresh_access_token(
        self, 
        refresh_token: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Refresh Microsoft OAuth access token.
        
        Args:
            refresh_token: Valid refresh token
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing new tokens and metadata
        """
        # This is a placeholder implementation
        # In a real implementation, this would make an HTTP POST request to Microsoft's token endpoint
        return {
            "access_token": "placeholder_new_access_token",
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def get_user_info(
        self, 
        access_token: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get Microsoft user information.
        
        Args:
            access_token: Valid access token
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing user information
        """
        # This is a placeholder implementation
        # In a real implementation, this would make an HTTP GET request to Microsoft Graph API
        return {
            "id": "placeholder_user_id",
            "mail": "placeholder@example.com",
            "displayName": "Placeholder User",
            "givenName": "Placeholder",
            "surname": "User",
            "userPrincipalName": "placeholder@example.com",
        }

    def validate_token(
        self, 
        access_token: str,
        **kwargs
    ) -> bool:
        """
        Validate Microsoft OAuth access token.
        
        Args:
            access_token: Access token to validate
            **kwargs: Additional parameters
            
        Returns:
            True if token is valid, False otherwise
        """
        # This is a placeholder implementation
        # In a real implementation, this would make an HTTP GET request to validate the token
        return True

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
        self, 
        token: str,
        token_type: str = "access_token",
        **kwargs
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
        # This is a placeholder implementation
        # In a real implementation, this would make an HTTP POST request to Microsoft's revoke endpoint
        return True

    def get_default_scopes(self) -> List[str]:
        """Get default Microsoft OAuth scopes."""
        return [
            "openid",
            "profile",
            "email",
            "User.Read",
        ]

    def get_required_scopes(self) -> List[str]:
        """Get required Microsoft OAuth scopes."""
        return ["openid"]
