"""
Context builder for calendar events to provide rich context to AgentCore.

This module extracts and builds comprehensive context from events including
recurrence patterns, user preferences, and processing history.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EventContext:
    """Rich context for event evaluation."""
    event_id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    user_id: int
    source: str
    processing_status: str
    recurrence_hint: Optional[str]
    last_processed: Optional[datetime]
    time_until_start: timedelta
    is_urgent: bool
    event_type: str
    location: Optional[str]
    attendees: Optional[List[str]]
    priority: str


class EventContextBuilder:
    """
    Builder for rich event context to provide to AgentCore.

    This class extracts recurrence patterns, user preferences, and other
    contextual information to help AI make intelligent decisions about events.
    """

    def __init__(self):
        self.logger = logger

    def build_event_context(self, event) -> EventContext:
        """
        Build rich context from an event object.

        Args:
            event: Event object from database

        Returns:
            EventContext with comprehensive information
        """
        now = datetime.utcnow()

        # Extract recurrence pattern from title
        recurrence_hint = self._extract_recurrence_hint(event.title)

        # Calculate time until event
        time_until_start = event.start_time - now

        # Determine if event is urgent
        is_urgent = time_until_start <= timedelta(minutes=30)

        # Categorize event type
        event_type = self._categorize_event_type(
            event.title, event.description)

        # Extract location
        location = self._extract_location(event.description)

        # Determine priority
        priority = self._determine_priority(
            event.title, is_urgent, time_until_start)

        return EventContext(
            event_id=event.id,
            title=event.title,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            user_id=event.user_id,
            source=event.source,
            processing_status=event.processing_status,
            recurrence_hint=recurrence_hint,
            last_processed=event.handled_at,
            time_until_start=time_until_start,
            is_urgent=is_urgent,
            event_type=event_type,
            location=location,
            attendees=None,  # Could be extracted from description
            priority=priority
        )

    def create_ai_context(self, event_context: EventContext) -> Dict[str, Any]:
        """
        Create context dictionary for AgentCore analysis.

        Args:
            event_context: Rich event context

        Returns:
            Dictionary with context for AI evaluation
        """
        return {
            "event": {
                "id": event_context.event_id,
                "title": event_context.title,
                "description": event_context.description,
                "start_time": event_context.start_time.isoformat(),
                "end_time": event_context.end_time.isoformat() if event_context.end_time else None,
                "type": event_context.event_type,
                "location": event_context.location,
                "priority": event_context.priority
            },
            "timing": {
                "time_until_start_hours": event_context.time_until_start.total_seconds() / 3600,
                "is_urgent": event_context.is_urgent,
                "is_soon": event_context.time_until_start <= timedelta(hours=1)
            },
            "recurrence": {
                "hint": event_context.recurrence_hint,
                "is_recurring": event_context.recurrence_hint is not None,
                "pattern": self._analyze_recurrence_pattern(event_context.recurrence_hint)
            },
            "processing": {
                "status": event_context.processing_status,
                "last_processed": event_context.last_processed.isoformat() if event_context.last_processed else None,
                "days_since_last_processed": self._days_since_processed(event_context.last_processed)
            },
            "user_context": {
                "user_id": event_context.user_id,
                "source": event_context.source
            }
        }

    def _extract_recurrence_hint(self, title: str) -> Optional[str]:
        """
        Extract recurrence pattern from event title.

        Args:
            title: Event title

        Returns:
            Recurrence hint or None
        """
        if not title:
            return None

        # Common recurrence patterns
        patterns = [
            r'every\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'every\s+(day|week|month|year)',
            r'weekly',
            r'monthly',
            r'yearly',
            r'bi-weekly',
            r'bi-monthly',
            r'daily',
            r'each\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?'
        ]

        title_lower = title.lower()
        for pattern in patterns:
            match = re.search(pattern, title_lower)
            if match:
                return match.group(0)

        return None

    def _analyze_recurrence_pattern(self, recurrence_hint: Optional[str]) -> Dict[str, Any]:
        """
        Analyze recurrence pattern for AI understanding.

        Args:
            recurrence_hint: Recurrence hint from title

        Returns:
            Dictionary with pattern analysis
        """
        if not recurrence_hint:
            return {"type": "none", "frequency": "none"}

        hint_lower = recurrence_hint.lower()

        # Analyze frequency
        if 'daily' in hint_lower or 'every day' in hint_lower:
            return {"type": "daily", "frequency": "daily"}
        elif 'weekly' in hint_lower or 'every week' in hint_lower:
            return {"type": "weekly", "frequency": "weekly"}
        elif 'monthly' in hint_lower or 'every month' in hint_lower:
            return {"type": "monthly", "frequency": "monthly"}
        elif 'yearly' in hint_lower or 'every year' in hint_lower:
            return {"type": "yearly", "frequency": "yearly"}
        elif any(day in hint_lower for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
            return {"type": "weekly", "frequency": "weekly", "specific_day": True}
        else:
            return {"type": "custom", "frequency": "unknown", "pattern": recurrence_hint}

    def _categorize_event_type(self, title: str, description: Optional[str]) -> str:
        """
        Categorize event type based on title and description.

        Args:
            title: Event title
            description: Event description

        Returns:
            Event type category
        """
        if not title:
            return "unknown"

        title_lower = title.lower()
        desc_lower = (description or "").lower()

        # Meeting/Appointment patterns
        if any(word in title_lower for word in ['meeting', 'appointment', 'call', 'interview']):
            return "meeting"

        # Task/Reminder patterns
        if any(word in title_lower for word in ['reminder', 'task', 'todo', 'check', 'review']):
            return "task"

        # Social patterns
        if any(word in title_lower for word in ['party', 'dinner', 'lunch', 'coffee', 'drinks', 'social']):
            return "social"

        # Work patterns
        if any(word in title_lower for word in ['work', 'project', 'deadline', 'report', 'presentation']):
            return "work"

        # Health patterns
        if any(word in title_lower for word in ['doctor', 'dentist', 'gym', 'workout', 'exercise', 'health']):
            return "health"

        # Travel patterns
        if any(word in title_lower for word in ['travel', 'flight', 'trip', 'vacation', 'holiday']):
            return "travel"

        return "general"

    def _extract_location(self, description: Optional[str]) -> Optional[str]:
        """
        Extract location from event description.

        Args:
            description: Event description

        Returns:
            Location string or None
        """
        if not description:
            return None

        # Simple location extraction (could be enhanced)
        location_patterns = [
            r'at\s+([A-Za-z0-9\s]+)',
            r'in\s+([A-Za-z0-9\s]+)',
            r'location:\s*([A-Za-z0-9\s]+)',
            r'venue:\s*([A-Za-z0-9\s]+)'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _determine_priority(self, title: str, is_urgent: bool, time_until_start: timedelta) -> str:
        """
        Determine event priority based on various factors.

        Args:
            title: Event title
            is_urgent: Whether event is urgent
            time_until_start: Time until event starts

        Returns:
            Priority level
        """
        if is_urgent:
            return "high"

        title_lower = title.lower()

        # High priority keywords
        if any(word in title_lower for word in ['urgent', 'important', 'critical', 'deadline', 'emergency']):
            return "high"

        # Medium priority keywords
        if any(word in title_lower for word in ['meeting', 'appointment', 'review', 'check']):
            return "medium"

        # Time-based priority
        if time_until_start <= timedelta(hours=1):
            return "medium"
        elif time_until_start <= timedelta(hours=4):
            return "low"
        else:
            return "low"

    def _days_since_processed(self, last_processed: Optional[datetime]) -> Optional[float]:
        """
        Calculate days since last processed.

        Args:
            last_processed: Last processed timestamp

        Returns:
            Days since processed or None
        """
        if not last_processed:
            return None

        now = datetime.utcnow()
        delta = now - last_processed
        return delta.total_seconds() / (24 * 3600)


def create_context_builder() -> EventContextBuilder:
    """
    Factory function to create a context builder.

    Returns:
        EventContextBuilder instance
    """
    return EventContextBuilder()
