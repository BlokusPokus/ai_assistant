# Component Relationships

## Overview

This document contains class diagrams and component relationship diagrams showing the internal structure of the personal assistant application. These diagrams illustrate class hierarchies, interface contracts, and component dependencies.

## Core Class Diagram

### Main Application Classes

```mermaid
classDiagram
    class AgentRunner {
        -tools: ToolRegistry
        -planner: LLMPlanner
        -max_steps: int
        -current_state: AgentState
        +set_context(agent_state, ltm_context, rag_context)
        +run(user_input) async
    }

    class LLMPlanner {
        -llm_client: LLMClient
        -tools: ToolRegistry
        +choose_action(state) Action
        +force_finish(state) str
    }

    class AgentState {
        -conversation_history: List[Dict]
        -memory_context: List[Dict]
        -step_count: int
        +add_tool_result(tool_call, result)
        +add_user_message(content)
        +add_assistant_message(content)
    }

    class ToolRegistry {
        -tools: Dict[str, Tool]
        +register_tool(tool)
        +get_tool(name) Tool
        +list_tools() List[str]
        +run_tool(name, **args) async
    }

    class Tool {
        <<abstract>>
        +name: str
        +description: str
        +parameters: Dict
        +execute(**args) async
    }

    class LLMClient {
        <<interface>>
        +generate_response(prompt) async
        +generate_embedding(text) async
    }

    AgentRunner --> LLMPlanner
    AgentRunner --> ToolRegistry
    AgentRunner --> AgentState
    LLMPlanner --> LLMClient
    ToolRegistry --> Tool
```

### Tool System Classes

```mermaid
classDiagram
    class Tool {
        <<abstract>>
        +name: str
        +description: str
        +parameters: Dict
        +execute(**args) async
    }

    class CalendarTool {
        -calendar_client: CalendarClient
        +execute(**args) async
        +create_event(event_data)
        +get_events(time_range)
        +update_event(event_id, updates)
    }

    class EmailTool {
        -email_client: EmailClient
        +execute(**args) async
        +send_email(to, subject, body)
        +read_emails(query)
        +search_emails(search_term)
    }

    class EventCreationTool {
        -calendar_tool: CalendarTool
        -email_tool: EmailTool
        +execute(**args) async
        +create_event_with_notifications(event_data)
        +send_event_invitations(event_id)
    }

    class NotesTool {
        -database: Database
        +execute(**args) async
        +create_note(content, tags)
        +search_notes(query)
        +update_note(note_id, content)
    }

    class ReminderTool {
        -scheduler: Scheduler
        +execute(**args) async
        +create_reminder(reminder_data)
        +list_reminders()
        +update_reminder(reminder_id, updates)
    }

    class ExpenseTool {
        -database: Database
        +execute(**args) async
        +add_expense(expense_data)
        +get_expenses(time_range)
        +generate_report(report_type)
    }

    class GroceryTool {
        -database: Database
        +execute(**args) async
        +add_item(item_data)
        +get_list()
        +mark_completed(item_id)
    }

    Tool <|-- CalendarTool
    Tool <|-- EmailTool
    Tool <|-- EventCreationTool
    Tool <|-- NotesTool
    Tool <|-- ReminderTool
    Tool <|-- ExpenseTool
    Tool <|-- GroceryTool
    EventCreationTool --> CalendarTool
    EventCreationTool --> EmailTool
```

### Memory System Classes

```mermaid
classDiagram
    class MemoryClient {
        <<interface>>
        +store_memory(memory_data) async
        +retrieve_memories(query) async
        +update_memory(memory_id, updates) async
    }

    class LTMClient {
        -database: Database
        +store_memory(memory_data) async
        +retrieve_memories(query) async
        +update_memory(memory_id, updates) async
        +search_structured_memories(query)
    }

    class RAGClient {
        -vector_db: VectorDatabase
        -embedding_model: EmbeddingModel
        +store_document(document) async
        +retrieve_documents(query) async
        +generate_embedding(text) async
        +search_semantic_documents(query)
    }

    class ContextManager {
        -ltm_client: LTMClient
        -rag_client: RAGClient
        +combine_contexts(ltm_context, rag_context)
        +format_for_injection(contexts)
        +prioritize_contexts(contexts)
    }

    class MemoryEntry {
        +id: str
        +content: str
        +metadata: Dict
        +created_at: datetime
        +updated_at: datetime
        +relevance_score: float
    }

    class DocumentEntry {
        +id: str
        +content: str
        +embedding: List[float]
        +metadata: Dict
        +created_at: datetime
    }

    MemoryClient <|-- LTMClient
    MemoryClient <|-- RAGClient
    ContextManager --> LTMClient
    ContextManager --> RAGClient
    LTMClient --> MemoryEntry
    RAGClient --> DocumentEntry
```

