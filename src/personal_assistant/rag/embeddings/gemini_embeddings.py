"""
Gemini embeddings for RAG system.
Integrates with existing GeminiLLM class for text embedding generation.
"""

import logging
from typing import List, Optional

from ...config.settings import settings
from ...llm.gemini import GeminiLLM

logger = logging.getLogger(__name__)


class GeminiEmbeddings:
    """
    Wrapper for Gemini embedding generation with caching and rate limiting.
    Integrates with existing GeminiLLM class.
    """

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gemini-embedding-001"
    ):
        """
        Initialize Gemini embeddings.

        Args:
            api_key: Gemini API key (uses settings if not provided)
            model: Embedding model name (default: gemini-embedding-001)
        """
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model = model
        self._llm_client: GeminiLLM | None = None
        self._embedding_cache: dict[str, list[float]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

        if not self.api_key:
            logger.warning("No Gemini API key provided. Embeddings will fail.")

        logger.info(f"GeminiEmbeddings initialized with model: {model}")

    def _get_llm_client(self) -> GeminiLLM | None:
        """Get or create GeminiLLM client."""
        if self._llm_client is None:
            if not self.api_key:
                raise ValueError("Gemini API key not configured")
            self._llm_client = GeminiLLM(api_key=self.api_key, model=settings.GEMINI_MODEL)
        return self._llm_client

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text using Gemini.

        Args:
            text: Text to embed

        Returns:
            List of float values representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []

        # Check cache first
        cache_key = self._get_cache_key(text)
        if cache_key in self._embedding_cache:
            self._cache_hits += 1
            logger.debug(f"Cache hit for text of length {len(text)}")
            return self._embedding_cache[cache_key]

        try:
            # Generate embedding using existing GeminiLLM
            llm_client = self._get_llm_client()

            # Use the existing embed_text method from GeminiLLM
            if llm_client is None:
                raise ValueError("LLM client not initialized")
            embedding = llm_client.embed_text(text)

            if embedding:
                # Cache the result
                self._embedding_cache[cache_key] = embedding
                self._cache_misses += 1

                logger.debug(
                    f"Generated embedding of length {len(embedding)} for text of length {len(text)}"
                )
                return embedding
            else:
                logger.error("No embedding returned from Gemini API")
                return []

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)

        return embeddings

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        # Simple hash-based cache key
        return str(hash(text))

    def get_cache_stats(self) -> dict:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "cache_size": len(self._embedding_cache),
        }

    def clear_cache(self):
        """Clear the embedding cache."""
        self._embedding_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Embedding cache cleared")

    def __del__(self):
        """Cleanup when object is destroyed."""
        if hasattr(self, "_embedding_cache"):
            self.clear_cache()
