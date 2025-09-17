# Agent Tools Documentation

This document provides comprehensive documentation for all agent tools in the Personal Assistant TDAH system.

## Overview

The agent tools system provides a modular, extensible framework for integrating various services and capabilities into the AI agent. Tools are organized by category and provide specific functionality for different user needs.

## Tool Architecture

### Base Tool System (`src/personal_assistant/tools/base.py`)

The foundation of the tool system with the `Tool` and `ToolRegistry` classes.

**Tool Class**:

- `name`: Tool identifier
- `func`: Function to execute
- `description`: Tool description for LLM
- `parameters`: JSON schema for parameters
- `category`: Tool category for organization
- `_last_user_intent`: Context for error handling

**Key Methods**:

- `set_category(category: str)`: Set tool category
- `set_user_intent(user_intent: str)`: Set user intent for context
- `validate_args(kwargs: Dict[str, Any])`: Validate parameters
- `execute(**kwargs)`: Execute tool with validation

**ToolRegistry Class**:

- Central registry for all tools
- Schema generation for LLM
- Safe execution with error handling
- Tool discovery and management

## Tool Categories

### Email Tools (`src/personal_assistant/tools/emails/`)

Comprehensive email management through Microsoft Graph API.

**EmailTool Class**:

- OAuth-based authentication
- Microsoft Graph integration
- Batch processing support
- Error handling and validation

**Available Tools**:

#### `read_emails`

- **Purpose**: Read recent emails from inbox
- **Parameters**:
  - `count`: Number of emails to fetch (default: 10)
  - `batch_size`: Emails per batch (default: 10)
- **Features**: Batch processing, error handling, OAuth authentication

#### `send_email`

- **Purpose**: Send emails to recipients
- **Parameters**:
  - `to_recipients`: Comma-separated email addresses
  - `subject`: Email subject line
  - `body`: Email content
  - `is_html`: HTML format flag (default: false)
- **Features**: Recipient validation, HTML support, OAuth authentication

#### `delete_email`

- **Purpose**: Delete email by ID
- **Parameters**:
  - `email_id`: Message ID to delete
- **Features**: ID validation, error handling

#### `get_email_content`

- **Purpose**: Get full email content
- **Parameters**:
  - `email_id`: Message ID to retrieve
- **Features**: Content cleaning, HTML processing

#### `get_sent_emails`

- **Purpose**: Read sent emails
- **Parameters**:
  - `count`: Number of emails (default: 10)
  - `batch_size`: Emails per batch (default: 10)
- **Features**: Sent items folder access, batch processing

#### `search_emails`

- **Purpose**: Search emails by query
- **Parameters**:
  - `query`: Search terms
  - `count`: Max results (default: 20)
  - `date_from`: Start date (YYYY-MM-DD)
  - `date_to`: End date (YYYY-MM-DD)
  - `folder`: Folder to search (default: inbox)
- **Features**: Native Graph API search, date filtering, client-side sorting

#### `move_email`

- **Purpose**: Move email between folders
- **Parameters**:
  - `email_id`: Message ID to move
  - `destination_folder`: Target folder name
- **Features**: Folder mapping, standard folder support

**Authentication**:

- OAuth 2.0 with Microsoft Graph
- Automatic token refresh
- User-specific authentication
- Integration service management

### Calendar Tools (`src/personal_assistant/tools/calendar/`)

Calendar management through Microsoft Graph API.

**CalendarTool Class**:

- Event creation and management
- Calendar view functionality
- Attendee support
- Error handling

**Available Tools**:

#### `view_calendar_events`

- **Purpose**: View upcoming calendar events
- **Parameters**:
  - `count`: Number of events to fetch
  - `days`: Days to look ahead
- **Features**: Date range filtering, event parsing

#### `create_calendar_event`

- **Purpose**: Create new calendar events
- **Parameters**:
  - `subject`: Event title
  - `start_time`: Start time (YYYY-MM-DD HH:MM)
  - `duration`: Duration in minutes
  - `location`: Event location
  - `attendees`: Comma-separated email addresses
- **Features**: Time validation, attendee management, location support

#### `delete_calendar_event`

- **Purpose**: Delete calendar events
- **Parameters**:
  - `event_id`: Event ID to delete
- **Features**: Event details retrieval, confirmation messages

**Features**:

