#!/usr/bin/env python3
"""
Basic tests for the authentication system.

This script tests the core authentication components:
- JWT service
- Password service
- Auth utilities
"""

from personal_assistant.auth.auth_utils import AuthUtils
from personal_assistant.auth.password_service import PasswordService
from personal_assistant.auth.jwt_service import JWTService
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_password_service():
    """Test password hashing and verification."""
    print("🧪 Testing Password Service...")

    password_service = PasswordService()

    # Test password validation
    try:
        password_service.hash_password("weak")
        print("❌ Should have rejected weak password")
        return False
    except Exception:
        print("  ✅ Rejected weak password")

    # Test strong password
    strong_password = "SecurePass123!"
    hashed = password_service.hash_password(strong_password)
    print(f"  ✅ Hashed strong password: {hashed[:20]}...")

    # Test verification
    assert password_service.verify_password(strong_password, hashed)
    print("  ✅ Password verification works")

    # Test wrong password
    assert not password_service.verify_password("WrongPass123!", hashed)
    print("  ✅ Wrong password correctly rejected")

    # Test password strength
    score, strength = password_service.get_password_strength(strong_password)
    print(f"  ✅ Password strength: {score}/100 ({strength})")

    return True


def test_jwt_service():
    """Test JWT token operations."""
    print("\n🧪 Testing JWT Service...")

    # Set a test secret key
    os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-testing-only'

    jwt_service = JWTService()

    # Test token creation
    user_data = {"user_id": 123, "email": "test@example.com",
                 "full_name": "Test User"}

    access_token = jwt_service.create_access_token(user_data)
    refresh_token = jwt_service.create_refresh_token(user_data)

    print(f"  ✅ Created access token: {access_token[:20]}...")
    print(f"  ✅ Created refresh token: {refresh_token[:20]}...")

    # Test token verification
    access_payload = jwt_service.verify_access_token(access_token)
    refresh_payload = jwt_service.verify_refresh_token(refresh_token)

    assert access_payload["user_id"] == 123
    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"
    print("  ✅ Token verification works")

    # Test token refresh
    new_access_token = jwt_service.refresh_access_token(refresh_token)
    new_payload = jwt_service.verify_access_token(new_access_token)
    assert new_payload["user_id"] == 123
    print("  ✅ Token refresh works")

    # Test expired token (this should fail)
    expired_data = user_data.copy()
    expired_data["exp"] = datetime.utcnow() - timedelta(minutes=1)
    expired_token = jwt_service.create_access_token(
        expired_data, timedelta(minutes=-1))

    try:
        jwt_service.verify_access_token(expired_token)
        print("❌ Should have rejected expired token")
        return False
    except Exception:
        print("  ✅ Rejected expired token")

    return True


def test_auth_utils():
    """Test authentication utilities."""
    print("\n🧪 Testing Auth Utils...")

    # Test user context creation
    user_context = AuthUtils.create_user_context(
        user_id=456,
        email="user@example.com",
        full_name="John Doe"
    )

    assert user_context["user_id"] == 456
    assert user_context["email"] == "user@example.com"
    assert user_context["full_name"] == "John Doe"
    print("  ✅ User context creation works")

    # Test user context validation
    try:
        AuthUtils.validate_user_context(456, 456)
        print("  ✅ User context validation works for same user")
    except Exception:
        print("❌ User context validation failed for same user")
        return False

    try:
        AuthUtils.validate_user_context(456, 789)
        print("❌ Should have rejected different user")
        return False
    except Exception:
        print("  ✅ User context validation correctly rejected different user")

    return True


def test_integration():
    """Test integration between services."""
    print("\n🧪 Testing Service Integration...")

    # Test complete flow: create user context -> generate tokens -> verify
    user_data = {"user_id": 789, "email": "integration@test.com",
                 "full_name": "Integration Test"}

    # Create JWT service
    os.environ['JWT_SECRET_KEY'] = 'integration-test-secret'
    jwt_service = JWTService()

    # Generate tokens
    access_token = jwt_service.create_access_token(user_data)
    refresh_token = jwt_service.create_refresh_token(user_data)

    # Verify tokens
    access_payload = jwt_service.verify_access_token(access_token)
    refresh_payload = jwt_service.verify_refresh_token(refresh_token)

    # Validate user context
    AuthUtils.validate_user_context(
        access_payload["user_id"],
        access_payload["user_id"]
    )

    print("  ✅ Complete authentication flow works")
    return True


async def main():
    """Run all tests."""
    print("🚀 Personal Assistant - Authentication System Tests")
    print("=" * 60)

    tests = [
        test_password_service,
        test_jwt_service,
        test_auth_utils,
        test_integration
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Authentication system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
