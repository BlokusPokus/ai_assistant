"""
Integration tests for Task 073: Chat Integration with Agent Service.

This module tests the complete chat functionality including API endpoints,
database operations, and AgentCore integration.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from apps.fastapi_app.main import app
from personal_assistant.database.models.users import User
from personal_assistant.database.models.conversation_state import ConversationState
from personal_assistant.database.models.conversation_message import ConversationMessage

client = TestClient(app)


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Create a test user for chat tests."""
    from personal_assistant.auth.password_service import password_service
    
    user = User(
        email="chat_test@example.com",
        full_name="Chat Test User",
        hashed_password=password_service.hash_password("testpassword123"),
        is_active=True,
        is_verified=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """Get authentication headers for the test user."""
    from personal_assistant.auth.jwt_service import jwt_service
    
    token = jwt_service.create_access_token({
        "user_id": test_user.id,
        "email": test_user.email,
        "full_name": test_user.full_name
    })
    
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_send_message_new_conversation(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test sending a message to start a new conversation."""
    with patch('apps.fastapi_app.services.chat_service.AgentCore') as mock_agent_core:
        # Mock the AgentCore run method
        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = "Hello! I'm your AI assistant. How can I help you today?"
        mock_agent_core.return_value = mock_agent_instance
        
        response = client.post(
            "/api/v1/chat/messages",
            json={"content": "Hello, AI!"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "user_message" in data
        assert "ai_message" in data
        assert "conversation_id" in data
        
        # Check user message
        user_msg = data["user_message"]
        assert user_msg["content"] == "Hello, AI!"
        assert user_msg["role"] == "user"
        assert user_msg["message_type"] == "user_input"
        
        # Check AI message
        ai_msg = data["ai_message"]
        assert ai_msg["role"] == "assistant"
        assert ai_msg["message_type"] == "assistant_response"
        assert ai_msg["content"] == "Hello! I'm your AI assistant. How can I help you today!"
        
        # Verify conversation was created in database
        conv_query = await db.execute(
            "SELECT * FROM conversation_states WHERE conversation_id = :conv_id",
            {"conv_id": data["conversation_id"]}
        )
        conversation = conv_query.fetchone()
        assert conversation is not None
        assert conversation.user_id == test_user.id


@pytest.mark.asyncio
async def test_send_message_existing_conversation(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test sending a message to an existing conversation."""
    # First create a conversation
    from apps.fastapi_app.services.chat_service import ChatService
    from personal_assistant.core import AgentCore
    
    chat_service = ChatService(AgentCore())
    conversation = await chat_service.create_conversation(db, test_user.id)
    
    with patch('apps.fastapi_app.services.chat_service.AgentCore') as mock_agent_core:
        # Mock the AgentCore run method
        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = "I understand. What else can I help you with?"
        mock_agent_core.return_value = mock_agent_instance
        
        response = client.post(
            "/api/v1/chat/messages",
            json={
                "content": "Tell me about the weather",
                "conversation_id": conversation.conversation_id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that the same conversation ID is returned
        assert data["conversation_id"] == conversation.conversation_id
        
        # Check user message
        user_msg = data["user_message"]
        assert user_msg["content"] == "Tell me about the weather"
        assert user_msg["conversation_id"] == conversation.conversation_id


@pytest.mark.asyncio
async def test_get_conversations(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test getting user's conversations."""
    # Create some test conversations
    from apps.fastapi_app.services.chat_service import ChatService
    from personal_assistant.core import AgentCore
    
    chat_service = ChatService(AgentCore())
    
    # Create multiple conversations
    conv1 = await chat_service.create_conversation(db, test_user.id)
    conv2 = await chat_service.create_conversation(db, test_user.id)
    
    # Add some messages to the conversations
    msg1 = ConversationMessage(
        conversation_id=conv1.conversation_id,
        role="user",
        content="Hello",
        message_type="user_input"
    )
    msg2 = ConversationMessage(
        conversation_id=conv1.conversation_id,
        role="assistant",
        content="Hi there!",
        message_type="assistant_response"
    )
    
    db.add_all([msg1, msg2])
    await db.commit()
    
    response = client.get("/api/v1/chat/conversations", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "conversations" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    
    assert data["total"] >= 2
    assert len(data["conversations"]) >= 2
    
    # Check that conversations are ordered by updated_at desc
    conversations = data["conversations"]
    for i in range(len(conversations) - 1):
        assert conversations[i]["updated_at"] >= conversations[i + 1]["updated_at"]


@pytest.mark.asyncio
async def test_get_conversation_messages(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test getting messages for a conversation."""
    # Create a conversation with messages
    from apps.fastapi_app.services.chat_service import ChatService
    from personal_assistant.core import AgentCore
    
    chat_service = ChatService(AgentCore())
    conversation = await chat_service.create_conversation(db, test_user.id)
    
    # Add messages
    messages = [
        ConversationMessage(
            conversation_id=conversation.conversation_id,
            role="user",
            content="Hello",
            message_type="user_input"
        ),
        ConversationMessage(
            conversation_id=conversation.conversation_id,
            role="assistant",
            content="Hi there!",
            message_type="assistant_response"
        ),
        ConversationMessage(
            conversation_id=conversation.conversation_id,
            role="user",
            content="How are you?",
            message_type="user_input"
        )
    ]
    
    db.add_all(messages)
    await db.commit()
    
    response = client.get(
        f"/api/v1/chat/conversations/{conversation.conversation_id}/messages",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 3
    assert data[0]["content"] == "Hello"
    assert data[0]["role"] == "user"
    assert data[1]["content"] == "Hi there!"
    assert data[1]["role"] == "assistant"
    assert data[2]["content"] == "How are you?"
    assert data[2]["role"] == "user"


@pytest.mark.asyncio
async def test_delete_conversation(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test deleting a conversation."""
    # Create a conversation
    from apps.fastapi_app.services.chat_service import ChatService
    from personal_assistant.core import AgentCore
    
    chat_service = ChatService(AgentCore())
    conversation = await chat_service.create_conversation(db, test_user.id)
    
    response = client.delete(
        f"/api/v1/chat/conversations/{conversation.conversation_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Conversation deleted successfully"
    
    # Verify conversation is deleted
    conv_query = await db.execute(
        "SELECT * FROM conversation_states WHERE conversation_id = :conv_id",
        {"conv_id": conversation.conversation_id}
    )
    conversation_check = conv_query.fetchone()
    assert conversation_check is None


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test that chat endpoints require authentication."""
    response = client.post(
        "/api/v1/chat/messages",
        json={"content": "Hello"}
    )
    assert response.status_code == 401
    
    response = client.get("/api/v1/chat/conversations")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_conversation_access_control(db: AsyncSession, auth_headers: dict):
    """Test that users can only access their own conversations."""
    # Create another user
    from personal_assistant.auth.password_service import password_service
    
    other_user = User(
        email="other_user@example.com",
        full_name="Other User",
        hashed_password=password_service.hash_password("testpassword123"),
        is_active=True,
        is_verified=True
    )
    db.add(other_user)
    await db.commit()
    await db.refresh(other_user)
    
    # Create a conversation for the other user
    from apps.fastapi_app.services.chat_service import ChatService
    from personal_assistant.core import AgentCore
    
    chat_service = ChatService(AgentCore())
    conversation = await chat_service.create_conversation(db, other_user.id)
    
    # Try to access the other user's conversation
    response = client.get(
        f"/api/v1/chat/conversations/{conversation.conversation_id}/messages",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_message_validation(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test message input validation."""
    # Test empty message
    response = client.post(
        "/api/v1/chat/messages",
        json={"content": ""},
        headers=auth_headers
    )
    assert response.status_code == 422
    
    # Test message too long
    long_message = "x" * 10001
    response = client.post(
        "/api/v1/chat/messages",
        json={"content": long_message},
        headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pagination(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test conversation pagination."""
    # Create multiple conversations
    from apps.fastapi_app.services.chat_service import ChatService
    from personal_assistant.core import AgentCore
    
    chat_service = ChatService(AgentCore())
    
    for i in range(5):
        await chat_service.create_conversation(db, test_user.id)
    
    # Test first page
    response = client.get(
        "/api/v1/chat/conversations?page=1&per_page=3",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["conversations"]) == 3
    assert data["page"] == 1
    assert data["per_page"] == 3
    assert data["total"] >= 5
    
    # Test second page
    response = client.get(
        "/api/v1/chat/conversations?page=2&per_page=3",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["conversations"]) >= 2
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_agent_core_integration(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test integration with AgentCore service."""
    with patch('apps.fastapi_app.services.chat_service.AgentCore') as mock_agent_core:
        # Mock the AgentCore run method to simulate different responses
        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = "I can help you with various tasks like creating reminders, managing your calendar, and organizing your notes. What would you like to do?"
        mock_agent_core.return_value = mock_agent_instance
        
        response = client.post(
            "/api/v1/chat/messages",
            json={"content": "What can you help me with?"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify AgentCore was called with correct parameters
        mock_agent_instance.run.assert_called_once_with("What can you help me with?", test_user.id)
        
        # Check AI response
        ai_msg = data["ai_message"]
        assert ai_msg["content"] == "I can help you with various tasks like creating reminders, managing your calendar, and organizing your notes. What would you like to do?"


@pytest.mark.asyncio
async def test_agent_core_error_handling(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test error handling when AgentCore fails."""
    with patch('apps.fastapi_app.services.chat_service.AgentCore') as mock_agent_core:
        # Mock AgentCore to raise an exception
        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.side_effect = Exception("AgentCore error")
        mock_agent_core.return_value = mock_agent_instance
        
        response = client.post(
            "/api/v1/chat/messages",
            json={"content": "Hello"},
            headers=auth_headers
        )
        
        assert response.status_code == 200  # Should still return 200 with error message
        data = response.json()
        
        # Check that error message is returned
        ai_msg = data["ai_message"]
        assert "I'm sorry, I encountered an error" in ai_msg["content"]

