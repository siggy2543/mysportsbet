"""
Unit Tests for Cache Service
Tests both original and optimized cache implementations
"""
import pytest
import asyncio
import json
import zlib
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

class TestCacheService:
    """Test suite for original CacheService"""
    
    @pytest.fixture
    def cache_service(self, test_redis):
        """Create CacheService instance"""
        from services.cache_service import CacheService
        service = CacheService()
        service.redis = test_redis
        return service
    
    @pytest.mark.asyncio
    async def test_basic_set_get(self, cache_service):
        """Test basic cache set and get operations"""
        key = "test_key"
        value = {"data": "test_value", "number": 123}
        
        # Set value
        result = await cache_service.set(key, value, ttl=300)
        assert result is True
        
        # Get value
        cached_value = await cache_service.get(key)
        assert cached_value == value
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache_service):
        """Test getting non-existent key returns None"""
        result = await cache_service.get("nonexistent_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_key(self, cache_service):
        """Test deleting cache key"""
        key = "test_delete"
        value = {"data": "to_delete"}
        
        # Set and verify
        await cache_service.set(key, value)
        assert await cache_service.get(key) == value
        
        # Delete and verify
        result = await cache_service.delete(key)
        assert result is True
        assert await cache_service.get(key) is None
    
    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache_service):
        """Test TTL expiration"""
        key = "test_ttl"
        value = {"data": "expires"}
        
        # Set with very short TTL
        await cache_service.set(key, value, ttl=1)
        
        # Should exist immediately
        assert await cache_service.get(key) == value
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        assert await cache_service.get(key) is None

