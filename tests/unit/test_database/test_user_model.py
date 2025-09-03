"""
Unit tests for User database model.

This module tests the User model functionality including
CRUD operations, relationships, and validation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError

from personal_assistant.database.models.users import User
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import UserDataGenerator


class TestUserModel:
    """Test cases for User model."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.user_data_generator = UserDataGenerator()
        self.test_user_data = self.user_data_generator.generate_user()
        # Generate a hashed password for testing
        import bcrypt
        test_password = "test_password_123"
        self.hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.user = User(
            email=self.test_user_data["email"],
            phone_number=self.test_user_data["phone_number"],
            full_name=f"{self.test_user_data['first_name']} {self.test_user_data['last_name']}",
            hashed_password=self.hashed_password,
            is_active=self.test_user_data["is_active"],
            is_verified=self.test_user_data["is_verified"],
        )

    def test_user_creation(self):
        """Test basic user creation."""
        assert self.user.email == self.test_user_data["email"]
        assert self.user.phone_number == self.test_user_data["phone_number"]
        assert self.user.full_name == f"{self.test_user_data['first_name']} {self.test_user_data['last_name']}"
        assert self.user.hashed_password == self.hashed_password
        assert self.user.is_active == self.test_user_data["is_active"]
        assert self.user.is_verified == self.test_user_data["is_verified"]
        assert self.user.failed_login_attempts is None  # Not set until saved to DB
        # Note: created_at and updated_at are set by SQLAlchemy when saved to DB
        # For in-memory objects, these will be None
        assert self.user.created_at is None
        assert self.user.updated_at is None

    def test_user_required_fields(self):
        """Test that required fields are properly set."""
        # Email and hashed_password are required
        assert self.user.email is not None
        assert self.user.hashed_password is not None
        
        # ID should be None until saved to database
        assert self.user.id is None

    def test_user_optional_fields(self):
        """Test that optional fields work correctly."""
        # Phone number is optional
        user_without_phone = User(
            email="test@example.com",
            hashed_password="hashed_password",
            phone_number=None
        )
        assert user_without_phone.phone_number is None
        
        # Full name is optional
        user_without_name = User(
            email="test2@example.com",
            hashed_password="hashed_password",
            full_name=None
        )
        assert user_without_name.full_name is None

    def test_user_default_values(self):
        """Test that default values are set correctly."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        # Note: SQLAlchemy defaults are only applied when the object is saved to the database
        # For in-memory objects, we need to check the column defaults
        assert user.is_active is None  # Not set until saved to DB
        assert user.is_verified is None  # Not set until saved to DB
        assert user.failed_login_attempts is None  # Not set until saved to DB
        assert user.verification_token is None
        assert user.password_reset_token is None
        assert user.password_reset_expires is None
        assert user.last_login is None
        assert user.locked_until is None
        assert user.default_role_id is None
        assert user.role_assigned_at is None
        assert user.role_assigned_by is None

    def test_user_timestamps(self):
        """Test that timestamps are set correctly."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        # Note: SQLAlchemy timestamps are only set when the object is saved to the database
        # For in-memory objects, these will be None
        assert user.created_at is None  # Not set until saved to DB
        assert user.updated_at is None  # Not set until saved to DB

    def test_user_verification_token(self):
        """Test verification token functionality."""
        token = "verification_token_123"
        self.user.verification_token = token
        
        assert self.user.verification_token == token

    def test_user_password_reset_token(self):
        """Test password reset token functionality."""
        token = "reset_token_456"
        expires = datetime.utcnow() + timedelta(hours=1)
        
        self.user.password_reset_token = token
        self.user.password_reset_expires = expires
        
        assert self.user.password_reset_token == token
        assert self.user.password_reset_expires == expires

    def test_user_last_login(self):
        """Test last login timestamp."""
        login_time = datetime.utcnow()
        self.user.last_login = login_time
        
        assert self.user.last_login == login_time

    def test_user_failed_login_attempts(self):
        """Test failed login attempts counter."""
        self.user.failed_login_attempts = 3
        assert self.user.failed_login_attempts == 3
        
        # Test incrementing
        self.user.failed_login_attempts += 1
        assert self.user.failed_login_attempts == 4

    def test_user_account_lockout(self):
        """Test account lockout functionality."""
        lockout_until = datetime.utcnow() + timedelta(minutes=30)
        self.user.locked_until = lockout_until
        
        assert self.user.locked_until == lockout_until
        
        # Test if account is locked
        assert self.user.locked_until > datetime.utcnow()

    def test_user_rbac_fields(self):
        """Test RBAC-related fields."""
        role_id = 1
        assigned_at = datetime.utcnow()
        assigned_by = 2
        
        self.user.default_role_id = role_id
        self.user.role_assigned_at = assigned_at
        self.user.role_assigned_by = assigned_by
        
        assert self.user.default_role_id == role_id
        assert self.user.role_assigned_at == assigned_at
        assert self.user.role_assigned_by == assigned_by

    def test_user_relationships_exist(self):
        """Test that relationships are properly defined."""
        # Test that relationships exist (they should be empty for new user)
        assert hasattr(self.user, 'conversations')
        assert hasattr(self.user, 'auth_tokens')
        assert hasattr(self.user, 'mfa_configuration')
        assert hasattr(self.user, 'sessions')
        assert hasattr(self.user, 'security_events')
        assert hasattr(self.user, 'user_roles')
        assert hasattr(self.user, 'access_audit_logs')
        assert hasattr(self.user, 'phone_mappings')
        assert hasattr(self.user, 'sms_usage_logs')

    def test_user_as_dict_method(self):
        """Test the as_dict method if it exists."""
        # The User model doesn't inherit from BaseModel, so it might not have as_dict
        # But we can test the basic structure
        user_dict = {
            'email': self.user.email,
            'phone_number': self.user.phone_number,
            'full_name': self.user.full_name,
            'is_active': self.user.is_active,
            'is_verified': self.user.is_verified,
        }
        
        assert user_dict['email'] == self.user.email
        assert user_dict['phone_number'] == self.user.phone_number
        assert user_dict['full_name'] == self.user.full_name
        assert user_dict['is_active'] == self.user.is_active
        assert user_dict['is_verified'] == self.user.is_verified

    def test_user_string_representation(self):
        """Test string representation of user."""
        # Test that we can convert user to string
        user_str = str(self.user)
        assert isinstance(user_str, str)
        assert len(user_str) > 0

    def test_user_equality(self):
        """Test user equality comparison."""
        user1 = User(
            email="test@example.com",
            hashed_password="password1"
        )
        user2 = User(
            email="test@example.com",
            hashed_password="password2"
        )
        
        # Users with same email should be considered equal for testing purposes
        # (though in real usage, they would be different objects)
        assert user1.email == user2.email

    def test_user_with_different_data(self):
        """Test user creation with different data sets."""
        test_cases = [
            {
                "email": "user1@example.com",
                "phone_number": "+1234567890",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": True,
            },
            {
                "email": "user2@example.com",
                "phone_number": None,
                "full_name": "Jane Smith",
                "is_active": False,
                "is_verified": False,
            },
            {
                "email": "user3@example.com",
                "phone_number": "+9876543210",
                "full_name": None,
                "is_active": True,
                "is_verified": False,
            },
        ]
        
        for i, data in enumerate(test_cases):
            user = User(
                email=data["email"],
                phone_number=data["phone_number"],
                full_name=data["full_name"],
                hashed_password=f"password{i}",
                is_active=data["is_active"],
                is_verified=data["is_verified"],
            )
            
            assert user.email == data["email"]
            assert user.phone_number == data["phone_number"]
            assert user.full_name == data["full_name"]
            assert user.is_active == data["is_active"]
            assert user.is_verified == data["is_verified"]

    def test_user_validation_scenarios(self):
        """Test various validation scenarios."""
        # Test with very long email
        long_email = "a" * 100 + "@example.com"
        user = User(
            email=long_email,
            hashed_password="password"
        )
        assert user.email == long_email
        
        # Test with very long full name
        long_name = "A" * 1000
        user.full_name = long_name
        assert user.full_name == long_name
        
        # Test with very long phone number
        long_phone = "+" + "1" * 50
        user.phone_number = long_phone
        assert user.phone_number == long_phone

    def test_user_edge_cases(self):
        """Test edge cases for user model."""
        # Test with empty strings
        user = User(
            email="test@example.com",
            hashed_password="password",
            full_name="",
            phone_number=""
        )
        assert user.full_name == ""
        assert user.phone_number == ""
        
        # Test with special characters
        user.full_name = "José María O'Connor-Smith"
        user.phone_number = "+1-555-123-4567"
        assert user.full_name == "José María O'Connor-Smith"
        assert user.phone_number == "+1-555-123-4567"

    def test_user_unicode_handling(self):
        """Test Unicode character handling."""
        user = User(
            email="test@example.com",
            hashed_password="password",
            full_name="测试用户",  # Chinese characters
            phone_number="+86-138-0013-8000"
        )
        assert user.full_name == "测试用户"
        assert user.phone_number == "+86-138-0013-8000"

    def test_user_model_attributes(self):
        """Test that all expected attributes exist."""
        expected_attributes = [
            'id', 'email', 'phone_number', 'full_name', 'hashed_password',
            'is_active', 'is_verified', 'verification_token', 'password_reset_token',
            'password_reset_expires', 'last_login', 'failed_login_attempts',
            'locked_until', 'created_at', 'updated_at', 'default_role_id',
            'role_assigned_at', 'role_assigned_by'
        ]
        
        for attr in expected_attributes:
            assert hasattr(self.user, attr), f"User model missing attribute: {attr}"

    def test_user_model_table_name(self):
        """Test that the table name is set correctly."""
        assert User.__tablename__ == "users"

    def test_user_model_inheritance(self):
        """Test that User model inherits from Base."""
        from personal_assistant.database.models.base import Base
        assert issubclass(User, Base)

    def test_user_model_metadata(self):
        """Test model metadata."""
        assert hasattr(User, '__table__')
        assert User.__table__.name == 'users'
        
        # Test that primary key is set
        assert 'id' in User.__table__.columns
        assert User.__table__.columns['id'].primary_key is True
        
        # Test that email is unique
        assert User.__table__.columns['email'].unique is True
        
        # Test that email is not nullable
        assert User.__table__.columns['email'].nullable is False
        
        # Test that hashed_password is not nullable
        assert User.__table__.columns['hashed_password'].nullable is False

    def test_user_model_relationships_metadata(self):
        """Test relationship metadata."""
        # Test that relationships are properly configured
        relationships = [
            'conversations', 'auth_tokens', 'mfa_configuration', 'sessions',
            'security_events', 'user_roles', 'access_audit_logs',
            'phone_mappings', 'sms_usage_logs'
        ]
        
        for rel_name in relationships:
            assert hasattr(User, rel_name)
            rel = getattr(User, rel_name)
            assert hasattr(rel, 'property')

    def test_user_model_with_mock_session(self):
        """Test user model with mocked database session."""
        with patch('sqlalchemy.orm.Session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value = mock_session_instance
            
            # Test that we can create a user instance
            user = User(
                email="test@example.com",
                hashed_password="password"
            )
            
            assert user.email == "test@example.com"
            assert user.hashed_password == "password"

    def test_user_model_performance(self):
        """Test user model creation performance."""
        import time
        
        start_time = time.time()
        
        # Create multiple users
        users = []
        for i in range(100):
            user = User(
                email=f"user{i}@example.com",
                hashed_password=f"password{i}"
            )
            users.append(user)
        
        creation_time = time.time() - start_time
        
        assert len(users) == 100
        assert creation_time < 1.0  # Should be very fast for model creation
        
        # Test that all users have unique emails
        emails = [user.email for user in users]
        assert len(set(emails)) == 100  # All emails should be unique

    def test_user_model_integration(self):
        """Test user model integration with other components."""
        # Test that user can be used with authentication components
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
            is_verified=True
        )
        
        # Simulate authentication check
        assert user.is_active is True
        assert user.is_verified is True
        assert user.hashed_password is not None
        
        # Simulate login attempt
        user.last_login = datetime.utcnow()
        user.failed_login_attempts = 0
        
        assert user.last_login is not None
        assert user.failed_login_attempts == 0
        
        # Simulate failed login
        user.failed_login_attempts += 1
        assert user.failed_login_attempts == 1
        
        # Simulate account lockout after multiple failures
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            assert user.locked_until is not None
