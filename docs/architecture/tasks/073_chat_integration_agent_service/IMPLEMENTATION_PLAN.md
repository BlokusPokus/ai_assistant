# Implementation Plan: Chat Integration with Agent Service

## 📋 **Overview**

This document provides detailed implementation steps for integrating the existing AgentCore service with a web-based chat interface, enabling real-time communication between users and the AI agent.

## 🏗 **Architecture Components**

### **1. Database Schema (Already Exists)**

The conversation tables already exist from **Task 053: Database Schema Redesign**:

**Existing Tables:**

- `conversation_states` - Core conversation information
- `conversation_messages` - Individual messages with metadata

**No Migration Needed** - The database schema is already in place!

### **2. Backend API Structure**

```
src/apps/fastapi_app/routes/chat.py
├── POST /api/v1/chat/messages
├── GET /api/v1/chat/conversations
├── GET /api/v1/chat/conversations/{id}/messages
├── DELETE /api/v1/chat/conversations/{id}
└── WebSocket /api/v1/chat/ws

src/apps/fastapi_app/models/chat.py
├── MessageCreate
├── MessageResponse
├── ConversationResponse
├── ConversationListResponse
└── ChatWebSocketMessage

src/apps/fastapi_app/services/chat_service.py
├── ChatService
├── ConversationManager
├── MessageProcessor
└── WebSocketManager
```

### **3. Frontend Integration**

```
src/apps/frontend/src/components/chat/
├── ChatPage.tsx (update existing)
├── MessageList.tsx
├── MessageInput.tsx
├── ConversationSidebar.tsx
└── WebSocketClient.ts

src/apps/frontend/src/services/
├── chatApi.ts
├── websocketService.ts
└── conversationService.ts
```

## 🚀 **Implementation Steps**

### **Step 1: Database Models (Already Exist)**

#### **1.1 Existing Models**

The conversation models already exist from **Task 053: Database Schema Redesign**:

```python
# src/personal_assistant/database/models/conversation_state.py
class ConversationState(Base):
    """Core conversation state table."""
    __tablename__ = "conversation_states"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_input = Column(Text)
    focus_areas = Column(JSON)
    step_count = Column(Integer, default=0)
    last_tool_result = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation_state", cascade="all, delete-orphan")

# src/personal_assistant/database/models/conversation_message.py
class ConversationMessage(Base):
    """Individual conversation messages table."""
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(255), ForeignKey("conversation_states.conversation_id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False, index=True)  # 'user', 'assistant', 'tool', 'system'
    content = Column(Text)
    message_type = Column(String(50), index=True)  # 'user_input', 'assistant_response', 'tool_call', 'tool_result', 'system_message'
    tool_name = Column(String(100), index=True)
    tool_success = Column(String(10), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    additional_data = Column(JSON)

    # Relationship to conversation state
    conversation_state = relationship("ConversationState", back_populates="messages")
```

#### **1.2 User Model Already Updated**

The User model already has the conversation relationship:

```python
# src/personal_assistant/database/models/users.py
class User(Base):
    # ... existing fields ...

    # Already exists from Task 053
    conversations = relationship("ConversationState", back_populates="user", cascade="all, delete-orphan")
```

### **Step 2: Backend API Implementation**

#### **2.1 Create Chat Models**

```python
# src/apps/fastapi_app/models/chat.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Request model for creating a new message."""
    content: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None


class MessageResponse(BaseModel):
    """Response model for a message."""
    id: int
    conversation_id: str
    role: str
    content: str
    message_type: Optional[str] = None
    tool_name: Optional[str] = None
    tool_success: Optional[str] = None
    timestamp: datetime
    additional_data: Optional[dict] = None


class ConversationResponse(BaseModel):
    """Response model for a conversation."""
    id: int
    conversation_id: str
    user_id: int
    user_input: Optional[str] = None
    focus_areas: Optional[dict] = None
    step_count: int = 0
    last_tool_result: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationListResponse(BaseModel):
    """Response model for conversation list."""
    conversations: List[ConversationResponse]
    total: int
    page: int
    per_page: int


class ChatWebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str  # 'message', 'typing', 'error', 'connection'
    data: dict
    conversation_id: Optional[str] = None
```

