# Database Schema

## Overview

This document contains comprehensive database schema diagrams for the personal assistant application. These diagrams show entity relationships, data models, and database operations.

## Entity Relationship Diagram

### Main Database Schema

```mermaid
erDiagram
    USERS {
        int id PK
        string phone_number UK
        string name
        json preferences
        datetime created_at
        datetime updated_at
    }

    CONVERSATIONS {
        int id PK
        int user_id FK
        json conversation_history
        int step_count
        datetime created_at
        datetime updated_at
    }

    MEMORIES {
        int id PK
        int user_id FK
        string content
        json metadata
        float relevance_score
        datetime created_at
        datetime updated_at
    }

    EVENTS {
        int id PK
        int user_id FK
        string title
        string description
        datetime start_time
        datetime end_time
        string calendar_id
        string event_id
        json metadata
        datetime created_at
        datetime updated_at
    }

    EMAILS {
        int id PK
        int user_id FK
        string subject
        text body
        string sender
        json recipients
        string email_id
        string thread_id
        json metadata
        datetime created_at
        datetime updated_at
    }

    NOTES {
        int id PK
        int user_id FK
        text content
        json tags
        datetime created_at
        datetime updated_at
    }

    REMINDERS {
        int id PK
        int user_id FK
        string title
        string description
        datetime due_time
        string status
        json metadata
        datetime created_at
        datetime updated_at
    }

    EXPENSES {
        int id PK
        int user_id FK
        string description
        decimal amount
        string category
        datetime date
        json metadata
        datetime created_at
        datetime updated_at
    }

    GROCERY_ITEMS {
        int id PK
        int user_id FK
        string name
        string category
        int quantity
        string unit
        boolean completed
        datetime created_at
        datetime updated_at
    }

    DOCUMENTS {
        int id PK
        int user_id FK
        text content
        vector embedding
        json metadata
        datetime created_at
        datetime updated_at
    }

    SCHEDULED_TASKS {
        int id PK
        int user_id FK
        string task_type
        json task_data
        string status
        datetime scheduled_time
        datetime created_at
        datetime updated_at
    }

    USERS ||--o{ CONVERSATIONS : "has"
    USERS ||--o{ MEMORIES : "has"
    USERS ||--o{ EVENTS : "has"
    USERS ||--o{ EMAILS : "has"
    USERS ||--o{ NOTES : "has"
    USERS ||--o{ REMINDERS : "has"
    USERS ||--o{ EXPENSES : "has"
    USERS ||--o{ GROCERY_ITEMS : "has"
    USERS ||--o{ DOCUMENTS : "has"
    USERS ||--o{ SCHEDULED_TASKS : "has"
```

### Memory System Schema

```mermaid
erDiagram
    MEMORIES {
        int id PK
        int user_id FK
        string content
        json metadata
        float relevance_score
        string memory_type
        datetime created_at
        datetime updated_at
    }

    MEMORY_TAGS {
        int id PK
        int memory_id FK
        string tag
        datetime created_at
    }

    MEMORY_RELATIONS {
        int id PK
        int memory_id FK
        int related_memory_id FK
        string relation_type
        float strength
        datetime created_at
    }

    DOCUMENTS {
        int id PK
        int user_id FK
        text content
        vector embedding
        json metadata
        string document_type
        datetime created_at
        datetime updated_at
    }

    DOCUMENT_CHUNKS {
        int id PK
        int document_id FK
        text chunk_content
        vector chunk_embedding
        int chunk_index
        json metadata
        datetime created_at
    }

    MEMORIES ||--o{ MEMORY_TAGS : "has"
    MEMORIES ||--o{ MEMORY_RELATIONS : "has"
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : "has"
```

### Calendar and Event Schema

```mermaid
erDiagram
    EVENTS {
        int id PK
        int user_id FK
        string title
        string description
        datetime start_time
        datetime end_time
        string calendar_id
        string event_id
        json metadata
        datetime created_at
        datetime updated_at
    }

    EVENT_ATTENDEES {
        int id PK
        int event_id FK
        string email
        string name
        string response_status
        datetime created_at
    }

    EVENT_NOTIFICATIONS {
        int id PK
        int event_id FK
        string notification_type
        datetime notification_time
        boolean sent
        datetime created_at
    }

    CALENDAR_SYNC {
        int id PK
        int user_id FK
        string calendar_id
        string sync_token
        datetime last_sync
        json sync_metadata
        datetime created_at
        datetime updated_at
    }

    EVENTS ||--o{ EVENT_ATTENDEES : "has"
    EVENTS ||--o{ EVENT_NOTIFICATIONS : "has"
    CALENDAR_SYNC ||--o{ EVENTS : "syncs"
```

## Data Model Visualizations

### User Data Model

