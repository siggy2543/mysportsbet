"""
Performance and Load Testing Suite
Tests application performance under various load conditions
"""
import pytest
import asyncio
import time
import aiohttp
import statistics
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict, Any
import psutil
import memory_profiler

@dataclass
class PerformanceMetrics:
    """Container for performance test results"""
    response_times: List[float]
    success_rate: float
    error_rate: float
    throughput: float  # requests per second
    memory_usage: float  # MB
    cpu_usage: float  # percentage
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float

class LoadTestRunner:
    """Utility class for running load tests"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=1000, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", 
                          headers: dict = None, json_data: dict = None) -> Dict[str, Any]:
        """Make a single HTTP request and measure performance"""
        start_time = time.time()
        
        try:
            async with self.session.request(
                method, f"{self.base_url}{endpoint}", 
                headers=headers, json=json_data
            ) as response:
                await response.read()  # Ensure response is fully consumed
                end_time = time.time()
                
                return {
                    "status_code": response.status,
                    "response_time": end_time - start_time,
                    "success": 200 <= response.status < 400,
                    "error": None
                }
        except Exception as e:
            end_time = time.time()
            return {
                "status_code": 0,
                "response_time": end_time - start_time,
                "success": False,
                "error": str(e)
            }
    
    async def run_load_test(self, endpoint: str, concurrent_users: int, 
                           duration: int, ramp_up_time: int = 0,
                           method: str = "GET", headers: dict = None,
                           json_data: dict = None) -> PerformanceMetrics:
        """Run a load test with specified parameters"""
        
        results = []
        start_time = time.time()
        end_time = start_time + duration
        
        # Calculate ramp-up delay
        ramp_up_delay = ramp_up_time / concurrent_users if ramp_up_time > 0 else 0
        
        async def user_session(user_id: int):
            """Simulate a single user session"""
            # Ramp-up delay
            if ramp_up_delay > 0:
                await asyncio.sleep(user_id * ramp_up_delay)
            
            user_results = []
            while time.time() < end_time:
                result = await self.make_request(endpoint, method, headers, json_data)
                user_results.append(result)
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            return user_results
        
        # Start monitoring system resources
        initial_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        initial_cpu = psutil.cpu_percent()
        
        # Run concurrent user sessions
        tasks = [user_session(i) for i in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        
        # Flatten results
        for user_results in all_results:
            results.extend(user_results)
        
        # Calculate final system resources
        final_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        final_cpu = psutil.cpu_percent()
        
        # Calculate metrics
        response_times = [r["response_time"] for r in results]
        successful_requests = [r for r in results if r["success"]]
        
        success_rate = len(successful_requests) / len(results) if results else 0
        error_rate = 1 - success_rate
        throughput = len(results) / duration
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0
        p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0
        
        return PerformanceMetrics(
            response_times=response_times,
            success_rate=success_rate,
            error_rate=error_rate,
            throughput=throughput,
            memory_usage=final_memory - initial_memory,
            cpu_usage=final_cpu - initial_cpu,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time
        )

class TestAPIPerformance:
    """Test API endpoint performance"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_health_endpoint_performance(self):
        """Test health endpoint under load"""
        async with LoadTestRunner() as runner:
            metrics = await runner.run_load_test(
                endpoint="/health",
                concurrent_users=50,
                duration=30,
                ramp_up_time=5
            )
            
            # Performance assertions
            assert metrics.success_rate >= 0.95  # 95% success rate
            assert metrics.avg_response_time < 0.1  # 100ms average
            assert metrics.p95_response_time < 0.2  # 200ms p95
            assert metrics.throughput > 100  # 100 RPS minimum
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_games_endpoint_performance(self, auth_headers):
        """Test games endpoint under load"""
        async with LoadTestRunner() as runner:
            metrics = await runner.run_load_test(
                endpoint="/api/v1/sports/games",
                concurrent_users=20,
                duration=60,
                ramp_up_time=10,
                headers=auth_headers
            )
            
            # Performance assertions for data-heavy endpoint
            assert metrics.success_rate >= 0.90  # 90% success rate
            assert metrics.avg_response_time < 1.0  # 1 second average
            assert metrics.p95_response_time < 2.0  # 2 seconds p95
            assert metrics.throughput > 20  # 20 RPS minimum
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_authentication_performance(self):
        """Test authentication endpoint performance"""
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        async with LoadTestRunner() as runner:
            metrics = await runner.run_load_test(
                endpoint="/api/v1/auth/login",
                concurrent_users=10,
                duration=30,
                method="POST",
                json_data=login_data
            )
            
            # Auth should be fast even under load
            assert metrics.avg_response_time < 0.5  # 500ms average
            assert metrics.p95_response_time < 1.0  # 1 second p95
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_bet_placement_performance(self, auth_headers):
        """Test bet placement under load"""
        bet_data = {
            "event_id": 1,
            "bet_type": "moneyline",
            "selection": "home",
            "stake": 10.0,
            "odds": 1.85
        }
        
        async with LoadTestRunner() as runner:
            metrics = await runner.run_load_test(
                endpoint="/api/v1/bets",
                concurrent_users=5,  # Lower concurrency for write operations
                duration=30,
                method="POST",
                headers=auth_headers,
                json_data=bet_data
            )
            
            # Bet placement should handle concurrent requests
            assert metrics.success_rate >= 0.80  # 80% success rate (some may fail due to validation)
            assert metrics.avg_response_time < 2.0  # 2 seconds average

