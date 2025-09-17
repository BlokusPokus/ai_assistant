# Backend Services Documentation

This document provides comprehensive documentation for all backend services in the Personal Assistant TDAH system.

## Overview

The backend services are organized into several key areas:

- **Core Services**: Agent orchestration and conversation management
- **Authentication Services**: User authentication, authorization, and security
- **OAuth Services**: External provider integration management
- **SMS Router Services**: SMS message processing and routing
- **AI Scheduler Services**: Task scheduling and execution
- **Background Services**: Asynchronous processing and optimization

## Core Services

### AgentCore (`src/personal_assistant/core/agent.py`)

The main orchestrator that coordinates all agent operations and services.

**Key Responsibilities**:

- Initialize and coordinate all service components
- Manage agent execution loop
- Handle user input processing
- Coordinate context retrieval and tool execution
- Manage conversation state and memory

**Key Methods**:

- `__init__(tools=None, llm=None)`: Initialize agent with tools and LLM
- `run(user_input: str, user_id: int) -> str`: Main execution method
- `_initialize_services()`: Initialize all service components

**Service Dependencies**:

- `ContextService`: Context retrieval and optimization
- `ConversationService`: Conversation management
- `BackgroundService`: Background processing
- `ContextInjectionService`: Context injection
- `ToolExecutionService`: Tool execution
- `AgentLoopService`: Agent loop management

### ContextService (`src/personal_assistant/core/services/context_service.py`)

Handles context retrieval from both LTM (Long-Term Memory) and RAG (Retrieval-Augmented Generation) systems.

**Key Responsibilities**:

- Retrieve relevant context from LTM system
- Query knowledge base for RAG context
- Optimize context with dynamic context manager
- Provide fallback mechanisms for context retrieval

**Key Methods**:

- `get_enhanced_context(user_id: int, user_input: str, agent_state: AgentState) -> Dict[str, Any]`
- `_get_ltm_context(user_id: int, user_input: str, agent_state: AgentState) -> Optional[str]`
- `_get_rag_context(user_id: int, user_input: str) -> list`

**Features**:

- Enhanced LTM retriever with smart context optimization
- Legacy LTM fallback for reliability
- RAG context integration
- Error handling and logging

### ConversationService (`src/personal_assistant/core/services/conversation_service.py`)

Manages conversation lifecycle and agent state loading.

**Key Responsibilities**:

- Create new conversations
- Resume existing conversations
- Load agent state from storage
- Manage conversation timestamps and expiration

**Key Methods**:

- `get_conversation_context(user_id: int, user_input: str) -> Tuple[str, AgentState]`

**Features**:

- Automatic conversation creation
- Smart conversation resumption logic
- State persistence and loading
- Conversation expiration handling

### BackgroundService (`src/personal_assistant/core/services/background_service.py`)

Handles all background processing after response is returned to the user.

**Key Responsibilities**:

- Process async operations after user response
- Optimize LTM learning
- Manage memory lifecycle
- Handle storage integration

**Key Methods**:

- `process_async(user_id: int, user_input: str, response: str, updated_state: AgentState, conversation_id: str, start_time: float)`

**Features**:

- Asynchronous processing
- LTM optimization
- Memory lifecycle management
- Performance logging

### ContextInjectionService (`src/personal_assistant/core/services/context_injection_service.py`)

Handles context injection into agent prompts and responses.

**Key Responsibilities**:

- Inject relevant context into prompts
- Manage context formatting
- Optimize context for LLM consumption

### ToolExecutionService (`src/personal_assistant/core/services/tool_execution_service.py`)

Manages tool execution within the agent loop.

**Key Responsibilities**:

- Execute agent tools
- Handle tool results
- Manage tool state

### AgentLoopService (`src/personal_assistant/core/services/agent_loop_service.py`)

Manages the main agent execution loop.

**Key Responsibilities**:

- Coordinate agent planning
- Manage tool execution
- Handle agent state transitions

## Authentication Services

### PermissionService (`src/personal_assistant/auth/permission_service.py`)

Core service for Role-Based Access Control (RBAC) and permission management.

**Key Responsibilities**:

- Check user permissions for resources
- Manage role assignments and inheritance
- Handle audit logging
- Cache permission results for performance

**Key Methods**:

