# Enhanced RAG System

## Overview

The Enhanced RAG (Retrieval-Augmented Generation) system provides semantic search and retrieval capabilities using real Gemini embeddings instead of fake ones. It's designed to integrate with Notion notes and provide personalized context to the AI agent.

## Features

### ✅ Phase 1 Complete

- **Real Gemini Embeddings**: Replaced fake embeddings with real semantic vectors
- **Enhanced Caching**: LRU cache with TTL for embedding storage
- **Content Extraction**: Notion content extraction and normalization
- **Improved Search**: Better error handling and result ranking
- **Configuration**: RAG-specific settings and environment variables

### 🚧 Phase 2 (In Progress)

- **Notion Indexing**: Automatic note indexing in RAG system
- **Real-time Sync**: Synchronization between Notion and RAG
- **Batch Operations**: Efficient bulk indexing capabilities

### 📋 Phase 3 (Planned)

- **Multi-source Queries**: Combined memory and Notion search
- **Smart Context**: Intelligent context selection and injection
- **Performance Optimization**: Advanced caching and search optimization

## Architecture

```
User Query → Gemini Embedding → Vector Search → Result Ranking → Context Injection
     ↓              ↓              ↓              ↓              ↓
  Text Input   Real Vectors   Database Query   Relevance Score   Agent Context
```

## Components

### Core Modules

- **`retriever.py`**: Main RAG query and indexing functions
- **`embeddings/`**: Embedding generation and caching
  - `gemini_embeddings.py`: Gemini API integration
  - `cache.py`: LRU cache with TTL
- **`notion_extractor.py`**: Notion content extraction and parsing

### Key Functions

- `embed_text(text)`: Generate real embeddings using Gemini
- `query_knowledge_base(user_id, query)`: Search for relevant documents
- `embed_and_index(document, metadata)`: Index new documents
- `get_embedding_stats()`: Get system performance statistics

## Configuration

### Environment Variables

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional RAG settings
RAG_MAX_CONTEXT_LENGTH=2000
RAG_NOTION_INDEXING_ENABLED=true
RAG_BATCH_INDEX_SIZE=10
RAG_EMBEDDING_CACHE_SIZE=1000
RAG_EMBEDDING_CACHE_TTL=3600
RAG_MAX_RESULTS=5
```

### Settings

The system automatically loads configuration from:

1. `config/{ENVIRONMENT}.env` (e.g., `config/development.env`)
2. Root `.env` file as fallback
3. Environment variables

## Usage

### Basic Embedding Generation

```python
from personal_assistant.rag import embed_text

# Generate embedding for text
embedding = await embed_text("Your text here")
print(f"Embedding length: {len(embedding)}")
```

### RAG Query

```python
from personal_assistant.rag import query_knowledge_base

# Search for relevant documents
results = await query_knowledge_base("user123", "project planning")
for result in results:
    print(f"Content: {result['content']}")
    print(f"Source: {result['metadata']['source']}")
```

### Content Extraction

```python
from personal_assistant.rag import NotionContentExtractor

extractor = NotionContentExtractor()
content = await extractor.extract_note_content("note_id", "user_id")
print(f"Title: {content['title']}")
print(f"Tags: {content['tags']}")
```

## Testing

Run the test suite to verify system functionality:

```bash
cd src/personal_assistant/rag
python test_enhanced_rag.py
```

## Performance

### Caching

- **Embedding Cache**: LRU cache with configurable TTL
- **Cache Hit Rate**: Monitored and reported via `get_embedding_stats()`
- **Memory Usage**: Configurable cache size limits

### Rate Limiting

- **API Calls**: Automatic fallback to fake embeddings if Gemini fails
- **Error Handling**: Graceful degradation with logging
- **Retry Logic**: Built-in error recovery

## Integration Points

### Existing Systems

- **Agent Core**: RAG context injection in `agent.py`
- **Memory System**: Vector database storage and retrieval
- **Tool Registry**: Notion tools integration

### Notion Integration

- **Content Access**: Uses existing `NotionNotesTool`
- **Metadata Preservation**: Maintains note structure and properties
- **Real-time Updates**: Automatic re-indexing on content changes

## Monitoring

### Statistics

```python
from personal_assistant.rag import get_embedding_stats

stats = await get_embedding_stats()
print(f"Cache hit rate: {stats['cache_stats']['hit_rate']:.2%}")
print(f"Total requests: {stats['cache_stats']['total_requests']}")
```

### Logging

The system provides detailed logging at the `RAG_LOG_LEVEL` setting:

- **DEBUG**: Detailed embedding and search operations
- **INFO**: High-level operations and statistics
- **WARNING**: Fallback operations and non-critical issues
- **ERROR**: Critical failures and exceptions

## Troubleshooting

### Common Issues

1. **No Embeddings Generated**

   - Check `GOOGLE_API_KEY` is set
   - Verify Gemini API access and quotas
   - Check logs for specific error messages

2. **Slow Performance**

   - Monitor cache hit rates
   - Adjust cache size and TTL settings
   - Check database query performance

3. **Content Extraction Failures**
   - Verify Notion API access
   - Check note ID validity
   - Review content format compatibility

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger("rag").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

- **Advanced Caching**: Redis-based distributed caching
- **Vector Optimization**: Approximate nearest neighbor search
- **Content Analysis**: AI-powered content summarization
- **User Preferences**: Personalized search and ranking
- **Analytics**: Usage patterns and performance metrics

### Performance Targets

- **Query Latency**: < 2 seconds for RAG queries
- **Cache Hit Rate**: > 80% for repeated queries
- **Indexing Speed**: < 5 seconds per note
- **Memory Usage**: < 100MB for embedding cache

## Contributing

When adding new features:

1. **Follow Patterns**: Use existing async/await patterns
2. **Error Handling**: Implement proper exception handling
3. **Logging**: Add appropriate debug and info logs
4. **Testing**: Include tests for new functionality
5. **Documentation**: Update this README and docstrings
