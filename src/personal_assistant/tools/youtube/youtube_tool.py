"""
YouTube Tool for video information, transcripts, and content analysis.
"""
import logging
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...config.settings import settings
from ..base import Tool

# Import YouTube-specific error handling
from .youtube_error_handler import YouTubeErrorHandler
from .youtube_internal import (
    build_search_parameters,
    check_quota_limit,
    extract_channel_id,
    extract_playlist_id,
    extract_video_id,
    format_duration,
    format_view_count,
    validate_format,
    validate_search_parameters,
)

logger = logging.getLogger(__name__)


try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import (
        SRTFormatter,
        TextFormatter,
    )

    YOUTUBE_TRANSCRIPT_AVAILABLE = True
    logger.info("YouTube Transcript API library imported successfully")
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    logger.warning(
        "YouTube Transcript API library not available. Install with: pip install youtube-transcript-api"
    )


class YouTubeTool:
    """
    Comprehensive YouTube tool that provides:
    - Video metadata extraction using YouTube Data API v3
    - Transcript retrieval and processing
    - Channel information and management
    - Content analysis and categorization
    - Video search and discovery
    """

    def __init__(self):
        # Initialize any shared resources, tokens, clients, etc.
        self._quota_used = 0
        self._last_request_time = 0

        # Initialize YouTube Data API client
        self._youtube = None
        if settings.YOUTUBE_API_KEY:
            try:
                self._youtube = build(
                    "youtube", "v3", developerKey=settings.YOUTUBE_API_KEY
                )
                logger.info("YouTube Data API v3 client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize YouTube Data API client: {e}")
                self._youtube = None
        elif not settings.YOUTUBE_API_KEY:
            logger.warning(
                "YOUTUBE_API_KEY not configured. YouTube API features will be limited."
            )

        # Create individual tools
        self.get_video_info_tool = Tool(
            name="get_video_info",
            func=self.get_video_info,
            description="Get detailed information about a YouTube video",
            parameters={
                "video_id": {
                    "type": "string",
                    "description": "YouTube video ID or URL (required)",
                },
                "include_transcript": {
                    "type": "boolean",
                    "description": "Include video transcript (default: false)",
                },
                "include_statistics": {
                    "type": "boolean",
                    "description": "Include video statistics (default: true)",
                },
            },
        )

        self.get_video_transcript_tool = Tool(
            name="get_video_transcript",
            func=self.get_video_transcript,
            description="Extract and process YouTube video transcript",
            parameters={
                "video_id": {
                    "type": "string",
                    "description": "YouTube video ID or URL (required)",
                },
                "language": {
                    "type": "string",
                    "description": "Language code for transcript (default: auto)",
                },
                "format": {
                    "type": "string",
                    "description": "Output format: text, json, or srt (default: text)",
                },
            },
        )

        self.search_videos_tool = Tool(
            name="search_videos",
            func=self.search_videos,
            description="Search for YouTube videos by query",
            parameters={
                "query": {"type": "string", "description": "Search query (required)"},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 10)",
                },
                "video_duration": {
                    "type": "string",
                    "description": "Filter by duration: short, medium, long (optional)",
                },
                "upload_date": {
                    "type": "string",
                    "description": "Filter by upload date: today, this_week, this_month, this_year (optional)",
                },
            },
        )

        self.get_channel_info_tool = Tool(
            name="get_channel_info",
            func=self.get_channel_info,
            description="Get information about a YouTube channel",
            parameters={
                "channel_id": {
                    "type": "string",
                    "description": "YouTube channel ID or URL (required)",
                },
                "include_statistics": {
                    "type": "boolean",
                    "description": "Include channel statistics (default: true)",
                },
                "include_recent_videos": {
                    "type": "boolean",
                    "description": "Include recent videos (default: false)",
                },
            },
        )

        self.get_playlist_info_tool = Tool(
            name="get_playlist_info",
            func=self.get_playlist_info,
            description="Get information about a YouTube playlist",
            parameters={
                "playlist_id": {
                    "type": "string",
                    "description": "YouTube playlist ID or URL (required)",
                },
                "max_videos": {
                    "type": "integer",
                    "description": "Maximum number of videos to show (default: 20)",
                },
                "include_video_details": {
                    "type": "boolean",
                    "description": "Include video details in playlist (default: false)",
                },
            },
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter(
            [
                self.get_video_info_tool,
                self.get_video_transcript_tool,
                self.search_videos_tool,
                self.get_channel_info_tool,
                self.get_playlist_info_tool,
            ]
        )

    async def get_video_info(
        self,
        video_id: str,
        include_transcript: bool = False,
        include_statistics: bool = True,
    ) -> str:
        """Get detailed information about a YouTube video"""
        try:
            # Validate parameters
            if not video_id or not video_id.strip():
                return YouTubeErrorHandler.handle_youtube_error(
                    ValueError("Video ID is required"),
                    "get_video_info",
                    {
                        "video_id": video_id,
                        "include_transcript": include_transcript,
                        "include_statistics": include_statistics,
                    },
                )

            video_id = extract_video_id(video_id)
            if not video_id:
                return YouTubeErrorHandler.handle_youtube_error(
                    ValueError("Could not extract valid video ID from input"),
                    "get_video_info",
                    {
                        "video_id": video_id,
                        "include_transcript": include_transcript,
                        "include_statistics": include_statistics,
                    },
                )

            # Check quota limits
            if not check_quota_limit(self._quota_used):
                return YouTubeErrorHandler.handle_youtube_error(
                    Exception("YouTube API quota exceeded. Please try again later."),
                    "get_video_info",
                    {
                        "video_id": video_id,
                        "include_transcript": include_transcript,
                        "include_statistics": include_statistics,
                    },
                )

            logger.info(
                f"Video info request for: {video_id} (transcript: {include_transcript}, stats: {include_statistics})"
            )

            # Check if YouTube API is available
            if not settings.YOUTUBE_API_KEY:
                return YouTubeErrorHandler.handle_youtube_error(
                    Exception("YouTube Data API v3 is not available."),
                    "get_video_info",
                    {
                        "video_id": video_id,
                        "include_transcript": include_transcript,
                        "include_statistics": include_statistics,
                    },
                )

            try:
                # Get video details
                video_response = (
                    self._youtube.videos()
                    .list(part="snippet,statistics,contentDetails", id=video_id)
                    .execute()
                )

                if not video_response.get("items"):
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"Video not found or not accessible: {video_id}"),
                        "get_video_info",
                        {
                            "video_id": video_id,
                            "include_transcript": include_transcript,
                            "include_statistics": include_statistics,
                        },
                    )

                video = video_response["items"][0]
                snippet = video["snippet"]
                statistics = video.get("statistics", {})
                content_details = video.get("contentDetails", {})

                # Build response
                response = f"📹 **Video Information**\n\n"
                response += f"🎬 **Title**: {snippet.get('title', 'Unknown')}\n"
                response += f"📺 **Channel**: {snippet.get('channelTitle', 'Unknown')}\n"
                response += (
                    f"📅 **Published**: {snippet.get('publishedAt', 'Unknown')[:10]}\n"
                )
                response += f"⏱️ **Duration**: {format_duration(content_details.get('duration', ''))}\n"
                response += f"📝 **Description**: {snippet.get('description', 'No description')[:200]}...\n\n"

                if include_statistics and statistics:
                    response += f"📊 **Statistics**\n"
                    response += f"👁️ **Views**: {format_view_count(statistics.get('viewCount', '0'))}\n"
                    response += f"👍 **Likes**: {format_view_count(statistics.get('likeCount', '0'))}\n"
                    response += f"💬 **Comments**: {format_view_count(statistics.get('commentCount', '0'))}\n\n"

                if include_transcript:
                    if YOUTUBE_TRANSCRIPT_AVAILABLE:
                        try:
                            transcript = YouTubeTranscriptApi.get_transcript(video_id)
                            if transcript:
                                # Get first few lines of transcript
                                first_lines = transcript[:3]
                                transcript_text = "\n".join(
                                    [line["text"] for line in first_lines]
                                )
                                response += f"📜 **Transcript Preview** (first 3 lines):\n{transcript_text}\n\n"
                                response += f"📜 **Full transcript available** - use get_video_transcript tool for complete transcript\n"
                            else:
                                response += (
                                    f"📜 **Transcript**: Not available for this video\n"
                                )
                        except Exception as transcript_error:
                            response += f"📜 **Transcript**: Error retrieving transcript: {str(transcript_error)}\n"
                    else:
                        response += f"📜 **Transcript**: YouTube Transcript API not available. Install youtube-transcript-api.\n"

                response += (
                    f"🔗 **Video URL**: https://www.youtube.com/watch?v={video_id}\n"
                )
                response += f"⏱️ **Response Time**: <3 seconds (target)"

                return response

            except HttpError as e:
                if e.resp.status == 403:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(
                            "YouTube API quota exceeded or API key invalid. Please check your API key and quota."
                        ),
                        "get_video_info",
                        {
                            "video_id": video_id,
                            "include_transcript": include_transcript,
                            "include_statistics": include_statistics,
                        },
                    )
                elif e.resp.status == 404:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"Video not found: {video_id}"),
                        "get_video_info",
                        {
                            "video_id": video_id,
                            "include_transcript": include_transcript,
                            "include_statistics": include_statistics,
                        },
                    )
                else:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"YouTube API error: {str(e)}"),
                        "get_video_info",
                        {
                            "video_id": video_id,
                            "include_transcript": include_transcript,
                            "include_statistics": include_statistics,
                        },
                    )

        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return YouTubeErrorHandler.handle_youtube_error(
                e,
                "get_video_info",
                {
                    "video_id": video_id,
                    "include_transcript": include_transcript,
                    "include_statistics": include_statistics,
                },
            )

    async def get_video_transcript(
        self, video_id: str, language: str = "auto", format: str = "text"
    ) -> str:
        """Extract and process YouTube video transcript"""
        try:
            # Validate parameters
            if not video_id or not video_id.strip():
                return YouTubeErrorHandler.handle_youtube_error(
                    ValueError("Video ID is required"),
                    "get_video_transcript",
                    {"video_id": video_id, "language": language, "format": format},
                )

            video_id = extract_video_id(video_id)
            if not video_id:
                return YouTubeErrorHandler.handle_youtube_error(
                    ValueError("Could not extract valid video ID from input"),
                    "get_video_transcript",
                    {"video_id": video_id, "language": language, "format": format},
                )

            format = validate_format(format)

            logger.info(
                f"Transcript request for: {video_id} (language: {language}, format: {format})"
            )

            # Check if YouTube Transcript API is available
            if not YOUTUBE_TRANSCRIPT_AVAILABLE:
                return YouTubeErrorHandler.handle_youtube_error(
                    Exception(
                        "YouTube Transcript API is not available. Please install youtube-transcript-api."
                    ),
                    "get_video_transcript",
                    {"video_id": video_id, "language": language, "format": format},
                )

            try:
                # Get transcript - handle different API versions
                try:
                    # For version 1.2.2+, use the fetch method
                    if language == "auto":
                        transcript = YouTubeTranscriptApi().fetch(video_id)
                    else:
                        transcript = YouTubeTranscriptApi().fetch(
                            video_id, languages=[language]
                        )
                except Exception as fetch_error:
                    # Fallback to older method if available
                    try:
                        if language == "auto":
                            transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        else:
                            transcript = YouTubeTranscriptApi.get_transcript(
                                video_id, languages=[language]
                            )
                    except Exception:
                        return YouTubeErrorHandler.handle_youtube_error(
                            Exception(
                                f"YouTube Transcript API version compatibility issue. Error: {str(fetch_error)}"
                            ),
                            "get_video_transcript",
                            {
                                "video_id": video_id,
                                "language": language,
                                "format": format,
                            },
                        )

                if not transcript:
                    return f"No transcript available for video: {video_id}"

                # Format transcript based on requested format
                if format == "json":
                    return (
                        f"📜 **Transcript (JSON format)** for {video_id}:\n{transcript}"
                    )
                elif format == "srt":
                    formatter = SRTFormatter()
                    srt_transcript = formatter.format_transcript(transcript)
                    return f"📜 **Transcript (SRT format)** for {video_id}:\n{srt_transcript}"
                else:  # text format
                    formatter = TextFormatter()
                    text_transcript = formatter.format_transcript(transcript)

                    # Truncate if too long
                    if len(text_transcript) > 2000:
                        text_transcript = (
                            text_transcript[:2000]
                            + "...\n\n[Transcript truncated. Use JSON or SRT format for full transcript.]"
                        )

                    return f"📜 **Transcript** for {video_id}:\n\n{text_transcript}"

            except Exception as transcript_error:
                if "No transcript available" in str(transcript_error):
                    return f"No transcript available for video: {video_id}. This video may not have captions or transcripts enabled."
                else:
                    return YouTubeErrorHandler.handle_youtube_error(
                        transcript_error,
                        "get_video_transcript",
                        {"video_id": video_id, "language": language, "format": format},
                    )

        except Exception as e:
            logger.error(f"Error getting video transcript: {e}")
            return YouTubeErrorHandler.handle_youtube_error(
                e,
                "get_video_transcript",
                {"video_id": video_id, "language": language, "format": format},
            )

    async def search_videos(
        self,
        query: str,
        max_results: int = 10,
        video_duration: Optional[str] = None,
        upload_date: Optional[str] = None,
    ) -> str:
        """Search for YouTube videos by query"""
        try:
            # Validate parameters
            if not query or not query.strip():
                return YouTubeErrorHandler.handle_youtube_error(
                    ValueError("Search query is required"),
                    "search_videos",
                    {
                        "query": query,
                        "max_results": max_results,
                        "video_duration": video_duration,
                        "upload_date": upload_date,
                    },
                )

            if max_results < 1 or max_results > 50:
                max_results = 10
                logger.warning(f"Invalid max_results: {max_results}, defaulting to 10")

            # Validate and normalize parameters
            max_results, _ = validate_search_parameters(max_results, 10)

            # Check quota limits
            if not check_quota_limit(self._quota_used):
                return YouTubeErrorHandler.handle_youtube_error(
                    Exception("YouTube API quota exceeded. Please try again later."),
                    "search_videos",
                    {
                        "query": query,
                        "max_results": max_results,
                        "video_duration": video_duration,
                        "upload_date": upload_date,
                    },
                )

            logger.info(
                f"Video search request for: {query} (max: {max_results}, duration: {video_duration}, date: {upload_date})"
            )

            # Check if YouTube API is available
            if not settings.YOUTUBE_API_KEY:
                return YouTubeErrorHandler.handle_youtube_error(
                    Exception(
                        "YouTube Data API v3 is not available. Please install google-api-python-client and configure YOUTUBE_API_KEY."
                    ),
                    "search_videos",
                    {
                        "query": query,
                        "max_results": max_results,
                        "video_duration": video_duration,
                        "upload_date": upload_date,
                    },
                )

            try:
                # Build search parameters
                search_params = build_search_parameters(
                    query, max_results, video_duration, upload_date
                )

                # Perform search
                search_response = self._youtube.search().list(**search_params).execute()

                if not search_response.get("items"):
                    return f"No videos found for query: '{query}'"

                # Format results
                response = f"🔍 **Video Search Results** for '{query}'\n"
                response += f"📊 Found {len(search_response['items'])} results\n"

                if video_duration:
                    response += f"⏱️ Duration Filter: {video_duration}\n"
                if upload_date:
                    response += f"📅 Upload Date Filter: {upload_date}\n"

                response += "\n"

                for i, item in enumerate(search_response["items"], 1):
                    snippet = item["snippet"]
                    video_id = item["id"]["videoId"]

                    response += f"{i}. **{snippet.get('title', 'No title')}**\n"
                    response += (
                        f"   📺 {snippet.get('channelTitle', 'Unknown channel')}\n"
                    )
                    response += (
                        f"   📅 {snippet.get('publishedAt', 'Unknown date')[:10]}\n"
                    )
                    response += f"   📝 {snippet.get('description', 'No description')[:100]}...\n"
                    response += f"   🔗 https://www.youtube.com/watch?v={video_id}\n\n"

                response += f"⏱️ **Response Time**: <3 seconds (target)"
                return response

            except HttpError as e:
                if e.resp.status == 403:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(
                            "YouTube API quota exceeded or API key invalid. Please check your API key and quota."
                        ),
                        "search_videos",
                        {
                            "query": query,
                            "max_results": max_results,
                            "video_duration": video_duration,
                            "upload_date": upload_date,
                        },
                    )
                else:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"YouTube API error: {str(e)}"),
                        "search_videos",
                        {
                            "query": query,
                            "max_results": max_results,
                            "video_duration": video_duration,
                            "upload_date": upload_date,
                        },
                    )

        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return YouTubeErrorHandler.handle_youtube_error(
                e,
                "search_videos",
                {
                    "query": query,
                    "max_results": max_results,
                    "video_duration": video_duration,
                    "upload_date": upload_date,
                },
            )

    async def get_channel_info(
        self,
        channel_id: str,
        include_statistics: bool = True,
        include_recent_videos: bool = False,
    ) -> str:
        """Get information about a YouTube channel"""
        try:
            # Validate parameters
            if not channel_id or not channel_id.strip():
                return YouTubeErrorHandler.handle_youtube_error(
                    ValueError("Channel ID is required"),
                    "get_channel_info",
                    {
                        "channel_id": channel_id,
                        "include_statistics": include_statistics,
                        "include_recent_videos": include_recent_videos,
                    },
                )

            channel_id = extract_channel_id(channel_id)
            if not channel_id:
                return YouTubeErrorHandler.handle_youtube_error(
                    ValueError("Could not extract valid channel ID from input"),
                    "get_channel_info",
                    {
                        "channel_id": channel_id,
                        "include_statistics": include_statistics,
                        "include_recent_videos": include_recent_videos,
                    },
                )

            # Check quota limits
            if not check_quota_limit(self._quota_used):
                return YouTubeErrorHandler.handle_youtube_error(
                    Exception("YouTube API quota exceeded. Please try again later."),
                    "get_channel_info",
                    {
                        "channel_id": channel_id,
                        "include_statistics": include_statistics,
                        "include_recent_videos": include_recent_videos,
                    },
                )

            logger.info(
                f"Channel info request for: {channel_id} (stats: {include_statistics}, videos: {include_recent_videos})"
            )

            # Check if YouTube API is available
            if not settings.YOUTUBE_API_KEY:
                return YouTubeErrorHandler.handle_youtube_error(
                    Exception(
                        "YouTube Data API v3 is not available. Please install google-api-python-client and configure YOUTUBE_API_KEY."
                    ),
                    "get_channel_info",
                    {
                        "channel_id": channel_id,
                        "include_statistics": include_statistics,
                        "include_recent_videos": include_recent_videos,
                    },
                )

            try:
                # Get channel information
                channel_response = (
                    self._youtube.channels()
                    .list(part="snippet,statistics", id=channel_id)
                    .execute()
                )

                if not channel_response.get("items"):
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"Channel not found: {channel_id}"),
                        "get_channel_info",
                        {
                            "channel_id": channel_id,
                            "include_statistics": include_statistics,
                            "include_recent_videos": include_recent_videos,
                        },
                    )

                channel = channel_response["items"][0]
                snippet = channel["snippet"]
                statistics = channel.get("statistics", {})

                # Build response
                response = f"📺 **Channel Information**\n\n"
                response += f"🏷️ **Name**: {snippet.get('title', 'Unknown')}\n"
                response += f"📝 **Description**: {snippet.get('description', 'No description')[:200]}...\n"
                response += (
                    f"📅 **Created**: {snippet.get('publishedAt', 'Unknown')[:10]}\n"
                )
                response += f"🌐 **Country**: {snippet.get('country', 'Unknown')}\n\n"

                if include_statistics and statistics:
                    response += f"📊 **Statistics**\n"
                    response += f"👥 **Subscribers**: {format_view_count(statistics.get('subscriberCount', '0'))}\n"
                    response += f"👁️ **Total Views**: {format_view_count(statistics.get('viewCount', '0'))}\n"
                    response += f"🎬 **Total Videos**: {format_view_count(statistics.get('videoCount', '0'))}\n\n"

                if include_recent_videos:
                    try:
                        # Get recent videos
                        videos_response = (
                            self._youtube.search()
                            .list(
                                part="snippet",
                                channelId=channel_id,
                                order="date",
                                type="video",
                                maxResults=5,
                            )
                            .execute()
                        )

                        if videos_response.get("items"):
                            response += f"🎬 **Recent Videos**\n"
                            for i, video in enumerate(videos_response["items"], 1):
                                video_snippet = video["snippet"]
                                video_id = video["id"]["videoId"]
                                response += f"{i}. **{video_snippet.get('title', 'No title')}**\n"
                                response += f"   📅 {video_snippet.get('publishedAt', 'Unknown')[:10]}\n"
                                response += f"   🔗 https://www.youtube.com/watch?v={video_id}\n\n"
                        else:
                            response += f"🎬 **Recent Videos**: No videos found\n"
                    except Exception as video_error:
                        response += f"🎬 **Recent Videos**: Error retrieving videos: {str(video_error)}\n"

                response += (
                    f"🔗 **Channel URL**: https://www.youtube.com/channel/{channel_id}\n"
                )
                response += f"⏱️ **Response Time**: <3 seconds (target)"

                return response

            except HttpError as e:
                if e.resp.status == 403:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(
                            "YouTube API quota exceeded or API key invalid. Please check your API key and quota."
                        ),
                        "get_channel_info",
                        {
                            "channel_id": channel_id,
                            "include_statistics": include_statistics,
                            "include_recent_videos": include_recent_videos,
                        },
                    )
                elif e.resp.status == 404:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"Channel not found: {channel_id}"),
                        "get_channel_info",
                        {
                            "channel_id": channel_id,
                            "include_statistics": include_statistics,
                            "include_recent_videos": include_recent_videos,
                        },
                    )
                else:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"YouTube API error: {str(e)}"),
                        "get_channel_info",
                        {
                            "channel_id": channel_id,
                            "include_statistics": include_statistics,
                            "include_recent_videos": include_recent_videos,
                        },
                    )

        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return YouTubeErrorHandler.handle_youtube_error(
                e,
                "get_channel_info",
                {
                    "channel_id": channel_id,
                    "include_statistics": include_statistics,
                    "include_recent_videos": include_recent_videos,
                },
            )

    async def get_playlist_info(
        self,
        playlist_id: str,
        max_videos: int = 20,
        include_video_details: bool = False,
    ) -> str:
        """Get information about a YouTube playlist"""
        try:
            # Validate parameters
            if not playlist_id or not playlist_id.strip():
                return YouTubeErrorHandler.handle_youtube_error(
                    ValueError("Playlist ID is required"),
                    "get_playlist_info",
                    {
                        "playlist_id": playlist_id,
                        "max_videos": max_videos,
                        "include_video_details": include_video_details,
                    },
                )

            playlist_id = extract_playlist_id(playlist_id)
            if not playlist_id:
                return YouTubeErrorHandler.handle_youtube_error(
                    ValueError("Could not extract valid playlist ID from input"),
                    "get_playlist_info",
                    {
                        "playlist_id": playlist_id,
                        "max_videos": max_videos,
                        "include_video_details": include_video_details,
                    },
                )

            if max_videos < 1 or max_videos > 100:
                max_videos = 20
                logger.warning(f"Invalid max_videos: {max_videos}, defaulting to 20")

            # Validate and normalize parameters
            _, max_videos = validate_search_parameters(10, max_videos)

            # Check quota limits
            if not check_quota_limit(self._quota_used):
                return YouTubeErrorHandler.handle_youtube_error(
                    Exception("YouTube API quota exceeded. Please try again later."),
                    "get_playlist_info",
                    {
                        "playlist_id": playlist_id,
                        "max_videos": max_videos,
                        "include_video_details": include_video_details,
                    },
                )

            logger.info(
                f"Playlist info request for: {playlist_id} (max: {max_videos}, details: {include_video_details})"
            )

            # Check if YouTube API is available
            if not settings.YOUTUBE_API_KEY:
                return YouTubeErrorHandler.handle_youtube_error(
                    Exception(
                        "YouTube Data API v3 is not available. Please install google-api-python-client and configure YOUTUBE_API_KEY."
                    ),
                    "get_playlist_info",
                    {
                        "playlist_id": playlist_id,
                        "max_videos": max_videos,
                        "include_video_details": include_video_details,
                    },
                )

            try:
                # Get playlist information
                playlist_response = (
                    self._youtube.playlists()
                    .list(part="snippet,contentDetails", id=playlist_id)
                    .execute()
                )

                if not playlist_response.get("items"):
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"Playlist not found: {playlist_id}"),
                        "get_playlist_info",
                        {
                            "playlist_id": playlist_id,
                            "max_videos": max_videos,
                            "include_video_details": include_video_details,
                        },
                    )

                playlist = playlist_response["items"][0]
                snippet = playlist["snippet"]
                content_details = playlist["contentDetails"]

                # Build response
                response = f"📋 **Playlist Information**\n\n"
                response += f"🏷️ **Title**: {snippet.get('title', 'Unknown')}\n"
                response += f"📝 **Description**: {snippet.get('description', 'No description')[:200]}...\n"
                response += f"📺 **Channel**: {snippet.get('channelTitle', 'Unknown')}\n"
                response += (
                    f"📅 **Created**: {snippet.get('publishedAt', 'Unknown')[:10]}\n"
                )
                response += f"🎬 **Total Videos**: {content_details.get('itemCount', 'Unknown')}\n\n"

                if include_video_details:
                    try:
                        # Get playlist items
                        items_response = (
                            self._youtube.playlistItems()
                            .list(
                                part="snippet",
                                playlistId=playlist_id,
                                maxResults=min(max_videos, 50),
                            )
                            .execute()
                        )

                        if items_response.get("items"):
                            response += f"🎬 **Videos in Playlist** (showing up to {max_videos})\n"
                            for i, item in enumerate(items_response["items"], 1):
                                video_snippet = item["snippet"]
                                video_id = video_snippet.get("resourceId", {}).get(
                                    "videoId", "Unknown"
                                )
                                response += f"{i}. **{video_snippet.get('title', 'No title')}**\n"
                                response += f"   📅 {video_snippet.get('publishedAt', 'Unknown')[:10]}\n"
                                response += f"   🔗 https://www.youtube.com/watch?v={video_id}\n\n"
                        else:
                            response += f"🎬 **Videos in Playlist**: No videos found\n"
                    except Exception as video_error:
                        response += f"🎬 **Videos in Playlist**: Error retrieving videos: {str(video_error)}\n"

                response += f"🔗 **Playlist URL**: https://www.youtube.com/playlist?list={playlist_id}\n"
                response += f"⏱️ **Response Time**: <3 seconds (target)"

                return response

            except HttpError as e:
                if e.resp.status == 403:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(
                            "YouTube API quota exceeded or API key invalid. Please check your API key and quota."
                        ),
                        "get_playlist_info",
                        {
                            "playlist_id": playlist_id,
                            "max_videos": max_videos,
                            "include_video_details": include_video_details,
                        },
                    )
                elif e.resp.status == 404:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"Playlist not found: {playlist_id}"),
                        "get_playlist_info",
                        {
                            "playlist_id": playlist_id,
                            "max_videos": max_videos,
                            "include_video_details": include_video_details,
                        },
                    )
                else:
                    return YouTubeErrorHandler.handle_youtube_error(
                        Exception(f"YouTube API error: {str(e)}"),
                        "get_playlist_info",
                        {
                            "playlist_id": playlist_id,
                            "max_videos": max_videos,
                            "include_video_details": include_video_details,
                        },
                    )

        except Exception as e:
            logger.error(f"Error getting playlist info: {e}")
            return YouTubeErrorHandler.handle_youtube_error(
                e,
                "get_playlist_info",
                {
                    "playlist_id": playlist_id,
                    "max_videos": max_videos,
                    "include_video_details": include_video_details,
                },
            )