- `check_permission(user_id: int, resource_type: str, action: str, resource_id: Optional[int] = None, context: Optional[Dict[str, Any]] = None) -> bool`
- `get_user_roles(user_id: int) -> List[Role]`
- `grant_role(user_id: int, role_name: str, granted_by: int, is_primary: bool = False, expires_at: Optional[datetime] = None) -> bool`
- `revoke_role(user_id: int, role_name: str, revoked_by: int) -> bool`
- `log_access_attempt(user_id: int, resource_type: str, action: str, resource_id: Optional[int], granted: bool, roles_checked: List[str], ip_address: Optional[str] = None, user_agent: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None`

**Features**:

- Role inheritance support
- Permission caching (5-minute TTL)
- Comprehensive audit logging
- Ownership checks for user resources
- Performance optimization

**Cache Management**:

- In-memory permission cache
- Role cache with timestamps
- Automatic cache invalidation
- Cache cleanup methods

## OAuth Services

### OAuthManager (`src/personal_assistant/oauth/oauth_manager.py`)

Main orchestrator for all OAuth operations across different providers.

**Key Responsibilities**:

- Manage OAuth provider registry
- Handle OAuth flow initiation and completion
- Manage token refresh and revocation
- Coordinate integration lifecycle

**Supported Providers**:

- Google OAuth
- Microsoft OAuth
- Notion OAuth
- YouTube OAuth

**Key Methods**:

- `get_provider(provider_name: str) -> BaseOAuthProvider`
- `initiate_oauth_flow(db: AsyncSession, user_id: int, provider_name: str, scopes: List[str], redirect_uri: Optional[str] = None, **kwargs) -> Dict[str, Any]`
- `handle_oauth_callback(db: AsyncSession, state_token: str, authorization_code: str, provider_name: str, **kwargs) -> Dict[str, Any]`
- `refresh_integration_tokens(db: AsyncSession, integration_id: int) -> bool`
- `revoke_integration(db: AsyncSession, integration_id: int, reason: Optional[str] = None) -> bool`
- `get_user_integrations(db: AsyncSession, user_id: int, provider: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]`

**Features**:

- Provider configuration management
- State token validation for CSRF protection
- Token storage and refresh
- Integration status management
- Security event logging
- Prometheus metrics integration

**Service Dependencies**:

- `OAuthTokenService`: Token management
- `OAuthConsentService`: Consent tracking
- `OAuthIntegrationService`: Integration lifecycle
- `OAuthSecurityService`: Security and audit

## SMS Router Services

### SMSRoutingEngine (`src/personal_assistant/sms_router/services/routing_engine.py`)

Main orchestrator for SMS message processing and routing.

**Key Responsibilities**:

- Route incoming SMS messages to appropriate users
- Process messages through the pipeline
- Integrate with AI agent for responses
- Track performance metrics

**Key Methods**:

- `route_sms(from_phone: str, message_body: str, message_sid: str) -> Any`

**Service Dependencies**:

- `UserIdentificationService`: User identification by phone number
- `MessageProcessor`: Message processing and validation
- `ResponseFormatter`: Response formatting
- `AgentIntegrationService`: AI agent integration

**Performance Tracking**:

- Total messages processed
- Successful routes count
- Failed routes count
- Average processing time

### MessageProcessor (`src/personal_assistant/sms_router/services/message_processor.py`)

Service for processing and validating SMS messages.

**Key Responsibilities**:

- Clean and normalize message content
- Detect spam and malicious content
- Extract commands from messages
- Analyze message metadata

**Key Methods**:

- `process_message(message: str, user_info: Dict[str, Any]) -> Dict[str, Any]`
- `validate_message_length(message: str, max_length: int = 160) -> bool`
- `get_message_metadata(message: str) -> Dict[str, Any]`

**Features**:

- Spam detection with configurable patterns
- Command extraction (/, !, : patterns)
- SMS abbreviation normalization
- Basic sentiment analysis
- Language detection
- Message length validation

**Spam Detection**:

- Pattern-based spam scoring
- Excessive caps detection
- Punctuation analysis
- Length-based filtering

**Command Processing**:

- Support for multiple command formats
- Built-in help, status, info, clear commands
- Extensible command system

## AI Scheduler Services

### TaskScheduler (`src/personal_assistant/tools/ai_scheduler/core/scheduler.py`)

Main scheduler for AI task processing and execution.

**Key Responsibilities**:

- Start Celery workers for task processing
- Manage periodic task scheduling
- Provide task statistics and monitoring
- Handle task creation and management

**Key Methods**:

