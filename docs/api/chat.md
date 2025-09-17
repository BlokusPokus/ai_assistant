# Chat API

The Chat API provides comprehensive chat functionality for interacting with the AI agent, including message sending, conversation management, and real-time communication capabilities.

## Base URL

```
/api/v1/chat
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Rate Limiting

- **Message sending**: 60 requests per minute
- **Conversation retrieval**: 200 requests per minute
- **WebSocket connections**: 5 concurrent connections per user

## Chat Endpoints

### Send Message

Send a message to the AI agent and receive a response.

**Endpoint**: `POST /messages`

**Request Body**:

```json
{
  "content": "What's the weather like today?",
  "conversation_id": "conv_abc123def456"
}
```

**Request Parameters**:

- `content` (string, required): Message content. Length: 1-10,000 characters
- `conversation_id` (string, optional): Existing conversation ID to continue the conversation

**Response**:

```json
{
  "user_message": {
    "id": 1001,
    "conversation_id": "conv_abc123def456",
    "role": "user",
    "content": "What's the weather like today?",
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
    "content": "I'd be happy to help you check the weather! However, I don't have access to real-time weather data. You can check the weather by visiting a weather website or using a weather app on your phone.",
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

**Status Codes**:

- `200 OK`: Message sent and response received successfully
- `400 Bad Request`: Invalid message content or conversation ID
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to process message

### Get Conversations

Get a paginated list of the current user's conversations.

**Endpoint**: `GET /conversations`

**Query Parameters**:

- `page` (integer, optional): Page number. Default: 1, minimum: 1
- `per_page` (integer, optional): Items per page. Default: 20, range: 1-100

**Response**:

```json
{
  "conversations": [
    {
      "id": 1,
      "conversation_id": "conv_abc123def456",
      "user_id": 123,
      "user_input": "What's the weather like today?",
      "focus_areas": {
        "areas": ["weather", "information"]
      },
      "step_count": 2,
      "last_tool_result": {
        "result": "Weather information requested"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:05Z",
      "message_count": 4
    },
    {
      "id": 2,
      "conversation_id": "conv_xyz789uvw012",
      "user_id": 123,
      "user_input": "Help me plan my day",
      "focus_areas": {
        "description": "daily planning"
      },
      "step_count": 1,
      "last_tool_result": null,
      "created_at": "2024-01-15T09:15:00Z",
      "updated_at": "2024-01-15T09:15:30Z",
      "message_count": 2
    }
  ],
  "total": 2,
  "page": 1,
  "per_page": 20
}
```

**Status Codes**:

- `200 OK`: Conversations retrieved successfully
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to retrieve conversations

### Get Conversation Messages

Get all messages for a specific conversation.

**Endpoint**: `GET /conversations/{conversation_id}/messages`

**Path Parameters**:

- `conversation_id` (string): ID of the conversation

**Query Parameters**:

- `limit` (integer, optional): Maximum number of messages to return. Default: 50, range: 1-200

**Response**:

```json
[
  {
    "id": 1001,
    "conversation_id": "conv_abc123def456",
    "role": "user",
    "content": "What's the weather like today?",
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
    "content": "I'd be happy to help you check the weather! However, I don't have access to real-time weather data. You can check the weather by visiting a weather website or using a weather app on your phone.",
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
    "content": "Can you help me find a weather app?",
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
    "content": "I can help you find weather apps! Here are some popular options:\n\n1. **Weather.com** - Official Weather Channel app\n2. **AccuWeather** - Detailed forecasts and radar\n3. **Dark Sky** - Hyperlocal weather predictions\n4. **Weather Underground** - Community-driven weather data\n\nWould you like me to help you with anything specific about these apps?",
    "message_type": "text",
    "tool_name": "web_search",
    "tool_success": "true",
    "timestamp": "2024-01-15T10:32:08Z",
    "additional_data": {
      "processing_time_ms": 2100,
      "tokens_used": 78,
      "search_results": 4
    }
  }
]
```

**Status Codes**:

- `200 OK`: Messages retrieved successfully
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Conversation not found or doesn't belong to user
- `500 Internal Server Error`: Failed to retrieve messages

### Delete Conversation

Delete a specific conversation and all its messages.

**Endpoint**: `DELETE /conversations/{conversation_id}`

**Path Parameters**:

- `conversation_id` (string): ID of the conversation to delete

**Response**:

```json
{
  "message": "Conversation deleted successfully"
}
```

**Status Codes**:

- `200 OK`: Conversation deleted successfully
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Conversation not found or doesn't belong to user
- `500 Internal Server Error`: Failed to delete conversation

## WebSocket Endpoint

### Real-time Chat WebSocket

Establish a WebSocket connection for real-time chat communication.

**Endpoint**: `WS /ws`

**Query Parameters**:

- `token` (string, required): JWT authentication token

**Connection**:

```javascript
const ws = new WebSocket(
  "wss://api.personalassistant.com/api/v1/chat/ws?token=<jwt_token>"
);

ws.onopen = function (event) {
  console.log("WebSocket connection established");
};

ws.onmessage = function (event) {
  const message = JSON.parse(event.data);
  console.log("Received message:", message);
};

ws.onclose = function (event) {
  console.log("WebSocket connection closed");
};

// Send a message
ws.send(
  JSON.stringify({
    type: "message",
    data: {
      content: "Hello, AI!",
      conversation_id: "conv_abc123def456",
    },
  })
);
```

**WebSocket Message Format**:

```json
{
  "type": "message",
  "data": {
    "content": "Hello, AI!",
    "conversation_id": "conv_abc123def456"
  }
}
```

**WebSocket Response Format**:

```json
{
  "type": "message",
  "data": {
    "id": 1005,
    "conversation_id": "conv_abc123def456",
    "role": "assistant",
    "content": "Hello! How can I help you today?",
    "message_type": "text",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

**Message Types**:

- `message`: Regular chat message
- `typing`: Typing indicator
- `error`: Error message
- `connection`: Connection status

**Status Codes**:

- `101 Switching Protocols`: WebSocket connection established
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Token expired or insufficient permissions

## Message Types and Roles

### Message Roles

- **user**: Messages sent by the user
- **assistant**: Messages sent by the AI agent
- **system**: System messages (not typically exposed to users)

### Message Types

- **text**: Regular text message
- **tool_result**: Result from a tool execution
- **error**: Error message
- **typing**: Typing indicator

### Tool Integration

Messages may include tool execution information:

- `tool_name`: Name of the tool that was executed
- `tool_success`: Whether the tool execution was successful
- `additional_data`: Additional metadata about the message or tool execution

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "detail": "Message content cannot be empty"
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication required"
}
```

### 404 Not Found

```json
{
  "detail": "Conversation not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to send message"
}
```

## Usage Examples

### Send a New Message

```bash
curl -X POST "https://api.personalassistant.com/api/v1/chat/messages" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What are the best practices for time management?",
    "conversation_id": null
  }'
```

### Continue Existing Conversation

```bash
curl -X POST "https://api.personalassistant.com/api/v1/chat/messages" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Can you give me more specific examples?",
    "conversation_id": "conv_abc123def456"
  }'
```

### Get User Conversations

```bash
curl -X GET "https://api.personalassistant.com/api/v1/chat/conversations?page=1&per_page=10" \
  -H "Authorization: Bearer <jwt_token>"
```

### Get Conversation Messages

```bash
curl -X GET "https://api.personalassistant.com/api/v1/chat/conversations/conv_abc123def456/messages?limit=20" \
  -H "Authorization: Bearer <jwt_token>"
```

### Delete Conversation

```bash
curl -X DELETE "https://api.personalassistant.com/api/v1/chat/conversations/conv_abc123def456" \
  -H "Authorization: Bearer <jwt_token>"
```

## Agent Integration

### Tool Execution

The chat system integrates with the agent's tool registry, allowing the AI to:

- Execute various tools (web search, file operations, etc.)
- Provide tool results in messages
- Handle tool errors gracefully

### Focus Areas

Conversations can have focus areas that help the AI understand the context:

- **Planning**: Task and schedule management
- **Information**: Research and data gathering
- **Communication**: Email, messaging, and notifications
- **Productivity**: Workflow optimization and automation

### Step Count

Tracks the number of steps in a conversation, useful for:

- Understanding conversation complexity
- Implementing conversation limits
- Analytics and usage tracking

## Performance Considerations

### Message Processing

- **Typical response time**: 1-3 seconds
- **Tool execution**: Additional 2-5 seconds depending on tool
- **Long conversations**: May have increased processing time

### Rate Limiting

- **Message sending**: 60 requests per minute per user
- **Conversation retrieval**: 200 requests per minute per user
- **WebSocket connections**: 5 concurrent connections per user

### Caching

- **Recent conversations**: Cached for 5 minutes
- **Message history**: Cached for 1 hour
- **Tool results**: Cached for 30 minutes

## Security Features

### Message Validation

- **Content length**: 1-10,000 characters
- **Content filtering**: Basic profanity and spam filtering
- **Rate limiting**: Prevents abuse and spam

### Conversation Privacy

- **User isolation**: Users can only access their own conversations
- **Data encryption**: Messages encrypted in transit and at rest
- **Audit logging**: All chat activities logged for security

### WebSocket Security

- **Token validation**: JWT token required for connection
- **Connection limits**: Maximum 5 concurrent connections per user
- **Message validation**: All WebSocket messages validated

## Data Retention

- **Active conversations**: Retained indefinitely
- **Deleted conversations**: Permanently deleted after 30 days
- **Message history**: Retained for 2 years
- **Chat logs**: Retained for 1 year for debugging and analytics
- **Tool execution logs**: Retained for 6 months

## Integration Notes

### Frontend Integration

- **Real-time updates**: Use WebSocket for live chat
- **Message history**: Implement pagination for large conversations
- **Typing indicators**: Show when AI is processing
- **Error handling**: Gracefully handle connection issues

### Mobile App Integration

- **Offline support**: Cache recent conversations locally
- **Push notifications**: Notify users of new messages
- **Background processing**: Handle WebSocket reconnection
- **Battery optimization**: Implement connection pooling

### Third-party Integration

- **Webhook support**: Send conversation summaries to external systems
- **API keys**: Support for external service integration
- **Custom tools**: Allow users to define custom tools
- **Export functionality**: Export conversations in various formats