```mermaid
graph TB
    subgraph "User Entity"
        USER[User]
        USER_PREFS[User Preferences]
        USER_SESSIONS[User Sessions]
    end

    subgraph "User Relationships"
        CONVERSATIONS[Conversations]
        MEMORIES[Memories]
        EVENTS[Events]
        EMAILS[Emails]
        NOTES[Notes]
        REMINDERS[Reminders]
    end

    USER --> USER_PREFS
    USER --> USER_SESSIONS
    USER --> CONVERSATIONS
    USER --> MEMORIES
    USER --> EVENTS
    USER --> EMAILS
    USER --> NOTES
    USER --> REMINDERS

    classDef user fill:#e3f2fd
    classDef data fill:#f3e5f5
    classDef relationships fill:#e8f5e8

    class USER,USER_PREFS,USER_SESSIONS user
    class CONVERSATIONS,MEMORIES,EVENTS,EMAILS,NOTES,REMINDERS relationships
```

### Memory Data Model

```mermaid
graph TB
    subgraph "Memory System"
        MEMORY[Memory Entry]
        MEMORY_TAGS[Memory Tags]
        MEMORY_RELATIONS[Memory Relations]
    end

    subgraph "Document System"
        DOCUMENT[Document]
        DOCUMENT_CHUNKS[Document Chunks]
        EMBEDDINGS[Embeddings]
    end

    subgraph "Memory Types"
        LTM[Long-Term Memory]
        RAG[RAG Documents]
        CONTEXT[Context Blocks]
    end

    MEMORY --> MEMORY_TAGS
    MEMORY --> MEMORY_RELATIONS
    DOCUMENT --> DOCUMENT_CHUNKS
    DOCUMENT_CHUNKS --> EMBEDDINGS
    MEMORY --> LTM
    DOCUMENT --> RAG
    LTM --> CONTEXT
    RAG --> CONTEXT

    classDef memory fill:#e3f2fd
    classDef document fill:#f3e5f5
    classDef types fill:#e8f5e8

    class MEMORY,MEMORY_TAGS,MEMORY_RELATIONS memory
    class DOCUMENT,DOCUMENT_CHUNKS,EMBEDDINGS document
    class LTM,RAG,CONTEXT types
```

## CRUD Operation Flows

### Create Operations

```mermaid
flowchart TD
    A[Create Request] --> B{Validate Input}
    B -->|Valid| C[Check Constraints]
    B -->|Invalid| D[Return Error]
    C -->|Pass| E[Create Entity]
    C -->|Fail| F[Return Constraint Error]
    E --> G[Generate ID]
    G --> H[Set Timestamps]
    H --> I[Save to Database]
    I --> J[Return Created Entity]
    I -->|Error| K[Rollback Transaction]
    K --> L[Return Database Error]
```

### Read Operations

```mermaid
flowchart TD
    A[Read Request] --> B{Validate Query}
    B -->|Valid| C[Build Query]
    B -->|Invalid| D[Return Error]
    C --> E[Execute Query]
    E --> F{Check Results}
    F -->|Found| G[Format Response]
    F -->|Not Found| H[Return Empty/Error]
    G --> I[Apply Filters]
    I --> J[Return Results]
    E -->|Error| K[Return Database Error]
```

### Update Operations

```mermaid
flowchart TD
    A[Update Request] --> B{Validate Input}
    B -->|Valid| C[Check Entity Exists]
    B -->|Invalid| D[Return Error]
    C -->|Exists| E[Check Permissions]
    C -->|Not Found| F[Return Not Found]
    E -->|Authorized| G[Update Entity]
    E -->|Unauthorized| H[Return Forbidden]
    G --> I[Update Timestamps]
    I --> J[Save Changes]
    J --> K[Return Updated Entity]
    J -->|Error| L[Rollback Transaction]
    L --> M[Return Database Error]
```

### Delete Operations

```mermaid
flowchart TD
    A[Delete Request] --> B{Validate ID}
    B -->|Valid| C[Check Entity Exists]
    B -->|Invalid| D[Return Error]
    C -->|Exists| E[Check Permissions]
    C -->|Not Found| F[Return Not Found]
    E -->|Authorized| G[Check Dependencies]
    E -->|Unauthorized| H[Return Forbidden]
    G -->|No Dependencies| I[Delete Entity]
    G -->|Has Dependencies| J[Return Constraint Error]
    I --> K[Update Timestamps]
    K --> L[Save Changes]
    L --> M[Return Success]
    L -->|Error| N[Rollback Transaction]
    N --> O[Return Database Error]
```

## Migration Patterns

### Database Migration Flow

```mermaid
flowchart TD
    A[Migration Request] --> B[Create Migration File]
    B --> C[Define Up Migration]
    C --> D[Define Down Migration]
    D --> E[Test Migration Locally]
    E --> F{Test Passed?}
    F -->|Yes| G[Deploy to Staging]
    F -->|No| H[Fix Migration]
    H --> E
    G --> I{Staging Tests Pass?}
    I -->|Yes| J[Deploy to Production]
    I -->|No| K[Rollback and Fix]
    K --> E
    J --> L[Monitor Migration]
    L --> M{Migration Successful?}
    M -->|Yes| N[Mark as Complete]
    M -->|No| O[Rollback Production]
    O --> P[Investigate and Fix]
    P --> E
```

