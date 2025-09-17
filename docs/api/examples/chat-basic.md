# Basic Chat Examples

This example demonstrates the fundamental chat functionality, including sending messages, managing conversations, and handling responses.

## Overview

The basic chat flow involves:

1. Sending a message to start a conversation
2. Continuing conversations with follow-up messages
3. Retrieving conversation history
4. Managing conversations (list, view, delete)

## Prerequisites

- Valid authentication token
- Access to chat API endpoints
- Understanding of conversation flow

## Step 1: Send Initial Message

### Start a new conversation

```bash
curl -X POST "https://api.personalassistant.com/api/v1/chat/messages" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello! Can you help me plan my day?",
    "conversation_id": null
  }'
```

**Expected Response:**

```json
{
  "user_message": {
    "id": 1001,
    "conversation_id": "conv_abc123def456",
    "role": "user",
    "content": "Hello! Can you help me plan my day?",
    "message_type": "text",
    "tool_name": null,
    "tool_success": null,
    "timestamp": "2024-01-15T10:30:00Z",
    "additional_data": null
  },
  "ai_message": {
    "id": 1002,
    "conversation_id": "conv_abc123def456",
    "role": "assistant",
    "content": "Hello! I'd be happy to help you plan your day. To get started, could you tell me:\n\n1. What are your main priorities for today?\n2. Do you have any specific deadlines or appointments?\n3. What time do you have available?\n\nOnce I know more about your schedule and goals, I can help you create an effective daily plan!",
    "message_type": "text",
    "tool_name": null,
    "tool_success": null,
    "timestamp": "2024-01-15T10:30:05Z",
    "additional_data": {
      "processing_time_ms": 1200,
      "tokens_used": 45
    }
  },
  "conversation_id": "conv_abc123def456"
}
```

### JavaScript Implementation

```javascript
class ChatService {
  constructor(accessToken) {
    this.baseURL = "https://api.personalassistant.com/api/v1/chat";
    this.accessToken = accessToken;
  }

  async sendMessage(content, conversationId = null) {
    const response = await fetch(`${this.baseURL}/messages`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async getConversations(page = 1, perPage = 20) {
    const response = await fetch(
      `${this.baseURL}/conversations?page=${page}&per_page=${perPage}`,
      {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async getConversationMessages(conversationId, limit = 50) {
    const response = await fetch(
      `${this.baseURL}/conversations/${conversationId}/messages?limit=${limit}`,
      {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  async deleteConversation(conversationId) {
    const response = await fetch(
      `${this.baseURL}/conversations/${conversationId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }
}

// Usage
const chatService = new ChatService("your_access_token");

// Start a new conversation
try {
  const result = await chatService.sendMessage(
    "Hello! Can you help me plan my day?"
  );
  console.log("Conversation started:", result.conversation_id);
  console.log("AI Response:", result.ai_message.content);
} catch (error) {
  console.error("Failed to send message:", error.message);
}
```

## Step 2: Continue Conversation

### Send follow-up message

```bash
curl -X POST "https://api.personalassistant.com/api/v1/chat/messages" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I have a meeting at 2 PM and need to finish a report by 5 PM. I have the morning free.",
    "conversation_id": "conv_abc123def456"
  }'
```

**Expected Response:**

```json
{
  "user_message": {
    "id": 1003,
    "conversation_id": "conv_abc123def456",
    "role": "user",
    "content": "I have a meeting at 2 PM and need to finish a report by 5 PM. I have the morning free.",
    "message_type": "text",
    "tool_name": null,
    "tool_success": null,
    "timestamp": "2024-01-15T10:32:00Z",
    "additional_data": null
  },
  "ai_message": {
    "id": 1004,
    "conversation_id": "conv_abc123def456",
    "role": "assistant",
    "content": "Great! Based on your schedule, here's a suggested plan for your day:\n\n**Morning (9 AM - 12 PM):**\n- Start working on your report (3 hours should be sufficient)\n- Take a 15-minute break every hour\n- Focus on the most challenging parts first\n\n**Lunch Break (12 PM - 1 PM):**\n- Take a proper lunch break to recharge\n- Maybe take a short walk to clear your mind\n\n**Afternoon (1 PM - 2 PM):**\n- Review and polish your report\n- Prepare for your 2 PM meeting\n\n**Meeting (2 PM - 3 PM):**\n- Attend your meeting\n\n**Late Afternoon (3 PM - 5 PM):**\n- Finalize your report\n- Submit before the 5 PM deadline\n\nWould you like me to help you break down the report into smaller tasks or adjust this schedule?",
    "message_type": "text",
    "tool_name": null,
    "tool_success": null,
    "timestamp": "2024-01-15T10:32:08Z",
    "additional_data": {
      "processing_time_ms": 2100,
      "tokens_used": 78
    }
  },
  "conversation_id": "conv_abc123def456"
}
```

## Step 3: Retrieve Conversation History

### Get all conversations

```bash
curl -X GET "https://api.personalassistant.com/api/v1/chat/conversations?page=1&per_page=10" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response:**