#### **2.2 Create Chat Service**

```python
# src/apps/fastapi_app/services/chat_service.py
import logging
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.core import AgentCore
from personal_assistant.database.models.conversation_state import ConversationState
from personal_assistant.database.models.conversation_message import ConversationMessage
from personal_assistant.database.models.users import User

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations and messages."""

    def __init__(self, agent_core: AgentCore):
        self.agent_core = agent_core

    async def create_conversation(self, db: AsyncSession, user_id: int, title: Optional[str] = None) -> ConversationState:
        """Create a new conversation."""
        conversation_id = str(uuid4())
        conversation = ConversationState(
            conversation_id=conversation_id,
            user_id=user_id,
            user_input=None,  # Will be set when first message is sent
            focus_areas=None,
            step_count=0,
            last_tool_result=None
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    async def get_user_conversations(
        self,
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[ConversationState], int]:
        """Get user's conversations with pagination."""
        # Get total count
        count_query = select(func.count(ConversationState.id)).where(ConversationState.user_id == user_id)
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get conversations
        offset = (page - 1) * per_page
        query = (
            select(ConversationState)
            .where(ConversationState.user_id == user_id)
            .order_by(ConversationState.updated_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await db.execute(query)
        conversations = result.scalars().all()

        return conversations, total

    async def get_conversation_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
        user_id: int,
        limit: int = 50
    ) -> List[ConversationMessage]:
        """Get messages for a conversation."""
        query = (
            select(ConversationMessage)
            .where(
                ConversationMessage.conversation_id == conversation_id
            )
            .order_by(ConversationMessage.timestamp.asc())
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def send_message(
        self,
        db: AsyncSession,
        user_id: int,
        content: str,
        conversation_id: Optional[str] = None
    ) -> tuple[ConversationMessage, ConversationMessage, str]:
        """Send a message and get AI response."""
        # Get or create conversation
        if conversation_id:
            conversation = await db.get(ConversationState, conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise ValueError("Conversation not found or access denied")
        else:
            conversation = await self.create_conversation(db, user_id)
            conversation_id = conversation.conversation_id

        # Save user message
        user_message = ConversationMessage(
            conversation_id=conversation_id,
            role="user",
            content=content,
            message_type="user_input"
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)

        # Get AI response
        try:
            ai_response = await self.agent_core.run(content, user_id)
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            ai_response = "I'm sorry, I encountered an error processing your message. Please try again."

        # Save AI response
        ai_message = ConversationMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
            message_type="assistant_response"
        )
        db.add(ai_message)
        await db.commit()
        await db.refresh(ai_message)

        return user_message, ai_message, conversation_id

    async def delete_conversation(self, db: AsyncSession, conversation_id: str, user_id: int) -> bool:
        """Delete a conversation."""
        conversation = await db.get(ConversationState, conversation_id)
        if not conversation or conversation.user_id != user_id:
            return False

        await db.delete(conversation)
        await db.commit()
        return True
```

#### **2.3 Create Chat API Routes**

