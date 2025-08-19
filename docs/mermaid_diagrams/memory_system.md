# Memory System

## Overview

This document contains comprehensive memory system diagrams showing how LTM (Long-Term Memory), RAG (Retrieval-Augmented Generation), and context injection work in the personal assistant application. These diagrams illustrate memory storage, retrieval, and integration processes.

## Memory System Architecture

### High-Level Memory Architecture

```mermaid
graph TB
    subgraph "Memory Input"
        USER_INPUT[User Input]
        CONVERSATION[Conversation History]
        TOOL_RESULTS[Tool Results]
        EXTERNAL_DATA[External Data]
    end

    subgraph "Memory Processing"
        EXTRACTION[Information Extraction]
        CLASSIFICATION[Memory Classification]
        ENCODING[Memory Encoding]
        STORAGE[Memory Storage]
    end

    subgraph "Memory Storage"
        LTM[Long-Term Memory<br/>Structured Storage]
        RAG[RAG System<br/>Document Storage]
        VECTOR_DB[Vector Database<br/>Embeddings]
        METADATA[Memory Metadata]
    end

    subgraph "Memory Retrieval"
        QUERY[Memory Query]
        SEARCH[Memory Search]
        RANKING[Result Ranking]
        CONTEXT[Context Generation]
    end

    subgraph "Context Injection"
        CONTEXT_MANAGER[Context Manager]
        PRIORITIZATION[Context Prioritization]
        FORMATTING[Context Formatting]
        INJECTION[Context Injection]
    end

    USER_INPUT --> EXTRACTION
    CONVERSATION --> EXTRACTION
    TOOL_RESULTS --> EXTRACTION
    EXTERNAL_DATA --> EXTRACTION
    EXTRACTION --> CLASSIFICATION
    CLASSIFICATION --> ENCODING
    ENCODING --> STORAGE
    STORAGE --> LTM
    STORAGE --> RAG
    RAG --> VECTOR_DB
    STORAGE --> METADATA
    QUERY --> SEARCH
    SEARCH --> LTM
    SEARCH --> RAG
    LTM --> RANKING
    RAG --> RANKING
    RANKING --> CONTEXT
    CONTEXT --> CONTEXT_MANAGER
    CONTEXT_MANAGER --> PRIORITIZATION
    PRIORITIZATION --> FORMATTING
    FORMATTING --> INJECTION

    classDef input fill:#e3f2fd
    classDef processing fill:#f3e5f5
    classDef storage fill:#e8f5e8
    classDef retrieval fill:#fff3e0
    classDef injection fill:#fce4ec

    class USER_INPUT,CONVERSATION,TOOL_RESULTS,EXTERNAL_DATA input
    class EXTRACTION,CLASSIFICATION,ENCODING,STORAGE processing
    class LTM,RAG,VECTOR_DB,METADATA storage
    class QUERY,SEARCH,RANKING,CONTEXT retrieval
    class CONTEXT_MANAGER,PRIORITIZATION,FORMATTING,INJECTION injection
```

### Memory Types and Relationships

```mermaid
graph LR
    subgraph "Memory Types"
        CONVERSATION_MEMORY[Conversation Memory]
        FACTUAL_MEMORY[Factual Memory]
        PROCEDURAL_MEMORY[Procedural Memory]
        EMOTIONAL_MEMORY[Emotional Memory]
    end

    subgraph "Storage Systems"
        LTM_STRUCTURED[LTM - Structured]
        RAG_DOCUMENTS[RAG - Documents]
        VECTOR_EMBEDDINGS[Vector Embeddings]
        METADATA_STORE[Metadata Store]
    end

    subgraph "Retrieval Methods"
        SEMANTIC_SEARCH[Semantic Search]
        KEYWORD_SEARCH[Keyword Search]
        TEMPORAL_SEARCH[Temporal Search]
        CONTEXTUAL_SEARCH[Contextual Search]
    end

    CONVERSATION_MEMORY --> LTM_STRUCTURED
    FACTUAL_MEMORY --> RAG_DOCUMENTS
    PROCEDURAL_MEMORY --> VECTOR_EMBEDDINGS
    EMOTIONAL_MEMORY --> METADATA_STORE
    LTM_STRUCTURED --> SEMANTIC_SEARCH
    RAG_DOCUMENTS --> KEYWORD_SEARCH
    VECTOR_EMBEDDINGS --> TEMPORAL_SEARCH
    METADATA_STORE --> CONTEXTUAL_SEARCH

    classDef types fill:#e3f2fd
    classDef storage fill:#f3e5f5
    classDef retrieval fill:#e8f5e8

    class CONVERSATION_MEMORY,FACTUAL_MEMORY,PROCEDURAL_MEMORY,EMOTIONAL_MEMORY types
    class LTM_STRUCTURED,RAG_DOCUMENTS,VECTOR_EMBEDDINGS,METADATA_STORE storage
    class SEMANTIC_SEARCH,KEYWORD_SEARCH,TEMPORAL_SEARCH,CONTEXTUAL_SEARCH retrieval
```

