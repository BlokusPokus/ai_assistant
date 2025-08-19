# Data Flow

## Overview

This document contains comprehensive data flow diagrams showing how information moves through the personal assistant application. These diagrams illustrate user interactions, tool execution, memory management, and communication flows.

## User Interaction Flow

### Main Conversation Loop

```mermaid
sequenceDiagram
    participant User
    participant Webhook
    participant AgentRunner
    participant LLMPlanner
    participant ToolRegistry
    participant Tool
    participant Database
    participant Memory
    participant Twilio

    User->>Webhook: Send SMS message
    Webhook->>AgentRunner: Process incoming message
    AgentRunner->>Memory: Retrieve relevant context
    Memory-->>AgentRunner: Return LTM & RAG context
    AgentRunner->>LLMPlanner: Request next action
    LLMPlanner->>AgentRunner: Return ToolCall or FinalAnswer

    alt Tool Execution
        AgentRunner->>ToolRegistry: Execute tool
        ToolRegistry->>Tool: Run specific tool
        Tool->>Database: Query/update data
        Database-->>Tool: Return results
        Tool-->>ToolRegistry: Return tool result
        ToolRegistry-->>AgentRunner: Return formatted result
        AgentRunner->>AgentRunner: Update conversation state
        AgentRunner->>LLMPlanner: Request next action
        LLMPlanner->>AgentRunner: Return FinalAnswer
    else Final Answer
        AgentRunner->>AgentRunner: Update conversation state
    end

    AgentRunner->>Twilio: Send response message
    Twilio->>User: Deliver SMS response
```

### Tool Execution Flow

```mermaid
sequenceDiagram
    participant AgentRunner
    participant LLMPlanner
    participant ToolRegistry
    participant Tool
    participant ExternalAPI
    participant Database
    participant AgentState

    AgentRunner->>LLMPlanner: Request tool selection
    LLMPlanner->>AgentRunner: Return ToolCall with args

    AgentRunner->>ToolRegistry: Execute tool(name, args)
    ToolRegistry->>Tool: Validate and run tool

    alt External API Call
        Tool->>ExternalAPI: Make API request
        ExternalAPI-->>Tool: Return API response
    else Database Operation
        Tool->>Database: Execute query/update
        Database-->>Tool: Return data
    end

    Tool->>Tool: Process results
    Tool-->>ToolRegistry: Return formatted result
    ToolRegistry-->>AgentRunner: Return tool result

    AgentRunner->>AgentState: Add tool result to state
    AgentRunner->>AgentState: Update conversation history
    AgentRunner->>LLMPlanner: Request next action
```

## Memory System Flow

### LTM Retrieval Process

```mermaid
sequenceDiagram
    participant AgentRunner
    participant LTMClient
    participant Database
    participant VectorDB
    participant ContextManager

    AgentRunner->>LTMClient: Request relevant memories
    LTMClient->>Database: Query structured memories
    Database-->>LTMClient: Return memory entries

    LTMClient->>VectorDB: Search semantic memories
    VectorDB-->>LTMClient: Return relevant documents

    LTMClient->>LTMClient: Rank and filter memories
    LTMClient->>ContextManager: Provide memory context
    ContextManager->>ContextManager: Format for injection
    ContextManager-->>AgentRunner: Return context blocks
```

### RAG Document Processing

```mermaid
sequenceDiagram
    participant AgentRunner
    participant RAGRetriever
    participant VectorDB
    participant EmbeddingModel
    participant DocumentStore
    participant ContextManager

    AgentRunner->>RAGRetriever: Request relevant documents
    RAGRetriever->>EmbeddingModel: Generate query embedding
    EmbeddingModel-->>RAGRetriever: Return embedding vector

    RAGRetriever->>VectorDB: Search similar documents
    VectorDB-->>RAGRetriever: Return candidate documents

    RAGRetriever->>DocumentStore: Retrieve full documents
    DocumentStore-->>RAGRetriever: Return document content

    RAGRetriever->>RAGRetriever: Rank and filter documents
    RAGRetriever->>ContextManager: Provide document context
    ContextManager->>ContextManager: Format for injection
    ContextManager-->>AgentRunner: Return context blocks
```

### Context Injection Flow

