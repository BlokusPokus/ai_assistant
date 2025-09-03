"""
External API Mock Implementations

This module provides comprehensive mocks for external APIs including
Twilio SMS, OAuth providers, and other third-party services.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from unittest.mock import AsyncMock, Mock, patch
import asyncio


class TwilioSMSMock:
    """Mock implementation for Twilio SMS API."""
    
    def __init__(self):
        self.messages = []
        self.accounts = []
        self.phone_numbers = []
        self._setup_default_data()
    
    def _setup_default_data(self):
        """Set up default mock data."""
        self.accounts = [
            {
                "sid": "AC1234567890abcdef1234567890abcdef",
                "friendly_name": "Test Account",
                "status": "active",
                "type": "Trial"
            }
        ]
        
        self.phone_numbers = [
            {
                "sid": "PN1234567890abcdef1234567890abcdef",
                "phone_number": "+1234567890",
                "friendly_name": "Test Phone Number",
                "capabilities": {
                    "sms": True,
                    "voice": True,
                    "mms": True
                }
            }
        ]
    
    def create_message(self, to: str, from_: str, body: str, **kwargs) -> Dict[str, Any]:
        """Mock message creation."""
        message = {
            "sid": f"SM{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "to": to,
            "from_": from_,
            "body": body,
            "status": "queued",
            "date_created": datetime.now().isoformat(),
            "date_updated": datetime.now().isoformat(),
            "date_sent": None,
            "error_code": None,
            "error_message": None,
            "price": "0.0075",
            "price_unit": "USD",
            "direction": "outbound-api",
            "messaging_service_sid": kwargs.get("messaging_service_sid"),
            "media": kwargs.get("media", []),
            "num_segments": "1",
            "num_media": "0"
        }
        
        self.messages.append(message)
        return message
    
    def get_message(self, sid: str) -> Optional[Dict[str, Any]]:
        """Mock message retrieval."""
        for message in self.messages:
            if message["sid"] == sid:
                return message
        return None
    
    def list_messages(self, **filters) -> List[Dict[str, Any]]:
        """Mock message listing."""
        filtered_messages = self.messages.copy()
        
        if "to" in filters:
            filtered_messages = [m for m in filtered_messages if m["to"] == filters["to"]]
        if "from_" in filters:
            filtered_messages = [m for m in filtered_messages if m["from_"] == filters["from_"]]
        if "date_sent_after" in filters:
            filtered_messages = [m for m in filtered_messages if m["date_created"] >= filters["date_sent_after"]]
        
        return filtered_messages
    
    def get_account(self, sid: str = None) -> Optional[Dict[str, Any]]:
        """Mock account retrieval."""
        if sid:
            for account in self.accounts:
                if account["sid"] == sid:
                    return account
            return None
        return self.accounts[0] if self.accounts else None
    
    def get_phone_number(self, sid: str) -> Optional[Dict[str, Any]]:
        """Mock phone number retrieval."""
        for phone_number in self.phone_numbers:
            if phone_number["sid"] == sid:
                return phone_number
        return None


class OAuthProviderMock:
    """Mock implementation for OAuth providers."""
    
    def __init__(self, provider_name: str = "google"):
        self.provider_name = provider_name
        self.tokens = {}
        self.users = {}
        self.authorizations = {}
        self._setup_default_data()
    
    def _setup_default_data(self):
        """Set up default mock data."""
        self.users = {
            "user123": {
                "id": "user123",
                "email": "test@example.com",
                "name": "Test User",
                "picture": "https://example.com/avatar.jpg",
                "verified_email": True,
                "locale": "en"
            }
        }
        
        self.authorizations = {
            "auth123": {
                "code": "auth123",
                "state": "state123",
                "user_id": "user123",
                "provider": self.provider_name,
                "scopes": ["read", "write"],
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
            }
        }
    
    def get_authorization_url(self, client_id: str, redirect_uri: str, 
                            scopes: List[str], state: str = None) -> str:
        """Mock authorization URL generation."""
        auth_code = f"auth{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.authorizations[auth_code] = {
            "code": auth_code,
            "state": state or "default_state",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scopes": scopes,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
        }
        
        return f"https://{self.provider_name}.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={'+'.join(scopes)}&state={state}&response_type=code"
    
    def exchange_code_for_token(self, code: str, client_id: str, 
                               client_secret: str, redirect_uri: str) -> Dict[str, Any]:
        """Mock token exchange."""
        if code not in self.authorizations:
            raise ValueError("Invalid authorization code")
        
        auth = self.authorizations[code]
        if auth["client_id"] != client_id:
            raise ValueError("Invalid client ID")
        
        # Generate tokens
        access_token = f"access_token_{code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        refresh_token = f"refresh_token_{code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": " ".join(auth["scopes"]),
            "created_at": datetime.now().isoformat()
        }
        
        self.tokens[access_token] = {
            **token_data,
            "user_id": auth.get("user_id", "user123"),
            "provider": self.provider_name
        }
        
        return token_data
    
    def refresh_token(self, refresh_token: str, client_id: str, 
                     client_secret: str) -> Dict[str, Any]:
        """Mock token refresh."""
        # Find the token
        for token_data in self.tokens.values():
            if token_data.get("refresh_token") == refresh_token:
                # Generate new access token
                new_access_token = f"access_token_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                new_token_data = {
                    "access_token": new_access_token,
                    "refresh_token": refresh_token,  # Keep the same refresh token
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": token_data["scope"],
                    "created_at": datetime.now().isoformat()
                }
                
                # Update tokens
                del self.tokens[token_data["access_token"]]
                self.tokens[new_access_token] = {
                    **new_token_data,
                    "user_id": token_data["user_id"],
                    "provider": token_data["provider"]
                }
                
                return new_token_data
        
        raise ValueError("Invalid refresh token")
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Mock user info retrieval."""
        if access_token not in self.tokens:
            raise ValueError("Invalid access token")
        
        token_data = self.tokens[access_token]
        user_id = token_data["user_id"]
        
        if user_id not in self.users:
            raise ValueError("User not found")
        
        return self.users[user_id]
    
    def revoke_token(self, access_token: str) -> bool:
        """Mock token revocation."""
        if access_token in self.tokens:
            del self.tokens[access_token]
            return True
        return False


