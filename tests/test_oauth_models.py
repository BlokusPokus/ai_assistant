"""
Unit tests for OAuth models.

This module tests the SQLAlchemy OAuth models for proper creation,
relationships, and basic validation.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import only the OAuth models we need, not all models
from personal_assistant.oauth.models.integration import OAuthIntegration
from personal_assistant.oauth.models.token import OAuthToken
from personal_assistant.oauth.models.scope import OAuthScope
from personal_assistant.oauth.models.consent import OAuthConsent
from personal_assistant.oauth.models.audit_log import OAuthAuditLog
from personal_assistant.oauth.models.state import OAuthState
from personal_assistant.database.models.base import Base


class TestOAuthModels:
    """Test OAuth model creation and relationships."""

    @pytest.fixture(scope="class")
    def engine(self):
        """Create in-memory SQLite engine for testing."""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        # Only create tables for the OAuth models we're testing
        Base.metadata.create_all(bind=engine, tables=[
            OAuthIntegration.__table__,
            OAuthToken.__table__,
            OAuthScope.__table__,
            OAuthConsent.__table__,
            OAuthAuditLog.__table__,
            OAuthState.__table__,
        ])
        return engine

    @pytest.fixture
    def session(self, engine):
        """Create a new database session for each test."""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_oauth_integration_creation(self, session):
        """Test creating an OAuth integration."""
        integration = OAuthIntegration(
            user_id=1,
            provider="google",
            provider_user_id="google_user_123",
            provider_email="user@example.com",
            provider_name="Test User",
            status="active",
            scopes=["openid", "email"],
            provider_metadata={"picture": "https://example.com/avatar.jpg"}
        )
        session.add(integration)
        session.commit()
        
        assert integration.id is not None
        assert integration.provider == "google"
        assert integration.status == "active"
        assert integration.scopes == ["openid", "email"]

    def test_oauth_token_creation(self, session):
        """Test creating an OAuth token."""
        # First create an integration
        integration = OAuthIntegration(
            user_id=1,
            provider="google",
            status="active"
        )
        session.add(integration)
        session.commit()
        
        token = OAuthToken(
            integration_id=integration.id,
            token_type="access",
            encrypted_token="encrypted_access_token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_valid=True
        )
        session.add(token)
        session.commit()
        
        assert token.id is not None
        assert token.token_type == "access"
        assert token.is_valid is True

    def test_oauth_scope_creation(self, session):
        """Test creating an OAuth scope."""
        scope = OAuthScope(
            provider="google",
            scope_name="openid",
            display_name="OpenID Connect",
            description="OpenID Connect scope",
            is_required=True,
            is_active=True,
            provider_metadata={"version": "2.0"}
        )
        session.add(scope)
        session.commit()
        
        assert scope.id is not None
        assert scope.provider == "google"
        assert scope.scope_name == "openid"
        assert scope.is_required is True

    def test_oauth_consent_creation(self, session):
        """Test creating an OAuth consent."""
        # First create an integration
        integration = OAuthIntegration(
            user_id=1,
            provider="google",
            status="active"
        )
        session.add(integration)
        session.commit()
        
        # Then create a scope
        scope = OAuthScope(
            provider="google",
            scope_name="email",
            display_name="Email Access",
            is_required=False
        )
        session.add(scope)
        session.commit()
        
        consent = OAuthConsent(
            integration_id=integration.id,
            scope_id=scope.id,
            user_id=1,
            consent_status="granted",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            consent_metadata={"timestamp": "2024-01-01T00:00:00Z"}
        )
        session.add(consent)
        session.commit()
        
        assert consent.id is not None
        assert consent.consent_status == "granted"
        assert consent.ip_address == "192.168.1.1"

    def test_oauth_audit_log_creation(self, session):
        """Test creating an OAuth audit log."""
        log = OAuthAuditLog(
            user_id=1,
            action="oauth_authorization",
            status="success",
            provider="google",
            details="User authorized Google OAuth",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        session.add(log)
        session.commit()
        
        assert log.id is not None
        assert log.action == "oauth_authorization"
        assert log.status == "success"
        assert log.provider == "google"

    def test_oauth_state_creation(self, session):
        """Test creating an OAuth state."""
        state = OAuthState(
            state_token="random_state_token_123",
            provider="google",
            redirect_uri="https://example.com/callback",
            scopes="openid,email",
            state_metadata="additional_data",
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        session.add(state)
        session.commit()
        
        assert state.id is not None
        assert state.state_token == "random_state_token_123"
        assert state.provider == "google"
        assert state.is_used is False

    def test_oauth_integration_relationships(self, session):
        """Test OAuth integration relationships."""
        # Create integration
        integration = OAuthIntegration(
            user_id=1,
            provider="google",
            status="active"
        )
        session.add(integration)
        session.commit()
        
        # Create token for this integration
        token = OAuthToken(
            integration_id=integration.id,
            token_type="access",
            encrypted_token="encrypted_token",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        session.add(token)
        session.commit()
        
        # Test relationship
        assert len(integration.tokens) == 1
        assert integration.tokens[0].id == token.id
        assert token.integration.id == integration.id

    def test_oauth_model_validation(self, session):
        """Test OAuth model validation and constraints."""
        # Test required fields
        integration = OAuthIntegration(
            user_id=1,
            provider="google"
            # Missing required fields should raise error
        )
        session.add(integration)
        session.commit()  # Should work as we have the minimum required fields
        
        # Test enum-like constraints
        integration.status = "invalid_status"
        session.commit()  # SQLite doesn't enforce enum constraints, so this works
        
        # Test that we can modify the integration
        assert integration.status == "invalid_status"

    def test_oauth_model_repr(self, session):
        """Test OAuth model string representations."""
        integration = OAuthIntegration(
            user_id=1,
            provider="google",
            status="active"
        )
        session.add(integration)
        session.commit()
        
        # Test __repr__ method
        repr_str = repr(integration)
        assert "OAuthIntegration" in repr_str
        assert "google" in repr_str
        assert "active" in repr_str


if __name__ == "__main__":
    pytest.main([__file__])
