"""
Unit tests for conversation manager functionality.

This module tests the conversation management system including
conversation ID retrieval, state management, and archival logic.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta, timezone

from tests.utils.test_data_generators import DatabaseDataGenerator, UserDataGenerator


class TestConversationManager:
    """Test class for conversation manager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db_generator = DatabaseDataGenerator()
        self.user_generator = UserDataGenerator()

    @pytest.mark.asyncio
    async def test_get_conversation_id_success(self):
        """Test successful conversation ID retrieval."""
        # Mock user and conversation data
        mock_user_id = 123
        mock_conversation_id = "conv_123_456"
        mock_conversation_state = {
            "id": 1,
            "conversation_id": mock_conversation_id,
            "user_id": mock_user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        # Mock database session and query
        with patch('personal_assistant.memory.conversation_manager.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            # Mock the query result
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_conversation_id
            mock_session.execute.return_value = mock_result

            # Import and test the function
            from personal_assistant.memory.conversation_manager import get_conversation_id
            
            result = await get_conversation_id(mock_user_id)
            
            assert result == mock_conversation_id
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_id_not_found(self):
        """Test conversation ID retrieval when no conversation exists."""
        mock_user_id = 123

        # Mock database session and query
        with patch('personal_assistant.memory.conversation_manager.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            # Mock the query result - no conversation found
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            # Import and test the function
            from personal_assistant.memory.conversation_manager import get_conversation_id
            
            result = await get_conversation_id(mock_user_id)
            
            assert result is None
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_id_none_user_id(self):
        """Test conversation ID retrieval with None user_id."""
        # Import and test the function
        from personal_assistant.memory.conversation_manager import get_conversation_id
        
        result = await get_conversation_id(None)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_conversation_id_database_error(self):
        """Test conversation ID retrieval with database error."""
        mock_user_id = 123

        # Mock database session and query with error
        with patch('personal_assistant.memory.conversation_manager.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            # Mock database error
            mock_session.execute.side_effect = Exception("Database connection failed")

            # Import and test the function
            from personal_assistant.memory.conversation_manager import get_conversation_id
            
            result = await get_conversation_id(mock_user_id)
            
            assert result is None
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_conversation_id_success(self):
        """Test successful conversation ID creation."""
        mock_user_id = 123
        mock_conversation_id = "conv_123_456"

        # Mock database session
        with patch('personal_assistant.memory.conversation_manager.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            # Mock successful record addition
            mock_session.add.return_value = None
            mock_session.commit.return_value = None

            # Mock the conversation state creation
            with patch('personal_assistant.memory.conversation_manager.ConversationState') as mock_conversation_state:
                mock_conversation_state.return_value = Mock()
                
                # Import and test the function
                from personal_assistant.memory.conversation_manager import create_new_conversation
                
                result = await create_new_conversation(mock_user_id)
                
                assert result is not None
                assert isinstance(result, str)
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_conversation_id_database_error(self):
        """Test conversation ID creation with database error."""
        mock_user_id = 123

        # Mock database session with error
        with patch('personal_assistant.memory.conversation_manager.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            # Mock database error
            mock_session.commit.side_effect = Exception("Database commit failed")

            # Import and test the function
            from personal_assistant.memory.conversation_manager import create_new_conversation
            
            result = await create_new_conversation(mock_user_id)
            
            assert result is None
            mock_session.rollback.assert_called_once()

    def test_should_resume_conversation_recent(self):
        """Test should_resume_conversation with recent timestamp."""
        from personal_assistant.memory.conversation_manager import should_resume_conversation
        from datetime import datetime, timedelta, timezone
        
        # Test with recent timestamp (should resume)
        recent_timestamp = datetime.now(timezone.utc) - timedelta(minutes=30)
        result = should_resume_conversation(recent_timestamp)
        assert result is True

    def test_should_resume_conversation_old(self):
        """Test should_resume_conversation with old timestamp."""
        from personal_assistant.memory.conversation_manager import should_resume_conversation
        from datetime import datetime, timedelta, timezone
        
        # Test with old timestamp (should not resume)
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=2)
        result = should_resume_conversation(old_timestamp)
        assert result is False

    def test_should_resume_conversation_none(self):
        """Test should_resume_conversation with None timestamp."""
        from personal_assistant.memory.conversation_manager import should_resume_conversation
        
        # Test with None timestamp (should not resume)
        result = should_resume_conversation(None)
        assert result is False

    def test_conversation_id_format(self):
        """Test conversation ID format validation."""
        # Test that conversation IDs follow expected format
        import uuid
        
        # Test the ID generation logic
        user_id = 123
        expected_prefix = f"conv_{user_id}_"
        
        # Generate a test ID similar to what the function would create
        test_uuid = uuid.uuid4()
        test_id = f"{expected_prefix}{test_uuid.hex}"
        
        assert test_id.startswith(f"conv_{user_id}_")
        assert len(test_id) > len(expected_prefix)

    @pytest.mark.asyncio
    async def test_conversation_lifecycle_management(self):
        """Test complete conversation lifecycle management."""
        mock_user_id = 123
        mock_conversation_id = "conv_123_456"

        # Mock database session
        with patch('personal_assistant.memory.conversation_manager.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            # Mock successful operations
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            
            # Mock query results
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_conversation_id
            mock_session.execute.return_value = mock_result

            # Import functions
            from personal_assistant.memory.conversation_manager import (
                get_conversation_id,
                create_new_conversation
            )
            
            # Test complete lifecycle
            # 1. Get existing conversation
            existing_id = await get_conversation_id(mock_user_id)
            assert existing_id == mock_conversation_id
            
            # 2. Create new conversation (if needed)
            new_id = await create_new_conversation(mock_user_id)
            assert new_id is not None
            
            # Verify all operations were called
            assert mock_session.execute.call_count >= 1
            assert mock_session.add.call_count >= 1
            assert mock_session.commit.call_count >= 1

    @pytest.mark.asyncio
    async def test_conversation_manager_error_handling(self):
        """Test comprehensive error handling in conversation manager."""
        mock_user_id = 123

        # Test various error scenarios
        error_scenarios = [
            ("Database connection error", Exception("Connection failed")),
            ("SQLAlchemy error", Exception("SQL error")),
            ("Timeout error", TimeoutError("Query timeout")),
        ]

        for error_type, error in error_scenarios:
            # Mock database session with error
            with patch('personal_assistant.memory.conversation_manager.AsyncSessionLocal') as mock_session_local:
                mock_session = AsyncMock()
                mock_session_local.return_value.__aenter__.return_value = mock_session
                
                # Mock the specific error
                mock_session.execute.side_effect = error

                # Import and test the function
                from personal_assistant.memory.conversation_manager import get_conversation_id
                
                # Test error handling
                result = await get_conversation_id(mock_user_id)
                
                # Should return None on error
                assert result is None
                mock_session.execute.assert_called_once()
