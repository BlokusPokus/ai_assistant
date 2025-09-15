"""
OAuth Token Encryption Security Tests

This module tests OAuth token encryption and security features.
"""

import pytest
from unittest.mock import Mock, patch
from personal_assistant.oauth.services.token_service import OAuthTokenService
from personal_assistant.oauth.exceptions import OAuthTokenError


class TestOAuthTokenEncryption:
    """Test cases for OAuth token encryption security."""

    @pytest.fixture
    def token_service(self):
        """Provide an OAuthTokenService instance for testing."""
        return OAuthTokenService()

    def test_token_encryption_uniqueness(self, token_service):
        """Test that identical tokens produce different encrypted values."""
        plain_token = "test_token_123"
        
        # Encrypt the same token multiple times
        encrypted_tokens = []
        for _ in range(10):
            encrypted_token = token_service.encrypt_token(plain_token)
            encrypted_tokens.append(encrypted_token)
        
        # All encrypted tokens should be different (due to random IV)
        assert len(set(encrypted_tokens)) == 10
        
        # But all should decrypt to the same plain token
        for encrypted_token in encrypted_tokens:
            decrypted_token = token_service.decrypt_token(encrypted_token)
            assert decrypted_token == plain_token

    def test_token_encryption_different_tokens(self, token_service):
        """Test that different tokens produce different encrypted values."""
        token1 = "token_123"
        token2 = "token_456"
        
        encrypted1 = token_service.encrypt_token(token1)
        encrypted2 = token_service.encrypt_token(token2)
        
        # Different tokens should produce different encrypted values
        assert encrypted1 != encrypted2
        
        # Each should decrypt to its original value
        assert token_service.decrypt_token(encrypted1) == token1
        assert token_service.decrypt_token(encrypted2) == token2

    def test_token_encryption_length(self, token_service):
        """Test that encrypted tokens are longer than plain tokens."""
        plain_token = "short"
        encrypted_token = token_service.encrypt_token(plain_token)
        
        assert len(encrypted_token) > len(plain_token)
        
        # Encrypted token should be significantly longer due to base64 encoding and IV
        assert len(encrypted_token) > len(plain_token) * 2

    def test_token_encryption_special_characters(self, token_service):
        """Test token encryption with special characters."""
        special_tokens = [
            "token with spaces",
            "token-with-dashes",
            "token_with_underscores",
            "token.with.dots",
            "token/with/slashes",
            "token+with+pluses",
            "token=with=equals",
            "token?with?questions",
            "token&with&ampersands",
            "token#with#hashes",
            "token@with@ats",
            "token!with!exclamations",
            "token$with$dollars",
            "token%with%percents",
            "token^with^carets",
            "token*with*asterisks",
            "token(with)parentheses",
            "token[with]brackets",
            "token{with}braces",
            "token|with|pipes",
            "token\\with\\backslashes",
            "token\"with\"quotes",
            "token'with'apostrophes",
            "token`with`backticks",
            "token~with~tildes",
            "token<with>angles",
            "token,with,commas",
            "token;with;semicolons",
            "token:with:colons",
            "token\nwith\nnewlines",
            "token\twith\ttabs",
            "token\rwith\rcarriage",
            "token\x00with\x00nulls",
            "token\xffwith\xffbytes",
            "token\u0000with\u0000unicode",
            "token\u00ffwith\u00ffunicode",
            "token\u0100with\u0100unicode",
            "token\u1000with\u1000unicode",
            "token\u2000with\u2000unicode",
            "token\u3000with\u3000unicode",
            "token\u4000with\u4000unicode",
            "token\u5000with\u5000unicode",
            "token\u6000with\u6000unicode",
            "token\u7000with\u7000unicode",
            "token\u8000with\u8000unicode",
            "token\u9000with\u9000unicode",
            "token\ua000with\ua000unicode",
            "token\ub000with\ub000unicode",
            "token\uc000with\uc000unicode",
            "token\ud000with\ud000unicode",
            "token\ue000with\ue000unicode",
            "token\uf000with\uf000unicode",
            "token\uff00with\uff00unicode",
            "token\uffffwith\uffffunicode"
        ]
        
        for plain_token in special_tokens:
            encrypted_token = token_service.encrypt_token(plain_token)
            decrypted_token = token_service.decrypt_token(encrypted_token)
            assert decrypted_token == plain_token

    def test_token_encryption_empty_token(self, token_service):
        """Test token encryption with empty token."""
        empty_token = ""
        
        encrypted_token = token_service.encrypt_token(empty_token)
        decrypted_token = token_service.decrypt_token(encrypted_token)
        
        assert decrypted_token == empty_token

    def test_token_encryption_very_long_token(self, token_service):
        """Test token encryption with very long token."""
        # Create a very long token (10KB)
        long_token = "a" * 10000
        
        encrypted_token = token_service.encrypt_token(long_token)
        decrypted_token = token_service.decrypt_token(encrypted_token)
        
        assert decrypted_token == long_token

    def test_token_encryption_binary_data(self, token_service):
        """Test token encryption with binary data."""
        import base64
        
        # Create binary data
        binary_data = bytes(range(256))
        binary_token = base64.b64encode(binary_data).decode('utf-8')
        
        encrypted_token = token_service.encrypt_token(binary_token)
        decrypted_token = token_service.decrypt_token(encrypted_token)
        
        assert decrypted_token == binary_token

    def test_token_encryption_unicode_token(self, token_service):
        """Test token encryption with Unicode token."""
        unicode_token = "🔐🔑🔒🔓🔍🔎🔏🔐🔑🔒🔓🔍🔎🔏"
        
        encrypted_token = token_service.encrypt_token(unicode_token)
        decrypted_token = token_service.decrypt_token(encrypted_token)
        
        assert decrypted_token == unicode_token

    def test_token_encryption_error_handling(self, token_service):
        """Test token encryption error handling."""
        # Test with None
        with pytest.raises(OAuthTokenError) as exc_info:
            token_service.encrypt_token(None)
        assert "Failed to encrypt token" in str(exc_info.value)
        
        # Test with non-string
        with pytest.raises(OAuthTokenError) as exc_info:
            token_service.encrypt_token(123)
        assert "Failed to encrypt token" in str(exc_info.value)

    def test_token_decryption_error_handling(self, token_service):
        """Test token decryption error handling."""
        # Test with None
        with pytest.raises(OAuthTokenError) as exc_info:
            token_service.decrypt_token(None)
        assert "Failed to decrypt token" in str(exc_info.value)
        
        # Test with invalid encrypted token
        with pytest.raises(OAuthTokenError) as exc_info:
            token_service.decrypt_token("invalid_encrypted_token")
        assert "Failed to decrypt token" in str(exc_info.value)
        
        # Test with empty string
        with pytest.raises(OAuthTokenError) as exc_info:
            token_service.decrypt_token("")
        assert "Failed to decrypt token" in str(exc_info.value)

    def test_token_encryption_key_isolation(self, token_service):
        """Test that different token service instances use different keys."""
        token_service2 = OAuthTokenService()
        
        plain_token = "test_token_123"
        
        encrypted1 = token_service.encrypt_token(plain_token)
        encrypted2 = token_service2.encrypt_token(plain_token)
        
        # Different instances should produce different encrypted values
        assert encrypted1 != encrypted2
        
        # Each should decrypt correctly with its own instance
        assert token_service.decrypt_token(encrypted1) == plain_token
        assert token_service2.decrypt_token(encrypted2) == plain_token
        
        # Cross-decryption should fail
        with pytest.raises(OAuthTokenError):
            token_service.decrypt_token(encrypted2)
        
        with pytest.raises(OAuthTokenError):
            token_service2.decrypt_token(encrypted1)

    def test_token_encryption_performance(self, token_service):
        """Test token encryption performance."""
        import time
        
        plain_token = "test_token_123"
        
        # Measure encryption time
        start_time = time.time()
        for _ in range(1000):
            encrypted_token = token_service.encrypt_token(plain_token)
        encryption_time = time.time() - start_time
        
        # Measure decryption time
        encrypted_token = token_service.encrypt_token(plain_token)
        start_time = time.time()
        for _ in range(1000):
            decrypted_token = token_service.decrypt_token(encrypted_token)
        decryption_time = time.time() - start_time
        
        # Both operations should be fast (less than 1 second for 1000 operations)
        assert encryption_time < 1.0
        assert decryption_time < 1.0
        
        # Decryption should be faster than encryption
        assert decryption_time < encryption_time

    def test_token_encryption_memory_usage(self, token_service):
        """Test that token encryption doesn't leak memory."""
        import gc
        
        # Create many tokens
        tokens = []
        for i in range(1000):
            plain_token = f"token_{i}_" + "x" * 100
            encrypted_token = token_service.encrypt_token(plain_token)
            decrypted_token = token_service.decrypt_token(encrypted_token)
            tokens.append((plain_token, encrypted_token, decrypted_token))
        
        # Force garbage collection
        gc.collect()
        
        # Verify all tokens are still accessible and correct
        for plain_token, encrypted_token, decrypted_token in tokens:
            assert decrypted_token == plain_token
            assert len(encrypted_token) > len(plain_token)

    def test_token_encryption_thread_safety(self, token_service):
        """Test token encryption thread safety."""
        import threading
        import time
        
        results = []
        errors = []
        
        def encrypt_token(thread_id):
            try:
                plain_token = f"token_from_thread_{thread_id}"
                encrypted_token = token_service.encrypt_token(plain_token)
                decrypted_token = token_service.decrypt_token(encrypted_token)
                results.append((thread_id, plain_token, encrypted_token, decrypted_token))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=encrypt_token, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0
        
        # Verify all results are correct
        assert len(results) == 10
        for thread_id, plain_token, encrypted_token, decrypted_token in results:
            assert decrypted_token == plain_token
            assert len(encrypted_token) > len(plain_token)
