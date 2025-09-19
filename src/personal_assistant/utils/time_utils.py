"""
Centralized time utilities for consistent timezone handling across the application.

This module provides standardized time functions to ensure all parts of the application
use consistent timezone handling, preventing time-related bugs and inconsistencies.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional


def get_current_utc_time() -> datetime:
    """
    Get current time in UTC timezone.
    
    Returns:
        datetime: Current time in UTC timezone
    """
    return datetime.now(timezone.utc)


def get_current_local_time() -> datetime:
    """
    Get current time in local system timezone.
    
    Returns:
        datetime: Current time in local system timezone
    """
    return datetime.now()


def format_time_for_display(dt: datetime, include_timezone: bool = True) -> str:
    """
    Format datetime for display in prompts and user interfaces.
    
    Args:
        dt: Datetime object to format
        include_timezone: Whether to include timezone information
        
    Returns:
        str: Formatted time string
    """
    if include_timezone:
        return dt.strftime('%Y-%m-%d %H:%M %Z')
    else:
        return dt.strftime('%Y-%m-%d %H:%M')


def get_current_time_for_prompts() -> str:
    """
    Get current time formatted for use in agent prompts.
    
    This function ensures consistent time display across all prompt builders.
    Shows Montreal local time for better user experience while maintaining
    UTC consistency for database storage.
    
    Returns:
        str: Formatted current time string in Montreal timezone
    """
    current_time = get_current_montreal_time()
    return format_time_for_display(current_time, include_timezone=True)


def get_current_montreal_time() -> datetime:
    """
    Get current time in Montreal timezone (Eastern Time).
    
    Automatically handles Daylight Saving Time transitions:
    - EDT (UTC-4) during summer months
    - EST (UTC-5) during winter months
    
    Returns:
        datetime: Current time in Montreal timezone
    """
    utc_time = get_current_utc_time()
    montreal_tz = get_montreal_timezone()
    return utc_time.astimezone(montreal_tz)


def get_montreal_timezone() -> timezone:
    """
    Get Montreal timezone with automatic DST handling.
    
    Returns:
        timezone: Montreal timezone object
    """
    # Montreal uses Eastern Time with automatic DST
    # We'll use a simple approach: check if we're in DST period
    now = datetime.now()
    
    # DST typically runs from second Sunday in March to first Sunday in November
    # For simplicity, we'll use approximate dates
    # March 10 to November 3 (approximate DST period)
    
    is_dst = _is_dst_period(now)
    offset_hours = -4 if is_dst else -5  # EDT is UTC-4, EST is UTC-5
    
    return timezone(timedelta(hours=offset_hours))


def _is_dst_period(dt: datetime) -> bool:
    """
    Determine if a given datetime falls within Daylight Saving Time period.
    
    Args:
        dt: Datetime to check
        
    Returns:
        bool: True if DST is active, False otherwise
    """
    # Approximate DST period: March 10 to November 3
    # This is a simplified approach - for production, consider using pytz or zoneinfo
    
    month = dt.month
    
    if month < 3 or month > 11:
        return False  # Winter months
    elif month > 3 and month < 11:
        return True   # Summer months
    elif month == 3:
        # March: DST starts around 2nd Sunday
        return dt.day >= 10
    elif month == 11:
        # November: DST ends around 1st Sunday
        return dt.day < 3
    
    return False


def get_current_time_for_logs() -> str:
    """
    Get current time formatted for logging purposes.
    
    Returns:
        str: ISO formatted current time string
    """
    return get_current_utc_time().isoformat()


def ensure_utc_timezone(dt: datetime) -> datetime:
    """
    Ensure a datetime object is timezone-aware and in UTC.
    
    Args:
        dt: Datetime object to convert
        
    Returns:
        datetime: UTC timezone-aware datetime
    """
    if dt.tzinfo is None:
        # Naive datetime - assume it's UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # Timezone-aware datetime - convert to UTC
        return dt.astimezone(timezone.utc)


def parse_time_string(time_str: str) -> Optional[datetime]:
    """
    Parse a time string and return UTC datetime.
    
    Args:
        time_str: Time string to parse
        
    Returns:
        datetime: Parsed datetime in UTC, or None if parsing fails
    """
    try:
        # Try parsing ISO format first
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return ensure_utc_timezone(dt)
    except ValueError:
        try:
            # Try parsing common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
                dt = datetime.strptime(time_str, fmt)
                return ensure_utc_timezone(dt)
        except ValueError:
            return None
