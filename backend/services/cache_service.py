"""
Optimized caching service with tiered TTL strategy
Implements cache warming, invalidation patterns, and efficient data access
"""
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import redis.asyncio as redis
import logging
from functools import wraps

from core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    """Enhanced caching service with smart TTL management"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        
        # Cache key patterns
        self.KEY_PATTERNS = {
            'event': 'event:{event_id}',
            'events_by_sport': 'events:sport:{sport}',
            'user_bets': 'user:{user_id}:bets',
            'odds': 'odds:{event_id}',
            'predictions': 'predictions:{event_id}',
            'league_standings': 'league:{league}:standings',
            'user_profile': 'user:{user_id}:profile',
        }
        
        # TTL mappings based on data type
        self.TTL_MAPPING = {
            'odds': settings.CACHE_TTL_SHORT,      # Live odds change frequently
            'event': settings.CACHE_TTL_MEDIUM,    # Event data moderately stable
            'user_bets': settings.CACHE_TTL_USER,  # User data caching
            'predictions': settings.CACHE_TTL_LONG, # ML predictions stable
            'league_standings': settings.CACHE_TTL_LONG,  # Standings change daily
            'user_profile': settings.CACHE_TTL_USER,
        }
    
    async def get(self, key_type: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get data from cache with automatic key generation"""
        try:
            cache_key = self._generate_key(key_type, **kwargs)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                logger.debug(f"Cache HIT for key: {cache_key}")
                return json.loads(cached_data)
            
            logger.debug(f"Cache MISS for key: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Cache GET error for key_type {key_type}: {e}")
            return None
    
    async def set(self, key_type: str, data: Dict[str, Any], ttl: Optional[int] = None, **kwargs) -> bool:
        """Set data in cache with appropriate TTL"""
        try:
            cache_key = self._generate_key(key_type, **kwargs)
            ttl = ttl or self.TTL_MAPPING.get(key_type, settings.CACHE_TTL_MEDIUM)
            
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data, default=str)
            )
            
            logger.debug(f"Cache SET for key: {cache_key} with TTL: {ttl}")
            return True
            
        except Exception as e:
            logger.error(f"Cache SET error for key_type {key_type}: {e}")
            return False
    
    async def delete(self, key_type: str, **kwargs) -> bool:
        """Delete specific cache entry"""
        try:
            cache_key = self._generate_key(key_type, **kwargs)
            deleted = await self.redis_client.delete(cache_key)
            
            if deleted:
                logger.debug(f"Cache DELETE for key: {cache_key}")
            
            return bool(deleted)
            
        except Exception as e:
            logger.error(f"Cache DELETE error for key_type {key_type}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache entries matching pattern"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries matching pattern: {pattern}")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Cache INVALIDATE error for pattern {pattern}: {e}")
            return 0
    
    async def warm_cache_for_upcoming_events(self) -> None:
        """Preload cache with upcoming events data"""
        try:
            from core.database import get_db_session, SportEvent
            from sqlalchemy import select
            
            # Get events happening in next 24 hours
            cutoff_time = datetime.utcnow() + timedelta(hours=24)
            
            async with get_db_session() as db:
                result = await db.execute(
                    select(SportEvent)
                    .where(SportEvent.event_date <= cutoff_time)
                    .where(SportEvent.status == 'scheduled')
                    .limit(100)  # Limit to avoid overwhelming
                )
                events = result.scalars().all()
                
                # Cache each event
                cache_tasks = []
                for event in events:
                    event_data = {
                        'id': event.id,
                        'external_id': event.external_id,
                        'sport': event.sport,
                        'league': event.league,
                        'home_team': event.home_team,
                        'away_team': event.away_team,
                        'event_date': event.event_date.isoformat(),
                        'odds_data': event.odds_data,
                        'status': event.status
                    }
                    
                    cache_tasks.append(
                        self.set('event', event_data, event_id=event.id)
                    )
                
                # Execute cache warming concurrently
                await asyncio.gather(*cache_tasks)
                logger.info(f"Cache warmed for {len(events)} upcoming events")
                
        except Exception as e:
            logger.error(f"Cache warming error: {e}")
    
    def _generate_key(self, key_type: str, **kwargs) -> str:
        """Generate cache key based on type and parameters"""
        if key_type not in self.KEY_PATTERNS:
            raise ValueError(f"Unknown cache key type: {key_type}")
        
        pattern = self.KEY_PATTERNS[key_type]
        return pattern.format(**kwargs)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            info = await self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                )
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100

# Decorator for automatic caching
def cache_result(key_type: str, ttl: Optional[int] = None, **cache_kwargs):
    """Decorator to automatically cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_service = CacheService()
            
            # Try to get from cache first
            cached_result = await cache_service.get(key_type, **cache_kwargs)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                await cache_service.set(key_type, result, ttl=ttl, **cache_kwargs)
            
            return result
        return wrapper
    return decorator

# Global cache service instance
cache_service = CacheService()