## LTM (Long-Term Memory) System

### LTM Storage Flow

```mermaid
flowchart TD
    A[Memory Input] --> B[Extract Key Information]
    B --> C[Classify Memory Type]
    C --> D{Memory Type}
    D -->|Conversation| E[Store Conversation Memory]
    D -->|Fact| F[Store Factual Memory]
    D -->|Procedure| G[Store Procedural Memory]
    D -->|Emotion| H[Store Emotional Memory]

    E --> I[Add Metadata]
    F --> I
    G --> I
    H --> I

    I --> J[Calculate Relevance Score]
    J --> K[Store in LTM Database]
    K --> L[Update Memory Index]
    L --> M[Memory Stored Successfully]
```

### LTM Retrieval Process

```mermaid
sequenceDiagram
    participant AgentRunner
    participant LTMClient
    participant Database
    participant RelevanceEngine
    participant ContextManager

    AgentRunner->>LTMClient: Request relevant memories
    LTMClient->>Database: Query structured memories
    Database-->>LTMClient: Return memory entries

    LTMClient->>RelevanceEngine: Calculate relevance scores
    RelevanceEngine->>RelevanceEngine: Analyze query context
    RelevanceEngine->>RelevanceEngine: Score memory relevance
    RelevanceEngine-->>LTMClient: Return scored memories

    LTMClient->>LTMClient: Filter and rank memories
    LTMClient->>ContextManager: Provide memory context
    ContextManager->>ContextManager: Format for injection
    ContextManager-->>AgentRunner: Return context blocks
```

### LTM Memory Structure

```mermaid
graph TB
    subgraph "Memory Entry"
        MEMORY_ID[Memory ID]
        USER_ID[User ID]
        CONTENT[Memory Content]
        MEMORY_TYPE[Memory Type]
        RELEVANCE_SCORE[Relevance Score]
        CREATED_AT[Created At]
        UPDATED_AT[Updated At]
    end

    subgraph "Memory Metadata"
        TAGS[Memory Tags]
        RELATIONS[Memory Relations]
        EMOTIONS[Emotional Context]
        CONFIDENCE[Confidence Level]
    end

    subgraph "Memory Types"
        CONVERSATION[Conversation Memory]
        FACTUAL[Factual Memory]
        PROCEDURAL[Procedural Memory]
        EMOTIONAL[Emotional Memory]
    end

    MEMORY_ID --> TAGS
    MEMORY_ID --> RELATIONS
    MEMORY_ID --> EMOTIONS
    MEMORY_ID --> CONFIDENCE
    MEMORY_TYPE --> CONVERSATION
    MEMORY_TYPE --> FACTUAL
    MEMORY_TYPE --> PROCEDURAL
    MEMORY_TYPE --> EMOTIONAL

    classDef entry fill:#e3f2fd
    classDef metadata fill:#f3e5f5
    classDef types fill:#e8f5e8

    class MEMORY_ID,USER_ID,CONTENT,MEMORY_TYPE,RELEVANCE_SCORE,CREATED_AT,UPDATED_AT entry
    class TAGS,RELATIONS,EMOTIONS,CONFIDENCE metadata
    class CONVERSATION,FACTUAL,PROCEDURAL,EMOTIONAL types
```

## RAG (Retrieval-Augmented Generation) System

### RAG Document Processing

```mermaid
flowchart TD
    A[Document Input] --> B[Document Preprocessing]
    B --> C[Text Chunking]
    C --> D[Generate Embeddings]
    D --> E[Store in Vector DB]
    E --> F[Index Documents]
    F --> G[Document Ready for Retrieval]

    B --> H[Extract Metadata]
    H --> I[Store Metadata]
    I --> J[Link to Vector DB]
```

### RAG Retrieval Flow

