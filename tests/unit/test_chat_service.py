"""
Unit tests for Task 073: Chat Integration with Agent Service.

This module tests the ChatService class methods in isolation.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from uuid import uuid4

from apps.fastapi_app.services.chat_service import ChatService
from personal_assistant.database.models.conversation_state import ConversationState
from personal_assistant.database.models.conversation_message import ConversationMessage
from personal_assistant.database.models.users import User


@pytest.fixture
def mock_agent_core():
    """Create a mock AgentCore instance."""
    agent_core = Mock()
    agent_core.run = AsyncMock(return_value="Mock AI response")
    return agent_core


@pytest.fixture
def chat_service(mock_agent_core):
    """Create a ChatService instance with mocked AgentCore."""
    return ChatService(mock_agent_core)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def test_user():
    """Create a test user."""
    return User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        is_active=True
    )


@pytest.mark.asyncio
async def test_create_conversation(chat_service, mock_db_session, test_user):
    """Test creating a new conversation."""
    # Mock the database operations
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None
    
    # Create conversation
    conversation = await chat_service.create_conversation(mock_db_session, test_user.id)
    
    # Verify conversation was created
    assert isinstance(conversation, ConversationState)
    assert conversation.user_id == test_user.id
    assert conversation.conversation_id is not None
    assert conversation.step_count == 0
    assert conversation.user_input is None
    
    # Verify database operations
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_conversations(chat_service, mock_db_session, test_user):
    """Test getting user conversations with pagination."""
    # Mock database query results
    mock_conversations = [
        ConversationState(
            id=1,
            conversation_id=str(uuid4()),
            user_id=test_user.id,
            step_count=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ConversationState(
            id=2,
            conversation_id=str(uuid4()),
            user_id=test_user.id,
            step_count=2,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    # Mock the execute method to return conversations
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = mock_conversations
    mock_db_session.execute.return_value = mock_result
    
    # Mock the count query
    mock_count_result = Mock()
    mock_count_result.scalar.return_value = 2
    mock_db_session.execute.side_effect = [mock_count_result, mock_result]
    
    # Get conversations
    conversations, total = await chat_service.get_user_conversations(
        mock_db_session, test_user.id, page=1, per_page=10
    )
    
    # Verify results
    assert len(conversations) == 2
    assert total == 2
    assert conversations[0].user_id == test_user.id
    assert conversations[1].user_id == test_user.id


@pytest.mark.asyncio
async def test_get_conversation_messages(chat_service, mock_db_session, test_user):
    """Test getting conversation messages."""
    conversation_id = str(uuid4())
    
    # Mock conversation verification
    mock_conversation = ConversationState(
        id=1,
        conversation_id=conversation_id,
        user_id=test_user.id
    )
    
    mock_conv_result = Mock()
    mock_conv_result.scalar_one_or_none.return_value = mock_conversation
    mock_db_session.execute.return_value = mock_conv_result
    
    # Mock messages query
    mock_messages = [
        ConversationMessage(
            id=1,
            conversation_id=conversation_id,
            role="user",
            content="Hello",
            message_type="user_input",
            timestamp=datetime.utcnow()
        ),
        ConversationMessage(
            id=2,
            conversation_id=conversation_id,
            role="assistant",
            content="Hi there!",
            message_type="assistant_response",
            timestamp=datetime.utcnow()
        )
    ]
    
    mock_msg_result = Mock()
    mock_msg_result.scalars.return_value.all.return_value = mock_messages
    mock_db_session.execute.side_effect = [mock_conv_result, mock_msg_result]
    
    # Get messages
    messages = await chat_service.get_conversation_messages(
        mock_db_session, conversation_id, test_user.id, limit=50
    )
    
    # Verify results
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


@pytest.mark.asyncio
async def test_get_conversation_messages_not_found(chat_service, mock_db_session, test_user):
    """Test getting messages for non-existent conversation."""
    conversation_id = str(uuid4())
    
    # Mock conversation not found
    mock_conv_result = Mock()
    mock_conv_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_conv_result
    
    # Should raise ValueError
    with pytest.raises(ValueError, match="Conversation not found or access denied"):
        await chat_service.get_conversation_messages(
            mock_db_session, conversation_id, test_user.id
        )


@pytest.mark.asyncio
async def test_send_message_new_conversation(chat_service, mock_db_session, test_user):
    """Test sending a message to start a new conversation."""
    message_content = "Hello, AI!"
    
    # Mock conversation creation
    mock_conversation = ConversationState(
        id=1,
        conversation_id=str(uuid4()),
        user_id=test_user.id,
        step_count=0
    )
    
    with patch.object(chat_service, 'create_conversation', return_value=mock_conversation):
        # Mock database operations
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # Send message
        user_msg, ai_msg, conv_id = await chat_service.send_message(
            mock_db_session, test_user.id, message_content
        )
        
        # Verify results
        assert user_msg.content == message_content
        assert user_msg.role == "user"
        assert user_msg.message_type == "user_input"
        
        assert ai_msg.role == "assistant"
        assert ai_msg.message_type == "assistant_response"
        assert ai_msg.content == "Mock AI response"
        
        assert conv_id == mock_conversation.conversation_id
        
        # Verify AgentCore was called
        chat_service.agent_core.run.assert_called_once_with(message_content, test_user.id)


@pytest.mark.asyncio
async def test_send_message_existing_conversation(chat_service, mock_db_session, test_user):
    """Test sending a message to an existing conversation."""
    conversation_id = str(uuid4())
    message_content = "Tell me about the weather"
    
    # Mock existing conversation
    mock_conversation = ConversationState(
        id=1,
        conversation_id=conversation_id,
        user_id=test_user.id,
        step_count=1
    )
    
    # Mock database operations
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None
    
    # Mock conversation query
    mock_conv_result = Mock()
    mock_conv_result.scalar_one_or_none.return_value = mock_conversation
    mock_db_session.execute.return_value = mock_conv_result
    
    # Send message
    user_msg, ai_msg, conv_id = await chat_service.send_message(
        mock_db_session, test_user.id, message_content, conversation_id
    )
    
    # Verify results
    assert user_msg.content == message_content
    assert ai_msg.content == "Mock AI response"
    assert conv_id == conversation_id
    
    # Verify conversation was updated
    assert mock_conversation.user_input == message_content
    assert mock_conversation.step_count == 2


@pytest.mark.asyncio
async def test_send_message_conversation_not_found(chat_service, mock_db_session, test_user):
    """Test sending message to non-existent conversation."""
    conversation_id = str(uuid4())
    message_content = "Hello"
    
    # Mock conversation not found
    mock_conv_result = Mock()
    mock_conv_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_conv_result
    
    # Should raise ValueError
    with pytest.raises(ValueError, match="Conversation not found or access denied"):
        await chat_service.send_message(
            mock_db_session, test_user.id, message_content, conversation_id
        )


@pytest.mark.asyncio
async def test_send_message_agent_core_error(chat_service, mock_db_session, test_user):
    """Test error handling when AgentCore fails."""
    message_content = "Hello"
    
    # Mock AgentCore to raise exception
    chat_service.agent_core.run.side_effect = Exception("AgentCore error")
    
    # Mock conversation creation
    mock_conversation = ConversationState(
        id=1,
        conversation_id=str(uuid4()),
        user_id=test_user.id,
        step_count=0
    )
    
    with patch.object(chat_service, 'create_conversation', return_value=mock_conversation):
        # Mock database operations
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # Send message
        user_msg, ai_msg, conv_id = await chat_service.send_message(
            mock_db_session, test_user.id, message_content
        )
        
        # Verify error message is returned
        assert ai_msg.content == "I'm sorry, I encountered an error processing your message. Please try again."


@pytest.mark.asyncio
async def test_delete_conversation(chat_service, mock_db_session, test_user):
    """Test deleting a conversation."""
    conversation_id = str(uuid4())
    
    # Mock conversation query
    mock_conversation = ConversationState(
        id=1,
        conversation_id=conversation_id,
        user_id=test_user.id
    )
    
    mock_conv_result = Mock()
    mock_conv_result.scalar_one_or_none.return_value = mock_conversation
    mock_db_session.execute.return_value = mock_conv_result
    
    # Delete conversation
    result = await chat_service.delete_conversation(
        mock_db_session, conversation_id, test_user.id
    )
    
    # Verify result
    assert result is True
    mock_db_session.delete.assert_called_once_with(mock_conversation)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_conversation_not_found(chat_service, mock_db_session, test_user):
    """Test deleting non-existent conversation."""
    conversation_id = str(uuid4())
    
    # Mock conversation not found
    mock_conv_result = Mock()
    mock_conv_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_conv_result
    
    # Delete conversation
    result = await chat_service.delete_conversation(
        mock_db_session, conversation_id, test_user.id
    )
    
    # Verify result
    assert result is False
    mock_db_session.delete.assert_not_called()


@pytest.mark.asyncio
async def test_get_conversation_by_id(chat_service, mock_db_session, test_user):
    """Test getting a conversation by ID."""
    conversation_id = str(uuid4())
    
    # Mock conversation
    mock_conversation = ConversationState(
        id=1,
        conversation_id=conversation_id,
        user_id=test_user.id
    )
    
    mock_conv_result = Mock()
    mock_conv_result.scalar_one_or_none.return_value = mock_conversation
    mock_db_session.execute.return_value = mock_conv_result
    
    # Get conversation
    conversation = await chat_service.get_conversation_by_id(
        mock_db_session, conversation_id, test_user.id
    )
    
    # Verify result
    assert conversation == mock_conversation


@pytest.mark.asyncio
async def test_get_conversation_by_id_not_found(chat_service, mock_db_session, test_user):
    """Test getting non-existent conversation by ID."""
    conversation_id = str(uuid4())
    
    # Mock conversation not found
    mock_conv_result = Mock()
    mock_conv_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_conv_result
    
    # Get conversation
    conversation = await chat_service.get_conversation_by_id(
        mock_db_session, conversation_id, test_user.id
    )
    
    # Verify result
    assert conversation is None