```json
{
  "conversations": [
    {
      "id": 1,
      "conversation_id": "conv_abc123def456",
      "user_id": 123,
      "user_input": "Hello! Can you help me plan my day?",
      "focus_areas": {
        "areas": ["planning", "productivity"]
      },
      "step_count": 2,
      "last_tool_result": null,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:32:08Z",
      "message_count": 4
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### Get messages for specific conversation

```bash
curl -X GET "https://api.personalassistant.com/api/v1/chat/conversations/conv_abc123def456/messages?limit=20" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response:**

```json
[
  {
    "id": 1001,
    "conversation_id": "conv_abc123def456",
    "role": "user",
    "content": "Hello! Can you help me plan my day?",
    "message_type": "text",
    "tool_name": null,
    "tool_success": null,
    "timestamp": "2024-01-15T10:30:00Z",
    "additional_data": null
  },
  {
    "id": 1002,
    "conversation_id": "conv_abc123def456",
    "role": "assistant",
    "content": "Hello! I'd be happy to help you plan your day. To get started, could you tell me:\n\n1. What are your main priorities for today?\n2. Do you have any specific deadlines or appointments?\n3. What time do you have available?\n\nOnce I know more about your schedule and goals, I can help you create an effective daily plan!",
    "message_type": "text",
    "tool_name": null,
    "tool_success": null,
    "timestamp": "2024-01-15T10:30:05Z",
    "additional_data": {
      "processing_time_ms": 1200,
      "tokens_used": 45
    }
  },
  {
    "id": 1003,
    "conversation_id": "conv_abc123def456",
    "role": "user",
    "content": "I have a meeting at 2 PM and need to finish a report by 5 PM. I have the morning free.",
    "message_type": "text",
    "tool_name": null,
    "tool_success": null,
    "timestamp": "2024-01-15T10:32:00Z",
    "additional_data": null
  },
  {
    "id": 1004,
    "conversation_id": "conv_abc123def456",
    "role": "assistant",
    "content": "Great! Based on your schedule, here's a suggested plan for your day:\n\n**Morning (9 AM - 12 PM):**\n- Start working on your report (3 hours should be sufficient)\n- Take a 15-minute break every hour\n- Focus on the most challenging parts first\n\n**Lunch Break (12 PM - 1 PM):**\n- Take a proper lunch break to recharge\n- Maybe take a short walk to clear your mind\n\n**Afternoon (1 PM - 2 PM):**\n- Review and polish your report\n- Prepare for your 2 PM meeting\n\n**Meeting (2 PM - 3 PM):**\n- Attend your meeting\n\n**Late Afternoon (3 PM - 5 PM):**\n- Finalize your report\n- Submit before the 5 PM deadline\n\nWould you like me to help you break down the report into smaller tasks or adjust this schedule?",
    "message_type": "text",
    "tool_name": null,
    "tool_success": null,
    "timestamp": "2024-01-15T10:32:08Z",
    "additional_data": {
      "processing_time_ms": 2100,
      "tokens_used": 78
    }
  }
]
```

## Step 4: Delete Conversation

### Delete a conversation