```python
# src/apps/fastapi_app/routes/chat.py
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.middleware.auth import get_current_user
from apps.fastapi_app.models.chat import (
    ConversationListResponse,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from apps.fastapi_app.services.chat_service import ChatService
from personal_assistant.core import AgentCore
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_chat_service() -> ChatService:
    """Get chat service instance."""
    agent_core = AgentCore()
    return ChatService(agent_core)


@router.post("/messages", response_model=dict)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Send a message to the AI agent."""
    try:
        user_message, ai_message, conversation_id = await chat_service.send_message(
            db, current_user.id, message_data.content, message_data.conversation_id
        )

        return {
            "user_message": MessageResponse.model_validate(user_message),
            "ai_message": MessageResponse.model_validate(ai_message),
            "conversation_id": conversation_id
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """Get user's conversations."""
    try:
        conversations, total = await chat_service.get_user_conversations(
            db, current_user.id, page, per_page
        )

        conversation_responses = [
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                is_active=conv.is_active,
                message_count=len(conv.messages)
            )
            for conv in conversations
        ]

        return ConversationListResponse(
            conversations=conversation_responses,
            total=total,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    limit: int = Query(50, ge=1, le=200),
):
    """Get messages for a conversation."""
    try:
        messages = await chat_service.get_conversation_messages(
            db, conversation_id, current_user.id, limit
        )

        return [MessageResponse.model_validate(msg) for msg in messages]
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Delete a conversation."""
    try:
        success = await chat_service.delete_conversation(db, conversation_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


# WebSocket endpoint for real-time communication
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()

    try:
        # TODO: Implement WebSocket authentication and real-time communication
        # This is a placeholder for future WebSocket implementation
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
```

### **Step 3: Frontend Integration**

#### **3.1 Create Chat API Service**

```typescript
// src/apps/frontend/src/services/chatApi.ts
import { apiClient } from "./apiClient";

export interface MessageCreate {
  content: string;
  conversation_id?: string;
}

export interface MessageResponse {
  id: number;
  conversation_id: string;
  role: string;
  content: string;
  message_type?: string;
  tool_name?: string;
  tool_success?: string;
  timestamp: string;
  additional_data?: any;
}

export interface ConversationResponse {
  id: number;
  conversation_id: string;
  user_id: number;
  user_input?: string;
  focus_areas?: any;
  step_count: number;
  last_tool_result?: any;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationListResponse {
  conversations: ConversationResponse[];
  total: number;
  page: number;
  per_page: number;
}

export const chatApi = {
  async sendMessage(messageData: MessageCreate) {
    const response = await apiClient.post("/api/v1/chat/messages", messageData);
    return response.data;
  },

  async getConversations(page = 1, perPage = 20) {
    const response = await apiClient.get("/api/v1/chat/conversations", {
      params: { page, per_page: perPage },
    });
    return response.data as ConversationListResponse;
  },

  async getConversationMessages(conversationId: string, limit = 50) {
    const response = await apiClient.get(
      `/api/v1/chat/conversations/${conversationId}/messages`,
      {
        params: { limit },
      }
    );
    return response.data as MessageResponse[];
  },

  async deleteConversation(conversationId: string) {
    const response = await apiClient.delete(
      `/api/v1/chat/conversations/${conversationId}`
    );
    return response.data;
  },
};
```

#### **3.2 Update ChatPage Component**

```typescript
// src/apps/frontend/src/components/chat/ChatPage.tsx
import React, { useState, useEffect, useRef } from "react";
import {
  chatApi,
  MessageResponse,
  ConversationResponse,
} from "../../services/chatApi";

interface ChatPageProps {
  // Add any props needed
}

export const ChatPage: React.FC<ChatPageProps> = () => {
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [conversations, setConversations] = useState<ConversationResponse[]>(
    []
  );
  const [currentConversationId, setCurrentConversationId] = useState<
    string | null
  >(null);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations on component mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversationId) {
      loadMessages(currentConversationId);
    } else {
      setMessages([]);
    }
  }, [currentConversationId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadConversations = async () => {
    try {
      const response = await chatApi.getConversations();
      setConversations(response.conversations);
    } catch (error) {
      console.error("Error loading conversations:", error);
    }
  };

  const loadMessages = async (conversationId: string) => {
    try {
      const messages = await chatApi.getConversationMessages(conversationId);
      setMessages(messages);
    } catch (error) {
      console.error("Error loading messages:", error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const messageContent = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        content: messageContent,
        conversation_id: currentConversationId || undefined,
      });

      // Update messages with both user and AI responses
      setMessages((prev) => [
        ...prev,
        response.user_message,
        response.ai_message,
      ]);

      // Set conversation ID if this was a new conversation
      if (response.conversation_id && !currentConversationId) {
        setCurrentConversationId(response.conversation_id);
        // Reload conversations to include the new one
        loadConversations();
      }
    } catch (error) {
      console.error("Error sending message:", error);
      // Restore input message on error
      setInputMessage(messageContent);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startNewConversation = () => {
    setCurrentConversationId(null);
    setMessages([]);
  };

  return (
    <div className="flex h-full">
      {/* Conversation Sidebar */}
      <div className="w-1/3 border-r border-gray-200 bg-gray-50">
        <div className="p-4">
          <button
            onClick={startNewConversation}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            New Conversation
          </button>
        </div>

        <div className="px-4">
          <h3 className="font-semibold text-gray-700 mb-3">Conversations</h3>
          <div className="space-y-2">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => setCurrentConversationId(conv.id)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  currentConversationId === conv.id
                    ? "bg-blue-100 border-blue-300"
                    : "hover:bg-gray-100"
                }`}
              >
                <div className="font-medium text-sm">
                  {conv.user_input
                    ? conv.user_input.substring(0, 50) + "..."
                    : "New Conversation"}
                </div>
                <div className="text-xs text-gray-500">
                  {conv.message_count} messages
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                <div className="text-sm">{message.content}</div>
                <div className="text-xs opacity-70 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                  <span className="text-sm">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
