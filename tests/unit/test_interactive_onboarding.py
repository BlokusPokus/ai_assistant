"""
Unit tests for interactive SMS onboarding flow.

This module tests the stateless interactive onboarding functionality.
"""

import pytest
from unittest.mock import MagicMock

from src.personal_assistant.sms_router.services.response_formatter import ResponseFormatter


class TestInteractiveOnboarding:
    """Test interactive onboarding flow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = ResponseFormatter()

    def test_welcome_message_first_contact(self):
        """Test welcome message for first contact."""
        response = self.formatter.format_unknown_user_response("+1234567890", "Hello")
        
        assert "Hi! I'm your AI assistant" in str(response)
        assert "A) See what I can do" in str(response)
        assert "B) Get started now" in str(response)
        assert "C) Learn more" in str(response)

    def test_feature_overview_response(self):
        """Test feature overview response."""
        response = self.formatter.format_unknown_user_response("+1234567890", "A")
        
        assert "I can help you with:" in str(response)
        assert "📝 Create and manage tasks" in str(response)
        assert "📅 Set reminders and events" in str(response)
        assert "📧 Manage emails" in str(response)
        assert "📊 Track your productivity" in str(response)
        assert "Reply 'YES' to create your account" in str(response)

    def test_signup_link_response(self):
        """Test signup link response."""
        response = self.formatter.format_unknown_user_response("+1234567890", "B")
        
        assert "Great! Let's get you set up quickly" in str(response)
        assert "https://yourwebsite.com/signup?phone=+1234567890" in str(response)
        assert "Complete signup there, then text me back!" in str(response)

    def test_learn_more_response(self):
        """Test learn more response."""
        response = self.formatter.format_unknown_user_response("+1234567890", "C")
        
        assert "I'm a personal AI assistant" in str(response)
        assert "Smart task management" in str(response)
        assert "Calendar integration" in str(response)
        assert "Email organization" in str(response)
        assert "Productivity analytics" in str(response)
        assert "Reply 'YES' to get started!" in str(response)

    def test_yes_response_after_features(self):
        """Test YES response after feature overview."""
        response = self.formatter.format_unknown_user_response("+1234567890", "YES")
        
        assert "Great! Let's get you set up quickly" in str(response)
        assert "https://yourwebsite.com/signup?phone=+1234567890" in str(response)

    def test_case_insensitive_responses(self):
        """Test that responses are case insensitive."""
        # Test lowercase
        response_lower = self.formatter.format_unknown_user_response("+1234567890", "a")
        response_upper = self.formatter.format_unknown_user_response("+1234567890", "A")
        
        assert str(response_lower) == str(response_upper)

    def test_variations_of_responses(self):
        """Test various ways users might respond."""
        test_cases = [
            ("SEE WHAT I CAN DO", "feature_overview"),
            ("GET STARTED NOW", "signup_link"),
            ("GET STARTED", "signup_link"),
            ("LEARN MORE", "learn_more"),
            ("yes", "signup_link"),
            ("Y", "signup_link"),
        ]
        
        for message, expected_type in test_cases:
            response = self.formatter.format_unknown_user_response("+1234567890", message)
            response_str = str(response)
            
            if expected_type == "feature_overview":
                assert "I can help you with:" in response_str
            elif expected_type == "signup_link":
                assert "https://yourwebsite.com/signup?phone=+1234567890" in response_str
            elif expected_type == "learn_more":
                assert "I'm a personal AI assistant" in response_str

    def test_unclear_input_fallback(self):
        """Test fallback to welcome message for unclear input."""
        response = self.formatter.format_unknown_user_response("+1234567890", "random text")
        
        assert "Hi! I'm your AI assistant" in str(response)
        assert "A) See what I can do" in str(response)

    def test_empty_message_fallback(self):
        """Test fallback to welcome message for empty input."""
        response = self.formatter.format_unknown_user_response("+1234567890", "")
        
        assert "Hi! I'm your AI assistant" in str(response)
        assert "A) See what I can do" in str(response)

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        response = self.formatter.format_unknown_user_response("+1234567890", "  A  ")
        
        assert "I can help you with:" in str(response)

    def test_phone_number_in_signup_link(self):
        """Test that phone number is properly included in signup link."""
        test_phone = "+15551234567"
        response = self.formatter.format_unknown_user_response(test_phone, "B")
        
        assert f"https://yourwebsite.com/signup?phone={test_phone}" in str(response)

    def test_message_length_optimization(self):
        """Test that messages are optimized for SMS length."""
        response = self.formatter.format_unknown_user_response("+1234567890", "A")
        response_str = str(response)
        
        # Should be reasonable length for SMS (under 1600 chars for concatenated SMS)
        assert len(response_str) < 1600

    def test_response_formatting(self):
        """Test that responses are properly formatted."""
        response = self.formatter.format_unknown_user_response("+1234567890", "A")
        
        # Should be a MessagingResponse object
        assert hasattr(response, 'message')
        assert hasattr(response, '__str__')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