```bash
curl -X DELETE "https://api.personalassistant.com/api/v1/chat/conversations/conv_abc123def456" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response:**

```json
{
  "message": "Conversation deleted successfully"
}
```

## Complete Chat Application Example

### HTML/CSS/JavaScript Implementation

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Personal Assistant Chat</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f5f5f5;
      }
      .chat-container {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        height: 500px;
        display: flex;
        flex-direction: column;
      }
      .chat-messages {
        flex: 1;
        overflow-y: auto;
        border: 1px solid #ddd;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
      }
      .message {
        margin-bottom: 10px;
        padding: 10px;
        border-radius: 5px;
      }
      .user-message {
        background-color: #007bff;
        color: white;
        margin-left: 20%;
      }
      .ai-message {
        background-color: #f8f9fa;
        color: #333;
        margin-right: 20%;
      }
      .message-input {
        display: flex;
        gap: 10px;
      }
      .message-input input {
        flex: 1;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
      }
      .message-input button {
        padding: 10px 20px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
      }
      .message-input button:hover {
        background-color: #0056b3;
      }
      .conversation-list {
        margin-bottom: 20px;
      }
      .conversation-item {
        padding: 10px;
        border: 1px solid #ddd;
        margin-bottom: 5px;
        border-radius: 5px;
        cursor: pointer;
        background: white;
      }
      .conversation-item:hover {
        background-color: #f8f9fa;
      }
      .conversation-item.active {
        background-color: #007bff;
        color: white;
      }
      .loading {
        text-align: center;
        color: #666;
        font-style: italic;
      }
    </style>
  </head>
  <body>
    <h1>Personal Assistant Chat</h1>

    <div class="conversation-list">
      <h3>Conversations</h3>
      <div id="conversations"></div>
      <button onclick="createNewConversation()">New Conversation</button>
    </div>

    <div class="chat-container">
      <div class="chat-messages" id="chatMessages">
        <div class="message ai-message">
          Welcome! Start a conversation by typing a message below.
        </div>
      </div>
      <div class="message-input">
        <input
          type="text"
          id="messageInput"
          placeholder="Type your message..."
          onkeypress="handleKeyPress(event)"
        />
        <button onclick="sendMessage()">Send</button>
      </div>
    </div>

    <script>
      class ChatApp {
        constructor() {
          this.accessToken = localStorage.getItem("access_token");
          this.currentConversationId = null;
          this.chatService = new ChatService(this.accessToken);
          this.init();
        }

        async init() {
          if (!this.accessToken) {
            alert("Please login first");
            return;
          }
          await this.loadConversations();
        }

        async loadConversations() {
          try {
            const response = await this.chatService.getConversations();
            this.displayConversations(response.conversations);
          } catch (error) {
            console.error("Failed to load conversations:", error);
          }
        }

        displayConversations(conversations) {
          const container = document.getElementById("conversations");
          container.innerHTML = "";

          conversations.forEach((conv) => {
            const div = document.createElement("div");
            div.className = "conversation-item";
            div.textContent = conv.user_input || "New Conversation";
            div.onclick = () => this.loadConversation(conv.conversation_id);
            container.appendChild(div);
          });
        }

        async loadConversation(conversationId) {
          this.currentConversationId = conversationId;
          try {
            const messages = await this.chatService.getConversationMessages(
              conversationId
            );
            this.displayMessages(messages);
          } catch (error) {
            console.error("Failed to load conversation:", error);
          }
        }

        displayMessages(messages) {
          const container = document.getElementById("chatMessages");
          container.innerHTML = "";

          messages.forEach((message) => {
            const div = document.createElement("div");
            div.className = `message ${
              message.role === "user" ? "user-message" : "ai-message"
            }`;
            div.textContent = message.content;
            container.appendChild(div);
          });

          container.scrollTop = container.scrollHeight;
        }

        async sendMessage() {
          const input = document.getElementById("messageInput");
          const content = input.value.trim();

          if (!content) return;

          input.value = "";

          // Add user message to chat
          this.addMessage("user", content);

          // Show loading
          this.addMessage("ai", "Thinking...", true);

          try {
            const response = await this.chatService.sendMessage(
              content,
              this.currentConversationId
            );

            // Remove loading message
            this.removeLastMessage();

            // Add AI response
            this.addMessage("ai", response.ai_message.content);

            // Update current conversation ID
            this.currentConversationId = response.conversation_id;

            // Reload conversations to show updated list
            await this.loadConversations();
          } catch (error) {
            this.removeLastMessage();
            this.addMessage("ai", `Error: ${error.message}`);
          }
        }

        addMessage(role, content, isTemporary = false) {
          const container = document.getElementById("chatMessages");
          const div = document.createElement("div");
          div.className = `message ${
            role === "user" ? "user-message" : "ai-message"
          }`;
          div.textContent = content;
          if (isTemporary) {
            div.className += " loading";
          }
          container.appendChild(div);
          container.scrollTop = container.scrollHeight;
          return div;
        }

        removeLastMessage() {
          const container = document.getElementById("chatMessages");
          const lastMessage = container.lastElementChild;
          if (lastMessage && lastMessage.classList.contains("loading")) {
            container.removeChild(lastMessage);
          }
        }

        async createNewConversation() {
          this.currentConversationId = null;
          document.getElementById("chatMessages").innerHTML =
            '<div class="message ai-message">Welcome! Start a conversation by typing a message below.</div>';
        }
      }

      // Initialize the chat app
      const chatApp = new ChatApp();

      function sendMessage() {
        chatApp.sendMessage();
      }

      function handleKeyPress(event) {
        if (event.key === "Enter") {
          sendMessage();
        }
      }

      function createNewConversation() {
        chatApp.createNewConversation();
      }
    </script>
  </body>
</html>
```

