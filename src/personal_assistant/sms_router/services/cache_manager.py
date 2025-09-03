"""
Cache manager for SMS Router Service.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """Simple in-memory cache manager for SMS Router Service."""

    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache manager.

        Args:
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.cache = {}
        self.default_ttl = default_ttl
        self.timestamps = {}

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            return None

        # Check if expired
        if key in self.timestamps:
            if datetime.now() > self.timestamps[key]:
                # Expired, remove from cache
                del self.cache[key]
                del self.timestamps[key]
                return None

        return self.cache[key]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate key
            if key is None:
                logger.error("Cannot cache with None key")
                return False

            ttl = ttl or self.default_ttl
            expiry = datetime.now() + timedelta(seconds=ttl)

            self.cache[key] = value
            self.timestamps[key] = expiry

            logger.debug(f"Cached key '{key}' with TTL {ttl}s")
            return True

        except Exception as e:
            logger.error(f"Error setting cache key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            if key in self.cache:
                del self.cache[key]
            if key in self.timestamps:
                del self.timestamps[key]

            logger.debug(f"Deleted cache key '{key}'")
            return True

        except Exception as e:
            logger.error(f"Error deleting cache key '{key}': {e}")
            return False

    async def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.cache.clear()
            self.timestamps.clear()

            logger.info("Cache cleared")
            return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    async def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        now = datetime.now()
        expired_keys = [key for key, expiry in self.timestamps.items() if now > expiry]

        return {
            "total_keys": len(self.cache),
            "expired_keys": len(expired_keys),
            "active_keys": len(self.cache) - len(expired_keys),
            "default_ttl": self.default_ttl,
        }

    def _cleanup_expired(self):
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_keys = [key for key, expiry in self.timestamps.items() if now > expiry]

        for key in expired_keys:
            del self.cache[key]
            del self.timestamps[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