- Microsoft Graph integration
- Time zone handling
- Attendee management
- Event validation
- Error handling with specific messages

### Enhanced Notes Tools (`src/personal_assistant/tools/notes/`)

AI-powered note management with Notion integration.

**EnhancedNotesTool Class**:

- LLM-powered content enhancement
- Notion API integration
- User-specific workspaces
- Intelligent search and analysis

**Available Tools**:

#### `create_enhanced_note`

- **Purpose**: Create AI-enhanced notes
- **Parameters**:
  - `content`: Basic content/ideas (required)
  - `title`: Note title (optional)
  - `note_type`: Type (meeting, project, personal, etc.)
  - `auto_tags`: Generate tags automatically (default: true)
- **Features**:
  - LLM content enhancement
  - Automatic categorization
  - Tag generation
  - Metadata inclusion

#### `smart_search_notes`

- **Purpose**: Search notes intelligently
- **Parameters**:
  - `query`: Search query (required)
  - `note_type`: Filter by type (optional)
  - `tags`: Filter by tags (optional)
  - `limit`: Max results (default: 20)
- **Features**:
  - Notion native search
  - LLM-based relevance selection
  - Content preview
  - Search statistics

#### `enhance_existing_note`

- **Purpose**: Enhance existing notes
- **Parameters**:
  - `search_query`: Search to find note (optional)
  - `page_id`: Specific page ID (optional)
  - `enhancement_type`: Type of enhancement (default: all)
- **Features**:
  - Content enhancement
  - Structure improvement
  - Tag suggestions
  - Action item extraction

#### `get_note_intelligence`

- **Purpose**: Get AI insights for notes
- **Parameters**:
  - `page_id`: Page ID to analyze (required)
- **Features**:
  - Key topic extraction
  - Action item identification
  - Structure suggestions
  - Confidence scoring

**LLM Integration**:

- Gemini LLM for content enhancement
- Specialized prompts for different note types
- Confidence scoring
- Action item extraction
- Topic analysis

### Reminder Tools (`src/personal_assistant/tools/reminders/`)

Task and reminder management system.

**ReminderTool Class**:

- Task creation and management
- Scheduling support
- Notification channels
- Status tracking

**Available Tools**:

#### `create_reminder`

- **Purpose**: Create new reminders
- **Parameters**:
  - `title`: Reminder title
  - `description`: Reminder description
  - `due_date`: Due date/time
  - `priority`: Priority level
  - `notification_channels`: Notification methods
- **Features**: Date validation, priority handling, multi-channel notifications

#### `get_reminders`

- **Purpose**: Retrieve reminders
- **Parameters**:
  - `status`: Filter by status
  - `priority`: Filter by priority
  - `limit`: Max results
- **Features**: Status filtering, priority sorting, pagination

#### `update_reminder`

- **Purpose**: Update existing reminders
- **Parameters**:
  - `reminder_id`: Reminder ID
  - `updates`: Fields to update
- **Features**: Partial updates, validation, status tracking

#### `delete_reminder`

- **Purpose**: Delete reminders
- **Parameters**:
  - `reminder_id`: Reminder ID to delete
- **Features**: Confirmation, cleanup, audit trail

### LTM (Long-Term Memory) Tools (`src/personal_assistant/tools/ltm/`)

Memory management and retrieval system.

**LTMTool Class**:

- Memory storage and retrieval
- Context-aware search
- Memory categorization
- Learning optimization

**Available Tools**:

#### `store_memory`

- **Purpose**: Store information in long-term memory
- **Parameters**:
  - `content`: Memory content
  - `tags`: Memory tags
  - `importance`: Importance level
  - `context`: Additional context
- **Features**: Tag-based organization, importance scoring, context preservation

#### `retrieve_memories`

- **Purpose**: Retrieve relevant memories
- **Parameters**:
  - `query`: Search query
  - `tags`: Filter by tags
  - `limit`: Max results
  - `importance_threshold`: Minimum importance
- **Features**: Semantic search, tag filtering, relevance scoring

#### `update_memory`

- **Purpose**: Update existing memories
- **Parameters**:
  - `memory_id`: Memory ID
  - `updates`: Fields to update
- **Features**: Partial updates, validation, version tracking

#### `delete_memory`

- **Purpose**: Delete memories
- **Parameters**:
  - `memory_id`: Memory ID to delete
