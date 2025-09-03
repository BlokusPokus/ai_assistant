"""
Unit tests for YouTube Tool.

This module tests the YouTube tool functionality including
video info, transcripts, search, channel info, and playlist info.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from googleapiclient.errors import HttpError

from personal_assistant.tools.youtube.youtube_tool import YouTubeTool, YOUTUBE_TRANSCRIPT_AVAILABLE
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import ToolDataGenerator


class TestYouTubeTool:
    """Test cases for YouTube Tool."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.youtube_tool = YouTubeTool()
        self.test_video_id = "dQw4w9WgXcQ"
        self.test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.test_channel_id = "UCuAXFkgsw1L7xaCfnd5JJOw"
        self.test_playlist_id = "PLrAXtmRdnEQy6nuLMOVuYqj4q9jvGNbw"
        self.test_query = "python programming tutorial"

    def _assert_error_response(self, result, expected_message):
        """Helper to assert error responses that can be either dict or string."""
        if isinstance(result, dict):
            assert result.get("error", False)
            assert expected_message in result.get("error_message", "")
        else:
            assert "Error" in result or expected_message in result

    def test_youtube_tool_initialization(self):
        """Test YouTube tool initialization."""
        assert self.youtube_tool is not None
        assert hasattr(self.youtube_tool, 'get_video_info_tool')
        assert hasattr(self.youtube_tool, 'get_video_transcript_tool')
        assert hasattr(self.youtube_tool, 'search_videos_tool')
        assert hasattr(self.youtube_tool, 'get_channel_info_tool')
        assert hasattr(self.youtube_tool, 'get_playlist_info_tool')
        assert self.youtube_tool._quota_used == 0
        assert self.youtube_tool._last_request_time == 0

    def test_youtube_tool_iteration(self):
        """Test that YouTube tool is iterable and returns all tools."""
        tools = list(self.youtube_tool)
        assert len(tools) == 5
        
        tool_names = [tool.name for tool in tools]
        expected_names = [
            "get_video_info",
            "get_video_transcript",
            "search_videos",
            "get_channel_info",
            "get_playlist_info"
        ]
        
        for expected_name in expected_names:
            assert expected_name in tool_names

    def test_get_video_info_tool_properties(self):
        """Test get video info tool properties."""
        tool = self.youtube_tool.get_video_info_tool
        assert tool.name == "get_video_info"
        assert "detailed information about a YouTube video" in tool.description
        assert "video_id" in tool.parameters
        assert "include_transcript" in tool.parameters
        assert "include_statistics" in tool.parameters

    def test_get_video_transcript_tool_properties(self):
        """Test get video transcript tool properties."""
        tool = self.youtube_tool.get_video_transcript_tool
        assert tool.name == "get_video_transcript"
        assert "Extract and process YouTube video transcript" in tool.description
        assert "video_id" in tool.parameters
        assert "language" in tool.parameters
        assert "format" in tool.parameters

    def test_search_videos_tool_properties(self):
        """Test search videos tool properties."""
        tool = self.youtube_tool.search_videos_tool
        assert tool.name == "search_videos"
        assert "Search for YouTube videos by query" in tool.description
        assert "query" in tool.parameters
        assert "max_results" in tool.parameters
        assert "video_duration" in tool.parameters
        assert "upload_date" in tool.parameters

    def test_get_channel_info_tool_properties(self):
        """Test get channel info tool properties."""
        tool = self.youtube_tool.get_channel_info_tool
        assert tool.name == "get_channel_info"
        assert "information about a YouTube channel" in tool.description
        assert "channel_id" in tool.parameters
        assert "include_statistics" in tool.parameters
        assert "include_recent_videos" in tool.parameters

    def test_get_playlist_info_tool_properties(self):
        """Test get playlist info tool properties."""
        tool = self.youtube_tool.get_playlist_info_tool
        assert tool.name == "get_playlist_info"
        assert "information about a YouTube playlist" in tool.description
        assert "playlist_id" in tool.parameters
        assert "max_videos" in tool.parameters
        assert "include_video_details" in tool.parameters

    @pytest.mark.asyncio
    async def test_get_video_info_empty_video_id(self):
        """Test get video info with empty video ID."""
        result = await self.youtube_tool.get_video_info("")
        
        self._assert_error_response(result, "Video ID is required")

    @pytest.mark.asyncio
    async def test_get_video_info_invalid_video_id(self):
        """Test get video info with invalid video ID."""
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract:
            mock_extract.return_value = None
            
            result = await self.youtube_tool.get_video_info("invalid_id")
            
            self._assert_error_response(result, "Could not extract valid video ID")

    @pytest.mark.asyncio
    async def test_get_video_info_no_api_key(self):
        """Test get video info when YouTube API key is not configured."""
        with patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota:
            
            mock_settings.YOUTUBE_API_KEY = None
            mock_extract.return_value = self.test_video_id
            mock_quota.return_value = True
            
            result = await self.youtube_tool.get_video_info(self.test_video_id)
            
            self._assert_error_response(result, "YouTube Data API v3 is not available")

    @pytest.mark.asyncio
    async def test_get_video_info_quota_exceeded(self):
        """Test get video info when quota is exceeded."""
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota:
            
            mock_extract.return_value = self.test_video_id
            mock_quota.return_value = False
            
            result = await self.youtube_tool.get_video_info(self.test_video_id)
            
            self._assert_error_response(result, "YouTube API quota exceeded")

    @pytest.mark.asyncio
    async def test_get_video_info_success(self):
        """Test successful video info retrieval."""
        mock_video_data = {
            "items": [{
                "snippet": {
                    "title": "Test Video",
                    "channelTitle": "Test Channel",
                    "publishedAt": "2024-01-01T00:00:00Z",
                    "description": "Test description"
                },
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "50",
                    "commentCount": "10"
                },
                "contentDetails": {
                    "duration": "PT5M30S"
                }
            }]
        }
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_extract.return_value = self.test_video_id
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_youtube.videos.return_value.list.return_value.execute.return_value = mock_video_data
            
            result = await self.youtube_tool.get_video_info(
                self.test_video_id,
                include_transcript=False,
                include_statistics=True
            )
            
            assert "Test Video" in result
            assert "Test Channel" in result
            assert "1.0K" in result  # View count is formatted
            assert "50" in result
            assert "10" in result

    @pytest.mark.asyncio
    async def test_get_video_info_video_not_found(self):
        """Test get video info when video is not found."""
        mock_empty_response = {"items": []}
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_extract.return_value = self.test_video_id
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_youtube.videos.return_value.list.return_value.execute.return_value = mock_empty_response
            
            result = await self.youtube_tool.get_video_info(self.test_video_id)
            
            self._assert_error_response(result, "Video not found")

    @pytest.mark.asyncio
    async def test_get_video_info_http_error_403(self):
        """Test get video info with HTTP 403 error (quota exceeded)."""
        mock_error = HttpError(Mock(status=403), b"Quota exceeded")
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_extract.return_value = self.test_video_id
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_youtube.videos.return_value.list.return_value.execute.side_effect = mock_error
            
            result = await self.youtube_tool.get_video_info(self.test_video_id)
            
            self._assert_error_response(result, "quota exceeded")

    @pytest.mark.asyncio
    async def test_get_video_info_http_error_404(self):
        """Test get video info with HTTP 404 error (video not found)."""
        mock_error = HttpError(Mock(status=404), b"Not found")
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_extract.return_value = self.test_video_id
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_youtube.videos.return_value.list.return_value.execute.side_effect = mock_error
            
            result = await self.youtube_tool.get_video_info(self.test_video_id)
            
            self._assert_error_response(result, "Video not found")

    @pytest.mark.asyncio
    async def test_get_video_transcript_empty_video_id(self):
        """Test get video transcript with empty video ID."""
        result = await self.youtube_tool.get_video_transcript("")
        
        self._assert_error_response(result, "Video ID is required")

    @pytest.mark.asyncio
    async def test_get_video_transcript_invalid_video_id(self):
        """Test get video transcript with invalid video ID."""
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract:
            mock_extract.return_value = None
            
            result = await self.youtube_tool.get_video_transcript("invalid_id")
            
            self._assert_error_response(result, "Could not extract valid video ID")

    @pytest.mark.asyncio
    async def test_get_video_transcript_no_transcript_api(self):
        """Test get video transcript when transcript API is not available."""
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.YOUTUBE_TRANSCRIPT_AVAILABLE', False):
            
            mock_extract.return_value = self.test_video_id
            
            result = await self.youtube_tool.get_video_transcript(self.test_video_id)
            
            self._assert_error_response(result, "YouTube Transcript API is not available")

    @pytest.mark.asyncio
    async def test_get_video_transcript_success_text_format(self):
        """Test successful video transcript retrieval in text format."""
        mock_transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 2.0},
            {"text": "This is a test", "start": 2.0, "duration": 3.0}
        ]
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.YOUTUBE_TRANSCRIPT_AVAILABLE', True), \
             patch('personal_assistant.tools.youtube.youtube_tool.YouTubeTranscriptApi') as mock_api, \
             patch('personal_assistant.tools.youtube.youtube_tool.TextFormatter') as mock_formatter:
            
            mock_extract.return_value = self.test_video_id
            mock_api.return_value.fetch.return_value = mock_transcript
            mock_formatter.return_value.format_transcript.return_value = "Hello world This is a test"
            
            result = await self.youtube_tool.get_video_transcript(
                self.test_video_id,
                language="auto",
                format="text"
            )
            
            assert "Hello world This is a test" in result
            assert "Transcript" in result

    @pytest.mark.asyncio
    async def test_get_video_transcript_success_json_format(self):
        """Test successful video transcript retrieval in JSON format."""
        mock_transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 2.0}
        ]
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.YOUTUBE_TRANSCRIPT_AVAILABLE', True), \
             patch('personal_assistant.tools.youtube.youtube_tool.YouTubeTranscriptApi') as mock_api:
            
            mock_extract.return_value = self.test_video_id
            mock_api.return_value.fetch.return_value = mock_transcript
            
            result = await self.youtube_tool.get_video_transcript(
                self.test_video_id,
                language="en",
                format="json"
            )
            
            assert "JSON format" in result
            assert "Hello world" in result

    @pytest.mark.asyncio
    async def test_get_video_transcript_success_srt_format(self):
        """Test successful video transcript retrieval in SRT format."""
        mock_transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 2.0}
        ]
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.YOUTUBE_TRANSCRIPT_AVAILABLE', True), \
             patch('personal_assistant.tools.youtube.youtube_tool.YouTubeTranscriptApi') as mock_api, \
             patch('personal_assistant.tools.youtube.youtube_tool.SRTFormatter') as mock_formatter:
            
            mock_extract.return_value = self.test_video_id
            mock_api.return_value.fetch.return_value = mock_transcript
            mock_formatter.return_value.format_transcript.return_value = "1\n00:00:00,000 --> 00:00:02,000\nHello world"
            
            result = await self.youtube_tool.get_video_transcript(
                self.test_video_id,
                language="en",
                format="srt"
            )
            
            assert "SRT format" in result
            assert "Hello world" in result

    @pytest.mark.asyncio
    async def test_get_video_transcript_no_transcript_available(self):
        """Test get video transcript when no transcript is available."""
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.YOUTUBE_TRANSCRIPT_AVAILABLE', True), \
             patch('personal_assistant.tools.youtube.youtube_tool.YouTubeTranscriptApi') as mock_api:
            
            mock_extract.return_value = self.test_video_id
            mock_api.return_value.fetch.return_value = None
            
            result = await self.youtube_tool.get_video_transcript(self.test_video_id)
            
            assert "No transcript available" in result

    @pytest.mark.asyncio
    async def test_search_videos_empty_query(self):
        """Test search videos with empty query."""
        result = await self.youtube_tool.search_videos("")
        
        self._assert_error_response(result, "Search query is required")

    @pytest.mark.asyncio
    async def test_search_videos_invalid_max_results(self):
        """Test search videos with invalid max_results."""
        with patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch('personal_assistant.tools.youtube.youtube_tool.build_search_parameters') as mock_build, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_build.return_value = {"q": self.test_query, "maxResults": 10}
            mock_youtube.search.return_value.list.return_value.execute.return_value = {"items": []}
            
            result = await self.youtube_tool.search_videos(
                self.test_query,
                max_results=100  # Invalid, should be capped at 50
            )
            
            # Should still work but with capped results
            assert "No videos found" in result

    @pytest.mark.asyncio
    async def test_search_videos_no_api_key(self):
        """Test search videos when YouTube API key is not configured."""
        with patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings:
            
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = None
            
            result = await self.youtube_tool.search_videos(self.test_query)
            
            self._assert_error_response(result, "YouTube Data API v3 is not available")

    @pytest.mark.asyncio
    async def test_search_videos_success(self):
        """Test successful video search."""
        mock_search_results = {
            "items": [
                {
                    "id": {"videoId": "test_video_1"},
                    "snippet": {
                        "title": "Test Video 1",
                        "channelTitle": "Test Channel 1",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "description": "Test description 1"
                    }
                },
                {
                    "id": {"videoId": "test_video_2"},
                    "snippet": {
                        "title": "Test Video 2",
                        "channelTitle": "Test Channel 2",
                        "publishedAt": "2024-01-02T00:00:00Z",
                        "description": "Test description 2"
                    }
                }
            ]
        }
        
        with patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch('personal_assistant.tools.youtube.youtube_tool.build_search_parameters') as mock_build, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_build.return_value = {"q": self.test_query, "maxResults": 10}
            mock_youtube.search.return_value.list.return_value.execute.return_value = mock_search_results
            
            result = await self.youtube_tool.search_videos(
                self.test_query,
                max_results=10,
                video_duration="short",
                upload_date="this_week"
            )
            
            assert "Test Video 1" in result
            assert "Test Video 2" in result
            assert "Test Channel 1" in result
            assert "Test Channel 2" in result
            assert "short" in result
            assert "this_week" in result

    @pytest.mark.asyncio
    async def test_search_videos_no_results(self):
        """Test search videos with no results."""
        mock_empty_results = {"items": []}
        
        with patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch('personal_assistant.tools.youtube.youtube_tool.build_search_parameters') as mock_build, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_build.return_value = {"q": self.test_query, "maxResults": 10}
            mock_youtube.search.return_value.list.return_value.execute.return_value = mock_empty_results
            
            result = await self.youtube_tool.search_videos(self.test_query)
            
            assert "No videos found" in result

    @pytest.mark.asyncio
    async def test_get_channel_info_empty_channel_id(self):
        """Test get channel info with empty channel ID."""
        result = await self.youtube_tool.get_channel_info("")
        
        self._assert_error_response(result, "Channel ID is required")

    @pytest.mark.asyncio
    async def test_get_channel_info_invalid_channel_id(self):
        """Test get channel info with invalid channel ID."""
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_channel_id') as mock_extract:
            mock_extract.return_value = None
            
            result = await self.youtube_tool.get_channel_info("invalid_id")
            
            self._assert_error_response(result, "Could not extract valid channel ID")

    @pytest.mark.asyncio
    async def test_get_channel_info_success(self):
        """Test successful channel info retrieval."""
        mock_channel_data = {
            "items": [{
                "snippet": {
                    "title": "Test Channel",
                    "description": "Test channel description",
                    "publishedAt": "2020-01-01T00:00:00Z",
                    "country": "US"
                },
                "statistics": {
                    "subscriberCount": "10000",
                    "viewCount": "1000000",
                    "videoCount": "100"
                }
            }]
        }
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_channel_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_extract.return_value = self.test_channel_id
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_youtube.channels.return_value.list.return_value.execute.return_value = mock_channel_data
            
            result = await self.youtube_tool.get_channel_info(
                self.test_channel_id,
                include_statistics=True,
                include_recent_videos=False
            )
            
            assert "Test Channel" in result
            assert "10.0K" in result  # Subscriber count is formatted
            assert "1.0M" in result  # View count is formatted
            assert "100" in result

    @pytest.mark.asyncio
    async def test_get_playlist_info_empty_playlist_id(self):
        """Test get playlist info with empty playlist ID."""
        result = await self.youtube_tool.get_playlist_info("")
        
        self._assert_error_response(result, "Playlist ID is required")

    @pytest.mark.asyncio
    async def test_get_playlist_info_invalid_playlist_id(self):
        """Test get playlist info with invalid playlist ID."""
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_playlist_id') as mock_extract:
            mock_extract.return_value = None
            
            result = await self.youtube_tool.get_playlist_info("invalid_id")
            
            self._assert_error_response(result, "Could not extract valid playlist ID")

    @pytest.mark.asyncio
    async def test_get_playlist_info_success(self):
        """Test successful playlist info retrieval."""
        mock_playlist_data = {
            "items": [{
                "snippet": {
                    "title": "Test Playlist",
                    "description": "Test playlist description",
                    "channelTitle": "Test Channel",
                    "publishedAt": "2024-01-01T00:00:00Z"
                },
                "contentDetails": {
                    "itemCount": "25"
                }
            }]
        }
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_playlist_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_extract.return_value = self.test_playlist_id
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_youtube.playlists.return_value.list.return_value.execute.return_value = mock_playlist_data
            
            result = await self.youtube_tool.get_playlist_info(
                self.test_playlist_id,
                max_videos=10,
                include_video_details=False
            )
            
            assert "Test Playlist" in result
            assert "Test Channel" in result
            assert "25" in result

    def test_tool_parameter_validation(self):
        """Test that tool parameters are properly defined."""
        # Test get_video_info_tool parameters
        video_info_params = self.youtube_tool.get_video_info_tool.parameters
        assert video_info_params["video_id"]["type"] == "string"
        assert video_info_params["include_transcript"]["type"] == "boolean"
        assert video_info_params["include_statistics"]["type"] == "boolean"
        
        # Test get_video_transcript_tool parameters
        transcript_params = self.youtube_tool.get_video_transcript_tool.parameters
        assert transcript_params["video_id"]["type"] == "string"
        assert transcript_params["language"]["type"] == "string"
        assert transcript_params["format"]["type"] == "string"
        
        # Test search_videos_tool parameters
        search_params = self.youtube_tool.search_videos_tool.parameters
        assert search_params["query"]["type"] == "string"
        assert search_params["max_results"]["type"] == "integer"
        assert search_params["video_duration"]["type"] == "string"
        assert search_params["upload_date"]["type"] == "string"

    def test_tool_descriptions(self):
        """Test that tool descriptions are informative."""
        # Test that descriptions contain key information
        assert "YouTube video" in self.youtube_tool.get_video_info_tool.description
        assert "transcript" in self.youtube_tool.get_video_transcript_tool.description
        assert "Search for YouTube videos" in self.youtube_tool.search_videos_tool.description
        assert "YouTube channel" in self.youtube_tool.get_channel_info_tool.description
        assert "YouTube playlist" in self.youtube_tool.get_playlist_info_tool.description

    def test_tool_categories(self):
        """Test that tools can have categories set."""
        tool = self.youtube_tool.get_video_info_tool
        tool.set_category("YouTube")
        assert tool.category == "YouTube"
        
        # Test that category is returned correctly
        assert tool.category == "YouTube"

    def test_tool_user_intent_tracking(self):
        """Test that tools can track user intent."""
        tool = self.youtube_tool.get_video_info_tool
        
        # Test setting user intent
        tool.set_user_intent("Get video information")
        assert tool.get_user_intent() == "Get video information"
        
        # Test default user intent
        new_tool = YouTubeTool().get_video_info_tool
        assert new_tool.get_user_intent() == "Unknown user intent"

    @pytest.mark.asyncio
    async def test_get_video_info_with_transcript(self):
        """Test get video info with transcript included."""
        mock_video_data = {
            "items": [{
                "snippet": {
                    "title": "Test Video",
                    "channelTitle": "Test Channel",
                    "publishedAt": "2024-01-01T00:00:00Z",
                    "description": "Test description"
                },
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "50",
                    "commentCount": "10"
                },
                "contentDetails": {
                    "duration": "PT5M30S"
                }
            }]
        }
        
        mock_transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 2.0},
            {"text": "This is a test", "start": 2.0, "duration": 3.0}
        ]
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch('personal_assistant.tools.youtube.youtube_tool.YOUTUBE_TRANSCRIPT_AVAILABLE', True), \
             patch('personal_assistant.tools.youtube.youtube_tool.YouTubeTranscriptApi') as mock_api, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_extract.return_value = self.test_video_id
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_youtube.videos.return_value.list.return_value.execute.return_value = mock_video_data
            mock_api.get_transcript.return_value = mock_transcript
            
            result = await self.youtube_tool.get_video_info(
                self.test_video_id,
                include_transcript=True,
                include_statistics=True
            )
            
            assert "Test Video" in result
            assert "Hello world" in result
            assert "This is a test" in result
            assert "Transcript Preview" in result

    @pytest.mark.asyncio
    async def test_get_video_transcript_fallback_method(self):
        """Test get video transcript with fallback to older API method."""
        mock_transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 2.0}
        ]
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.YOUTUBE_TRANSCRIPT_AVAILABLE', True), \
             patch('personal_assistant.tools.youtube.youtube_tool.YouTubeTranscriptApi') as mock_api, \
             patch('personal_assistant.tools.youtube.youtube_tool.TextFormatter') as mock_formatter:
            
            mock_extract.return_value = self.test_video_id
            # First call (new method) fails, second call (old method) succeeds
            mock_api.return_value.fetch.side_effect = Exception("New method failed")
            mock_api.get_transcript.return_value = mock_transcript
            mock_formatter.return_value.format_transcript.return_value = "Hello world"
            
            result = await self.youtube_tool.get_video_transcript(
                self.test_video_id,
                language="auto",
                format="text"
            )
            
            assert "Hello world" in result
            assert "Transcript" in result

    @pytest.mark.asyncio
    async def test_get_video_transcript_long_text_truncation(self):
        """Test get video transcript with long text that gets truncated."""
        long_text = "A" * 3000  # Longer than 2000 character limit
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_video_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.YOUTUBE_TRANSCRIPT_AVAILABLE', True), \
             patch('personal_assistant.tools.youtube.youtube_tool.YouTubeTranscriptApi') as mock_api, \
             patch('personal_assistant.tools.youtube.youtube_tool.TextFormatter') as mock_formatter:
            
            mock_extract.return_value = self.test_video_id
            mock_api.return_value.fetch.return_value = [{"text": "test", "start": 0, "duration": 1}]
            mock_formatter.return_value.format_transcript.return_value = long_text
            
            result = await self.youtube_tool.get_video_transcript(
                self.test_video_id,
                language="auto",
                format="text"
            )
            
            assert "Transcript truncated" in result
            assert len(result) < len(long_text) + 100  # Should be truncated

    @pytest.mark.asyncio
    async def test_get_channel_info_with_recent_videos(self):
        """Test get channel info with recent videos included."""
        mock_channel_data = {
            "items": [{
                "snippet": {
                    "title": "Test Channel",
                    "description": "Test channel description",
                    "publishedAt": "2020-01-01T00:00:00Z",
                    "country": "US"
                },
                "statistics": {
                    "subscriberCount": "10000",
                    "viewCount": "1000000",
                    "videoCount": "100"
                }
            }]
        }
        
        mock_recent_videos = {
            "items": [
                {
                    "id": {"videoId": "recent_video_1"},
                    "snippet": {
                        "title": "Recent Video 1",
                        "publishedAt": "2024-01-01T00:00:00Z"
                    }
                }
            ]
        }
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_channel_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_extract.return_value = self.test_channel_id
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_youtube.channels.return_value.list.return_value.execute.return_value = mock_channel_data
            mock_youtube.search.return_value.list.return_value.execute.return_value = mock_recent_videos
            
            result = await self.youtube_tool.get_channel_info(
                self.test_channel_id,
                include_statistics=True,
                include_recent_videos=True
            )
            
            assert "Test Channel" in result
            assert "Recent Video 1" in result
            assert "Recent Videos" in result

    @pytest.mark.asyncio
    async def test_get_playlist_info_with_video_details(self):
        """Test get playlist info with video details included."""
        mock_playlist_data = {
            "items": [{
                "snippet": {
                    "title": "Test Playlist",
                    "description": "Test playlist description",
                    "channelTitle": "Test Channel",
                    "publishedAt": "2024-01-01T00:00:00Z"
                },
                "contentDetails": {
                    "itemCount": "25"
                }
            }]
        }
        
        mock_playlist_items = {
            "items": [
                {
                    "snippet": {
                        "title": "Playlist Video 1",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "resourceId": {"videoId": "playlist_video_1"}
                    }
                }
            ]
        }
        
        with patch('personal_assistant.tools.youtube.youtube_tool.extract_playlist_id') as mock_extract, \
             patch('personal_assistant.tools.youtube.youtube_tool.check_quota_limit') as mock_quota, \
             patch('personal_assistant.tools.youtube.youtube_tool.settings') as mock_settings, \
             patch.object(self.youtube_tool, '_youtube') as mock_youtube:
            
            mock_extract.return_value = self.test_playlist_id
            mock_quota.return_value = True
            mock_settings.YOUTUBE_API_KEY = "test_key"
            mock_youtube.playlists.return_value.list.return_value.execute.return_value = mock_playlist_data
            mock_youtube.playlistItems.return_value.list.return_value.execute.return_value = mock_playlist_items
            
            result = await self.youtube_tool.get_playlist_info(
                self.test_playlist_id,
                max_videos=10,
                include_video_details=True
            )
            
            assert "Test Playlist" in result
            assert "Playlist Video 1" in result
            assert "Videos in Playlist" in result
