"""
Caching utilities for embeddings and RAG operations.
"""

import logging
import time
from collections import OrderedDict
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class LRUCache:
    """
    Least Recently Used (LRU) cache implementation.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[int] = None):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of items in cache
            ttl_seconds: Time to live for cache items (None = no expiration)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        self.timestamps = {}

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key not in self.cache:
            return None

        # Check TTL
        if self.ttl_seconds is not None:
            timestamp = self.timestamps.get(key, 0)
            if time.time() - timestamp > self.ttl_seconds:
                self.delete(key)
                return None

        # Move to end (most recently used)
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def put(self, key: str, value: Any):
        """Put item in cache."""
        # Remove if already exists
        if key in self.cache:
            self.cache.pop(key)

        # Add new item
        self.cache[key] = value
        self.timestamps[key] = time.time()

        # Remove oldest if cache is full
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            self.delete(oldest_key)

    def delete(self, key: str):
        """Delete item from cache."""
        if key in self.cache:
            self.cache.pop(key)
        if key in self.timestamps:
            del self.timestamps[key]

    def clear(self):
        """Clear all items from cache."""
        self.cache.clear()
        self.timestamps.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

    def keys(self):
        """Get all cache keys."""
        return list(self.cache.keys())


class EmbeddingCache:
    """
    Specialized cache for embeddings with metadata.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize embedding cache.

        Args:
            max_size: Maximum number of embeddings to cache
            ttl_seconds: Time to live for embeddings (1 hour default)
        """
        self.cache = LRUCache(max_size=max_size, ttl_seconds=ttl_seconds)
        self.stats = {"hits": 0, "misses": 0, "total_requests": 0}

    def get_embedding(self, text: str) -> Optional[list]:
        """Get cached embedding for text."""
        self.stats["total_requests"] += 1

        cache_key = self._get_cache_key(text)
        embedding = self.cache.get(cache_key)

        if embedding is not None:
            self.stats["hits"] += 1
            logger.debug(f"Embedding cache hit for text of length {len(text)}")
        else:
            self.stats["misses"] += 1
            logger.debug(f"Embedding cache miss for text of length {len(text)}")

        return embedding

    def put_embedding(self, text: str, embedding: list):
        """Cache embedding for text."""
        cache_key = self._get_cache_key(text)
        self.cache.put(cache_key, embedding)
        logger.debug(f"Cached embedding for text of length {len(text)}")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return str(hash(text))

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.stats["total_requests"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0

        return {**self.stats, "hit_rate": hit_rate, "cache_size": self.cache.size()}

    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.stats = {"hits": 0, "misses": 0, "total_requests": 0}
        logger.info("Embedding cache cleared")