```

### **Step 4: Integration and Testing**

#### **4.1 Update FastAPI App**

```python
# Add to src/apps/fastapi_app/main.py
from apps.fastapi_app.routes import chat

# Add chat router
app.include_router(chat.router)
```

#### **4.2 Update Frontend Routes**

```typescript
// Update src/apps/frontend/src/App.tsx to include ChatPage
import { ChatPage } from "./components/chat/ChatPage";

// Add route for chat page
<Route path="/chat" element={<ChatPage />} />;
```

#### **4.3 Create Tests**

```python
# tests/integration/test_chat_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.main import app
from personal_assistant.database.models.users import User

client = TestClient(app)

@pytest.mark.asyncio
async def test_send_message(db: AsyncSession, test_user: User):
    """Test sending a message to the AI agent."""
    response = client.post(
        "/api/v1/chat/messages",
        json={"content": "Hello, AI!"},
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "user_message" in data
    assert "ai_message" in data
    assert "conversation_id" in data
    assert data["user_message"]["content"] == "Hello, AI!"
    assert data["user_message"]["role"] == "user"
    assert data["ai_message"]["role"] == "assistant"

@pytest.mark.asyncio
async def test_get_conversations(db: AsyncSession, test_user: User):
    """Test getting user conversations."""
    response = client.get(
        "/api/v1/chat/conversations",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert "total" in data
    assert isinstance(data["conversations"], list)
```

## 🧪 **Testing Strategy**

### **Unit Tests**

- Chat service methods
- Message creation and retrieval
- Conversation management
- Error handling

### **Integration Tests**

- API endpoint functionality
- Database operations
- AgentCore integration
- Authentication and authorization

### **End-to-End Tests**

- Complete chat flow
- Frontend-backend integration
- Real-time communication
- Error scenarios

## 🚀 **Deployment Checklist**

- [ ] Run database migration
- [ ] Deploy backend API changes
- [ ] Deploy frontend changes
- [ ] Test API endpoints
- [ ] Test frontend integration
- [ ] Monitor performance and errors
- [ ] Update documentation

## 📊 **Performance Considerations**

- **Database Indexing**: Proper indexes on conversation and message tables
- **Pagination**: Limit message history to prevent large data transfers
- **Caching**: Consider Redis caching for frequently accessed conversations
- **Connection Pooling**: Use existing database connection pooling
- **Rate Limiting**: Implement rate limiting for message sending

## 🔒 **Security Considerations**

- **Authentication**: All endpoints require valid JWT tokens
- **Authorization**: Users can only access their own conversations
- **Input Validation**: Validate message content and length
- **SQL Injection**: Use parameterized queries
- **XSS Prevention**: Sanitize message content for display

---

**Document Status**: Implementation Ready  
**Last Updated**: December 2024  
**Version**: 1.0
