import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.tools.event_creation.event_creation_tool import EventCreationTool
from personal_assistant.tools.event_creation.event_details import EventDetails, ValidationStatus
from personal_assistant.llm.llm_client import LLMClient


class TestEventCreationTool:
    """Test the EventCreationTool class."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        client = MagicMock(spec=LLMClient)
        client.complete = AsyncMock()
        return client

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock(spec=AsyncSession)
        session.add = AsyncMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session

    @pytest.fixture
    def event_creation_tool(self, mock_llm_client, mock_db_session):
        """Create an EventCreationTool instance."""
        return EventCreationTool(mock_llm_client, mock_db_session)

    def test_event_details_creation(self):
        """Test EventDetails creation and serialization."""
        start_time = datetime.now() + timedelta(hours=1)

        event_details = EventDetails(
            title="Test Meeting",
            start_time=start_time,
            duration=60,
            location="Conference Room",
            description="Test meeting description"
        )

        # Test to_dict
        event_dict = event_details.to_dict()
        assert event_dict['title'] == "Test Meeting"
        assert event_dict['duration'] == 60
        assert event_dict['location'] == "Conference Room"

        # Test from_dict
        recreated_event = EventDetails.from_dict(event_dict)
        assert recreated_event.title == "Test Meeting"
        assert recreated_event.duration == 60
        assert recreated_event.location == "Conference Room"

    def test_recurrence_pattern_validation(self):
        """Test RecurrencePattern validation."""
        from personal_assistant.tools.event_creation.event_details import RecurrencePattern

        # Valid pattern
        valid_pattern = RecurrencePattern(
            frequency="weekly",
            interval=1,
            weekdays=[1, 3, 5]  # Monday, Wednesday, Friday
        )
        assert valid_pattern.is_valid()

        # Invalid pattern - missing weekdays for weekly
        invalid_pattern = RecurrencePattern(
            frequency="weekly",
            interval=1
        )
        assert not invalid_pattern.is_valid()

        # Invalid pattern - invalid frequency
        invalid_pattern2 = RecurrencePattern(
            frequency="invalid",
            interval=1
        )
        assert not invalid_pattern2.is_valid()

    def test_validation_result(self):
        """Test ValidationResult functionality."""
        from personal_assistant.tools.event_creation.event_details import ValidationResult

        # Valid result
        valid_result = ValidationResult(
            status=ValidationStatus.VALID,
            errors=[],
            warnings=[],
            suggestions=[]
        )
        assert valid_result.is_valid
        assert not valid_result.has_errors
        assert not valid_result.has_warnings

        # Invalid result
        invalid_result = ValidationResult(
            status=ValidationStatus.INVALID,
            errors=["Title is required"],
            warnings=[],
            suggestions=[]
        )
        assert not invalid_result.is_valid
        assert invalid_result.has_errors
        assert not invalid_result.has_warnings

        # Partial result
        partial_result = ValidationResult(
            status=ValidationStatus.PARTIAL,
            errors=[],
            warnings=["Event is in the past"],
            suggestions=[]
        )
        assert not partial_result.is_valid
        assert not partial_result.has_errors
        assert partial_result.has_warnings

    @pytest.mark.asyncio
    async def test_format_response_details(self, event_creation_tool):
        """Test response formatting."""
        start_time = datetime.now() + timedelta(hours=1)

        event_details = EventDetails(
            title="Test Meeting",
            start_time=start_time,
            duration=60,
            location="Conference Room",
            description="Test meeting description"
        )

        # Test basic formatting
        response = event_creation_tool._format_response_details(
            event_details, 1)
        assert "📅 Test Meeting" in response
        assert "⏰" in response

        # Test with recurrence
        event_details.recurrence_pattern = {
            'frequency': 'weekly',
            'interval': 1,
            'weekdays': [1]
        }

        response = event_creation_tool._format_response_details(
            event_details, 5)
        assert "🔄 Recurring weekly" in response
        assert "📊 Created 5 instances" in response

    @pytest.mark.asyncio
    async def test_generate_recurring_instances(self, event_creation_tool):
        """Test recurring instance generation."""
        from personal_assistant.database.models.events import Event
        from personal_assistant.database.models.recurrence_patterns import RecurrencePattern as DBRecurrencePattern

        # Create a base event
        base_event = Event(
            user_id=1,
            title="Weekly Meeting",
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=1),
            source='test'
        )

        # Create a weekly pattern
        pattern = DBRecurrencePattern(
            frequency="weekly",
            interval=1,
            weekdays=[1]  # Monday
        )

        # Generate instances
        instances = event_creation_tool._generate_recurring_instances(
            base_event, pattern)

        # Should generate instances (limited by max_instances)
        assert len(instances) > 0
        assert len(instances) <= 52  # Max for weekly

        # All instances should be on Mondays
        for instance in instances:
            assert instance.weekday() == 0  # Monday is 0

    def test_sms_handler_event_detection(self):
        """Test SMS handler event detection."""
        from personal_assistant.tools.event_creation.sms_handler import EventCreationSMSHandler

        # Mock dependencies
        mock_llm_client = MagicMock()
        mock_db_session = AsyncMock()

        handler = EventCreationSMSHandler(mock_llm_client, mock_db_session)

        # Test event creation requests
        assert handler._is_event_creation_request(
            "Meeting with John tomorrow at 2pm")
        assert handler._is_event_creation_request(
            "Weekly team meeting every Monday at 10am")
        assert handler._is_event_creation_request(
            "Coffee with Sarah at Starbucks tomorrow at 3pm")

        # Test non-event requests
        assert not handler._is_event_creation_request("Hello, how are you?")
        assert not handler._is_event_creation_request(
            "What's the weather like?")
        assert not handler._is_event_creation_request("Show me my calendar")

    def test_sms_handler_parsing(self):
        """Test SMS handler parsing functions."""
        from personal_assistant.tools.event_creation.sms_handler import EventCreationSMSHandler

        # Mock dependencies
        mock_llm_client = MagicMock()
        mock_db_session = AsyncMock()

        handler = EventCreationSMSHandler(mock_llm_client, mock_db_session)

        # Test deletion parsing
        event_id = handler._parse_deletion_request("Delete event 123")
        assert event_id == 123

        event_id = handler._parse_deletion_request("Remove meeting 456")
        assert event_id == 456

        # Test modification parsing
        event_id, updates = handler._parse_modification_request(
            "Change event 123 to tomorrow at 3pm")
        assert event_id == 123

        # Test non-matching requests
        event_id = handler._parse_deletion_request("Hello world")
        assert event_id is None