```mermaid
sequenceDiagram
    participant AgentRunner
    participant RAGRetriever
    participant EmbeddingModel
    participant VectorDB
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

### RAG Document Structure

```mermaid
graph TB
    subgraph "Document Entry"
        DOCUMENT_ID[Document ID]
        USER_ID[User ID]
        CONTENT[Document Content]
        DOCUMENT_TYPE[Document Type]
        CREATED_AT[Created At]
        UPDATED_AT[Updated At]
    end

    subgraph "Document Chunks"
        CHUNK_ID[Chunk ID]
        CHUNK_CONTENT[Chunk Content]
        CHUNK_INDEX[Chunk Index]
        CHUNK_EMBEDDING[Chunk Embedding]
    end

    subgraph "Document Metadata"
        TITLE[Document Title]
        AUTHOR[Document Author]
        TAGS[Document Tags]
        CONFIDENCE[Confidence Level]
    end

    DOCUMENT_ID --> CHUNK_ID
    CHUNK_ID --> CHUNK_CONTENT
    CHUNK_ID --> CHUNK_INDEX
    CHUNK_ID --> CHUNK_EMBEDDING
    DOCUMENT_ID --> TITLE
    DOCUMENT_ID --> AUTHOR
    DOCUMENT_ID --> TAGS
    DOCUMENT_ID --> CONFIDENCE

    classDef document fill:#e3f2fd
    classDef chunks fill:#f3e5f5
    classDef metadata fill:#e8f5e8

    class DOCUMENT_ID,USER_ID,CONTENT,DOCUMENT_TYPE,CREATED_AT,UPDATED_AT document
    class CHUNK_ID,CHUNK_CONTENT,CHUNK_INDEX,CHUNK_EMBEDDING chunks
    class TITLE,AUTHOR,TAGS,CONFIDENCE metadata
```

## Context Injection System

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

### Context Prioritization

```mermaid
flowchart TD
    A[Memory Contexts] --> B[Calculate Relevance Scores]
    B --> C[Rank by Relevance]
    C --> D[Filter by Threshold]
    D --> E[Group by Type]
    E --> F[Apply Priority Rules]
    F --> G[Limit Context Size]
    G --> H[Format for Injection]
    H --> I[Inject into Conversation]
```

### Context Formatting

```mermaid
graph TB
    subgraph "Context Sources"
        LTM_CONTEXT[LTM Context]
        RAG_CONTEXT[RAG Context]
        CONVERSATION_CONTEXT[Conversation Context]
        TOOL_CONTEXT[Tool Context]
    end

    subgraph "Context Processing"
        COMBINATION[Context Combination]
        PRIORITIZATION[Context Prioritization]
        FORMATTING[Context Formatting]
        VALIDATION[Context Validation]
    end

    subgraph "Context Output"
        FORMATTED_CONTEXT[Formatted Context]
        INJECTION_READY[Injection Ready]
        CONTEXT_BLOCKS[Context Blocks]
    end

    LTM_CONTEXT --> COMBINATION
    RAG_CONTEXT --> COMBINATION
    CONVERSATION_CONTEXT --> COMBINATION
    TOOL_CONTEXT --> COMBINATION
    COMBINATION --> PRIORITIZATION
    PRIORITIZATION --> FORMATTING
    FORMATTING --> VALIDATION
    VALIDATION --> FORMATTED_CONTEXT
    FORMATTED_CONTEXT --> INJECTION_READY
    INJECTION_READY --> CONTEXT_BLOCKS

    classDef sources fill:#e3f2fd
    classDef processing fill:#f3e5f5
    classDef output fill:#e8f5e8

    class LTM_CONTEXT,RAG_CONTEXT,CONVERSATION_CONTEXT,TOOL_CONTEXT sources
    class COMBINATION,PRIORITIZATION,FORMATTING,VALIDATION processing
    class FORMATTED_CONTEXT,INJECTION_READY,CONTEXT_BLOCKS output
```

## Memory Retrieval and Search

### Semantic Search Process

```mermaid
flowchart TD
    A[Search Query] --> B[Generate Query Embedding]
    B --> C[Search Vector Database]
    C --> D[Retrieve Similar Vectors]
    D --> E[Calculate Similarity Scores]
    E --> F[Rank Results]
    F --> G[Filter by Threshold]
    G --> H[Return Top Results]