```mermaid
sequenceDiagram
    participant AgentRunner
    participant LTMClient
    participant RAGRetriever
    participant ContextManager
    participant LLMPlanner

    AgentRunner->>LTMClient: Request LTM context
    LTMClient-->>AgentRunner: Return structured memories

    AgentRunner->>RAGRetriever: Request RAG context
    RAGRetriever-->>AgentRunner: Return document context

    AgentRunner->>ContextManager: Combine memory contexts
    ContextManager->>ContextManager: Format and prioritize
    ContextManager-->>AgentRunner: Return combined context

    AgentRunner->>AgentRunner: Inject context into state
    AgentRunner->>LLMPlanner: Request action with context
    LLMPlanner-->>AgentRunner: Return informed decision
```

## Communication Flow

### SMS Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant Twilio
    participant WebhookHandler
    participant MessageRouter
    participant AgentRunner
    participant ResponseHandler
    participant TwilioClient

    User->>Twilio: Send SMS message
    Twilio->>WebhookHandler: POST webhook with message
    WebhookHandler->>WebhookHandler: Validate webhook signature
    WebhookHandler->>MessageRouter: Route incoming message
    MessageRouter->>AgentRunner: Process user message

    AgentRunner->>AgentRunner: Execute conversation loop
    AgentRunner-->>MessageRouter: Return response
    MessageRouter->>ResponseHandler: Format response
    ResponseHandler->>TwilioClient: Send SMS response
    TwilioClient->>Twilio: POST SMS API call
    Twilio->>User: Deliver SMS response
```

### Webhook Handling

```mermaid
sequenceDiagram
    participant Twilio
    participant WebhookHandler
    participant AuthService
    participant MessageValidator
    participant AgentRunner
    participant ErrorHandler

    Twilio->>WebhookHandler: POST webhook request

    WebhookHandler->>AuthService: Validate request signature
    AuthService-->>WebhookHandler: Return validation result

    alt Valid Request
        WebhookHandler->>MessageValidator: Validate message format
        MessageValidator-->>WebhookHandler: Return validation result
        WebhookHandler->>AgentRunner: Process valid message
        AgentRunner-->>WebhookHandler: Return processing result
        WebhookHandler-->>Twilio: Return 200 OK
    else Invalid Request
        WebhookHandler->>ErrorHandler: Handle invalid request
        ErrorHandler-->>WebhookHandler: Return error response
        WebhookHandler-->>Twilio: Return error status
    end
```

## Tool Execution Flow

### Calendar Tool Flow

```mermaid
sequenceDiagram
    participant AgentRunner
    participant CalendarTool
    participant GoogleCalendarAPI
    participant Database
    participant AgentState

    AgentRunner->>CalendarTool: Execute calendar operation
    CalendarTool->>CalendarTool: Parse tool arguments

    alt Create Event
        CalendarTool->>GoogleCalendarAPI: Create calendar event
        GoogleCalendarAPI-->>CalendarTool: Return event details
    else Query Events
        CalendarTool->>GoogleCalendarAPI: Query calendar events
        GoogleCalendarAPI-->>CalendarTool: Return event list
    else Update Event
        CalendarTool->>GoogleCalendarAPI: Update existing event
        GoogleCalendarAPI-->>CalendarTool: Return updated event
    end

    CalendarTool->>Database: Store event metadata
    Database-->>CalendarTool: Confirm storage
    CalendarTool->>CalendarTool: Format result for agent
    CalendarTool-->>AgentRunner: Return formatted result
    AgentRunner->>AgentState: Update conversation state
```

### Email Tool Flow

```mermaid
sequenceDiagram
    participant AgentRunner
    participant EmailTool
    participant GmailAPI
    participant Database
    participant AgentState

    AgentRunner->>EmailTool: Execute email operation
    EmailTool->>EmailTool: Parse tool arguments

    alt Send Email
        EmailTool->>GmailAPI: Send email message
        GmailAPI-->>EmailTool: Return send confirmation
    else Read Emails
        EmailTool->>GmailAPI: Query email messages
        GmailAPI-->>EmailTool: Return email list
    else Search Emails
        EmailTool->>GmailAPI: Search email content
        GmailAPI-->>EmailTool: Return search results
    end

    EmailTool->>Database: Store email metadata
    Database-->>EmailTool: Confirm storage
    EmailTool->>EmailTool: Format result for agent
    EmailTool-->>AgentRunner: Return formatted result
    AgentRunner->>AgentState: Update conversation state
