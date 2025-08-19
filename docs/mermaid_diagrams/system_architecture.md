# System Architecture

## Overview

This document contains comprehensive system architecture diagrams for the personal assistant application. These diagrams show the high-level structure, component relationships, and technology stack of the entire system.

## Main System Architecture

### High-Level System Overview

```mermaid
graph TB
    %% External Services
    subgraph "External Services"
        TWILIO[Twilio API]
        LLM[LLM Providers<br/>Gemini, OpenAI]
        CALENDAR[Calendar APIs<br/>Google Calendar]
        EMAIL[Email APIs<br/>Gmail, Outlook]
        DB[(Database<br/>SQLite/PostgreSQL)]
    end

    %% Core Application
    subgraph "Personal Assistant Application"
        subgraph "Core Agent System"
            RUNNER[AgentRunner<br/>Main conversation loop]
            PLANNER[LLMPlanner<br/>Decision making]
            STATE[AgentState<br/>State management]
        end

        subgraph "Tool System"
            REGISTRY[ToolRegistry<br/>Tool discovery & execution]
            TOOLS[Tools<br/>Calendar, Email, Notes, etc.]
        end

        subgraph "Memory System"
            LTM[Long-Term Memory<br/>Structured storage]
            RAG[RAG System<br/>Document retrieval]
            CONTEXT[Context Injection<br/>Memory integration]
        end

        subgraph "Communication"
            TWILIO_CLIENT[Twilio Client<br/>SMS handling]
            WEBHOOK[Webhook Handler<br/>Incoming messages]
        end

        subgraph "Scheduler"
            CELERY[Celery<br/>Background tasks]
            TASKS[Scheduled Tasks<br/>Reminders, sync]
        end
    end

    %% Data Flow
    USER[User Input] --> WEBHOOK
    WEBHOOK --> RUNNER
    RUNNER --> PLANNER
    PLANNER --> REGISTRY
    REGISTRY --> TOOLS
    TOOLS --> CALENDAR
    TOOLS --> EMAIL
    TOOLS --> DB
    RUNNER --> LTM
    RUNNER --> RAG
    LTM --> CONTEXT
    RAG --> CONTEXT
    CONTEXT --> RUNNER
    RUNNER --> TWILIO_CLIENT
    TWILIO_CLIENT --> TWILIO
    CELERY --> TASKS
    TASKS --> CALENDAR
    TASKS --> EMAIL

    %% Styling
    classDef external fill:#e1f5fe
    classDef core fill:#f3e5f5
    classDef tool fill:#e8f5e8
    classDef memory fill:#fff3e0
    classDef comm fill:#fce4ec
    classDef scheduler fill:#f1f8e9

    class TWILIO,LLM,CALENDAR,EMAIL,DB external
    class RUNNER,PLANNER,STATE core
    class REGISTRY,TOOLS tool
    class LTM,RAG,CONTEXT memory
    class TWILIO_CLIENT,WEBHOOK comm
    class CELERY,TASKS scheduler
```

### Component Relationships

```mermaid
graph LR
    %% Core Components
    subgraph "Core Agent"
        A[AgentRunner]
        B[LLMPlanner]
        C[AgentState]
    end

    %% Tool System
    subgraph "Tools"
        D[ToolRegistry]
        E[Calendar Tools]
        F[Email Tools]
        G[Event Creation]
        H[Notes Tools]
        I[Reminder Tools]
    end

    %% Memory System
    subgraph "Memory"
        J[LTM Client]
        K[RAG Retriever]
        L[Context Manager]
    end

    %% Communication
    subgraph "Communication"
        M[Twilio Client]
        N[Webhook Handler]
        O[Message Router]
    end

    %% Database
    subgraph "Database"
        P[Models]
        Q[CRUD Operations]
        R[Migrations]
    end

    %% Scheduler
    subgraph "Scheduler"
        S[Celery Worker]
        T[Task Queue]
        U[Scheduled Jobs]
    end

    %% Relationships
    A --> B
    A --> C
    A --> D
    A --> J
    A --> K
    A --> M
    B --> D
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    J --> L
    K --> L
    L --> A
    M --> N
    N --> O
    O --> A
    E --> P
    F --> P
    G --> P
    H --> P
    I --> P
    S --> T
    T --> U
    U --> E
    U --> F

    %% Styling
    classDef core fill:#f3e5f5
    classDef tool fill:#e8f5e8
    classDef memory fill:#fff3e0
    classDef comm fill:#fce4ec
    classDef db fill:#e0f2f1
    classDef scheduler fill:#f1f8e9

    class A,B,C core
    class D,E,F,G,H,I tool
    class J,K,L memory
    class M,N,O comm
    class P,Q,R db
    class S,T,U scheduler
```

