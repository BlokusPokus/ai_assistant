"""
Time utilities for calendar event processing.

This module provides time-related utilities for filtering and processing
calendar events, including timezone handling and time window calculations.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


def get_time_window(hours_ahead: int = 2) -> Tuple[datetime, datetime]:
    """
    Get the time window for upcoming events.

    Args:
        hours_ahead: Number of hours to look ahead (default: 2)

    Returns:
        Tuple of (start_time, end_time) in UTC
    """
    now = datetime.utcnow()
    end_time = now + timedelta(hours=hours_ahead)

    logger.debug(f"Time window: {now} to {end_time} (UTC)")
    return now, end_time


def is_event_in_timeframe(event_start: datetime, event_end: Optional[datetime],
                          window_start: datetime, window_end: datetime) -> bool:
    """
    Check if an event falls within the specified time window.

    Args:
        event_start: Event start time
        event_end: Event end time (optional)
        window_start: Window start time
        window_end: Window end time

    Returns:
        True if event overlaps with time window
    """
    # Event starts within the window
    if window_start <= event_start <= window_end:
        return True

    # Event ends within the window
    if event_end and window_start <= event_end <= window_end:
        return True

    # Event spans the entire window
    if event_start <= window_start and event_end and event_end >= window_end:
        return True

    return False


def normalize_event_time(event_time: datetime, timezone: str = 'UTC') -> datetime:
    """
    Normalize event time to a specific timezone.

    Args:
        event_time: Event time to normalize
        timezone: Target timezone (default: UTC)

    Returns:
        Normalized datetime in target timezone
    """
    try:
        if event_time.tzinfo is None:
            # Assume UTC if no timezone info
            event_time = event_time.replace(tzinfo=ZoneInfo('UTC'))

        # Convert to target timezone
        target_tz = ZoneInfo(timezone)
        normalized_time = event_time.astimezone(target_tz)

        logger.debug(
            f"Normalized {event_time} to {normalized_time} ({timezone})")
        return normalized_time

    except Exception as e:
        logger.warning(f"Error normalizing time {event_time}: {e}")
        return event_time


def calculate_event_duration(start_time: datetime, end_time: Optional[datetime]) -> Optional[timedelta]:
    """
    Calculate the duration of an event.

    Args:
        start_time: Event start time
        end_time: Event end time (optional)

    Returns:
        Event duration as timedelta, or None if end_time is not provided
    """
    if not end_time:
        return None

    return end_time - start_time


def is_event_urgent(event_start: datetime, hours_threshold: int = 1) -> bool:
    """
    Check if an event is urgent (starting within threshold hours).

    Args:
        event_start: Event start time
        hours_threshold: Hours threshold for urgency (default: 1)

    Returns:
        True if event is urgent
    """
    now = datetime.utcnow()
    threshold_time = now + timedelta(hours=hours_threshold)

    return now <= event_start <= threshold_time


def format_event_time(event_time: datetime, timezone: str = 'UTC') -> str:
    """
    Format event time for display.

    Args:
        event_time: Event time to format
        timezone: Timezone for formatting (default: UTC)

    Returns:
        Formatted time string
    """
    try:
        normalized_time = normalize_event_time(event_time, timezone)
        return normalized_time.strftime('%Y-%m-%d %H:%M %Z')
    except Exception as e:
        logger.warning(f"Error formatting time {event_time}: {e}")
        return event_time.strftime('%Y-%m-%d %H:%M')


def get_user_timezone(user_id: int) -> str:
    """
    Get user's timezone preference.

    Args:
        user_id: User ID

    Returns:
        User's timezone (default: UTC)
    """
    # TODO: Implement user timezone lookup from database
    # For now, return UTC as default
    return 'UTC'


def validate_event_times(start_time: datetime, end_time: Optional[datetime]) -> bool:
    """
    Validate event start and end times.

    Args:
        start_time: Event start time
        end_time: Event end time (optional)

    Returns:
        True if times are valid
    """
    if not start_time:
        logger.warning("Event start time is required")
        return False

    if end_time and start_time >= end_time:
        logger.warning("Event start time must be before end time")
        return False

    return True
