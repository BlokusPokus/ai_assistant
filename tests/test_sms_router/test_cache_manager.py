"""
Unit tests for CacheManager service.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from personal_assistant.sms_router.services.cache_manager import CacheManager


class TestCacheManager:
    """Test cases for CacheManager service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache_manager = CacheManager(default_ttl=3600)

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test setting and getting cache values."""
        # Set a value
        success = await self.cache_manager.set("test_key", "test_value")
        assert success is True
        
        # Get the value
        value = await self.cache_manager.get("test_key")
        assert value == "test_value"
        
        # Test with custom TTL
        success = await self.cache_manager.set("test_key_ttl", "test_value_ttl", ttl=7200)
        assert success is True
        
        value = await self.cache_manager.get("test_key_ttl")
        assert value == "test_value_ttl"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        """Test getting non-existent cache keys."""
        value = await self.cache_manager.get("nonexistent_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test deleting cache keys."""
        # Set a value
        await self.cache_manager.set("delete_key", "delete_value")
        
        # Verify it exists
        value = await self.cache_manager.get("delete_key")
        assert value == "delete_value"
        
        # Delete it
        success = await self.cache_manager.delete("delete_key")
        assert success is True
        
        # Verify it's gone
        value = await self.cache_manager.get("delete_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_clear(self):
        """Test clearing all cache entries."""
        # Set multiple values
        await self.cache_manager.set("key1", "value1")
        await self.cache_manager.set("key2", "value2")
        await self.cache_manager.set("key3", "value3")
        
        # Verify they exist
        assert await self.cache_manager.get("key1") == "value1"
        assert await self.cache_manager.get("key2") == "value2"
        assert await self.cache_manager.get("key3") == "value3"
        
        # Clear all
        success = await self.cache_manager.clear()
        assert success is True
        
        # Verify they're gone
        assert await self.cache_manager.get("key1") is None
        assert await self.cache_manager.get("key2") is None
        assert await self.cache_manager.get("key3") is None

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting cache statistics."""
        # Set some values
        await self.cache_manager.set("key1", "value1")
        await self.cache_manager.set("key2", "value2")
        
        # Get stats
        stats = await self.cache_manager.get_stats()
        
        assert "total_keys" in stats
        assert "expired_keys" in stats
        assert "active_keys" in stats
        assert "default_ttl" in stats
        
        assert stats["total_keys"] == 2
        assert stats["active_keys"] == 2
        assert stats["default_ttl"] == 3600

    @pytest.mark.asyncio
    async def test_expiration(self):
        """Test cache expiration."""
        # Set a value with very short TTL
        success = await self.cache_manager.set("expire_key", "expire_value", ttl=1)
        assert success is True
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Value should be expired
        value = await self.cache_manager.get("expire_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_different_data_types(self):
        """Test caching different data types."""
        test_data = [
            ("string_key", "string_value"),
            ("int_key", 42),
            ("float_key", 3.14),
            ("bool_key", True),
            ("list_key", [1, 2, 3]),
            ("dict_key", {"a": 1, "b": 2}),
            ("none_key", None),
        ]
        
        for key, value in test_data:
            success = await self.cache_manager.set(key, value)
            assert success is True
            
            retrieved = await self.cache_manager.get(key)
            assert retrieved == value

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in cache operations."""
        # Test with invalid TTL
        success = await self.cache_manager.set("error_key", "error_value", ttl=-1)
        assert success is True  # Should still work with invalid TTL
        
        # Test with None key
        success = await self.cache_manager.set(None, "value")
        assert success is False
        
        # Test getting with None key
        value = await self.cache_manager.get(None)
        assert value is None

    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test concurrent cache access."""
        async def set_value(key, value):
            return await self.cache_manager.set(key, value)
        
        async def get_value(key):
            return await self.cache_manager.get(key)
        
        # Set multiple values concurrently
        tasks = [
            set_value(f"concurrent_key_{i}", f"value_{i}")
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        assert all(results)
        
        # Get multiple values concurrently
        get_tasks = [
            get_value(f"concurrent_key_{i}")
            for i in range(10)
        ]
        
        values = await asyncio.gather(*get_tasks)
        assert values == [f"value_{i}" for i in range(10)]
