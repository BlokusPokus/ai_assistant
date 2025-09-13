"""
Internal functions for YouTube Tool.

This module contains internal utility functions and helper methods
that are used by the main YouTubeTool class.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def extract_video_id(video_input: str) -> str:
    """Extract video ID from various YouTube URL formats"""
    if not video_input:
        return ""

    video_input = video_input.strip()

    # Handle different YouTube URL formats
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",  # Direct video ID
    ]

    for pattern in patterns:
        match = re.search(pattern, video_input)
        if match:
            return match.group(1)

    # If no pattern matches, assume it's already a video ID
    return video_input


def extract_channel_id(channel_input: str) -> str:
    """Extract channel ID from various YouTube channel formats"""
    if not channel_input:
        return ""

    channel_input = channel_input.strip()

    # Handle different YouTube channel URL formats
    patterns = [
        r"(?:youtube\.com/channel/|youtube\.com/c/|youtube\.com/user/|youtube\.com/@)([a-zA-Z0-9_-]+)",
        r"^([a-zA-Z0-9_-]+)$",  # Direct channel ID/username
    ]

    for pattern in patterns:
        match = re.search(pattern, channel_input)
        if match:
            return match.group(1)

    return channel_input


def extract_playlist_id(playlist_input: str) -> str:
    """Extract playlist ID from various YouTube playlist formats"""
    if not playlist_input:
        return ""

    playlist_input = playlist_input.strip()

    # Handle different YouTube playlist URL formats
    patterns = [
        r"(?:youtube\.com/playlist\?list=|youtube\.com/watch\?v=.*&list=)([a-zA-Z0-9_-]+)",
        r"^([a-zA-Z0-9_-]+)$",  # Direct playlist ID
    ]

    for pattern in patterns:
        match = re.search(pattern, playlist_input)
        if match:
            return match.group(1)

    return playlist_input


def check_quota_limit(quota_used: int) -> bool:
    """Check if we're within YouTube API quota limits"""
    # Simple quota checking - in production, implement proper quota tracking
    if quota_used > 10000:  # Daily quota is typically 10,000 units
        logger.warning("YouTube API quota limit approaching")
        return False
    return True


def validate_format(format_type: str) -> str:
    """Validate and normalize output format"""
    valid_formats = ["text", "json", "srt"]
    if format_type not in valid_formats:
        logger.warning(f"Invalid format: {format_type}, defaulting to text")
        return "text"
    return format_type


def format_duration(duration: str) -> str:
    """Convert ISO 8601 duration to human readable format"""
    if not duration:
        return "Unknown"

    # Parse ISO 8601 duration (PT1H2M3S)
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if match:
        hours, minutes, seconds = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    return duration


def format_view_count(view_count: str) -> str:
    """Format view count with K, M, B suffixes"""
    if not view_count:
        return "0"

    try:
        count = int(view_count)
        if count >= 1000000000:
            return f"{count/1000000000:.1f}B"
        elif count >= 1000000:
            return f"{count/1000000:.1f}M"
        elif count >= 1000:
            return f"{count/1000:.1f}K"
        else:
            return str(count)
    except (ValueError, TypeError):
        return view_count


def build_search_parameters(
    query: str,
    max_results: int,
    video_duration: Optional[str] = None,
    upload_date: Optional[str] = None,
) -> dict:
    """Build search parameters for YouTube API search"""
    search_params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": min(max_results, 50),
        "order": "relevance",
    }

    # Add duration filter
    if video_duration:
        duration_map = {
            "short": "short",  # < 4 minutes
            "medium": "medium",  # 4-20 minutes
            "long": "long",  # > 20 minutes
        }
        if video_duration in duration_map:
            search_params["videoDuration"] = duration_map[video_duration]

    # Add date filter
    if upload_date:
        date_map = {
            "hour": "thisHour",
            "today": "today",
            "week": "thisWeek",
            "month": "thisMonth",
            "year": "thisYear",
        }
        if upload_date in date_map:
            search_params["publishedAfter"] = date_map[upload_date]

    return search_params


def validate_search_parameters(max_results: int, max_videos: int) -> tuple[int, int]:
    """Validate and normalize search parameters"""
    if max_results < 1 or max_results > 50:
        max_results = 10
        logger.warning(f"Invalid max_results: {max_results}, defaulting to 10")

    if max_videos < 1 or max_videos > 100:
        max_videos = 20
        logger.warning(f"Invalid max_videos: {max_videos}, defaulting to 20")

    return max_results, max_videos
