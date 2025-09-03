"""
Message processing service for SMS Router.
"""

import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Service for processing and validating SMS messages."""

    def __init__(self):
        # Common message patterns and filters
        self.spam_patterns = [
            r"\b(?:free|win|winner|won|prize|cash|money|urgent|limited|offer)\b",
            r"\b(?:click|link|http|www|\.com|\.org|\.net)\b",
            r"\b(?:call\s+now|act\s+now|limited\s+time|expires)\b",
        ]

        self.command_patterns = [
            r"^/(\w+)(?:\s+(.+))?$",  # /command [args]
            r"^!(\w+)(?:\s+(.+))?$",  # !command [args]
            r"^(\w+):\s*(.+)$",  # command: args
        ]

    async def process_message(
        self, message: str, user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process incoming SMS message.

        Args:
            message: Raw SMS message content
            user_info: User information dictionary

        Returns:
            Processed message dictionary
        """
        try:
            # Basic validation
            if not message or not message.strip():
                return {"error": "Empty message", "processed": False}

            # Clean and normalize message
            cleaned_message = self._clean_message(message)

            # Check for spam indicators
            spam_score = self._calculate_spam_score(cleaned_message)

            # Check for commands
            command_info = self._extract_command(cleaned_message)

            # Process message content
            processed_content = self._process_content(cleaned_message, command_info)

            result = {
                "original_message": message,
                "cleaned_message": cleaned_message,
                "spam_score": spam_score,
                "is_spam": spam_score > 0.7,
                "command_info": command_info,
                "processed_content": processed_content,
                "user_id": user_info["id"],
                "user_email": user_info["email"],
                "processed": True,
            }

            logger.info(
                f"Processed message for user {user_info['id']}: {cleaned_message[:50]}..."
            )
            return result

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"error": str(e), "processed": False}

    def _clean_message(self, message: str) -> str:
        """Clean and normalize message content."""
        # Remove extra whitespace
        cleaned = re.sub(r"\s+", " ", message.strip())

        # Remove common SMS abbreviations and normalize
        abbreviations = {
            "u": "you",
            "ur": "your",
            "r": "are",
            "2": "to",
            "4": "for",
            "b": "be",
            "c": "see",
            "y": "why",
            "n": "and",
            "w/": "with",
            "w/o": "without",
        }

        for abbr, full in abbreviations.items():
            # Use word boundaries to avoid partial replacements
            cleaned = re.sub(
                r"\b" + re.escape(abbr) + r"\b", full, cleaned, flags=re.IGNORECASE
            )

        return cleaned

    def _calculate_spam_score(self, message: str) -> float:
        """Calculate spam probability score (0.0 to 1.0)."""
        score = 0.0
        message_lower = message.lower()

        # Check for spam patterns
        for pattern in self.spam_patterns:
            matches = len(re.findall(pattern, message_lower, re.IGNORECASE))
            if matches > 0:
                score += min(matches * 0.2, 0.5)  # Cap at 0.5 per pattern

        # Check for excessive caps
        caps_ratio = (
            sum(1 for c in message if c.isupper()) / len(message) if message else 0
        )
        if caps_ratio > 0.7:
            score += 0.3

        # Check for excessive punctuation
        punct_ratio = (
            sum(1 for c in message if c in "!?.,;:") / len(message) if message else 0
        )
        if punct_ratio > 0.3:
            score += 0.2

        # Check for suspicious length patterns
        if len(message) < 5:
            score += 0.1
        elif len(message) > 500:
            score += 0.1

        return min(score, 1.0)

    def _extract_command(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract command information from message."""
        for pattern in self.command_patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return {
                        "command": groups[0].lower(),
                        "args": groups[1].strip() if groups[1] else "",
                        "pattern": pattern,
                    }
                elif len(groups) == 1:
                    return {
                        "command": groups[0].lower(),
                        "args": "",
                        "pattern": pattern,
                    }

        return None

    def _process_content(
        self, message: str, command_info: Optional[Dict[str, Any]]
    ) -> str:
        """Process message content based on command or context."""
        if command_info:
            # Handle command-based processing
            command = command_info["command"]
            args = command_info["args"]

            # Common command processing
            if command in ["help", "h", "?"]:
                return "Available commands: /help, /status, /info, /clear"
            elif command in ["status", "s"]:
                return "Your assistant is ready to help!"
            elif command in ["info", "i"]:
                return "Personal Assistant v1.0 - SMS Router Service"
            elif command in ["clear", "c"]:
                return "Conversation context cleared"
            else:
                return f"Unknown command: {command}. Type /help for available commands."

        # Regular message processing
        return message

    def validate_message_length(self, message: str, max_length: int = 160) -> bool:
        """Validate message length for SMS compatibility."""
        return len(message) <= max_length

    def get_message_metadata(self, message: str) -> Dict[str, Any]:
        """Extract metadata from message."""
        return {
            "length": len(message),
            "word_count": len(message.split()),
            "has_commands": bool(self._extract_command(message)),
            "language": self._detect_language(message),
            "sentiment": self._analyze_sentiment(message),
        }

    def _detect_language(self, message: str) -> str:
        """Simple language detection (basic implementation)."""
        # This is a basic implementation - could be enhanced with proper language detection
        if re.search(r"[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]", message, re.IGNORECASE):
            return "likely_non_english"
        return "likely_english"

    def _analyze_sentiment(self, message: str) -> str:
        """Basic sentiment analysis (basic implementation)."""
        positive_words = [
            "good",
            "great",
            "excellent",
            "awesome",
            "love",
            "like",
            "happy",
            "thanks",
            "thank you",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "dislike",
            "sad",
            "angry",
            "upset",
            "frustrated",
        ]

        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