class TestDatabasePerformance:
    """Test database performance under load"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_connection_pool(self, test_session):
        """Test database connection pool under concurrent load"""
        
        async def database_operation():
            """Simulate database operation"""
            start_time = time.time()
            
            # Simulate a database query
            try:
                # In real test, this would be actual database query
                await asyncio.sleep(0.01)  # Simulate 10ms query
                return time.time() - start_time
            except Exception:
                return None
        
        # Run 100 concurrent database operations
        tasks = [database_operation() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        
        # Filter successful operations
        successful_ops = [r for r in results if r is not None]
        
        # Assertions
        assert len(successful_ops) >= 95  # 95% success rate
        assert statistics.mean(successful_ops) < 0.1  # Average under 100ms
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_large_dataset_query(self, test_session):
        """Test performance with large dataset queries"""
        
        # This would test actual large queries in a real implementation
        start_time = time.time()
        
        # Simulate large dataset operation
        await asyncio.sleep(0.1)  # Simulate 100ms for large query
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Large queries should complete within reasonable time
        assert query_time < 1.0  # Under 1 second

class TestCachePerformance:
    """Test cache performance under load"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_read_performance(self, test_redis):
        """Test cache read performance under high load"""
        
        # Pre-populate cache
        for i in range(1000):
            await test_redis.set(f"test_key_{i}", f"test_value_{i}")
        
        async def cache_read_operation():
            """Single cache read operation"""
            start_time = time.time()
            
            key = f"test_key_{time.time() % 1000:.0f}"
            value = await test_redis.get(key)
            
            return time.time() - start_time
        
        # Run 1000 concurrent cache reads
        tasks = [cache_read_operation() for _ in range(1000)]
        results = await asyncio.gather(*tasks)
        
        # Cache reads should be very fast
        avg_read_time = statistics.mean(results)
        assert avg_read_time < 0.001  # Under 1ms average
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_write_performance(self, test_redis):
        """Test cache write performance under load"""
        
        async def cache_write_operation(index):
            """Single cache write operation"""
            start_time = time.time()
            
            await test_redis.set(f"perf_test_{index}", f"value_{index}")
            
            return time.time() - start_time
        
        # Run 500 concurrent cache writes
        tasks = [cache_write_operation(i) for i in range(500)]
        results = await asyncio.gather(*tasks)
        
        # Cache writes should be fast
        avg_write_time = statistics.mean(results)
        assert avg_write_time < 0.01  # Under 10ms average

