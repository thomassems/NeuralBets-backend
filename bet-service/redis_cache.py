import os
import json
import redis
from datetime import datetime, timedelta
from typing import Optional, Any

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Cache settings
CACHE_EXPIRY_SECONDS = 60  # 1 minute cache expiry

class RedisCache:
    """Redis cache manager with time-based invalidation"""
    
    def __init__(self):
        self.client = None
        self.available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            self.client.ping()
            self.available = True
            print(f"[redis_cache] Redis connected successfully at {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            print(f"[redis_cache] Redis not available: {e}")
            print(f"[redis_cache] Caching will be disabled")
            self.available = False
    
    def get_cached_odds(self, cache_key: str = 'live_odds') -> Optional[dict]:
        """
        Get cached odds if available and not expired.
        
        Returns:
            dict with 'data' and 'cached_at' keys, or None if not available
        """
        if not self.available:
            return None
        
        try:
            cached_data = self.client.get(cache_key)
            if cached_data:
                parsed_data = json.loads(cached_data)
                cached_at = datetime.fromisoformat(parsed_data['cached_at'])
                
                # Check if cache is still valid (within 1 minute)
                if datetime.utcnow() - cached_at < timedelta(seconds=CACHE_EXPIRY_SECONDS):
                    print(f"[redis_cache] Returning cached odds from {cached_at}")
                    return parsed_data
                else:
                    print(f"[redis_cache] Cache expired (cached at {cached_at})")
                    return None
            return None
        except Exception as e:
            print(f"[redis_cache] Error retrieving cache: {e}")
            return None
    
    def set_cached_odds(self, data: Any, cache_key: str = 'live_odds') -> bool:
        """
        Cache the odds data with timestamp.
        
        Args:
            data: The odds data to cache
            cache_key: Redis key to use
            
        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            return False
        
        try:
            cache_data = {
                'data': data,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            # Set with expiry (TTL) as a safety measure
            self.client.setex(
                cache_key,
                CACHE_EXPIRY_SECONDS + 5,  # Add 5 seconds buffer
                json.dumps(cache_data)
            )
            print(f"[redis_cache] Cached odds at {cache_data['cached_at']}")
            return True
        except Exception as e:
            print(f"[redis_cache] Error setting cache: {e}")
            return False
    
    def should_refresh_cache(self, cache_key: str = 'live_odds') -> bool:
        """
        Check if cache should be refreshed based on time.
        
        Returns:
            True if cache should be refreshed, False otherwise
        """
        if not self.available:
            return True
        
        try:
            cached_data = self.client.get(cache_key)
            if not cached_data:
                return True
            
            parsed_data = json.loads(cached_data)
            cached_at = datetime.fromisoformat(parsed_data['cached_at'])
            
            # Check if more than 1 minute has passed
            time_diff = datetime.utcnow() - cached_at
            should_refresh = time_diff >= timedelta(seconds=CACHE_EXPIRY_SECONDS)
            
            if should_refresh:
                print(f"[redis_cache] Cache needs refresh (last cached: {cached_at}, age: {time_diff.seconds}s)")
            
            return should_refresh
        except Exception as e:
            print(f"[redis_cache] Error checking cache freshness: {e}")
            return True
    
    def clear_cache(self, cache_key: str = 'live_odds') -> bool:
        """Clear the cache for a specific key"""
        if not self.available:
            return False
        
        try:
            self.client.delete(cache_key)
            print(f"[redis_cache] Cache cleared for key: {cache_key}")
            return True
        except Exception as e:
            print(f"[redis_cache] Error clearing cache: {e}")
            return False

# Global cache instance
redis_cache = RedisCache()
