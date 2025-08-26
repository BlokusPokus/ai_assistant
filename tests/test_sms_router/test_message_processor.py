"""
Unit tests for MessageProcessor service.
"""

import pytest
from personal_assistant.sms_router.services.message_processor import MessageProcessor


class TestMessageProcessor:
    """Test cases for MessageProcessor service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = MessageProcessor()

    @pytest.mark.asyncio
    async def test_process_message_basic(self):
        """Test basic message processing."""
        user_info = {
            'id': 1,
            'email': 'test@example.com',
            'full_name': 'Test User',
            'is_active': True
        }

        message = "Hello, how are you?"
        result = await self.processor.process_message(message, user_info)

        assert result['processed'] is True
        assert result['cleaned_message'] == "Hello, how are you?"
        assert result['spam_score'] == 0.0
        assert result['is_spam'] is False
        assert result['user_id'] == 1

    @pytest.mark.asyncio
    async def test_process_message_empty(self):
        """Test processing empty messages."""
        user_info = {
            'id': 1,
            'email': 'test@example.com',
            'full_name': 'Test User',
            'is_active': True
        }

        result = await self.processor.process_message("", user_info)
        assert result['processed'] is False
        assert 'error' in result

    @pytest.mark.asyncio
    async def test_clean_message(self):
        """Test message cleaning functionality."""
        # Test whitespace normalization
        cleaned = self.processor._clean_message("  Hello   World  ")
        assert cleaned == "Hello World"

        # Test abbreviation replacement
        cleaned = self.processor._clean_message("u r awesome")
        assert cleaned == "you are awesome"

        # Test multiple abbreviations
        cleaned = self.processor._clean_message("u 2 b here")
        assert cleaned == "you to be here"

    def test_calculate_spam_score(self):
        """Test spam score calculation."""
        # Test normal message
        score = self.processor._calculate_spam_score("Hello, how are you?")
        assert score == 0.0

        # Test spam indicators
        score = self.processor._calculate_spam_score("FREE MONEY! CLICK NOW!")
        assert score > 0.0

        # Test excessive caps
        score = self.processor._calculate_spam_score(
            "HELLO WORLD THIS IS A TEST")
        assert score > 0.0

        # Test excessive punctuation
        score = self.processor._calculate_spam_score(
            "Hello!!! How are you??? !!! ??? !!!")
        assert score > 0.0

    def test_extract_command(self):
        """Test command extraction."""
        # Test slash command
        command_info = self.processor._extract_command("/help")
        assert command_info is not None
        assert command_info['command'] == 'help'
        assert command_info['args'] == ''

        # Test exclamation command
        command_info = self.processor._extract_command("!status")
        assert command_info is not None
        assert command_info['command'] == 'status'

        # Test colon command
        command_info = self.processor._extract_command(
            "info: get system status")
        assert command_info is not None
        assert command_info['command'] == 'info'
        assert command_info['args'] == 'get system status'

        # Test no command
        command_info = self.processor._extract_command("Hello world")
        assert command_info is None

    def test_process_content_with_commands(self):
        """Test content processing with commands."""
        # Test help command
        result = self.processor._process_content("Hello", None)
        assert result == "Hello"

        # Test help command
        command_info = {'command': 'help', 'args': '', 'pattern': '/help'}
        result = self.processor._process_content("Hello", command_info)
        assert "Available commands" in result

        # Test status command
        command_info = {'command': 'status', 'args': '', 'pattern': '!status'}
        result = self.processor._process_content("Hello", command_info)
        assert "ready to help" in result

        # Test unknown command
        command_info = {'command': 'unknown',
                        'args': '', 'pattern': '/unknown'}
        result = self.processor._process_content("Hello", command_info)
        assert "Unknown command" in result

    def test_validate_message_length(self):
        """Test message length validation."""
        # Test valid length
        assert self.processor.validate_message_length(
            "Hello world", max_length=20) is True

        # Test invalid length
        long_message = "A" * 200
        assert self.processor.validate_message_length(
            long_message, max_length=160) is False

        # Test edge case
        edge_message = "A" * 160
        assert self.processor.validate_message_length(
            edge_message, max_length=160) is True

    def test_get_message_metadata(self):
        """Test message metadata extraction."""
        message = "Hello world! How are you today?"
        metadata = self.processor.get_message_metadata(message)

        assert metadata['length'] == 31
        assert metadata['word_count'] == 6
        assert metadata['has_commands'] is False
        assert metadata['language'] == 'likely_english'
        assert metadata['sentiment'] == 'neutral'

    def test_detect_language(self):
        """Test language detection."""
        # Test English
        assert self.processor._detect_language(
            "Hello world") == 'likely_english'

        # Test non-English (with accented characters)
        assert self.processor._detect_language(
            "Héllo wórld") == 'likely_non_english'

        # Test empty string
        assert self.processor._detect_language("") == 'likely_english'

    def test_analyze_sentiment(self):
        """Test sentiment analysis."""
        # Test positive
        assert self.processor._analyze_sentiment(
            "I love this! It's great!") == 'positive'

        # Test negative
        assert self.processor._analyze_sentiment(
            "I hate this! It's terrible!") == 'negative'

        # Test neutral
        assert self.processor._analyze_sentiment("Hello world") == 'neutral'

        # Test mixed
        assert self.processor._analyze_sentiment(
            "I like this but I don't hate that") == 'neutral'

    @pytest.mark.asyncio
    async def test_process_message_with_spam(self):
        """Test message processing with spam detection."""
        user_info = {
            'id': 1,
            'email': 'test@example.com',
            'full_name': 'Test User',
            'is_active': True
        }

        spam_message = "FREE MONEY! CLICK HERE NOW! LIMITED TIME OFFER!"
        result = await self.processor.process_message(spam_message, user_info)

        assert result['processed'] is True
        assert result['is_spam'] is True
        assert result['spam_score'] > 0.7

    @pytest.mark.asyncio
    async def test_process_message_with_command(self):
        """Test message processing with command."""
        user_info = {
            'id': 1,
            'email': 'test@example.com',
            'full_name': 'Test User',
            'is_active': True
        }

        command_message = "/help"
        result = await self.processor.process_message(command_message, user_info)

        assert result['processed'] is True
        assert result['command_info'] is not None
        assert result['command_info']['command'] == 'help'
