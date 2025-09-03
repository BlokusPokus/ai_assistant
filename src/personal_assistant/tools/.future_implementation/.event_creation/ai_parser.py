import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from ...llm.llm_client import LLMClient
from .event_details import (
    EventDetails,
    RecurrencePattern,
    ValidationResult,
    ValidationStatus,
)

logger = logging.getLogger(__name__)


class EventAIParser:
    """AI-powered event parsing and recurrence recognition."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def parse_event_details(self, user_input: str) -> EventDetails:
        """Parse event details from natural language."""
        try:
            # Create prompt for event parsing
            prompt = self._create_parsing_prompt(user_input)

            # Define the function schema for structured output
            function_schema = {
                "name": "parse_event_details",
                "description": "Parse event details from natural language input",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Event title or name",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time in ISO format (YYYY-MM-DDTHH:MM:SS)",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Duration in minutes (default 60)",
                        },
                        "location": {
                            "type": "string",
                            "description": "Event location (optional)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Event description (optional)",
                        },
                        "recurrence_pattern": {
                            "type": "object",
                            "description": "Recurrence pattern if event is recurring",
                            "properties": {
                                "frequency": {
                                    "type": "string",
                                    "enum": ["daily", "weekly", "monthly", "yearly"],
                                },
                                "interval": {
                                    "type": "integer",
                                    "description": "Interval between occurrences",
                                },
                                "weekdays": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                    "description": "Weekdays for weekly patterns (0=Monday, 6=Sunday)",
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "End date in ISO format (optional)",
                                },
                                "max_occurrences": {
                                    "type": "integer",
                                    "description": "Maximum number of occurrences (optional)",
                                },
                            },
                        },
                    },
                    "required": ["title", "start_time"],
                },
            }

            # Get LLM response
            response = self.llm_client.complete(prompt, [function_schema])

            # Parse the response
            if "function_call" in response:
                args = json.loads(response["function_call"]["arguments"])
                return self._create_event_details_from_args(args)
            else:
                # Fallback parsing
                return self._fallback_parsing(user_input)

        except Exception as e:
            logger.error(f"Error parsing event details: {e}")
            raise

    async def extract_recurrence_pattern(
        self, description: str
    ) -> Optional[RecurrencePattern]:
        """Extract recurrence pattern using AI."""
        try:
            # Create prompt for recurrence pattern extraction
            prompt = self._create_recurrence_prompt(description)

            # Define function schema for recurrence parsing
            function_schema = {
                "name": "extract_recurrence_pattern",
                "description": "Extract recurrence pattern from event description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "frequency": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly", "yearly"],
                            "description": "Frequency of recurrence",
                        },
                        "interval": {
                            "type": "integer",
                            "description": "Interval between occurrences (default 1)",
                        },
                        "weekdays": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Weekdays for weekly patterns (0=Monday, 6=Sunday)",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in ISO format (optional)",
                        },
                        "max_occurrences": {
                            "type": "integer",
                            "description": "Maximum number of occurrences (optional)",
                        },
                    },
                    "required": ["frequency"],
                },
            }

            # Get LLM response
            response = self.llm_client.complete(prompt, [function_schema])

            # Parse the response
            if "function_call" in response:
                args = json.loads(response["function_call"]["arguments"])
                return RecurrencePattern(**args)
            else:
                return None

        except Exception as e:
            logger.error(f"Error extracting recurrence pattern: {e}")
            return None

    async def validate_event_details(self, details: EventDetails) -> ValidationResult:
        """Validate parsed event details."""
        errors = []
        warnings = []
        suggestions = []

        # Validate title
        if not details.title or len(details.title.strip()) == 0:
            errors.append("Event title is required")

        # Validate start time
        if details.start_time < datetime.now():
            warnings.append("Event start time is in the past")

        # Validate duration
        if details.duration <= 0:
            errors.append("Duration must be positive")
        elif details.duration > 1440:  # 24 hours
            warnings.append("Event duration is very long")

        # Validate recurrence pattern
        if details.recurrence_pattern:
            pattern = RecurrencePattern(**details.recurrence_pattern)
            if not pattern.is_valid():
                errors.append("Invalid recurrence pattern")

        # Determine validation status
        if errors:
            status = ValidationStatus.INVALID
        elif warnings:
            status = ValidationStatus.PARTIAL
        else:
            status = ValidationStatus.VALID

        return ValidationResult(
            status=status, errors=errors, warnings=warnings, suggestions=suggestions
        )

    def _create_parsing_prompt(self, user_input: str) -> str:
        """Create prompt for event parsing."""
        return f"""
You are an AI assistant that helps parse natural language event descriptions into structured data.

Parse the following event description and extract the event details:

"{user_input}"

Rules:
1. Extract the event title, start time, duration, location, and description
2. If the event is recurring, extract the recurrence pattern
3. Use current date/time as reference for relative dates (tomorrow, next week, etc.)
4. Default duration is 60 minutes if not specified
5. Return structured data in the specified format

Current date/time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _create_recurrence_prompt(self, description: str) -> str:
        """Create prompt for recurrence pattern extraction."""
        return f"""
You are an AI assistant that extracts recurrence patterns from event descriptions.

Extract the recurrence pattern from this description:

"{description}"

Rules:
1. Look for keywords like "every", "weekly", "monthly", "daily", "yearly"
2. Identify the frequency (daily, weekly, monthly, yearly)
3. Extract the interval (every N days/weeks/months/years)
4. For weekly patterns, identify which weekdays
5. Look for end dates or maximum occurrences
6. Return structured recurrence pattern data

Current date/time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _create_event_details_from_args(self, args: Dict[str, Any]) -> EventDetails:
        """Create EventDetails from parsed arguments."""
        # Parse start time
        start_time = datetime.fromisoformat(args["start_time"])

        # Create event details
        event_details = EventDetails(
            title=args["title"],
            start_time=start_time,
            duration=args.get("duration", 60),
            location=args.get("location", ""),
            description=args.get("description", ""),
            recurrence_pattern=args.get("recurrence_pattern"),
        )

        return event_details

    def _fallback_parsing(self, user_input: str) -> EventDetails:
        """Fallback parsing when AI parsing fails."""
        # Simple fallback parsing
        words = user_input.lower().split()

        # Extract basic information
        title = user_input  # Use full input as title for now
        start_time = datetime.now() + timedelta(hours=1)  # Default to 1 hour from now
        duration = 60  # Default duration

        # Try to extract time information
        for i, word in enumerate(words):
            if word in ["tomorrow", "today"]:
                if word == "tomorrow":
                    start_time = datetime.now() + timedelta(days=1)
                # Try to find time
                if i + 1 < len(words):
                    time_word = words[i + 1]
                    try:
                        # Simple time parsing
                        if "pm" in time_word or "am" in time_word:
                            # Basic time parsing
                            pass
                    except (ValueError, TypeError, IndexError):
                        # Ignore parsing errors for time words
                        pass

        return EventDetails(title=title, start_time=start_time, duration=duration)