### Schema Evolution

```mermaid
graph TB
    subgraph "Schema Version 1"
        V1_USERS[Users Table]
        V1_EVENTS[Events Table]
    end

    subgraph "Schema Version 2"
        V2_USERS[Users Table + Preferences]
        V2_EVENTS[Events Table + Metadata]
        V2_MEMORIES[Memories Table]
    end

    subgraph "Schema Version 3"
        V3_USERS[Users Table + Preferences]
        V3_EVENTS[Events Table + Metadata]
        V3_MEMORIES[Memories Table + Tags]
        V3_DOCUMENTS[Documents Table]
    end

    V1_USERS --> V2_USERS
    V1_EVENTS --> V2_EVENTS
    V2_MEMORIES --> V3_MEMORIES
    V3_DOCUMENTS

    classDef version1 fill:#e3f2fd
    classDef version2 fill:#f3e5f5
    classDef version3 fill:#e8f5e8

    class V1_USERS,V1_EVENTS version1
    class V2_USERS,V2_EVENTS,V2_MEMORIES version2
    class V3_USERS,V3_EVENTS,V3_MEMORIES,V3_DOCUMENTS version3
```

## Data Access Patterns

### Query Optimization

```mermaid
flowchart TD
    A[Query Request] --> B[Parse Query]
    B --> C[Check Cache]
    C -->|Cache Hit| D[Return Cached Result]
    C -->|Cache Miss| E[Build Query Plan]
    E --> F[Execute Query]
    F --> G[Process Results]
    G --> H[Update Cache]
    H --> I[Return Results]
    F -->|Error| J[Handle Error]
    J --> K[Return Error Response]
```

### Transaction Management

```mermaid
flowchart TD
    A[Transaction Start] --> B[Begin Transaction]
    B --> C[Execute Operations]
    C --> D{All Operations Success?}
    D -->|Yes| E[Commit Transaction]
    D -->|No| F[Rollback Transaction]
    E --> G[Return Success]
    F --> H[Return Error]
    C --> I[Check Timeout]
    I -->|Timeout| J[Rollback Transaction]
    J --> K[Return Timeout Error]
```

## Indexing Strategy

### Database Indexes

```mermaid
graph TB
    subgraph "Primary Indexes"
        PK_USERS[Users.id]
        PK_EVENTS[Events.id]
        PK_MEMORIES[Memories.id]
    end

    subgraph "Foreign Key Indexes"
        FK_CONVERSATIONS[Conversations.user_id]
        FK_EVENTS[Events.user_id]
        FK_MEMORIES[Memories.user_id]
    end

    subgraph "Search Indexes"
        IDX_USER_PHONE[Users.phone_number]
        IDX_EVENT_TIME[Events.start_time]
        IDX_MEMORY_SCORE[Memories.relevance_score]
    end

    subgraph "Composite Indexes"
        IDX_USER_TIME[Users.id, Conversations.created_at]
        IDX_EVENT_USER_TIME[Events.user_id, Events.start_time]
    end

    classDef primary fill:#e3f2fd
    classDef foreign fill:#f3e5f5
    classDef search fill:#e8f5e8
    classDef composite fill:#fff3e0

    class PK_USERS,PK_EVENTS,PK_MEMORIES primary
    class FK_CONVERSATIONS,FK_EVENTS,FK_MEMORIES foreign
    class IDX_USER_PHONE,IDX_EVENT_TIME,IDX_MEMORY_SCORE search
    class IDX_USER_TIME,IDX_EVENT_USER_TIME composite
```

## Notes

### Database Design Principles

1. **Normalization**: Tables are normalized to reduce redundancy
2. **Referential Integrity**: Foreign key constraints ensure data consistency
3. **Indexing Strategy**: Strategic indexes for common query patterns
4. **Soft Deletes**: Important data is soft-deleted rather than hard-deleted
5. **Audit Trail**: All tables include created_at and updated_at timestamps

### Performance Considerations

- **Connection Pooling**: Database connections are pooled for efficiency
- **Query Optimization**: Complex queries are optimized with proper indexes
- **Caching Strategy**: Frequently accessed data is cached
- **Batch Operations**: Bulk operations are batched for performance
- **Async Operations**: Database operations are async where possible

### Data Integrity

- **Constraints**: Database constraints ensure data validity
- **Validation**: Application-level validation complements database constraints
- **Transactions**: ACID transactions ensure data consistency
- **Backup Strategy**: Regular backups with point-in-time recovery
- **Migration Safety**: All schema changes are backward compatible

### Security Measures

- **Encryption**: Sensitive data is encrypted at rest
- **Access Control**: Database access is restricted by user roles
- **Audit Logging**: All database changes are logged
- **SQL Injection Prevention**: Parameterized queries prevent injection
- **Connection Security**: Database connections use SSL/TLS

This database schema provides a robust foundation for storing and managing all application data while ensuring performance, security, and data integrity.