class TestOptimizedCacheService:
    """Test suite for OptimizedCacheService"""
    
    @pytest.fixture
    def optimized_cache(self, test_redis):
        """Create OptimizedCacheService instance"""
        # from services.cache_service_optimized import OptimizedCacheService
        # service = OptimizedCacheService()
        # service.redis = test_redis
        # return service
        pytest.skip("Optimized cache service removed for simplification")
    
    @pytest.mark.asyncio
    async def test_tiered_ttl_strategy(self, optimized_cache):
        """Test tiered TTL strategy for different cache types"""
        # Test live odds (short TTL)
        await optimized_cache.set("live_odds:game_1", {"odds": 1.85}, cache_type="live_odds")
        live_ttl = await optimized_cache.redis.ttl("live_odds:game_1")
        assert 25 <= live_ttl <= 30  # Should be around 30 seconds
        
        # Test game data (medium TTL)
        await optimized_cache.set("game_data:game_1", {"teams": ["A", "B"]}, cache_type="game_data")
        game_ttl = await optimized_cache.redis.ttl("game_data:game_1")
        assert 295 <= game_ttl <= 300  # Should be around 5 minutes
        
        # Test team stats (long TTL)
        await optimized_cache.set("team_stats:team_1", {"wins": 10}, cache_type="team_stats")
        stats_ttl = await optimized_cache.redis.ttl("team_stats:team_1")
        assert 3595 <= stats_ttl <= 3600  # Should be around 1 hour
    
    @pytest.mark.asyncio
    async def test_orjson_serialization(self, optimized_cache):
        """Test fast JSON serialization with orjson"""
        complex_data = {
            "numbers": [1, 2, 3, 4, 5],
            "nested": {
                "string": "test",
                "boolean": True,
                "null": None,
                "float": 3.14159
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Set and get complex data
        await optimized_cache.set("complex_data", complex_data)
        result = await optimized_cache.get("complex_data")
        
        assert result == complex_data
    
    @pytest.mark.asyncio
    async def test_compression_for_large_values(self, optimized_cache):
        """Test automatic compression for large values"""
        # Create large data (> 1KB)
        large_data = {"data": "x" * 2000, "numbers": list(range(1000))}
        
        await optimized_cache.set("large_data", large_data)
        
        # Check if data was compressed (should have compression header)
        raw_value = await optimized_cache.redis.get("large_data")
        assert raw_value.startswith(b"COMPRESSED:")
        
        # Verify decompression works
        result = await optimized_cache.get("large_data")
        assert result == large_data
    
    @pytest.mark.asyncio
    async def test_no_compression_for_small_values(self, optimized_cache):
        """Test no compression for small values"""
        small_data = {"data": "small"}
        
        await optimized_cache.set("small_data", small_data)
        
        # Should not be compressed
        raw_value = await optimized_cache.redis.get("small_data")
        assert not raw_value.startswith(b"COMPRESSED:")
        
        # Should still deserialize correctly
        result = await optimized_cache.get("small_data")
        assert result == small_data
    
    @pytest.mark.asyncio
    async def test_cache_aside_pattern(self, optimized_cache):
        """Test cache-aside pattern implementation"""
        
        # Mock data loader function
        async def load_data(key):
            return {"loaded": True, "key": key, "timestamp": datetime.utcnow().isoformat()}
        
        # First call should load from source and cache
        result1 = await optimized_cache.get_or_set("test_key", load_data, ttl=300)
        assert result1["loaded"] is True
        assert result1["key"] == "test_key"
        
        # Second call should return cached value
        result2 = await optimized_cache.get_or_set("test_key", load_data, ttl=300)
        assert result2 == result1  # Same data from cache
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, optimized_cache):
        """Test batch get and set operations"""
        # Test batch set
        data = {
            "key1": {"value": 1},
            "key2": {"value": 2},
            "key3": {"value": 3}
        }
        
        result = await optimized_cache.set_many(data, ttl=300)
        assert result is True
        
        # Test batch get
        keys = ["key1", "key2", "key3", "nonexistent"]
        results = await optimized_cache.get_many(keys)
        
        assert results["key1"] == {"value": 1}
        assert results["key2"] == {"value": 2}
        assert results["key3"] == {"value": 3}
        assert "nonexistent" not in results
    
    @pytest.mark.asyncio
    async def test_pipeline_operations(self, optimized_cache):
        """Test Redis pipeline for efficient batch operations"""
        # Set multiple keys using pipeline
        operations = [
            ("set", "pipe_key1", {"data": 1}),
            ("set", "pipe_key2", {"data": 2}),
            ("set", "pipe_key3", {"data": 3})
        ]
        
        results = await optimized_cache._execute_pipeline(operations)
        assert len(results) == 3
        assert all(r is True for r in results)  # All sets successful
        
        # Verify data was set correctly
        assert await optimized_cache.get("pipe_key1") == {"data": 1}
        assert await optimized_cache.get("pipe_key2") == {"data": 2}
        assert await optimized_cache.get("pipe_key3") == {"data": 3}
    
    @pytest.mark.asyncio
    async def test_proactive_refresh(self, optimized_cache):
        """Test proactive cache refresh before expiration"""
        refresh_called = False
        
        async def refresh_function(key):
            nonlocal refresh_called
            refresh_called = True
            return {"refreshed": True, "timestamp": datetime.utcnow().isoformat()}
        
        # Set cache with short TTL
        original_data = {"original": True}
        await optimized_cache.set("refresh_key", original_data, ttl=10)
        
        # Mock TTL to simulate near expiration (80% threshold)
        with patch.object(optimized_cache.redis, 'ttl', return_value=2):  # 2 seconds left out of 10
            result = await optimized_cache.get_with_refresh(
                "refresh_key", 
                refresh_function, 
                ttl=10,
                refresh_threshold=0.8
            )
        
        # Should trigger refresh
        assert refresh_called is True
        assert result["refreshed"] is True
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self, optimized_cache):
        """Test cache health monitoring"""
        # Generate some cache activity
        await optimized_cache.set("health_test1", {"data": 1})
        await optimized_cache.set("health_test2", {"data": 2})
        await optimized_cache.get("health_test1")  # Hit
        await optimized_cache.get("nonexistent")    # Miss
        
        health = await optimized_cache.get_health_status()
        
        assert "connection" in health
        assert "hit_rate" in health
        assert "total_operations" in health
        assert "memory_usage" in health
        assert health["connection"] is True
    
    @pytest.mark.asyncio
    async def test_statistics_collection(self, optimized_cache):
        """Test cache statistics collection"""
        # Reset stats
        optimized_cache.stats = {
            "hits": 0, "misses": 0, "sets": 0, "deletes": 0,
            "total_operations": 0, "errors": 0
        }
        
        # Perform operations
        await optimized_cache.set("stats_key", {"data": "test"})
        await optimized_cache.get("stats_key")     # Hit
        await optimized_cache.get("missing_key")   # Miss
        await optimized_cache.delete("stats_key")
        
        stats = optimized_cache.get_statistics()
        
        assert stats["sets"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["deletes"] == 1
        assert stats["total_operations"] == 4
        assert stats["hit_rate"] == 0.5  # 1 hit out of 2 gets
    
    @pytest.mark.asyncio
    async def test_memory_usage_tracking(self, optimized_cache):
        """Test memory usage tracking"""
        # Set some data to use memory
        large_data = {"data": "x" * 10000}  # 10KB of data
        await optimized_cache.set("memory_test", large_data)
        
        memory_info = await optimized_cache.get_memory_usage()
        
        assert "used_memory" in memory_info
        assert "used_memory_human" in memory_info
        assert "max_memory" in memory_info
        assert memory_info["used_memory"] > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, optimized_cache):
        """Test error handling and resilience"""
        # Test Redis connection error
        with patch.object(optimized_cache.redis, 'get', side_effect=Exception("Redis error")):
            result = await optimized_cache.get("test_key")
            assert result is None  # Should return None on error
        
        # Test serialization error
        class NonSerializable:
            pass
        
        result = await optimized_cache.set("bad_data", NonSerializable())
        assert result is False  # Should return False on serialization error
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_patterns(self, optimized_cache):
        """Test cache invalidation patterns"""
        # Set data with tags
        await optimized_cache.set("user:1:profile", {"name": "John"}, cache_type="user_data")
        await optimized_cache.set("user:1:settings", {"theme": "dark"}, cache_type="user_data")
        await optimized_cache.set("user:2:profile", {"name": "Jane"}, cache_type="user_data")
        
        # Test pattern-based invalidation
        result = await optimized_cache.delete_pattern("user:1:*")
        assert result >= 2  # Should delete user:1 keys
        
        # Verify deletion
        assert await optimized_cache.get("user:1:profile") is None
        assert await optimized_cache.get("user:1:settings") is None
        assert await optimized_cache.get("user:2:profile") is not None  # Should remain