### Communication System Classes

```mermaid
classDiagram
    class CommunicationClient {
        <<interface>>
        +send_message(to, content) async
        +receive_message(message_data) async
        +validate_message(message) bool
    }

    class TwilioClient {
        -client: TwilioClient
        -account_sid: str
        -auth_token: str
        +send_message(to, content) async
        +receive_message(message_data) async
        +validate_message(message) bool
    }

    class WebhookHandler {
        -twilio_client: TwilioClient
        -agent_runner: AgentRunner
        +handle_webhook(request_data) async
        +validate_signature(request) bool
        +process_message(message_data) async
    }

    class MessageRouter {
        -handlers: Dict[str, MessageHandler]
        +route_message(message_data) async
        +register_handler(message_type, handler)
        +process_incoming_message(message)
    }

    class ResponseHandler {
        -twilio_client: TwilioClient
        +format_response(response_data) str
        +send_response(to, response) async
        +handle_error(error) str
    }

    CommunicationClient <|-- TwilioClient
    WebhookHandler --> TwilioClient
    WebhookHandler --> AgentRunner
    MessageRouter --> WebhookHandler
    ResponseHandler --> TwilioClient
```

### Database Layer Classes

```mermaid
classDiagram
    class Database {
        <<interface>>
        +connect() async
        +disconnect() async
        +execute_query(query) async
        +execute_transaction(operations) async
    }

    class SQLAlchemyDatabase {
        -engine: Engine
        -session: Session
        +connect() async
        +disconnect() async
        +execute_query(query) async
        +execute_transaction(operations) async
    }

    class BaseModel {
        <<abstract>>
        +id: int
        +created_at: datetime
        +updated_at: datetime
    }

    class User {
        +id: int
        +phone_number: str
        +name: str
        +preferences: Dict
        +created_at: datetime
    }

    class Conversation {
        +id: int
        +user_id: int
        +conversation_history: List[Dict]
        +step_count: int
        +created_at: datetime
    }

    class Memory {
        +id: int
        +user_id: int
        +content: str
        +metadata: Dict
        +relevance_score: float
        +created_at: datetime
    }

    class Event {
        +id: int
        +user_id: int
        +title: str
        +description: str
        +start_time: datetime
        +end_time: datetime
        +calendar_id: str
    }

    class Email {
        +id: int
        +user_id: int
        +subject: str
        +body: str
        +sender: str
        +recipients: List[str]
        +email_id: str
    }

    class Note {
        +id: int
        +user_id: int
        +content: str
        +tags: List[str]
        +created_at: datetime
    }

    class Reminder {
        +id: int
        +user_id: int
        +title: str
        +description: str
        +due_time: datetime
        +status: str
    }

    Database <|-- SQLAlchemyDatabase
    BaseModel <|-- User
    BaseModel <|-- Conversation
    BaseModel <|-- Memory
    BaseModel <|-- Event
    BaseModel <|-- Email
    BaseModel <|-- Note
    BaseModel <|-- Reminder
    Conversation --> User
    Memory --> User
    Event --> User
    Email --> User
    Note --> User
    Reminder --> User
```

### Scheduler System Classes