class EmailServiceMock:
    """Mock implementation for email services."""
    
    def __init__(self):
        self.sent_emails = []
        self.templates = {}
        self._setup_default_templates()
    
    def _setup_default_templates(self):
        """Set up default email templates."""
        self.templates = {
            "welcome": {
                "subject": "Welcome to Personal Assistant",
                "html": "<h1>Welcome!</h1><p>Thank you for joining us.</p>",
                "text": "Welcome! Thank you for joining us."
            },
            "password_reset": {
                "subject": "Password Reset Request",
                "html": "<h1>Password Reset</h1><p>Click <a href='{reset_link}'>here</a> to reset your password.</p>",
                "text": "Password Reset: {reset_link}"
            },
            "verification": {
                "subject": "Email Verification",
                "html": "<h1>Verify Your Email</h1><p>Click <a href='{verification_link}'>here</a> to verify your email.</p>",
                "text": "Email Verification: {verification_link}"
            }
        }
    
    def send_email(self, to: str, subject: str, html: str = None, 
                   text: str = None, from_email: str = None, **kwargs) -> Dict[str, Any]:
        """Mock email sending."""
        email = {
            "id": f"email_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "to": to,
            "from": from_email or "noreply@personalassistant.com",
            "subject": subject,
            "html": html,
            "text": text,
            "status": "sent",
            "sent_at": datetime.now().isoformat(),
            "metadata": kwargs
        }
        
        self.sent_emails.append(email)
        return email
    
    def send_template_email(self, to: str, template_name: str, 
                           template_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Mock template email sending."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        template_data = template_data or {}
        
        # Format template with data
        subject = template["subject"].format(**template_data)
        html = template["html"].format(**template_data)
        text = template["text"].format(**template_data)
        
        return self.send_email(to, subject, html, text, **kwargs)
    
    def get_sent_emails(self, to: str = None, from_date: datetime = None) -> List[Dict[str, Any]]:
        """Mock email retrieval."""
        filtered_emails = self.sent_emails.copy()
        
        if to:
            filtered_emails = [e for e in filtered_emails if e["to"] == to]
        if from_date:
            filtered_emails = [e for e in filtered_emails if e["sent_at"] >= from_date.isoformat()]
        
        return filtered_emails


class FileStorageMock:
    """Mock implementation for file storage services."""
    
    def __init__(self):
        self.files = {}
        self.buckets = {}
        self._setup_default_buckets()
    
    def _setup_default_buckets(self):
        """Set up default storage buckets."""
        self.buckets = {
            "user-uploads": {
                "name": "user-uploads",
                "created_at": datetime.now().isoformat(),
                "size_bytes": 0,
                "file_count": 0
            },
            "temp-files": {
                "name": "temp-files",
                "created_at": datetime.now().isoformat(),
                "size_bytes": 0,
                "file_count": 0
            }
        }
    
    def upload_file(self, file_path: str, content: bytes, 
                   bucket: str = "user-uploads", **metadata) -> Dict[str, Any]:
        """Mock file upload."""
        file_id = f"file_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        file_data = {
            "id": file_id,
            "path": file_path,
            "bucket": bucket,
            "size_bytes": len(content),
            "content_type": metadata.get("content_type", "application/octet-stream"),
            "uploaded_at": datetime.now().isoformat(),
            "metadata": metadata,
            "url": f"https://storage.example.com/{bucket}/{file_id}",
            "checksum": f"checksum_{hash(content)}"
        }
        
        self.files[file_id] = file_data
        
        # Update bucket stats
        if bucket in self.buckets:
            self.buckets[bucket]["size_bytes"] += len(content)
            self.buckets[bucket]["file_count"] += 1
        
        return file_data
    
    def download_file(self, file_id: str) -> Dict[str, Any]:
        """Mock file download."""
        if file_id not in self.files:
            raise ValueError(f"File '{file_id}' not found")
        
        file_data = self.files[file_id]
        return {
            "id": file_id,
            "content": b"mock file content",  # In real implementation, this would be the actual content
            "metadata": file_data,
            "downloaded_at": datetime.now().isoformat()
        }
    
    def delete_file(self, file_id: str) -> bool:
        """Mock file deletion."""
        if file_id not in self.files:
            return False
        
        file_data = self.files[file_id]
        bucket = file_data["bucket"]
        
        # Update bucket stats
        if bucket in self.buckets:
            self.buckets[bucket]["size_bytes"] -= file_data["size_bytes"]
            self.buckets[bucket]["file_count"] -= 1
        
        del self.files[file_id]
        return True
    
    def list_files(self, bucket: str = None, prefix: str = None) -> List[Dict[str, Any]]:
        """Mock file listing."""
        filtered_files = list(self.files.values())
        
        if bucket:
            filtered_files = [f for f in filtered_files if f["bucket"] == bucket]
        if prefix:
            filtered_files = [f for f in filtered_files if f["path"].startswith(prefix)]
        
        return filtered_files
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Mock file metadata retrieval."""
        return self.files.get(file_id)


class ExternalAPIMockManager:
    """Manager for all external API mocks."""
    
    def __init__(self):
        self.twilio_sms = TwilioSMSMock()
        self.oauth_providers = {
            "google": OAuthProviderMock("google"),
            "microsoft": OAuthProviderMock("microsoft"),
            "notion": OAuthProviderMock("notion"),
            "youtube": OAuthProviderMock("youtube")
        }
        self.email_service = EmailServiceMock()
        self.file_storage = FileStorageMock()
    
    def get_oauth_provider(self, provider_name: str) -> OAuthProviderMock:
        """Get OAuth provider mock."""
        if provider_name not in self.oauth_providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        return self.oauth_providers[provider_name]
    
    def reset_all_mocks(self):
        """Reset all mocks to initial state."""
        self.twilio_sms = TwilioSMSMock()
        self.oauth_providers = {
            "google": OAuthProviderMock("google"),
            "microsoft": OAuthProviderMock("microsoft"),
            "notion": OAuthProviderMock("notion"),
            "youtube": OAuthProviderMock("youtube")
        }
        self.email_service = EmailServiceMock()
        self.file_storage = FileStorageMock()
    
    def get_mock_statistics(self) -> Dict[str, Any]:
        """Get statistics about mock usage."""
        return {
            "twilio_sms": {
                "messages_sent": len(self.twilio_sms.messages),
                "accounts": len(self.twilio_sms.accounts),
                "phone_numbers": len(self.twilio_sms.phone_numbers)
            },
            "oauth_providers": {
                provider: {
                    "tokens_issued": len(provider_mock.tokens),
                    "authorizations": len(provider_mock.authorizations),
                    "users": len(provider_mock.users)
                }
                for provider, provider_mock in self.oauth_providers.items()
            },
            "email_service": {
                "emails_sent": len(self.email_service.sent_emails),
                "templates": len(self.email_service.templates)
            },
            "file_storage": {
                "files_uploaded": len(self.file_storage.files),
                "buckets": len(self.file_storage.buckets)
            }
        }


# Global mock manager instance
mock_manager = ExternalAPIMockManager()


def get_twilio_sms_mock():
    """Get Twilio SMS mock."""
    return mock_manager.twilio_sms


def get_oauth_provider_mock(provider_name: str):
    """Get OAuth provider mock."""
    return mock_manager.get_oauth_provider(provider_name)


def get_email_service_mock():
    """Get email service mock."""
    return mock_manager.email_service


def get_file_storage_mock():
    """Get file storage mock."""
    return mock_manager.file_storage


def reset_all_external_mocks():
    """Reset all external API mocks."""
    mock_manager.reset_all_mocks()


def get_mock_statistics():
    """Get mock usage statistics."""
    return mock_manager.get_mock_statistics()