- `start_worker(loglevel: str = "INFO") -> None`
- `start_beat(loglevel: str = "INFO") -> None`
- `test_connection() -> Dict[str, Any]`
- `get_status() -> Dict[str, Any]`
- `get_task_statistics() -> Dict[str, Any]`
- `create_test_task() -> Dict[str, Any]`

**Features**:

- Celery integration for distributed task processing
- Periodic task scheduling with Celery Beat
- Task statistics and monitoring
- Connection testing and health checks
- Test task creation for debugging

**Task Types**:

- Reminders
- Periodic tasks
- One-time tasks
- Notification tasks

**Service Dependencies**:

- `AITaskManager`: Task database operations
- Celery workers system
- Background task processing

## Service Architecture Patterns

### Service Initialization

All services follow a consistent initialization pattern:

```python
class ServiceName:
    def __init__(self, dependencies):
        self.dependency = dependency
        self.logger = get_logger("service_name")
        # Initialize service components
```

### Error Handling

Services implement comprehensive error handling:

- Structured logging with appropriate log levels
- Graceful degradation when dependencies fail
- Fallback mechanisms for critical operations
- Error propagation with context

### Performance Optimization

Services include performance optimizations:

- Caching mechanisms (PermissionService)
- Connection pooling (Database services)
- Async/await patterns for I/O operations
- Metrics collection and monitoring

### Security Considerations

All services implement security best practices:

- Input validation and sanitization
- Permission checking and audit logging
- Secure token handling
- CSRF protection (OAuth)
- Rate limiting and abuse prevention

## Service Dependencies

### Core Service Dependencies

```
AgentCore
├── ContextService
│   ├── SmartLTMRetriever
│   └── DynamicContextManager
├── ConversationService
│   └── StorageIntegrationManager
├── BackgroundService
│   ├── LTMLearningManager
│   └── EnhancedMemoryLifecycleManager
├── ContextInjectionService
├── ToolExecutionService
└── AgentLoopService
```

### Authentication Service Dependencies

```
PermissionService
├── AsyncSession (Database)
├── Role Model
├── UserRole Model
└── AccessAuditLog Model
```

### OAuth Service Dependencies

```
OAuthManager
├── OAuthTokenService
├── OAuthConsentService
├── OAuthIntegrationService
├── OAuthSecurityService
└── Provider-specific implementations
```

### SMS Router Service Dependencies

```
SMSRoutingEngine
├── UserIdentificationService
├── MessageProcessor
├── ResponseFormatter
└── AgentIntegrationService
```

## Configuration and Environment

### Service Configuration

Services are configured through environment variables and settings:

- Database connections
- OAuth provider credentials
- SMS service configuration
- Logging levels and destinations
- Cache TTL settings

### Environment Variables

Key environment variables for services:

```bash
# Database
DATABASE_URL=postgresql://...

# OAuth Providers
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
MICROSOFT_OAUTH_CLIENT_ID=...
MICROSOFT_OAUTH_CLIENT_SECRET=...

# SMS Service
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...

# Redis (for caching and background tasks)
REDIS_URL=redis://...

# Logging
LOG_LEVEL=INFO
```

## Monitoring and Observability

### Metrics Collection

Services integrate with Prometheus for metrics:

- OAuth operation metrics
- SMS routing performance
- Task execution statistics
- Error rates and response times

### Logging

Structured logging across all services:

- Service-specific loggers
- Performance metrics logging
- Error tracking and debugging
- Audit trail maintenance

### Health Checks

Services provide health check endpoints:

- Database connectivity
- External service availability
- Cache system status
- Background task processing

## Development Guidelines

### Service Development

When creating new services:

1. Follow the established initialization pattern
2. Implement comprehensive error handling
3. Add appropriate logging and metrics
4. Include health check methods
5. Write unit tests for all methods
6. Document all public methods and properties

### Testing

Services should include:

- Unit tests for individual methods
- Integration tests for service interactions
- Mock external dependencies
- Performance tests for critical paths
- Error condition testing

### Documentation

Service documentation should include:

- Purpose and responsibilities
- Key methods and their parameters
- Dependencies and requirements
- Configuration options
- Error handling behavior
- Performance characteristics

## Future Enhancements

### Planned Improvements

- Service mesh architecture for microservices
- Advanced caching strategies
- Real-time service monitoring
- Automated scaling and load balancing
- Enhanced security features
- Service discovery and registration

### Integration Roadmap

- Additional OAuth providers
- Advanced SMS routing algorithms
- Machine learning for context optimization
- Real-time collaboration features
- Mobile app service integration
- Third-party API integrations
