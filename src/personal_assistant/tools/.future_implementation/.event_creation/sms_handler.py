import logging
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ...llm.llm_client import LLMClient
from .db_operations import EventDatabaseOperations
from .event_creation_tool import EventCreationTool

logger = logging.getLogger(__name__)


class EventCreationSMSHandler:
    """Handle event creation via SMS."""

    def __init__(self, llm_client: LLMClient, db_session: AsyncSession):
        self.llm_client = llm_client
        self.db_session = db_session
        self.event_tool = EventCreationTool(llm_client, db_session)
        self.db_ops = EventDatabaseOperations(db_session)

    async def handle_event_creation_sms(self, user_input: str, user_id: int) -> str:
        """Handle event creation via SMS."""
        try:
            # Check if this looks like an event creation request
            if not self._is_event_creation_request(user_input):
                return "I didn't understand that. To create an event, try: 'Meeting with John tomorrow at 2pm'"

            # Create the event
            result = await self.event_tool.create_event(user_input, user_id)

            if result["success"]:
                return self._format_success_response(result)
            else:
                return self._format_error_response(result["error"])

        except Exception as e:
            logger.error(f"Error handling event creation SMS: {e}")
            return self._format_error_response(
                "Sorry, I couldn't create your event. Please try again."
            )

    async def handle_event_modification_sms(self, user_input: str, user_id: int) -> str:
        """Handle event modification via SMS."""
        try:
            # Extract event ID and new details from user input
            event_id, updates = self._parse_modification_request(user_input)

            if not event_id:
                return "Please specify which event to modify. Try: 'Change event 123 to tomorrow at 3pm'"

            # Update the event
            success = await self.db_ops.update_event(event_id, user_id, updates)

            if success:
                return f"✅ Updated event {event_id}"
            else:
                return f"❌ Could not update event {event_id}"

        except Exception as e:
            logger.error(f"Error handling event modification SMS: {e}")
            return "Sorry, I couldn't modify your event. Please try again."

    async def handle_event_deletion_sms(self, user_input: str, user_id: int) -> str:
        """Handle event deletion via SMS."""
        try:
            # Extract event ID from user input
            event_id = self._parse_deletion_request(user_input)

            if not event_id:
                return "Please specify which event to delete. Try: 'Delete event 123'"

            # Delete the event
            success = await self.db_ops.delete_event(event_id, user_id)

            if success:
                return f"✅ Deleted event {event_id}"
            else:
                return f"❌ Could not delete event {event_id}"

        except Exception as e:
            logger.error(f"Error handling event deletion SMS: {e}")
            return "Sorry, I couldn't delete your event. Please try again."

    async def handle_event_listing_sms(self, user_input: str, user_id: int) -> str:
        """Handle event listing via SMS."""
        try:
            # Get upcoming events
            # 1 week
            events = await self.db_ops.get_upcoming_events(user_id, hours_ahead=168)

            if not events:
                return "You have no upcoming events in the next week."

            # Format the response
            response = "📅 Your upcoming events:\n\n"
            for event in events[:5]:  # Limit to 5 events
                time_str = event.start_time.strftime("%A, %B %d at %I:%M %p")
                response += f"• {event.title} - {time_str}\n"

            if len(events) > 5:
                response += f"\n... and {len(events) - 5} more events"

            return response

        except Exception as e:
            logger.error(f"Error handling event listing SMS: {e}")
            return "Sorry, I couldn't retrieve your events. Please try again."

    def _is_event_creation_request(self, user_input: str) -> bool:
        """Check if the input looks like an event creation request."""
        # Simple keyword-based detection
        event_keywords = [
            "meeting",
            "appointment",
            "call",
            "conference",
            "lunch",
            "dinner",
            "breakfast",
            "coffee",
            "interview",
            "presentation",
            "workshop",
            "training",
            "review",
            "check-in",
            "standup",
            "sync",
        ]

        time_keywords = [
            "tomorrow",
            "today",
            "next",
            "at",
            "pm",
            "am",
            "morning",
            "afternoon",
            "evening",
            "night",
            "noon",
            "midnight",
        ]

        input_lower = user_input.lower()

        # Check for event-related keywords
        has_event_keyword = any(keyword in input_lower for keyword in event_keywords)

        # Check for time-related keywords
        has_time_keyword = any(keyword in input_lower for keyword in time_keywords)

        # Check for common event creation patterns
        has_event_pattern = any(
            [
                "with" in input_lower
                and any(time_word in input_lower for time_word in ["at", "pm", "am"]),
                "meeting" in input_lower
                and any(
                    time_word in input_lower
                    for time_word in ["tomorrow", "today", "next"]
                ),
                "call" in input_lower
                and any(time_word in input_lower for time_word in ["at", "pm", "am"]),
            ]
        )

        return has_event_keyword or has_time_keyword or has_event_pattern

    def _parse_modification_request(
        self, user_input: str
    ) -> tuple[Optional[int], Dict[str, Any]]:
        """Parse event modification request."""
        # Simple parsing - look for event ID and new details
        words = user_input.lower().split()

        event_id = None
        updates = {}

        for i, word in enumerate(words):
            if (
                word.isdigit()
                and i > 0
                and words[i - 1] in ["event", "meeting", "appointment"]
            ):
                event_id = int(word)
                break

        # For now, return basic structure - this would need more sophisticated parsing
        return event_id, updates

    def _parse_deletion_request(self, user_input: str) -> Optional[int]:
        """Parse event deletion request."""
        words = user_input.lower().split()

        for i, word in enumerate(words):
            if (
                word.isdigit()
                and i > 0
                and words[i - 1] in ["event", "meeting", "appointment"]
            ):
                return int(word)

        return None

    def _format_success_response(self, result: Dict[str, Any]) -> str:
        """Format successful event creation response."""
        return f"✅ {result['details']}"

    def _format_error_response(self, error: str) -> str:
        """Format error response for SMS."""
        return f"❌ {error}\n\nTry: 'Meeting with John tomorrow at 2pm' or 'Weekly team meeting every Monday at 10am'"

    def _format_help_response(self) -> str:
        """Format help response."""
        return """📅 Event Creation Help:

• One-time event: "Meeting with John tomorrow at 2pm"
• Recurring event: "Weekly team meeting every Monday at 10am"
• With location: "Coffee with Sarah tomorrow at 3pm at Starbucks"
• With duration: "1-hour call with client tomorrow at 2pm"

To list events: "Show my events"
To delete: "Delete event 123"
To modify: "Change event 123 to tomorrow at 3pm"
"""