```

### Memory Search Strategies

```mermaid
graph TB
    subgraph "Search Types"
        SEMANTIC_SEARCH[Semantic Search]
        KEYWORD_SEARCH[Keyword Search]
        TEMPORAL_SEARCH[Temporal Search]
        CONTEXTUAL_SEARCH[Contextual Search]
    end

    subgraph "Search Methods"
        VECTOR_SIMILARITY[Vector Similarity]
        TEXT_MATCHING[Text Matching]
        TIME_FILTERING[Time Filtering]
        CONTEXT_MATCHING[Context Matching]
    end

    subgraph "Search Results"
        RANKED_RESULTS[Ranked Results]
        RELEVANCE_SCORES[Relevance Scores]
        CONFIDENCE_LEVELS[Confidence Levels]
        METADATA[Result Metadata]
    end

    SEMANTIC_SEARCH --> VECTOR_SIMILARITY
    KEYWORD_SEARCH --> TEXT_MATCHING
    TEMPORAL_SEARCH --> TIME_FILTERING
    CONTEXTUAL_SEARCH --> CONTEXT_MATCHING
    VECTOR_SIMILARITY --> RANKED_RESULTS
    TEXT_MATCHING --> RELEVANCE_SCORES
    TIME_FILTERING --> CONFIDENCE_LEVELS
    CONTEXT_MATCHING --> METADATA

    classDef search fill:#e3f2fd
    classDef methods fill:#f3e5f5
    classDef results fill:#e8f5e8

    class SEMANTIC_SEARCH,KEYWORD_SEARCH,TEMPORAL_SEARCH,CONTEXTUAL_SEARCH search
    class VECTOR_SIMILARITY,TEXT_MATCHING,TIME_FILTERING,CONTEXT_MATCHING methods
    class RANKED_RESULTS,RELEVANCE_SCORES,CONFIDENCE_LEVELS,METADATA results
```

## Memory Management and Optimization

### Memory Cleanup Process

```mermaid
flowchart TD
    A[Memory Cleanup Trigger] --> B[Identify Old Memories]
    B --> C[Calculate Memory Value]
    C --> D[Rank by Importance]
    D --> E[Select for Cleanup]
    E --> F[Archive Important Memories]
    F --> G[Delete Low-Value Memories]
    G --> H[Update Memory Index]
    H --> I[Cleanup Complete]
```

### Memory Performance Optimization

```mermaid
graph TB
    subgraph "Performance Metrics"
        RETRIEVAL_TIME[Retrieval Time]
        STORAGE_EFFICIENCY[Storage Efficiency]
        SEARCH_ACCURACY[Search Accuracy]
        CONTEXT_RELEVANCE[Context Relevance]
    end

    subgraph "Optimization Techniques"
        CACHING[Memory Caching]
        INDEXING[Memory Indexing]
        COMPRESSION[Memory Compression]
        PARTITIONING[Memory Partitioning]
    end

    subgraph "Monitoring"
        PERFORMANCE_MONITORING[Performance Monitoring]
        MEMORY_USAGE[Memory Usage Tracking]
        SEARCH_ANALYTICS[Search Analytics]
        OPTIMIZATION_ALERTS[Optimization Alerts]
    end

    RETRIEVAL_TIME --> PERFORMANCE_MONITORING
    STORAGE_EFFICIENCY --> MEMORY_USAGE
    SEARCH_ACCURACY --> SEARCH_ANALYTICS
    CONTEXT_RELEVANCE --> OPTIMIZATION_ALERTS
    PERFORMANCE_MONITORING --> CACHING
    MEMORY_USAGE --> INDEXING
    SEARCH_ANALYTICS --> COMPRESSION
    OPTIMIZATION_ALERTS --> PARTITIONING

    classDef metrics fill:#e3f2fd
    classDef optimization fill:#f3e5f5
    classDef monitoring fill:#e8f5e8

    class RETRIEVAL_TIME,STORAGE_EFFICIENCY,SEARCH_ACCURACY,CONTEXT_RELEVANCE metrics
    class CACHING,INDEXING,COMPRESSION,PARTITIONING optimization
    class PERFORMANCE_MONITORING,MEMORY_USAGE,SEARCH_ANALYTICS,OPTIMIZATION_ALERTS monitoring
```

## Notes

### Memory System Design Principles

1. **Separation of Concerns**: LTM and RAG serve different purposes
2. **Scalability**: Memory system scales with data growth
3. **Performance**: Fast retrieval and efficient storage
4. **Accuracy**: High-quality memory retrieval and context injection
5. **Flexibility**: Support for different memory types and formats

### Memory Characteristics

- **LTM**: Structured, persistent, high-reliability memories
- **RAG**: Document-based, semantic search capabilities
- **Context Injection**: Real-time, relevant context provision
- **Memory Management**: Automatic cleanup and optimization

### Performance Considerations

- **Vector Search**: Optimized for semantic similarity
- **Caching**: Frequently accessed memories are cached
- **Indexing**: Efficient indexing for fast retrieval
- **Compression**: Memory compression for storage efficiency
- **Partitioning**: Memory partitioning for scalability

### Security and Privacy

- **Data Encryption**: All memory data is encrypted
- **Access Control**: Memory access is user-specific
- **Audit Logging**: Memory operations are logged
- **Data Retention**: Configurable memory retention policies
- **Privacy Compliance**: GDPR and privacy regulation compliance

This memory system provides a comprehensive foundation for storing, retrieving, and utilizing user information to enhance the personal assistant's capabilities.
