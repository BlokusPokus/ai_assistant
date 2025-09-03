# Configure module logger
from ..config.logging_config import get_logger

# Import document processor
from .document_processor import DocumentProcessor

# Import embedding models
from .embeddings import EmbeddingCache, GeminiEmbeddings, LRUCache

# Import content extractor
from .notion_extractor import NotionContentExtractor

# Import main RAG functions
from .retriever import (
    embed_and_index,
    embed_text,
    generate_embeddings_for_content,
    generate_missing_embeddings,
    get_embedding_model,
    get_embedding_stats,
    get_query_performance_stats,
    query_knowledge_base,
)

logger = get_logger("rag")

__all__ = [
    "query_knowledge_base",
    "embed_text",
    "embed_and_index",
    "get_embedding_stats",
    "get_embedding_model",
    "generate_embeddings_for_content",
    "generate_missing_embeddings",
    "get_query_performance_stats",
    "GeminiEmbeddings",
    "LRUCache",
    "EmbeddingCache",
    "NotionContentExtractor",
    "DocumentProcessor",
]