## Python Implementation

```python
import requests
import json
from typing import Optional, List, Dict

class ChatService:
    def __init__(self, access_token: str):
        self.base_url = 'https://api.personalassistant.com/api/v1/chat'
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def send_message(self, content: str, conversation_id: Optional[str] = None) -> Dict:
        """Send a message to the chat API."""
        data = {
            'content': content,
            'conversation_id': conversation_id
        }

        response = requests.post(
            f'{self.base_url}/messages',
            headers=self.headers,
            json=data
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

    def get_conversations(self, page: int = 1, per_page: int = 20) -> Dict:
        """Get user's conversations."""
        params = {'page': page, 'per_page': per_page}

        response = requests.get(
            f'{self.base_url}/conversations',
            headers=self.headers,
            params=params
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get messages for a specific conversation."""
        params = {'limit': limit}

        response = requests.get(
            f'{self.base_url}/conversations/{conversation_id}/messages',
            headers=self.headers,
            params=params
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

    def delete_conversation(self, conversation_id: str) -> Dict:
        """Delete a conversation."""
        response = requests.delete(
            f'{self.base_url}/conversations/{conversation_id}',
            headers=self.headers
        )

        if not response.ok:
            error = response.json()
            raise Exception(error['detail'])

        return response.json()

# Usage example
def demonstrate_chat():
    # Initialize chat service
    chat_service = ChatService('your_access_token')

    try:
        # Start a new conversation
        print("Starting new conversation...")
        result = chat_service.send_message("Hello! Can you help me plan my day?")
        conversation_id = result['conversation_id']
        print(f"Conversation started: {conversation_id}")
        print(f"AI Response: {result['ai_message']['content']}")

        # Continue the conversation
        print("\nContinuing conversation...")
        result = chat_service.send_message(
            "I have a meeting at 2 PM and need to finish a report by 5 PM.",
            conversation_id
        )
        print(f"AI Response: {result['ai_message']['content']}")

        # Get conversation history
        print("\nGetting conversation history...")
        messages = chat_service.get_conversation_messages(conversation_id)
        print(f"Total messages: {len(messages)}")

        # List all conversations
        print("\nGetting all conversations...")
        conversations = chat_service.get_conversations()
        print(f"Total conversations: {conversations['total']}")

    except Exception as e:
        print(f"Error: {e}")

# Run the demonstration
if __name__ == "__main__":
    demonstrate_chat()
```

## Error Handling

### Common Chat Errors

```javascript
function handleChatError(error, response) {
  switch (response.status) {
    case 400:
      console.error("Bad Request:", error.detail);
      // Invalid message content or conversation ID
      break;
    case 401:
      console.error("Unauthorized:", error.detail);
      // Token expired or invalid
      break;
    case 404:
      console.error("Not Found:", error.detail);
      // Conversation not found
      break;
    case 429:
      console.error("Rate Limited:", error.detail);
      // Too many requests
      break;
    case 500:
      console.error("Server Error:", error.detail);
      // Internal server error
      break;
    default:
      console.error("Unknown Error:", error.detail);
  }
}
```

## Best Practices

### Message Handling

1. **Validate input**: Check message length and content
2. **Handle errors gracefully**: Show user-friendly error messages
3. **Implement retry logic**: Handle network failures
4. **Show loading states**: Provide feedback during processing

### Conversation Management

1. **Cache conversations**: Store recent conversations locally
2. **Implement pagination**: Handle large conversation lists
3. **Auto-save drafts**: Save unsent messages
4. **Handle offline mode**: Queue messages when offline

### Performance Optimization

1. **Debounce input**: Avoid sending too many requests
2. **Implement message queuing**: Handle multiple messages
3. **Use WebSocket**: For real-time updates
4. **Optimize rendering**: Virtualize long message lists
