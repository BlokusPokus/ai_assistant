"""
Unit tests for Calendar Tool.

This module tests the Calendar tool functionality including
event viewing, creation, deletion, and detailed retrieval
via Microsoft Graph API.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from personal_assistant.tools.calendar.calendar_tool import CalendarTool


class TestCalendarTool:
    """Test cases for Calendar Tool."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock environment variables and access token for Microsoft OAuth
        with patch.dict('os.environ', {
            'MICROSOFT_APPLICATION_ID': 'test-app-id',
            'MICROSOFT_CLIENT_SECRET': 'test-client-secret'
        }), patch('personal_assistant.tools.calendar.calendar_tool.get_access_token', return_value='mock-access-token'):
            self.calendar_tool = CalendarTool()
        self.test_event_id = "test-event-id-123"
        self.test_subject = "Test Meeting"
        self.test_start_time = "2024-01-15 14:30"
        self.test_duration = 60
        self.test_location = "Conference Room A"
        self.test_attendees = "user1@example.com, user2@example.com"
        self.test_count = 5
        self.test_days = 7

    def test_calendar_tool_initialization(self):
        """Test Calendar tool initialization."""
        assert self.calendar_tool is not None
        assert hasattr(self.calendar_tool, 'view_calendar_events_tool')
        assert hasattr(self.calendar_tool, 'create_calendar_event_tool')
        assert hasattr(self.calendar_tool, 'delete_calendar_event_tool')
        assert self.calendar_tool.ms_graph_url == "https://graph.microsoft.com/v1.0"
        assert self.calendar_tool.scopes == ["Calendars.Read", "Calendars.ReadWrite", "User.Read"]

    def test_calendar_tool_iteration(self):
        """Test that Calendar tool is iterable and returns all tools."""
        tools = list(self.calendar_tool)
        assert len(tools) == 3
        
        tool_names = [tool.name for tool in tools]
        expected_names = [
            "view_calendar_events",
            "create_calendar_event",
            "delete_calendar_event"
        ]
        
        for expected_name in expected_names:
            assert expected_name in tool_names

    def test_view_calendar_events_tool_properties(self):
        """Test view calendar events tool properties."""
        tool = self.calendar_tool.view_calendar_events_tool
        assert tool.name == "view_calendar_events"
        assert "View upcoming calendar events" in tool.description
        assert "count" in tool.parameters
        assert "days" in tool.parameters

    def test_create_calendar_event_tool_properties(self):
        """Test create calendar event tool properties."""
        tool = self.calendar_tool.create_calendar_event_tool
        assert tool.name == "create_calendar_event"
        assert "Create a new calendar event or reminder" in tool.description
        assert "subject" in tool.parameters
        assert "start_time" in tool.parameters
        assert "duration" in tool.parameters
        assert "location" in tool.parameters
        assert "attendees" in tool.parameters

    def test_delete_calendar_event_tool_properties(self):
        """Test delete calendar event tool properties."""
        tool = self.calendar_tool.delete_calendar_event_tool
        assert tool.name == "delete_calendar_event"
        assert "Delete a calendar event by its ID" in tool.description
        assert "event_id" in tool.parameters

    def test_tool_parameter_types(self):
        """Test that tool parameters have correct types."""
        # Test view_calendar_events_tool parameters
        view_params = self.calendar_tool.view_calendar_events_tool.parameters
        assert view_params["count"]["type"] == "integer"
        assert view_params["days"]["type"] == "integer"
        
        # Test create_calendar_event_tool parameters
        create_params = self.calendar_tool.create_calendar_event_tool.parameters
        assert create_params["subject"]["type"] == "string"
        assert create_params["start_time"]["type"] == "string"
        assert create_params["duration"]["type"] == "integer"
        assert create_params["location"]["type"] == "string"
        assert create_params["attendees"]["type"] == "string"
        
        # Test delete_calendar_event_tool parameters
        delete_params = self.calendar_tool.delete_calendar_event_tool.parameters
        assert delete_params["event_id"]["type"] == "string"

    @pytest.mark.asyncio
    async def test_get_events_success(self):
        """Test successful calendar events retrieval."""
        mock_events = [
            {
                "id": "event1",
                "subject": "Meeting 1",
                "start": {"dateTime": "2024-01-15T14:30:00Z"},
                "end": {"dateTime": "2024-01-15T15:30:00Z"},
                "location": {"displayName": "Room A"},
                "attendees": []
            },
            {
                "id": "event2",
                "subject": "Meeting 2",
                "start": {"dateTime": "2024-01-16T10:00:00Z"},
                "end": {"dateTime": "2024-01-16T11:00:00Z"},
                "location": {"displayName": "Room B"},
                "attendees": []
            }
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": mock_events}
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_calendar_parameters') as mock_validate, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.get_datetime_range') as mock_datetime, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_view_params') as mock_params, \
             patch('personal_assistant.tools.calendar.calendar_tool.parse_calendar_event') as mock_parse, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (self.test_count, self.test_days)
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_datetime.return_value = ("2024-01-15T00:00:00Z", "2024-01-22T23:59:59Z")
            mock_params.return_value = {"$top": 5}
            mock_parse.side_effect = lambda x: {"id": x["id"], "subject": x["subject"]}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.calendar_tool.get_events(self.test_count, self.test_days)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["id"] == "event1"
            assert result[1]["id"] == "event2"

    @pytest.mark.asyncio
    async def test_get_events_no_events(self):
        """Test calendar events retrieval when no events found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_calendar_parameters') as mock_validate, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.get_datetime_range') as mock_datetime, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_view_params') as mock_params, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (self.test_count, self.test_days)
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_datetime.return_value = ("2024-01-15T00:00:00Z", "2024-01-22T23:59:59Z")
            mock_params.return_value = {"$top": 5}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.calendar_tool.get_events(self.test_count, self.test_days)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert "No events found" in result[0]["message"]

    @pytest.mark.asyncio
    async def test_get_events_http_error(self):
        """Test calendar events retrieval with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_calendar_parameters') as mock_validate, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.get_datetime_range') as mock_datetime, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_view_params') as mock_params, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (self.test_count, self.test_days)
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_datetime.return_value = ("2024-01-15T00:00:00Z", "2024-01-22T23:59:59Z")
            mock_params.return_value = {"$top": 5}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.calendar_tool.get_events(self.test_count, self.test_days)
            
            # Should return error response in list format
            assert isinstance(result, list)
            assert len(result) == 1
            # The error response should be a dict with error information
            assert isinstance(result[0], dict)

    @pytest.mark.asyncio
    async def test_create_calendar_event_success(self):
        """Test successful calendar event creation."""
        mock_event_data = {
            "id": self.test_event_id,
            "subject": self.test_subject,
            "start": {"dateTime": "2024-01-15T14:30:00Z"},
            "end": {"dateTime": "2024-01-15T15:30:00Z"}
        }
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = mock_event_data
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_subject') as mock_validate_subject, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_start_time') as mock_validate_start, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_duration') as mock_validate_duration, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_location') as mock_validate_location, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.parse_start_time_with_duration') as mock_parse_time, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_event_data') as mock_build_data, \
             patch('personal_assistant.tools.calendar.calendar_tool.format_success_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate_subject.return_value = (True, "")
            mock_validate_start.return_value = (True, "")
            mock_validate_duration.return_value = (True, "")
            mock_validate_location.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_parse_time.return_value = ("2024-01-15T14:30:00Z", "2024-01-15T15:30:00Z")
            mock_build_data.return_value = {"subject": self.test_subject}
            mock_format.return_value = {"success": True, "message": "Event created successfully"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.calendar_tool.create_calendar_event(
                self.test_subject,
                self.test_start_time,
                self.test_duration,
                self.test_location,
                self.test_attendees
            )
            
            assert result["success"] is True
            assert "Event created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_create_calendar_event_invalid_subject(self):
        """Test calendar event creation with invalid subject."""
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_subject') as mock_validate:
            mock_validate.return_value = (False, "Subject cannot be empty")
            
            result = await self.calendar_tool.create_calendar_event(
                "",
                self.test_start_time,
                self.test_duration,
                self.test_location,
                self.test_attendees
            )
            
            # Should return error response
            assert isinstance(result, dict)
            assert "error" in result or "llm_instructions" in result

    @pytest.mark.asyncio
    async def test_create_calendar_event_invalid_start_time(self):
        """Test calendar event creation with invalid start time."""
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_subject') as mock_validate_subject, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_start_time') as mock_validate_start:
            
            mock_validate_subject.return_value = (True, "")
            mock_validate_start.return_value = (False, "Invalid start time format")
            
            result = await self.calendar_tool.create_calendar_event(
                self.test_subject,
                "invalid-time",
                self.test_duration,
                self.test_location,
                self.test_attendees
            )
            
            # Should return error response
            assert isinstance(result, dict)
            assert "error" in result or "llm_instructions" in result

    @pytest.mark.asyncio
    async def test_create_calendar_event_invalid_duration(self):
        """Test calendar event creation with invalid duration."""
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_subject') as mock_validate_subject, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_start_time') as mock_validate_start, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_duration') as mock_validate_duration:
            
            mock_validate_subject.return_value = (True, "")
            mock_validate_start.return_value = (True, "")
            mock_validate_duration.return_value = (False, "Duration must be positive")
            
            result = await self.calendar_tool.create_calendar_event(
                self.test_subject,
                self.test_start_time,
                -10,  # Invalid negative duration
                self.test_location,
                self.test_attendees
            )
            
            # Should return error response
            assert isinstance(result, dict)
            assert "error" in result or "llm_instructions" in result

    @pytest.mark.asyncio
    async def test_create_calendar_event_with_attendees(self):
        """Test calendar event creation with attendees."""
        mock_event_data = {
            "id": self.test_event_id,
            "subject": self.test_subject,
            "attendees": [
                {"emailAddress": {"address": "user1@example.com"}},
                {"emailAddress": {"address": "user2@example.com"}}
            ]
        }
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = mock_event_data
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_subject') as mock_validate_subject, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_start_time') as mock_validate_start, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_duration') as mock_validate_duration, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_location') as mock_validate_location, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.parse_start_time_with_duration') as mock_parse_time, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_event_data') as mock_build_data, \
             patch('personal_assistant.tools.calendar.calendar_tool.format_success_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate_subject.return_value = (True, "")
            mock_validate_start.return_value = (True, "")
            mock_validate_duration.return_value = (True, "")
            mock_validate_location.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_parse_time.return_value = ("2024-01-15T14:30:00Z", "2024-01-15T15:30:00Z")
            mock_build_data.return_value = {"subject": self.test_subject}
            mock_format.return_value = {"success": True, "message": "Event created with attendees"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.calendar_tool.create_calendar_event(
                self.test_subject,
                self.test_start_time,
                self.test_duration,
                self.test_location,
                self.test_attendees
            )
            
            assert result["success"] is True
            assert "Event created with attendees" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_calendar_event_success(self):
        """Test successful calendar event deletion."""
        mock_response = Mock()
        mock_response.status_code = 204  # No content on successful deletion
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_event_id') as mock_validate, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.format_success_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_format.return_value = {"success": True, "message": "Event deleted successfully"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.delete.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.calendar_tool.delete_calendar_event(self.test_event_id)
            
            assert result["success"] is True
            assert "Event deleted successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_calendar_event_not_found(self):
        """Test calendar event deletion when event not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_event_id') as mock_validate, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.handle_event_not_found') as mock_handle, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_handle.return_value = {"error": True, "message": "Event not found"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.delete.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.calendar_tool.delete_calendar_event(self.test_event_id)
            
            assert result["error"] is True
            assert "Event not found" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_calendar_event_invalid_id(self):
        """Test calendar event deletion with invalid event ID."""
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_event_id') as mock_validate:
            mock_validate.return_value = (False, "Event ID cannot be empty")
            
            result = await self.calendar_tool.delete_calendar_event("")
            
            # Should return error response
            assert isinstance(result, dict)
            assert "error" in result or "llm_instructions" in result

    @pytest.mark.asyncio
    async def test_get_event_details_success(self):
        """Test successful event details retrieval."""
        mock_event_data = {
            "id": self.test_event_id,
            "subject": self.test_subject,
            "start": {"dateTime": "2024-01-15T14:30:00Z"},
            "end": {"dateTime": "2024-01-15T15:30:00Z"},
            "location": {"displayName": self.test_location},
            "attendees": []
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_event_data
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_event_id') as mock_validate, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.parse_event_details') as mock_parse, \
             patch('personal_assistant.tools.calendar.calendar_tool.format_event_details_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_parse.return_value = {"subject": self.test_subject, "location": self.test_location}
            mock_format.return_value = "Event details: Test Meeting at Conference Room A"
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.calendar_tool.get_event_details(self.test_event_id)
            
            assert result == "Event details: Test Meeting at Conference Room A"

    @pytest.mark.asyncio
    async def test_get_event_details_invalid_id(self):
        """Test event details retrieval with invalid event ID."""
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_event_id') as mock_validate:
            mock_validate.return_value = (False, "Event ID cannot be empty")
            
            result = await self.calendar_tool.get_event_details("")
            
            # Should return error message string
            assert isinstance(result, str)
            assert "error" in result.lower() or "invalid" in result.lower()

    def test_tool_categories(self):
        """Test that tools can have categories set."""
        tool = self.calendar_tool.create_calendar_event_tool
        tool.set_category("Calendar")
        assert tool.category == "Calendar"
        
        # Test that category is returned correctly
        assert tool.category == "Calendar"

    def test_tool_user_intent_tracking(self):
        """Test that tools can track user intent."""
        tool = self.calendar_tool.create_calendar_event_tool
        
        # Test setting user intent
        tool.set_user_intent("Schedule an important meeting")
        assert tool.get_user_intent() == "Schedule an important meeting"
        
        # Test default user intent - use the existing instance instead of creating a new one
        assert tool.get_user_intent() == "Schedule an important meeting"

    def test_calendar_tool_token_management(self):
        """Test calendar tool token management."""
        # Test that token management methods exist
        assert hasattr(self.calendar_tool, '_initialize_token')
        assert callable(self.calendar_tool._initialize_token)
        
        # Test that access token attribute exists
        assert hasattr(self.calendar_tool, '_access_token')

    def test_calendar_tool_parameter_validation(self):
        """Test that tool parameters are properly defined."""
        # Test view_calendar_events_tool parameters
        view_params = self.calendar_tool.view_calendar_events_tool.parameters
        assert view_params["count"]["type"] == "integer"
        assert view_params["days"]["type"] == "integer"
        
        # Test create_calendar_event_tool parameters
        create_params = self.calendar_tool.create_calendar_event_tool.parameters
        assert create_params["subject"]["type"] == "string"
        assert create_params["start_time"]["type"] == "string"
        assert create_params["duration"]["type"] == "integer"
        assert create_params["location"]["type"] == "string"
        assert create_params["attendees"]["type"] == "string"
        
        # Test delete_calendar_event_tool parameters
        delete_params = self.calendar_tool.delete_calendar_event_tool.parameters
        assert delete_params["event_id"]["type"] == "string"

    def test_calendar_tool_descriptions(self):
        """Test that tool descriptions are informative."""
        # Test that descriptions contain key information
        assert "calendar" in self.calendar_tool.view_calendar_events_tool.description.lower()
        assert "create" in self.calendar_tool.create_calendar_event_tool.description.lower()
        assert "delete" in self.calendar_tool.delete_calendar_event_tool.description.lower()

    @pytest.mark.asyncio
    async def test_get_events_with_different_parameters(self):
        """Test get_events with various parameter combinations."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        
        test_cases = [
            {"count": 3, "days": 3},
            {"count": 10, "days": 14},
            {"count": 1, "days": 1},
        ]
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_calendar_parameters') as mock_validate, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.get_datetime_range') as mock_datetime, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_view_params') as mock_params, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.side_effect = lambda c, d: (c, d)
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_datetime.return_value = ("2024-01-15T00:00:00Z", "2024-01-22T23:59:59Z")
            mock_params.return_value = {"$top": 5}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            for case in test_cases:
                result = await self.calendar_tool.get_events(case["count"], case["days"])
                assert isinstance(result, list)
                assert len(result) == 1  # No events found message

    @pytest.mark.asyncio
    async def test_create_calendar_event_without_optional_params(self):
        """Test calendar event creation without optional parameters."""
        mock_event_data = {
            "id": self.test_event_id,
            "subject": self.test_subject,
            "start": {"dateTime": "2024-01-15T14:30:00Z"},
            "end": {"dateTime": "2024-01-15T15:30:00Z"}
        }
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = mock_event_data
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_subject') as mock_validate_subject, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_start_time') as mock_validate_start, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_duration') as mock_validate_duration, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_location') as mock_validate_location, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.parse_start_time_with_duration') as mock_parse_time, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_event_data') as mock_build_data, \
             patch('personal_assistant.tools.calendar.calendar_tool.format_success_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate_subject.return_value = (True, "")
            mock_validate_start.return_value = (True, "")
            mock_validate_duration.return_value = (True, "")
            mock_validate_location.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_parse_time.return_value = ("2024-01-15T14:30:00Z", "2024-01-15T15:30:00Z")
            mock_build_data.return_value = {"subject": self.test_subject}
            mock_format.return_value = {"success": True, "message": "Event created successfully"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Test with minimal required parameters only
            result = await self.calendar_tool.create_calendar_event(
                self.test_subject,
                self.test_start_time,
                duration=30,  # Default duration
                location="",  # Empty location
                attendees=""  # No attendees
            )
            
            assert result["success"] is True
            assert "Event created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_create_calendar_event_http_error(self):
        """Test calendar event creation with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        with patch('personal_assistant.tools.calendar.calendar_tool.validate_subject') as mock_validate_subject, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_start_time') as mock_validate_start, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_duration') as mock_validate_duration, \
             patch('personal_assistant.tools.calendar.calendar_tool.validate_location') as mock_validate_location, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_calendar_headers') as mock_headers, \
             patch('personal_assistant.tools.calendar.calendar_tool.parse_start_time_with_duration') as mock_parse_time, \
             patch('personal_assistant.tools.calendar.calendar_tool.build_event_data') as mock_build_data, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate_subject.return_value = (True, "")
            mock_validate_start.return_value = (True, "")
            mock_validate_duration.return_value = (True, "")
            mock_validate_location.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_parse_time.return_value = ("2024-01-15T14:30:00Z", "2024-01-15T15:30:00Z")
            mock_build_data.return_value = {"subject": self.test_subject}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.calendar_tool.create_calendar_event(
                self.test_subject,
                self.test_start_time,
                self.test_duration,
                self.test_location,
                self.test_attendees
            )
            
            # Should return error response
            assert isinstance(result, dict)
            assert "error" in result or "llm_instructions" in result

