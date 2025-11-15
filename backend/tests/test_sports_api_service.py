"""
Unit Tests for Sports API Service
Tests both original and optimized versions
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from datetime import datetime, timedelta

# Test original SportsAPIService
class TestSportsAPIService:
    """Test suite for original SportsAPIService"""
    
    @pytest.fixture
    def sports_api_service(self):
        """Create SportsAPIService instance"""
        from services.sports_api_service import SportsAPIService
        return SportsAPIService()
    
    @pytest.mark.asyncio
    async def test_fetch_espn_data_success(self, sports_api_service, mock_sports_api):
        """Test successful ESPN data fetching"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "events": [
                    {
                        "id": "test_1",
                        "sport": {"name": "Football"},
                        "league": {"name": "NFL"},
                        "competitions": [{
                            "competitors": [
                                {"team": {"displayName": "Team A"}, "homeAway": "home"},
                                {"team": {"displayName": "Team B"}, "homeAway": "away"}
                            ],
                            "date": "2025-11-01T20:00:00Z"
                        }]
                    }
                ]
            })
            mock_response.status = 200
            mock_response.raise_for_status = MagicMock()
            
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.return_value.get.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await sports_api_service.fetch_espn_data("football")
            
            assert len(result) == 1
            assert result[0]["external_id"] == "test_1"
            assert result[0]["sport"] == "football"
            assert result[0]["home_team"] == "Team A"
    
    @pytest.mark.asyncio
    async def test_fetch_espn_data_api_error(self, sports_api_service):
        """Test ESPN API error handling"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value.get.side_effect = aiohttp.ClientError("API Error")
            
            result = await sports_api_service.fetch_espn_data("football")
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_fetch_odds_data_success(self, sports_api_service):
        """Test successful odds data fetching"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "events": [
                    {
                        "id": "odds_1",
                        "sportsbook": "DraftKings",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Team A", "price": 1.85},
                                    {"name": "Team B", "price": 2.10}
                                ]
                            }
                        ]
                    }
                ]
            })
            mock_response.status = 200
            mock_response.raise_for_status = MagicMock()
            
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.return_value.get.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await sports_api_service.fetch_odds_data("football")
            
            assert len(result) > 0

