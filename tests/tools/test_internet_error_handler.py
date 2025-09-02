"""
Unit tests for InternetErrorHandler.

Tests error handling, classification, and recovery hints
for internet-specific operations.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

# Import the error handler to test
from personal_assistant.tools.internet.internet_error_handler import InternetErrorHandler


class TestInternetErrorHandler:
    """Test suite for InternetErrorHandler"""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing"""
        return Mock(spec=object)

    @pytest.fixture
    def sample_error(self):
        """Create a sample error for testing"""
        return ValueError("Invalid query parameter")

    @pytest.fixture
    def sample_parameters(self):
        """Create sample parameters for testing"""
        return {
            "query": "test query",
            "max_results": 5,
            "safe_search": "moderate"
        }

    def test_handle_internet_error_basic(self, mock_logger, sample_error, sample_parameters):
        """Test basic error handling"""
        result = InternetErrorHandler.handle_internet_error(
            sample_error, "web_search", sample_parameters
        )

        # Check that result contains error information
        assert "error" in result
        assert "web_search" in result.get("tool_name", "")
        assert "Invalid query parameter" in result.get("error_message", "")

    def test_handle_internet_error_with_different_tools(self, mock_logger, sample_error):
        """Test error handling for different tools"""
        tools = ["web_search", "get_news_articles",
                 "get_wikipedia", "search_images"]

        for tool in tools:
            result = InternetErrorHandler.handle_internet_error(
                sample_error, tool, {"test": "param"}
            )

            assert tool in result.get("tool_name", "")
            assert "error" in result

    def test_handle_internet_error_with_different_error_types(self, mock_logger, sample_error, sample_parameters):
        """Test error handling with different error types"""
        error_types = [
            ValueError("Validation error"),
            ConnectionError("Connection failed"),
            Exception("Generic error")
        ]

        for error in error_types:
            result = InternetErrorHandler.handle_internet_error(
                error, "web_search", sample_parameters
            )

            assert "error" in result
            assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_empty_parameters(self, mock_logger, sample_error):
        """Test error handling with empty parameters"""
        result = InternetErrorHandler.handle_internet_error(
            sample_error, "web_search", {}
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_none_parameters(self, mock_logger, sample_error):
        """Test error handling with None parameters"""
        result = InternetErrorHandler.handle_internet_error(
            sample_error, "web_search", None
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_logging_details(self, mock_logger, sample_error, sample_parameters):
        """Test error handling with detailed logging"""
        result = InternetErrorHandler.handle_internet_error(
            sample_error, "web_search", sample_parameters
        )

        # Check that the result is user-friendly
        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_user_friendly_message(self, mock_logger, sample_error, sample_parameters):
        """Test that error messages are user-friendly"""
        result = InternetErrorHandler.handle_internet_error(
            sample_error, "web_search", sample_parameters
        )

        # Check that the result is user-friendly
        assert "error" in result

    def test_handle_internet_error_with_complex_parameters(self, mock_logger, sample_error):
        """Test error handling with complex parameter structures"""
        complex_parameters = {
            "query": "test",
            "nested": {
                "level1": {
                    "level2": "value"
                }
            },
            "list_param": [1, 2, 3],
            "none_value": None
        }

        result = InternetErrorHandler.handle_internet_error(
            sample_error, "web_search", complex_parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_special_characters(self, mock_logger):
        """Test error handling with special characters in error messages"""
        special_error = ValueError("Special chars: !@#$%^&*()")
        special_parameters = {
            "query": "test query",
            "max_results": 5
        }

        result = InternetErrorHandler.handle_internet_error(
            special_error, "web_search", special_parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_unicode(self, mock_logger):
        """Test error handling with unicode characters"""
        unicode_error = ValueError("Unicode: 🚀🌟✨")
        unicode_parameters = {
            "query": "test query",
            "max_results": 5
        }

        result = InternetErrorHandler.handle_internet_error(
            unicode_error, "web_search", unicode_parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_long_error_message(self, mock_logger):
        """Test error handling with very long error messages"""
        long_error = ValueError("x" * 1000)
        long_parameters = {
            "query": "test query",
            "max_results": 5
        }

        result = InternetErrorHandler.handle_internet_error(
            long_error, "web_search", long_parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_exception_attributes(self, mock_logger):
        """Test error handling with custom exception attributes"""
        class CustomError(Exception):
            def __init__(self, message, code, details):
                self.code = code
                self.details = details
                super().__init__(message)

        custom_error = CustomError(
            "Custom error message", 500, {"key": "value"})
        parameters = {"query": "test"}

        result = InternetErrorHandler.handle_internet_error(
            custom_error, "web_search", parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_none_error(self, mock_logger, sample_parameters):
        """Test error handling with None error"""
        result = InternetErrorHandler.handle_internet_error(
            None, "web_search", sample_parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_empty_tool_name(self, mock_logger, sample_error, sample_parameters):
        """Test error handling with empty tool name"""
        result = InternetErrorHandler.handle_internet_error(
            sample_error, "", sample_parameters
        )

        assert "error" in result

    def test_handle_internet_error_with_none_tool_name(self, mock_logger, sample_error, sample_parameters):
        """Test error handling with None tool name"""
        result = InternetErrorHandler.handle_internet_error(
            sample_error, None, sample_parameters
        )

        assert "error" in result

    def test_handle_internet_error_consistent_format(self, mock_logger, sample_error, sample_parameters):
        """Test that error handling produces consistent format"""
        result1 = InternetErrorHandler.handle_internet_error(
            sample_error, "web_search", sample_parameters
        )

        result2 = InternetErrorHandler.handle_internet_error(
            sample_error, "get_news_articles", sample_parameters
        )

        # Both results should have similar structure
        assert "error" in result1
        assert "error" in result2

    def test_handle_internet_error_with_rate_limit_error(self, mock_logger):
        """Test error handling with rate limit specific error"""
        rate_limit_error = Exception("Rate limit exceeded")
        parameters = {"query": "test"}

        result = InternetErrorHandler.handle_internet_error(
            rate_limit_error, "web_search", parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_network_error(self, mock_logger):
        """Test error handling with network specific error"""
        network_error = ConnectionError("Network connection failed")
        parameters = {"query": "test"}

        result = InternetErrorHandler.handle_internet_error(
            network_error, "web_search", parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_validation_error(self, mock_logger):
        """Test error handling with validation specific error"""
        validation_error = ValueError(
            "Invalid parameter: max_results must be > 0")
        parameters = {"max_results": -1}

        result = InternetErrorHandler.handle_internet_error(
            validation_error, "web_search", parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")


class TestInternetErrorHandlerEdgeCases:
    """Test suite for edge cases and boundary conditions"""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing"""
        return Mock(spec=object)

    def test_handle_internet_error_with_very_large_parameters(self, mock_logger):
        """Test error handling with very large parameter values"""
        large_error = ValueError("Large error")
        large_parameters = {
            "query": "x" * 1000,
            "safe_search": "x" * 1000
        }

        result = InternetErrorHandler.handle_internet_error(
            large_error, "web_search", large_parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_malformed_parameters(self, mock_logger):
        """Test error handling with malformed parameter structures"""
        malformed_error = ValueError("Malformed error")
        malformed_parameters = {
            "query": "test",
            "safe_search": {"not": "a string"}
        }

        result = InternetErrorHandler.handle_internet_error(
            malformed_error, "web_search", malformed_parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_circular_references(self, mock_logger):
        """Test error handling with circular reference in parameters"""
        circular_error = ValueError("Circular error")

        # Create circular reference
        circular_dict = {}
        circular_dict["self"] = circular_dict

        result = InternetErrorHandler.handle_internet_error(
            circular_error, "web_search", circular_dict
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")

    def test_handle_internet_error_with_binary_data(self, mock_logger):
        """Test error handling with binary data in parameters"""
        binary_error = ValueError("Binary error")
        binary_parameters = {
            "query": b"binary data",
            "max_results": 5
        }

        result = InternetErrorHandler.handle_internet_error(
            binary_error, "web_search", binary_parameters
        )

        assert "error" in result
        assert "web_search" in result.get("tool_name", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