## Technology Stack

### Backend Architecture

```mermaid
graph TB
    %% Technology Stack
    subgraph "Application Layer"
        PYTHON[Python 3.x]
        FASTAPI[FastAPI]
        ASYNC[Async/Await]
    end

    subgraph "AI/ML Layer"
        LLM_PROVIDERS[LLM Providers<br/>Gemini, OpenAI]
        VECTOR_DB[Vector Database<br/>Chroma, Pinecone]
        EMBEDDINGS[Embeddings<br/>Text embeddings]
    end

    subgraph "Data Layer"
        SQLITE[SQLite/PostgreSQL]
        MIGRATIONS[Alembic Migrations]
        ORM[SQLAlchemy ORM]
    end

    subgraph "External APIs"
        TWILIO_API[Twilio API]
        CALENDAR_API[Calendar APIs]
        EMAIL_API[Email APIs]
    end

    subgraph "Task Queue"
        CELERY_WORKER[Celery Worker]
        REDIS[Redis Broker]
        BEAT[Celery Beat]
    end

    %% Relationships
    PYTHON --> FASTAPI
    FASTAPI --> ASYNC
    ASYNC --> LLM_PROVIDERS
    ASYNC --> VECTOR_DB
    LLM_PROVIDERS --> EMBEDDINGS
    VECTOR_DB --> EMBEDDINGS
    FASTAPI --> SQLITE
    SQLITE --> MIGRATIONS
    SQLITE --> ORM
    FASTAPI --> TWILIO_API
    FASTAPI --> CALENDAR_API
    FASTAPI --> EMAIL_API
    FASTAPI --> CELERY_WORKER
    CELERY_WORKER --> REDIS
    CELERY_WORKER --> BEAT

    %% Styling
    classDef app fill:#e3f2fd
    classDef ai fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef external fill:#fff3e0
    classDef queue fill:#fce4ec

    class PYTHON,FASTAPI,ASYNC app
    class LLM_PROVIDERS,VECTOR_DB,EMBEDDINGS ai
    class SQLITE,MIGRATIONS,ORM data
    class TWILIO_API,CALENDAR_API,EMAIL_API external
    class CELERY_WORKER,REDIS,BEAT queue
```

## Deployment Architecture

### Production Deployment

```mermaid
graph TB
    %% Infrastructure
    subgraph "Load Balancer"
        LB[NGINX Load Balancer]
    end

    subgraph "Application Servers"
        APP1[App Server 1]
        APP2[App Server 2]
        APP3[App Server 3]
    end

    subgraph "Database Layer"
        DB_MASTER[(Master DB)]
        DB_REPLICA[(Replica DB)]
    end

    subgraph "Cache Layer"
        REDIS_CACHE[Redis Cache]
        REDIS_QUEUE[Redis Queue]
    end

    subgraph "External Services"
        TWILIO_SERVICE[Twilio]
        LLM_SERVICE[LLM APIs]
        CALENDAR_SERVICE[Calendar APIs]
    end

    subgraph "Background Workers"
        WORKER1[Celery Worker 1]
        WORKER2[Celery Worker 2]
        WORKER3[Celery Worker 3]
    end

    %% Connections
    LB --> APP1
    LB --> APP2
    LB --> APP3
    APP1 --> DB_MASTER
    APP2 --> DB_MASTER
    APP3 --> DB_MASTER
    DB_MASTER --> DB_REPLICA
    APP1 --> REDIS_CACHE
    APP2 --> REDIS_CACHE
    APP3 --> REDIS_CACHE
    APP1 --> REDIS_QUEUE
    APP2 --> REDIS_QUEUE
    APP3 --> REDIS_QUEUE
    WORKER1 --> REDIS_QUEUE
    WORKER2 --> REDIS_QUEUE
    WORKER3 --> REDIS_QUEUE
    APP1 --> TWILIO_SERVICE
    APP2 --> TWILIO_SERVICE
    APP3 --> TWILIO_SERVICE
    APP1 --> LLM_SERVICE
    APP2 --> LLM_SERVICE
    APP3 --> LLM_SERVICE
    APP1 --> CALENDAR_SERVICE
    APP2 --> CALENDAR_SERVICE
    APP3 --> CALENDAR_SERVICE

    %% Styling
    classDef lb fill:#e3f2fd
    classDef app fill:#f3e5f5
    classDef db fill:#e8f5e8
    classDef cache fill:#fff3e0
    classDef external fill:#fce4ec
    classDef worker fill:#f1f8e9

    class LB lb
    class APP1,APP2,APP3 app
    class DB_MASTER,DB_REPLICA db
    class REDIS_CACHE,REDIS_QUEUE cache
    class TWILIO_SERVICE,LLM_SERVICE,CALENDAR_SERVICE external
    class WORKER1,WORKER2,WORKER3 worker
```