- **Features**: Soft deletion, cleanup, audit trail

### Internet Tools (`src/personal_assistant/tools/internet/`)

Web search and information retrieval.

**InternetTool Class**:

- Web search capabilities
- Information extraction
- Content summarization
- Source validation

**Available Tools**:

#### `web_search`

- **Purpose**: Search the web
- **Parameters**:
  - `query`: Search query
  - `num_results`: Number of results
  - `date_range`: Date filter
  - `site`: Site-specific search
- **Features**: Multiple search engines, result filtering, source tracking

#### `get_webpage_content`

- **Purpose**: Extract webpage content
- **Parameters**:
  - `url`: Webpage URL
  - `extract_type`: Content extraction method
- **Features**: Content cleaning, text extraction, metadata retrieval

#### `summarize_content`

- **Purpose**: Summarize web content
- **Parameters**:
  - `url`: Content URL
  - `summary_length`: Length of summary
- **Features**: AI-powered summarization, key point extraction

### YouTube Tools (`src/personal_assistant/tools/youtube/`)

YouTube integration and video management.

**YouTubeTool Class**:

- Video search and retrieval
- Playlist management
- Channel information
- OAuth integration

**Available Tools**:

#### `search_youtube_videos`

- **Purpose**: Search YouTube videos
- **Parameters**:
  - `query`: Search query
  - `max_results`: Max results
  - `order`: Sort order
  - `published_after`: Date filter
- **Features**: Advanced search filters, result sorting, metadata extraction

#### `get_video_details`

- **Purpose**: Get video information
- **Parameters**:
  - `video_id`: YouTube video ID
- **Features**: Detailed metadata, statistics, comments

#### `create_playlist`

- **Purpose**: Create YouTube playlists
- **Parameters**:
  - `title`: Playlist title
  - `description`: Playlist description
  - `privacy`: Privacy setting
- **Features**: OAuth authentication, privacy controls

### Planning Tools (`src/personal_assistant/tools/planning/`)

AI-powered task planning and execution.

**LLMPlannerTool Class**:

- Intelligent task planning
- Tool recommendation
- ADHD-friendly strategies
- Progress tracking

**Available Tools**:

#### `create_plan`

- **Purpose**: Create execution plans
- **Parameters**:
  - `user_request`: User's request
  - `planning_style`: Planning approach
  - `available_tools`: Available tools
- **Features**:
  - Step-by-step planning
  - Tool recommendations
  - Time estimates
  - Progress tracking

#### `get_tool_guidelines`

- **Purpose**: Get tool-specific guidance
- **Parameters**:
  - `tool_names`: Tools to get guidelines for
- **Features**: Best practices, usage examples, troubleshooting

#### `identify_relevant_tools`

- **Purpose**: Identify relevant tools for tasks
- **Parameters**:
  - `user_request`: User's request
  - `available_tools`: Available tools
- **Features**: LLM-based tool selection, capability matching

### AI Scheduler Tools (`src/personal_assistant/tools/ai_scheduler/`)

Intelligent task scheduling and execution.

**TaskScheduler Class**:

- AI task management
- Scheduling algorithms
- Background execution
- Performance monitoring

**Available Tools**:

#### `create_ai_task`

- **Purpose**: Create AI-managed tasks
- **Parameters**:
  - `title`: Task title
  - `description`: Task description
  - `schedule_type`: Scheduling type
  - `schedule_config`: Schedule configuration
  - `notification_channels`: Notification methods
- **Features**: Flexible scheduling, notification management, status tracking

#### `get_task_status`

- **Purpose**: Get task execution status
- **Parameters**:
  - `task_id`: Task ID
- **Features**: Real-time status, execution history, performance metrics

#### `execute_task`

- **Purpose**: Execute AI tasks
- **Parameters**:
  - `task_id`: Task ID to execute
- **Features**: Background execution, error handling, result tracking

## Tool Registry System

### Tool Registration

Tools are registered in the main registry (`src/personal_assistant/tools/__init__.py`):

```python
def create_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    # Register email tools
    email_tool = EmailTool()
    for tool in email_tool:
        tool.set_category("Email")
        registry.register(tool)

    # Register other tools...
    return registry
```

### Tool Categories

Tools are organized into categories:

