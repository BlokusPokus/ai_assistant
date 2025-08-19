# Configure module logger
from ..config.logging_config import get_logger

# Import main RAG functions
from .retriever import (
    query_knowledge_base,
    embed_text,
    embed_and_index,
    get_embedding_stats,
    get_embedding_model,
    generate_embeddings_for_content,
    generate_missing_embeddings,
    get_query_performance_stats
)

# Import embedding models
from .embeddings import GeminiEmbeddings, LRUCache, EmbeddingCache

# Import content extractor
from .notion_extractor import NotionContentExtractor

# Import document processor
from .document_processor import DocumentProcessor

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
    "DocumentProcessor"
]