## Service Boundaries

### Microservices Overview

```mermaid
graph TB
    %% Service Boundaries
    subgraph "API Gateway"
        GATEWAY[API Gateway<br/>Request routing]
    end

    subgraph "Core Services"
        AGENT_SERVICE[Agent Service<br/>Conversation management]
        TOOL_SERVICE[Tool Service<br/>Tool execution]
        MEMORY_SERVICE[Memory Service<br/>LTM & RAG]
    end

    subgraph "Communication Services"
        SMS_SERVICE[SMS Service<br/>Twilio integration]
        WEBHOOK_SERVICE[Webhook Service<br/>Incoming messages]
    end

    subgraph "Data Services"
        USER_SERVICE[User Service<br/>User management]
        CALENDAR_SERVICE[Calendar Service<br/>Event management]
        EMAIL_SERVICE[Email Service<br/>Email handling]
    end

    subgraph "Background Services"
        SCHEDULER_SERVICE[Scheduler Service<br/>Task scheduling]
        SYNC_SERVICE[Sync Service<br/>Data synchronization]
    end

    %% Service Communication
    GATEWAY --> AGENT_SERVICE
    GATEWAY --> TOOL_SERVICE
    GATEWAY --> MEMORY_SERVICE
    GATEWAY --> SMS_SERVICE
    GATEWAY --> WEBHOOK_SERVICE
    AGENT_SERVICE --> TOOL_SERVICE
    AGENT_SERVICE --> MEMORY_SERVICE
    TOOL_SERVICE --> CALENDAR_SERVICE
    TOOL_SERVICE --> EMAIL_SERVICE
    SMS_SERVICE --> AGENT_SERVICE
    WEBHOOK_SERVICE --> AGENT_SERVICE
    SCHEDULER_SERVICE --> CALENDAR_SERVICE
    SCHEDULER_SERVICE --> EMAIL_SERVICE
    SYNC_SERVICE --> CALENDAR_SERVICE
    SYNC_SERVICE --> EMAIL_SERVICE

    %% Styling
    classDef gateway fill:#e3f2fd
    classDef core fill:#f3e5f5
    classDef comm fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef background fill:#fce4ec

    class GATEWAY gateway
    class AGENT_SERVICE,TOOL_SERVICE,MEMORY_SERVICE core
    class SMS_SERVICE,WEBHOOK_SERVICE comm
    class USER_SERVICE,CALENDAR_SERVICE,EMAIL_SERVICE data
    class SCHEDULER_SERVICE,SYNC_SERVICE background
```

## Key Design Principles

### 1. **Modular Architecture**

- Clear separation of concerns
- Loose coupling between components
- High cohesion within modules

### 2. **Event-Driven Design**

- Asynchronous message processing
- Event sourcing for state changes
- Reactive programming patterns

### 3. **Scalability Patterns**

- Horizontal scaling capability
- Load balancing support
- Database sharding ready

### 4. **Reliability Features**

- Fault tolerance mechanisms
- Circuit breaker patterns
- Retry logic with exponential backoff

### 5. **Security Considerations**

- API authentication and authorization
- Data encryption in transit and at rest
- Secure external API integrations

## Notes

- All components are designed for async operation
- Database connections are pooled for efficiency
- External API calls include proper error handling
- Background tasks are queued for reliability
- Memory systems are optimized for fast retrieval
- Communication channels support multiple protocols

This architecture provides a solid foundation for the personal assistant application, ensuring scalability, maintainability, and reliability.