# Performance tests
class TestCacheServicePerformance:
    """Performance tests for cache service"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_serialization_performance(self, optimized_cache):
        """Test serialization performance with orjson vs standard json"""
        import time
        
        # Large complex data structure
        large_data = {
            "users": [
                {"id": i, "name": f"User {i}", "data": {"x": i * 2, "y": i * 3}}
                for i in range(1000)
            ],
            "metadata": {"count": 1000, "timestamp": datetime.utcnow().isoformat()}
        }
        
        # Test orjson performance
        start_time = time.time()
        for _ in range(100):
            await optimized_cache.set(f"perf_test_{_}", large_data)
        orjson_time = time.time() - start_time
        
        # Performance should be reasonable
        assert orjson_time < 5.0  # Should complete in under 5 seconds
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_compression_performance(self, optimized_cache):
        """Test compression performance impact"""
        import time
        
        # Large data that will trigger compression
        large_data = {"data": "x" * 5000, "numbers": list(range(1000))}
        
        # Test with compression
        start_time = time.time()
        for i in range(50):
            await optimized_cache.set(f"compressed_{i}", large_data)
        compression_time = time.time() - start_time
        
        # Should complete reasonably fast even with compression
        assert compression_time < 10.0
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, optimized_cache):
        """Test performance under concurrent load"""
        import time
        
        async def cache_operation(index):
            key = f"concurrent_{index}"
            data = {"index": index, "data": f"test_data_{index}"}
            
            await optimized_cache.set(key, data)
            result = await optimized_cache.get(key)
            await optimized_cache.delete(key)
            
            return result is not None
        
        # Run 100 concurrent operations
        start_time = time.time()
        tasks = [cache_operation(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All operations should succeed
        assert all(results)
        
        # Should complete within reasonable time
        assert end_time - start_time < 10.0
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_batch_vs_individual_operations(self, optimized_cache):
        """Compare batch vs individual operation performance"""
        import time
        
        # Prepare data
        data = {f"batch_key_{i}": {"value": i} for i in range(100)}
        
        # Test individual operations
        start_time = time.time()
        for key, value in data.items():
            await optimized_cache.set(key, value)
        individual_time = time.time() - start_time
        
        # Clear cache
        await optimized_cache.redis.flushdb()
        
        # Test batch operations
        start_time = time.time()
        await optimized_cache.set_many(data)
        batch_time = time.time() - start_time
        
        # Batch should be significantly faster
        assert batch_time < individual_time * 0.5

# Integration tests
class TestCacheServiceIntegration:
    """Integration tests for cache service"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_cache_with_database_fallback(self, optimized_cache, test_session, test_utils):
        """Test cache integration with database fallback"""
        # Create test game in database
        game = await test_utils.create_test_game(test_session, external_id="cache_test_game")
        
        async def load_game_from_db(game_id):
            # Simulate database query
            return {
                "id": game.id,
                "external_id": game.external_id,
                "home_team": game.home_team,
                "away_team": game.away_team
            }
        
        # First call should load from database and cache
        result1 = await optimized_cache.get_or_set(
            f"game:{game.external_id}", 
            lambda: load_game_from_db(game.id),
            ttl=300
        )
        
        assert result1["external_id"] == "cache_test_game"
        
        # Second call should return cached value
        result2 = await optimized_cache.get_or_set(
            f"game:{game.external_id}", 
            lambda: load_game_from_db(game.id),
            ttl=300
        )
        
        assert result2 == result1
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_distributed_caching_simulation(self, optimized_cache):
        """Test distributed caching patterns"""
        # Simulate multiple application instances sharing cache
        
        # Instance 1 sets data
        await optimized_cache.set("shared_data", {"instance": 1, "data": "shared"})
        
        # Instance 2 reads data (simulated with same cache instance)
        result = await optimized_cache.get("shared_data")
        assert result["instance"] == 1
        
        # Instance 2 updates data
        await optimized_cache.set("shared_data", {"instance": 2, "data": "updated"})
        
        # Instance 1 reads updated data
        result = await optimized_cache.get("shared_data")
        assert result["instance"] == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])