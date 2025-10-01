"""
Response formatter service for SMS Router.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from twilio.twiml.messaging_response import MessagingResponse

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Service for formatting responses for SMS delivery."""

    def __init__(self):
        self.max_sms_length: int = 1600
        self.max_concatenated_length: int = 3200

    def format_response(
        self, agent_response: str, user_info: Dict[str, Any]
    ) -> MessagingResponse:
        """
        Format agent response for SMS delivery.

        Args:
            agent_response: Raw response from agent
            user_info: User information dictionary

        Returns:
            Formatted TwiML response
        """
        try:
            response = MessagingResponse()

            # Clean and format the response
            formatted_text = self._format_text(agent_response)

            # Check if response needs to be split
            if len(formatted_text) <= self.max_sms_length:
                # Single SMS
                response.message(formatted_text)
            else:
                # Split into multiple SMS
                segments = self._split_message(formatted_text)
                for i, segment in enumerate(segments):
                    if i == 0:
                        response.message(segment)
                    else:
                        # Add continuation indicator
                        response.message(f"(continued {i+1}/{len(segments)}) {segment}")

            logger.info(
                f"Formatted response for user {user_info['id']}: {len(formatted_text)} chars"
            )
            return response

        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            # Fallback to simple response
            fallback_response = MessagingResponse()
            fallback_response.message(
                "I'm sorry, there was an error processing your request. Please try again."
            )
            return fallback_response

    def _format_text(self, text: str) -> str:
        """Format text for SMS delivery while preserving SMS-friendly formatting."""
        if not text:
            return "No response generated."

        # Remove excessive whitespace but preserve intentional line breaks
        formatted = re.sub(r"[ \t]+", " ", text.strip())
        
        # Handle multiple consecutive line breaks (reduce to single)
        formatted = re.sub(r"\n\s*\n", "\n", formatted)
        
        # Remove HTML-like tags if present
        formatted = re.sub(r"<[^>]+>", "", formatted)
        
        # Ensure proper sentence endings
        if not formatted.endswith((".", "!", "?")):
            formatted += "."

        return formatted

    def _split_message(self, message: str) -> list[str]:
        """Split long message into SMS segments."""
        if len(message) <= self.max_sms_length:
            return [message]

        segments: List[str] = []
        remaining = message

        while remaining and len(segments) < 10:  # Max 10 segments
            if len(remaining) <= self.max_sms_length:
                segments.append(remaining)
                break

            # Find the best split point
            split_point = self._find_split_point(remaining[: self.max_sms_length])
            segment = remaining[:split_point].strip()
            segments.append(segment)

            remaining = remaining[split_point:].strip()

        # If we still have remaining text, add it as the last segment
        if remaining and len(segments) < 10:
            segments.append(remaining[: self.max_sms_length])

        return segments

    def _find_split_point(self, text: str) -> int:
        """Find the best point to split text for SMS."""
        if len(text) <= self.max_sms_length:
            return len(text)

        # Try to split at sentence boundaries
        sentence_endings = [".", "!", "?"]
        for char in sentence_endings:
            pos = text.rfind(char)
            if pos > 0 and pos < self.max_sms_length - 10:  # Leave some buffer
                return pos + 1

        # Try to split at word boundaries
        words = text.split()
        current_length = 0
        for i, word in enumerate(words):
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > self.max_sms_length:
                if i > 0:
                    return current_length
                else:
                    # Word is too long, split at character limit
                    return self.max_sms_length

        # If we get here, split at the limit
        return self.max_sms_length

    def format_error_response(
        self, error_message: str, user_info: Optional[Dict[str, Any]] = None
    ) -> MessagingResponse:
        """Format error response for SMS delivery."""
        response = MessagingResponse()

        # Create user-friendly error message
        if "not found" in error_message.lower():
            message = "Your phone number is not registered. Please sign up first."
        elif "inactive" in error_message.lower():
            message = "Your account is currently inactive. Please contact support."
        elif "rate limit" in error_message.lower():
            message = "Too many requests. Please wait a moment before trying again."
        else:
            message = "I'm sorry, there was an error processing your request. Please try again."

        response.message(message)
        return response

    def format_unknown_user_response(self, phone_number: str, message: str = "") -> MessagingResponse:
        """Format interactive response for unknown phone numbers."""
        response = MessagingResponse()

        # Analyze the message to determine appropriate response
        message_clean = message.strip().upper()
        
        if message_clean in ['A', 'SEE WHAT I CAN DO']:
            response_message = self._get_feature_overview()
        elif message_clean in ['B', 'GET STARTED NOW', 'YES', 'GET STARTED', 'Y']:
            response_message = self._get_signup_link_message(phone_number)
        elif message_clean in ['C', 'LEARN MORE']:
            response_message = self._get_learn_more_message()
        else:
            # Default welcome message for first contact or unclear input
            response_message = self._get_welcome_message()

        response.message(response_message)
        return response

    def _get_welcome_message(self) -> str:
        """Get the initial welcome message."""
        return (
            "Hi! I'm your AI assistant. I can help with tasks, reminders, and more.You are currently not registered. "
            "Would you like to:\n"
            "A) See what I can do\n"
            "B) Get started now\n"
            "C) Learn more"
        )

    def _get_feature_overview(self) -> str:
        """Get the feature overview message."""
        return (
            "I can help you with:\n"
            "📝 Create and manage tasks\n"
            "📅 Set reminders and events\n"
            "📧 Manage emails\n"
            "📊 Track your productivity\n"
            "And much more!\n\n"
            "Ready to get started? Reply 'YES' to create your account."
        )

    def _get_signup_link_message(self, phone_number: str) -> str:
        """Get the signup link message."""
        signup_link = f"https://yourwebsite.com/signup?phone={phone_number}"
        return (
            "Great! Let's get you set up quickly.\n\n"
            f"Here's your signup link:\n{signup_link}\n\n"
            "Complete signup there, then text me back!"
        )

    def _get_learn_more_message(self) -> str:
        """Get the learn more message."""
        return (
            "I'm a personal AI assistant that helps you stay organized and productive.\n\n"
            "Key features:\n"
            "• Smart task management with priorities\n"
            "• Calendar integration and reminders\n"
            "• Email organization and responses\n"
            "• Productivity analytics\n\n"
            "Want to try it? Reply 'YES' to get started!"
        )

    def format_inactive_user_response(self, phone_number: str) -> MessagingResponse:
        """Format response for inactive users."""
        response = MessagingResponse()

        message = (
            "Your account is currently inactive. "
            "Please contact support to reactivate your account."
        )

        response.message(message)
        return response

    def format_spam_response(self, phone_number: str) -> MessagingResponse:
        """Format response for suspected spam messages."""
        response = MessagingResponse()

        message = (
            "Your message appears to be spam and cannot be processed. "
            "If this is an error, please contact support."
        )

        response.message(message)
        return response

    def add_typing_indicator(self, response: MessagingResponse) -> MessagingResponse:
        """Add typing indicator to response (if supported by Twilio)."""
        # Note: Twilio doesn't support typing indicators in SMS, but this could be used
        # for other messaging channels in the future
        return response

    def add_quick_replies(
        self, response: MessagingResponse, options: list[str]
    ) -> MessagingResponse:
        """Add quick reply options to response."""
        # Note: Twilio SMS doesn't support quick replies, but this could be used
        # for other messaging channels in the future
        return response