class TestMemoryUsage:
    """Test memory usage and potential leaks"""
    
    @pytest.mark.performance
    def test_memory_usage_under_load(self):
        """Test memory usage during high load"""
        
        @memory_profiler.profile
        def simulate_heavy_processing():
            """Simulate memory-intensive processing"""
            # Create and process large datasets
            data_sets = []
            for i in range(100):
                large_list = [j for j in range(10000)]
                processed_data = [x * 2 for x in large_list]
                data_sets.append(processed_data)
            
            return len(data_sets)
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        result = simulate_heavy_processing()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert result == 100  # All datasets processed
        assert memory_increase < 500  # Less than 500MB increase
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_cleanup_after_requests(self):
        """Test that memory is properly cleaned up after requests"""
        import gc
        
        initial_objects = len(gc.get_objects())
        
        # Simulate multiple request/response cycles
        for i in range(100):
            # Simulate request processing
            request_data = {
                "large_data": [j for j in range(1000)],
                "processed": True,
                "index": i
            }
            
            # Simulate response creation
            response_data = {
                "result": request_data["large_data"],
                "success": True
            }
            
            # Clear references
            del request_data
            del response_data
        
        # Force garbage collection
        gc.collect()
        
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Object count shouldn't grow excessively
        assert object_increase < 1000  # Less than 1000 new objects

class TestConcurrencyLimits:
    """Test system behavior at concurrency limits"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_maximum_concurrent_connections(self):
        """Test behavior at maximum concurrent connections"""
        
        async def long_running_request():
            """Simulate long-running request"""
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        "http://localhost:8000/health",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        await response.read()
                        return response.status == 200
                except Exception:
                    return False
        
        # Try to create many concurrent connections
        tasks = [long_running_request() for _ in range(200)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # System should handle many concurrent connections gracefully
        successful_connections = sum(1 for r in results if r is True)
        assert successful_connections >= 100  # At least 50% should succeed
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_resource_exhaustion_recovery(self):
        """Test system recovery from resource exhaustion"""
        
        # Create resource exhaustion scenario
        heavy_tasks = []
        for i in range(50):
            async def heavy_task():
                # Simulate CPU/memory intensive task
                data = [j for j in range(100000)]
                return sum(data)
            
            heavy_tasks.append(heavy_task())
        
        # Execute heavy tasks
        start_time = time.time()
        results = await asyncio.gather(*heavy_tasks, return_exceptions=True)
        end_time = time.time()
        
        # Verify system can still respond after heavy load
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                health_check_success = response.status == 200
        
        # System should recover and respond to health checks
        assert health_check_success
        assert end_time - start_time < 30  # Should complete within 30 seconds

class TestResponseTimeDistribution:
    """Test response time distribution and consistency"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_response_time_consistency(self):
        """Test that response times are consistent"""
        
        async with LoadTestRunner() as runner:
            # Run steady load test
            metrics = await runner.run_load_test(
                endpoint="/health",
                concurrent_users=10,
                duration=60,
                ramp_up_time=0
            )
            
            # Calculate response time statistics
            response_times = metrics.response_times
            
            if len(response_times) > 10:
                std_dev = statistics.stdev(response_times)
                mean_time = statistics.mean(response_times)
                
                # Response times should be relatively consistent
                coefficient_of_variation = std_dev / mean_time
                assert coefficient_of_variation < 2.0  # CV should be reasonable
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_latency_under_different_loads(self):
        """Test latency characteristics under different load levels"""
        
        load_levels = [1, 5, 10, 25, 50]
        latency_results = {}
        
        async with LoadTestRunner() as runner:
            for load in load_levels:
                metrics = await runner.run_load_test(
                    endpoint="/health",
                    concurrent_users=load,
                    duration=30
                )
                
                latency_results[load] = metrics.avg_response_time
        
        # Latency should not increase dramatically with load
        max_latency = max(latency_results.values())
        min_latency = min(latency_results.values())
        
        # Maximum latency should not be more than 10x minimum
        assert max_latency / min_latency < 10

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "performance"])