- **Email**: Email management and communication
- **Calendar**: Calendar and event management
- **EnhancedNotes**: AI-powered note management
- **Reminders**: Task and reminder management
- **LTM**: Long-term memory management
- **Internet**: Web search and information retrieval
- **YouTube**: YouTube integration
- **Planning**: AI-powered planning and execution
- **AIScheduler**: Intelligent task scheduling

### Tool Discovery

The registry provides:

- Tool discovery by category
- Schema generation for LLM
- Parameter validation
- Error handling
- Execution tracking

## Tool Execution Framework

### Execution Flow

1. **Tool Selection**: LLM selects appropriate tools
2. **Parameter Validation**: Validate input parameters
3. **Authentication**: Handle OAuth and API authentication
4. **Execution**: Execute tool function
5. **Error Handling**: Handle and report errors
6. **Result Formatting**: Format results for user

### Error Handling

All tools implement comprehensive error handling:

- Parameter validation errors
- Authentication failures
- API errors
- Network timeouts
- Rate limiting
- User-friendly error messages

### Authentication

Tools support multiple authentication methods:

- OAuth 2.0 for external services
- API key authentication
- User-specific authentication
- Automatic token refresh

## Tool Development Guidelines

### Creating New Tools

1. **Inherit from Base Tool**: Use the `Tool` class
2. **Define Parameters**: Create JSON schema for parameters
3. **Implement Function**: Create the main tool function
4. **Add Error Handling**: Implement comprehensive error handling
5. **Add Authentication**: Handle service authentication
6. **Register Tool**: Add to tool registry
7. **Write Tests**: Create unit and integration tests
8. **Document Tool**: Add comprehensive documentation

### Tool Structure

```python
class NewTool:
    def __init__(self):
        self.tool_name = Tool(
            name="tool_name",
            func=self.tool_function,
            description="Tool description",
            parameters={
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            }
        )

    async def tool_function(self, param1: str, user_id: int = None) -> Dict[str, Any]:
        try:
            # Tool implementation
            return {"success": True, "result": "..."}
        except Exception as e:
            return {"error": str(e)}

    def __iter__(self):
        return iter([self.tool_name])
```

### Best Practices

1. **Parameter Validation**: Always validate input parameters
2. **Error Handling**: Provide clear, actionable error messages
3. **Authentication**: Handle authentication gracefully
4. **Rate Limiting**: Respect API rate limits
5. **Logging**: Log important operations and errors
6. **Documentation**: Document all parameters and behaviors
7. **Testing**: Write comprehensive tests
8. **User Experience**: Provide helpful feedback and guidance

## Tool Integration

### LLM Integration

Tools integrate with the LLM through:

- Function calling schemas
- Parameter descriptions
- Error handling
- Result formatting
- Context preservation

### Service Integration

Tools integrate with external services:

- Microsoft Graph API (Email, Calendar)
- Notion API (Notes)
- YouTube API (Video management)
- Web search APIs (Internet tools)
- Custom APIs (Internal services)

### Database Integration

Tools integrate with the database:

- User-specific data
- Tool execution logs
- Performance metrics
- Error tracking
- Audit trails

## Performance Considerations

### Optimization Strategies

1. **Caching**: Cache frequently accessed data
2. **Batch Processing**: Process multiple items together
3. **Async Operations**: Use async/await for I/O operations
4. **Connection Pooling**: Reuse database connections
5. **Rate Limiting**: Respect API limits
6. **Error Recovery**: Implement retry mechanisms

### Monitoring

Tools include monitoring capabilities:

- Execution time tracking
- Success/failure rates
- Error logging
- Performance metrics
- Usage statistics

## Security Considerations

### Authentication Security

- OAuth 2.0 implementation
- Token refresh mechanisms
- Secure credential storage
- User isolation
- Permission validation

### Data Security

- Input sanitization
- Output validation
- Secure API communication
- Data encryption
- Access control

### Error Security

- No sensitive data in error messages
- Secure error logging
- User-friendly error messages
- Audit trail maintenance

## Future Enhancements

### Planned Features

- Additional OAuth providers
- Advanced caching strategies
- Real-time tool execution
- Tool performance analytics
- Automated tool testing
- Tool marketplace

### Integration Roadmap

- More external service integrations
- Advanced AI capabilities
- Real-time collaboration
- Mobile app integration
- Third-party tool support
- Custom tool development framework
