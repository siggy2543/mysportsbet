"""
Performance monitoring and metrics collection
Provides Prometheus metrics, request tracking, and performance insights
"""
import time
import logging
from typing import Callable, Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from fastapi import FastAPI
import psutil
import asyncio

logger = logging.getLogger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

CACHE_HIT_RATE = Gauge(
    'cache_hit_rate_percentage',
    'Cache hit rate percentage'
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percentage',
    'CPU usage percentage'
)

BET_PLACEMENT_RATE = Counter(
    'bets_placed_total',
    'Total number of bets placed',
    ['bet_type', 'status']
)

API_ERRORS = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type']
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()
        
        # Increment active connections
        ACTIVE_CONNECTIONS.inc()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            endpoint = self._get_endpoint_name(request)
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            # Log slow requests
            if duration > 1.0:  # Requests taking more than 1 second
                logger.warning(
                    f"Slow request detected: {request.method} {endpoint} "
                    f"took {duration:.2f}s"
                )
            
            return response
            
        except Exception as e:
            # Record API errors
            endpoint = self._get_endpoint_name(request)
            API_ERRORS.labels(
                endpoint=endpoint,
                error_type=type(e).__name__
            ).inc()
            
            logger.error(f"Request failed: {request.method} {endpoint} - {e}")
            raise
        
        finally:
            # Decrement active connections
            ACTIVE_CONNECTIONS.dec()
    
    def _get_endpoint_name(self, request: Request) -> str:
        """Extract endpoint name from request"""
        if hasattr(request, 'url') and request.url.path:
            path = request.url.path
            # Remove IDs and dynamic parts for better grouping
            import re
            path = re.sub(r'/\d+', '/{id}', path)
            return path
        return "unknown"

class PerformanceMonitor:
    """System performance monitoring"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_task = None
    
    async def start_monitoring(self):
        """Start system monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_system())
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    async def _monitor_system(self):
        """Monitor system metrics continuously"""
        while self.monitoring:
            try:
                # Memory usage
                memory_info = psutil.virtual_memory()
                MEMORY_USAGE.set(memory_info.used)
                
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                CPU_USAGE.set(cpu_percent)
                
                # Log warnings for high resource usage
                if memory_info.percent > 80:
                    logger.warning(f"High memory usage: {memory_info.percent:.1f}%")
                
                if cpu_percent > 80:
                    logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def update_cache_metrics(self, hit_rate: float):
        """Update cache hit rate metrics"""
        CACHE_HIT_RATE.set(hit_rate)
    
    async def update_database_metrics(self, active_connections: int):
        """Update database connection metrics"""
        DATABASE_CONNECTIONS.set(active_connections)
    
    def record_bet_placement(self, bet_type: str, status: str):
        """Record bet placement metrics"""
        BET_PLACEMENT_RATE.labels(
            bet_type=bet_type,
            status=status
        ).inc()

# Global monitor instance
performance_monitor = PerformanceMonitor()

def setup_metrics(app: FastAPI):
    """Setup metrics collection for FastAPI app"""
    
    # Add metrics middleware
    app.add_middleware(MetricsMiddleware)
    
    # Add metrics endpoint
    @app.get("/metrics")
    async def get_metrics():
        """Prometheus metrics endpoint"""
        return PlainTextResponse(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    # Enhanced health check with metrics
    @app.get("/health/detailed")
    async def detailed_health_check():
        """Detailed health check with performance metrics"""
        memory_info = psutil.virtual_memory()
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "metrics": {
                "memory_usage_percent": memory_info.percent,
                "cpu_usage_percent": psutil.cpu_percent(interval=0.1),
                "active_connections": ACTIVE_CONNECTIONS._value._value,
                "database_connections": DATABASE_CONNECTIONS._value._value,
                "cache_hit_rate": CACHE_HIT_RATE._value._value,
            },
            "timestamp": time.time()
        }

def get_performance_summary() -> Dict[str, Any]:
    """Get current performance summary"""
    return {
        "active_connections": ACTIVE_CONNECTIONS._value._value,
        "database_connections": DATABASE_CONNECTIONS._value._value,
        "cache_hit_rate": CACHE_HIT_RATE._value._value,
        "memory_usage_mb": MEMORY_USAGE._value._value / (1024 * 1024),
        "cpu_usage_percent": CPU_USAGE._value._value,
    }