```mermaid
classDiagram
    class Scheduler {
        <<interface>>
        +schedule_task(task_data) async
        +cancel_task(task_id) async
        +get_task_status(task_id) async
    }

    class CeleryScheduler {
        -celery_app: Celery
        +schedule_task(task_data) async
        +cancel_task(task_id) async
        +get_task_status(task_id) async
        +start_worker()
        +stop_worker()
    }

    class Task {
        <<abstract>>
        +id: str
        +name: str
        +status: str
        +created_at: datetime
        +execute() async
    }

    class ReminderTask {
        -reminder_data: Dict
        +execute() async
        +send_notification()
        +update_reminder_status()
    }

    class SyncTask {
        -sync_type: str
        +execute() async
        +sync_calendar()
        +sync_email()
    }

    class CleanupTask {
        -cleanup_type: str
        +execute() async
        +cleanup_old_memories()
        +cleanup_expired_reminders()
    }

    Scheduler <|-- CeleryScheduler
    Task <|-- ReminderTask
    Task <|-- SyncTask
    Task <|-- CleanupTask
    CeleryScheduler --> Task
```

### Configuration Classes

```mermaid
classDiagram
    class Config {
        <<interface>>
        +get_setting(key) Any
        +set_setting(key, value)
        +load_from_env()
        +validate_settings() bool
    }

    class Settings {
        -settings: Dict
        +get_setting(key) Any
        +set_setting(key, value)
        +load_from_env()
        +validate_settings() bool
        +get_database_url() str
        +get_twilio_credentials() Dict
        +get_llm_credentials() Dict
    }

    class EnvironmentConfig {
        -env_vars: Dict
        +load_from_env()
        +get_env_var(key) str
        +validate_required_vars() bool
    }

    class DatabaseConfig {
        -database_url: str
        -pool_size: int
        -max_overflow: int
        +get_connection_params() Dict
        +validate_connection() bool
    }

    class APIConfig {
        -api_keys: Dict
        -base_urls: Dict
        +get_api_key(service) str
        +get_base_url(service) str
        +validate_api_credentials() bool
    }

    Config <|-- Settings
    Settings --> EnvironmentConfig
    Settings --> DatabaseConfig
    Settings --> APIConfig
```

## Interface Contracts

### Tool Interface

```mermaid
classDiagram
    class ToolInterface {
        <<interface>>
        +name: str
        +description: str
        +parameters: Dict
        +execute(**args) async
        +validate_args(args) bool
        +format_result(result) str
    }

    class BaseTool {
        +name: str
        +description: str
        +parameters: Dict
        +execute(**args) async
        +validate_args(args) bool
        +format_result(result) str
        +handle_error(error) str
    }

    ToolInterface <|-- BaseTool
```

### Memory Interface

```mermaid
classDiagram
    class MemoryInterface {
        <<interface>>
        +store(data) async
        +retrieve(query) async
        +update(id, data) async
        +delete(id) async
    }

    class BaseMemory {
        +store(data) async
        +retrieve(query) async
        +update(id, data) async
        +delete(id) async
        +validate_data(data) bool
        +format_query(query) str
    }

    MemoryInterface <|-- BaseMemory
```

### Communication Interface

```mermaid
classDiagram
    class CommunicationInterface {
        <<interface>>
        +send_message(to, content) async
        +receive_message(data) async
        +validate_message(data) bool
        +handle_error(error) str
    }

    class BaseCommunication {
        +send_message(to, content) async
        +receive_message(data) async
        +validate_message(data) bool
        +handle_error(error) str
        +format_message(content) str
        +parse_response(response) Dict
    }

    CommunicationInterface <|-- BaseCommunication
```

## Notes

### Design Patterns Used

1. **Strategy Pattern**: Different tools implement the same interface
2. **Factory Pattern**: Tool registry creates tool instances
3. **Observer Pattern**: State changes notify dependent components
4. **Template Method**: Base classes define common behavior
5. **Dependency Injection**: Components receive dependencies externally

### Key Relationships

1. **Composition**: AgentRunner contains ToolRegistry and LLMPlanner
2. **Inheritance**: All tools inherit from base Tool class
3. **Association**: Tools use external APIs and databases
4. **Dependency**: Components depend on interfaces, not implementations
5. **Aggregation**: Memory system aggregates LTM and RAG clients

### Interface Design Principles

1. **Single Responsibility**: Each interface has one clear purpose
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes are substitutable for base types
4. **Interface Segregation**: Clients depend only on methods they use
5. **Dependency Inversion**: High-level modules don't depend on low-level modules

This class structure provides a solid foundation for the personal assistant application, ensuring maintainability, extensibility, and testability.