```

## State Management Flow

### Conversation State Updates

```mermaid
sequenceDiagram
    participant AgentRunner
    participant AgentState
    participant Memory
    participant Database
    participant LLMPlanner

    AgentRunner->>AgentState: Add user message
    AgentState->>AgentState: Update conversation history

    AgentRunner->>Memory: Retrieve context
    Memory-->>AgentRunner: Return memory context
    AgentRunner->>AgentState: Inject memory context

    AgentRunner->>LLMPlanner: Request action
    LLMPlanner-->>AgentRunner: Return decision

    alt Tool Execution
        AgentRunner->>AgentState: Add tool call
        AgentRunner->>AgentState: Add tool result
    else Final Answer
        AgentRunner->>AgentState: Add assistant response
    end

    AgentState->>Database: Persist state changes
    Database-->>AgentState: Confirm persistence
    AgentState->>AgentState: Update step count
```

### Memory Storage Flow

```mermaid
sequenceDiagram
    participant AgentRunner
    participant MemoryManager
    participant LTMClient
    participant RAGClient
    participant Database
    participant VectorDB

    AgentRunner->>MemoryManager: Store conversation memory
    MemoryManager->>MemoryManager: Extract key information

    alt Structured Memory
        MemoryManager->>LTMClient: Store structured memory
        LTMClient->>Database: Store memory entry
        Database-->>LTMClient: Confirm storage
        LTMClient-->>MemoryManager: Return storage result
    else Document Memory
        MemoryManager->>RAGClient: Store document memory
        RAGClient->>VectorDB: Store document embedding
        VectorDB-->>RAGClient: Confirm storage
        RAGClient-->>MemoryManager: Return storage result
    end

    MemoryManager-->>AgentRunner: Confirm memory storage
```

## Error Handling Flow

### Tool Execution Error Handling

```mermaid
sequenceDiagram
    participant AgentRunner
    participant ToolRegistry
    participant Tool
    participant ErrorHandler
    participant LLMPlanner

    AgentRunner->>ToolRegistry: Execute tool
    ToolRegistry->>Tool: Run tool

    alt Tool Success
        Tool-->>ToolRegistry: Return result
        ToolRegistry-->>AgentRunner: Return formatted result
    else Tool Error
        Tool->>ErrorHandler: Handle tool error
        ErrorHandler->>ErrorHandler: Log error details
        ErrorHandler-->>Tool: Return error response
        Tool-->>ToolRegistry: Return error result
        ToolRegistry-->>AgentRunner: Return error message
    end

    AgentRunner->>LLMPlanner: Request next action with error context
    LLMPlanner-->>AgentRunner: Return recovery action
```

### Communication Error Handling

```mermaid
sequenceDiagram
    participant Twilio
    participant WebhookHandler
    participant AgentRunner
    participant ErrorHandler
    participant RetryQueue

    Twilio->>WebhookHandler: Send webhook

    alt Processing Success
        WebhookHandler->>AgentRunner: Process message
        AgentRunner-->>WebhookHandler: Return response
        WebhookHandler-->>Twilio: Return 200 OK
    else Processing Error
        WebhookHandler->>ErrorHandler: Handle processing error
        ErrorHandler->>ErrorHandler: Log error details
        ErrorHandler->>RetryQueue: Queue for retry
        ErrorHandler-->>WebhookHandler: Return error response
        WebhookHandler-->>Twilio: Return error status
    end
```

## Notes

### Key Flow Characteristics

1. **Asynchronous Processing**: Most operations are async to handle high concurrency
2. **Error Resilience**: Comprehensive error handling at each step
3. **State Consistency**: State updates are atomic and consistent
4. **Memory Integration**: Context is injected at multiple points
5. **Tool Abstraction**: Tools are executed through a common interface

### Performance Considerations

- Database connections are pooled
- External API calls include timeouts
- Memory retrieval is cached when possible
- Tool execution is parallelized where appropriate
- State updates are batched for efficiency

### Security Measures

- All external API calls are authenticated
- Webhook signatures are validated
- Sensitive data is encrypted
- Error messages don't expose internal details
- Rate limiting is applied to prevent abuse

This data flow architecture ensures reliable, secure, and efficient processing of user interactions while maintaining system integrity and performance.
