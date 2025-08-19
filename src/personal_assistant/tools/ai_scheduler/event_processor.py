"""
Event processor for calendar event filtering and normalization.

This module provides enhanced event processing logic including data normalization,
filtering, and validation for calendar events.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .db_queries import get_upcoming_events
from .time_utils import (
    calculate_event_duration,
    format_event_time,
    get_time_window,
    get_user_timezone,
    is_event_in_timeframe,
    is_event_urgent,
    normalize_event_time,
    validate_event_times,
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessedEvent:
    """Normalized event data structure."""
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[timedelta]
    location: Optional[str]
    user_id: int
    source: str
    processing_status: str
    is_urgent: bool
    formatted_start_time: str
    formatted_end_time: Optional[str]
    timezone: str


class EventProcessor:
    """
    Enhanced event processor for calendar events.
    """

    def __init__(self, default_timezone: str = 'UTC'):
        self.default_timezone = default_timezone
        self.logger = logger

    async def get_filtered_events(self, hours_ahead: int = 2, user_id: Optional[int] = None) -> List[ProcessedEvent]:
        """
        Get filtered and processed upcoming events.

        Args:
            hours_ahead: Number of hours to look ahead
            user_id: User ID for timezone preference

        Returns:
            List of processed events
        """
        try:
            # Get time window
            window_start, window_end = get_time_window(hours_ahead)

            # Get user timezone
            user_tz = get_user_timezone(
                user_id) if user_id else self.default_timezone

            # Query database for upcoming events
            raw_events = await get_upcoming_events(hours_ahead=hours_ahead)

            # Process and filter events
            processed_events = []
            for event in raw_events:
                try:
                    processed_event = self._process_event(
                        event, window_start, window_end, user_tz)
                    if processed_event:
                        processed_events.append(processed_event)
                except Exception as e:
                    self.logger.error(
                        f"Error processing event {event.id}: {e}")
                    continue

            self.logger.info(
                f"Processed {len(processed_events)} events from {len(raw_events)} raw events")
            return processed_events

        except Exception as e:
            self.logger.error(f"Error getting filtered events: {e}")
            return []

    def _process_event(self, event, window_start: datetime, window_end: datetime, timezone: str) -> Optional[ProcessedEvent]:
        """
        Process a single event.

        Args:
            event: Raw event from database
            window_start: Time window start
            window_end: Time window end
            timezone: User timezone

        Returns:
            Processed event or None if invalid
        """
        try:
            # Validate event times
            if not validate_event_times(event.start_time, event.end_time):
                self.logger.warning(
                    f"Invalid event times for event {event.id}")
                return None

            # Check if event is in timeframe
            if not is_event_in_timeframe(event.start_time, event.end_time, window_start, window_end):
                return None

            # Calculate duration
            duration = calculate_event_duration(
                event.start_time, event.end_time)

            # Check if urgent
            is_urgent = is_event_urgent(event.start_time)

            # Format times
            formatted_start = format_event_time(event.start_time, timezone)
            formatted_end = format_event_time(
                event.end_time, timezone) if event.end_time else None

            # Extract location from description (simple heuristic)
            location = self._extract_location(event.description)

            return ProcessedEvent(
                id=event.id,
                title=event.title or "Untitled Event",
                description=event.description,
                start_time=event.start_time,
                end_time=event.end_time,
                duration=duration,
                location=location,
                user_id=event.user_id,
                source=event.source or "unknown",
                processing_status=event.processing_status or "pending",
                is_urgent=is_urgent,
                formatted_start_time=formatted_start,
                formatted_end_time=formatted_end,
                timezone=timezone
            )

        except Exception as e:
            self.logger.error(f"Error processing event {event.id}: {e}")
            return None

    def _extract_location(self, description: Optional[str]) -> Optional[str]:
        """
        Extract location from event description.

        Args:
            description: Event description

        Returns:
            Extracted location or None
        """
        if not description:
            return None

        # Simple location extraction - look for common patterns
        location_keywords = [
            "room", "conference", "meeting", "office", "building",
            "floor", "suite", "hall", "auditorium", "cafe", "restaurant"
        ]

        description_lower = description.lower()
        for keyword in location_keywords:
            if keyword in description_lower:
                # Extract the phrase containing the keyword
                words = description.split()
                for i, word in enumerate(words):
                    if keyword.lower() in word.lower():
                        # Get surrounding context
                        start = max(0, i - 2)
                        end = min(len(words), i + 3)
                        location = " ".join(words[start:end])
                        return location

        return None

    def categorize_event(self, event: ProcessedEvent) -> str:
        """
        Categorize an event based on its properties.

        Args:
            event: Processed event

        Returns:
            Event category
        """
        title_lower = event.title.lower()
        description_lower = (event.description or "").lower()

        # Meeting patterns
        if any(word in title_lower for word in ["meeting", "call", "conference", "sync"]):
            return "meeting"

        # Appointment patterns
        if any(word in title_lower for word in ["appointment", "consultation", "session"]):
            return "appointment"

        # Task patterns
        if any(word in title_lower for word in ["task", "todo", "deadline", "due"]):
            return "task"

        # Social patterns
        if any(word in title_lower for word in ["lunch", "dinner", "coffee", "party", "celebration"]):
            return "social"

        # Travel patterns
        if any(word in title_lower for word in ["flight", "train", "travel", "trip"]):
            return "travel"

        return "other"

    def get_event_priority(self, event: ProcessedEvent) -> int:
        """
        Calculate event priority (1-5, where 1 is highest priority).

        Args:
            event: Processed event

        Returns:
            Priority level (1-5)
        """
        priority = 3  # Default priority

        # Urgent events get highest priority
        if event.is_urgent:
            priority = 1

        # Meetings and appointments get higher priority
        category = self.categorize_event(event)
        if category in ["meeting", "appointment"]:
            priority = min(priority, 2)

        # Long duration events get lower priority
        if event.duration and event.duration > timedelta(hours=2):
            priority = min(priority + 1, 5)

        return priority

    def create_event_context(self, event: ProcessedEvent) -> Dict[str, Any]:
        """
        Create rich context for an event.

        Args:
            event: Processed event

        Returns:
            Event context dictionary
        """
        category = self.categorize_event(event)
        priority = self.get_event_priority(event)

        context = {
            "event_id": event.id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "duration_minutes": int(event.duration.total_seconds() / 60) if event.duration else None,
            "location": event.location,
            "category": category,
            "priority": priority,
            "is_urgent": event.is_urgent,
            "formatted_start_time": event.formatted_start_time,
            "formatted_end_time": event.formatted_end_time,
            "timezone": event.timezone,
            "source": event.source,
            "processing_status": event.processing_status
        }

        return context


def create_event_processor(timezone: str = 'UTC') -> EventProcessor:
    """
    Factory function to create an event processor.

    Args:
        timezone: Default timezone

    Returns:
        EventProcessor instance
    """
    return EventProcessor(default_timezone=timezone)