# Test optimized SportsAPIService
class TestOptimizedSportsAPIService:
    """Test suite for OptimizedSportsAPIService"""
    
    @pytest.fixture
    def optimized_service(self):
        """Create OptimizedSportsAPIService instance"""
        # from services.sports_api_service_optimized import OptimizedSportsAPIService
        # return OptimizedSportsAPIService()
        pytest.skip("Optimized sports API service removed for simplification")
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self, optimized_service):
        """Test circuit breaker in closed state"""
        # Circuit breaker should be closed initially
        assert optimized_service.circuit_breaker.state == "closed"
        assert optimized_service.circuit_breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_open_after_failures(self, optimized_service):
        """Test circuit breaker opens after repeated failures"""
        circuit_breaker = optimized_service.circuit_breaker
        
        # Simulate failures
        for _ in range(circuit_breaker.failure_threshold):
            circuit_breaker._record_failure()
        
        assert circuit_breaker.state == "open"
    
    @pytest.mark.asyncio
    async def test_concurrent_data_collection(self, optimized_service):
        """Test concurrent data collection from multiple sources"""
        with patch.object(optimized_service, '_fetch_with_retry') as mock_fetch:
            mock_fetch.return_value = [{"id": "test", "sport": "football"}]
            
            result = await optimized_service.collect_all_sports_data(["football", "basketball"])
            
            # Should have called fetch for both sports
            assert mock_fetch.call_count >= 2
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, optimized_service):
        """Test API rate limiting functionality"""
        # Test rate limiter allows requests within limit
        async with optimized_service.rate_limiter:
            pass  # Should not raise exception
        
        # Simulate hitting rate limit
        optimized_service.rate_limiter._tokens = 0
        
        start_time = asyncio.get_event_loop().time()
        async with optimized_service.rate_limiter:
            pass
        end_time = asyncio.get_event_loop().time()
        
        # Should have waited for token refill
        assert end_time > start_time
    
    @pytest.mark.asyncio
    async def test_batch_database_operations(self, optimized_service, test_session):
        """Test batch database insert operations"""
        games_data = [
            {
                "external_id": f"game_{i}",
                "sport": "football",
                "league": "NFL",
                "home_team": f"Home {i}",
                "away_team": f"Away {i}",
                "event_date": datetime.utcnow() + timedelta(days=1),
                "odds_data": {"moneyline": {"home": 1.85, "away": 2.10}}
            }
            for i in range(10)
        ]
        
        with patch.object(optimized_service, 'db') as mock_db:
            mock_db.return_value = test_session
            
            result = await optimized_service._batch_insert_games(games_data)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self, optimized_service):
        """Test service health monitoring"""
        health_status = await optimized_service.get_health_status()
        
        assert "circuit_breaker" in health_status
        assert "rate_limiter" in health_status
        assert "connection_pool" in health_status
        assert "last_update" in health_status
        
        # Health status should indicate healthy state initially
        assert health_status["circuit_breaker"]["state"] == "closed"
        assert health_status["rate_limiter"]["available_tokens"] > 0
    
    @pytest.mark.asyncio
    async def test_connection_pool_management(self, optimized_service):
        """Test HTTP connection pool management"""
        # Verify connection pool is created
        assert optimized_service.session is not None
        
        # Test connection pool limits
        connector = optimized_service.session.connector
        assert connector.limit == 100  # Total connections
        assert connector.limit_per_host == 20  # Per host
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, optimized_service):
        """Test retry mechanism with backoff"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # First call fails, second succeeds
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={"events": []})
            mock_response.status = 200
            mock_response.raise_for_status = MagicMock()
            
            mock_get.side_effect = [
                aiohttp.ClientError("Temporary failure"),
                MagicMock(__aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock())
            ]
            
            result = await optimized_service._fetch_with_retry("http://test.com")
            
            # Should have retried and succeeded
            assert mock_get.call_count == 2
            assert result == {"events": []}
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, optimized_service):
        """Test performance metrics collection"""
        # Generate some activity
        await optimized_service.get_health_status()
        
        metrics = optimized_service.get_performance_metrics()
        
        assert "api_calls_total" in metrics
        assert "average_response_time" in metrics
        assert "error_rate" in metrics
        assert "cache_hit_rate" in metrics
    
    @pytest.mark.asyncio
    async def test_memory_usage_optimization(self, optimized_service):
        """Test memory-efficient data processing"""
        # Create large dataset
        large_dataset = [
            {"id": f"item_{i}", "data": f"test_data_{i}" * 100}
            for i in range(1000)
        ]
        
        # Test generator-based processing
        processed_count = 0
        async for item in optimized_service._process_data_stream(large_dataset):
            processed_count += 1
            if processed_count >= 10:  # Process only first 10 for test
                break
        
        assert processed_count == 10
    
    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self, optimized_service):
        """Test concurrent API calls with proper semaphore limiting"""
        urls = [f"http://api{i}.test.com" for i in range(20)]
        
        with patch.object(optimized_service, '_fetch_with_retry') as mock_fetch:
            mock_fetch.return_value = {"status": "success"}
            
            results = await optimized_service._make_concurrent_requests(urls)
            
            # Should have made all requests
            assert len(results) == 20
            assert all(r["status"] == "success" for r in results)
    
    @pytest.mark.asyncio
    async def test_smart_scheduling(self, optimized_service):
        """Test smart data collection scheduling"""
        # Test different priority levels
        high_priority_tasks = ["live_odds", "game_updates"]
        low_priority_tasks = ["historical_data", "team_stats"]
        
        schedule = optimized_service._create_collection_schedule(
            high_priority_tasks, low_priority_tasks
        )
        
        # High priority tasks should be scheduled more frequently
        assert schedule["live_odds"]["interval"] < schedule["historical_data"]["interval"]
        assert schedule["game_updates"]["interval"] < schedule["team_stats"]["interval"]
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, optimized_service):
        """Test automatic error recovery mechanisms"""
        # Simulate service failure and recovery
        optimized_service.circuit_breaker.state = "open"
        
        # Wait for recovery timeout
        optimized_service.circuit_breaker.last_failure_time = (
            asyncio.get_event_loop().time() - optimized_service.circuit_breaker.recovery_timeout - 1
        )
        
        # Next successful call should close circuit
        with patch.object(optimized_service, '_fetch_with_retry') as mock_fetch:
            mock_fetch.return_value = {"status": "success"}
            
            result = await optimized_service._make_request_with_circuit_breaker("http://test.com")
            
            assert optimized_service.circuit_breaker.state == "closed"
            assert result["status"] == "success"

# Performance tests
class TestSportsAPIServicePerformance:
    """Performance tests for SportsAPIService"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self, optimized_service):
        """Test performance under concurrent load"""
        import time
        
        async def make_request():
            with patch.object(optimized_service, '_fetch_with_retry') as mock_fetch:
                mock_fetch.return_value = {"data": "test"}
                return await optimized_service._fetch_with_retry("http://test.com")
        
        # Test with 50 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 5.0  # 5 seconds max
        assert len(results) == 50
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, optimized_service):
        """Test memory usage under heavy load"""
        import gc
        import sys
        
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process large amount of data
        for batch in range(10):
            large_data = [{"id": f"item_{i}_{batch}"} for i in range(1000)]
            
            async for item in optimized_service._process_data_stream(large_data):
                pass  # Process items
        
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory growth should be reasonable
        object_growth = final_objects - initial_objects
        assert object_growth < 10000  # Allow some growth but not excessive

# Integration tests
class TestSportsAPIServiceIntegration:
    """Integration tests for SportsAPIService"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_data_collection_pipeline(self, optimized_service, test_session):
        """Test complete data collection and storage pipeline"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock successful API responses
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "events": [
                    {
                        "id": "integration_test_1",
                        "sport": {"name": "Football"},
                        "league": {"name": "NFL"},
                        "competitions": [{
                            "competitors": [
                                {"team": {"displayName": "Test Home"}, "homeAway": "home"},
                                {"team": {"displayName": "Test Away"}, "homeAway": "away"}
                            ],
                            "date": "2025-11-01T20:00:00Z"
                        }]
                    }
                ]
            })
            mock_response.status = 200
            mock_response.raise_for_status = MagicMock()
            
            mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Run full collection pipeline
            with patch.object(optimized_service, 'db') as mock_db:
                mock_db.return_value = test_session
                
                result = await optimized_service.run_complete_collection()
                
                assert result["success"] is True
                assert result["games_collected"] > 0
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_time_updates(self, optimized_service, test_redis):
        """Test real-time data updates and notifications"""
        # Simulate real-time update
        update_data = {
            "game_id": "test_game_1",
            "odds_update": {
                "moneyline": {"home": 1.90, "away": 2.05}
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with patch.object(optimized_service, 'cache_service') as mock_cache:
            mock_cache.set = AsyncMock(return_value=True)
            mock_cache.publish = AsyncMock(return_value=True)
            
            result = await optimized_service._process_real_time_update(update_data)
            
            assert result is True
            mock_cache.set.assert_called_once()
            mock_cache.publish.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])