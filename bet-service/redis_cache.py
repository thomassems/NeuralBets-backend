import os
import json
import redis
from datetime import datetime, timedelta
from typing import Optional, Any

# Redis configuration
# Supports Upstash REST API (with token), traditional Redis URL, or local Redis
UPSTASH_REDIS_REST_URL = os.getenv('UPSTASH_REDIS_REST_URL', None)  # Upstash REST URL
UPSTASH_REDIS_REST_TOKEN = os.getenv('UPSTASH_REDIS_REST_TOKEN', None)  # Upstash REST Token
REDIS_URL = os.getenv('REDIS_URL', None)  # Traditional Redis URL (rediss://)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Cache settings
CACHE_EXPIRY_SECONDS = 60  # 1 minute cache expiry

class RedisCache:
    """
    Redis cache manager with time-based invalidation.
    Supports Upstash REST API (production), traditional Redis, and local Redis (development).
    """
    
    def __init__(self):
        self.client = None
        self.available = False
        self.is_upstash_rest = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Redis connection (Upstash REST API, Redis URL, or local)"""
        try:
            # Priority 1: Use Upstash REST API (serverless-friendly, no persistent connections)
            if UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN:
                from upstash_redis import Redis as UpstashRedis
                print(f"[redis_cache] Connecting to Upstash REST API")
                self.client = UpstashRedis(
                    url=UPSTASH_REDIS_REST_URL,
                    token=UPSTASH_REDIS_REST_TOKEN
                )
                self.is_upstash_rest = True
                # Test connection
                self.client.ping()
                self.available = True
                print(f"[redis_cache] ✅ Upstash REST connected successfully")
                
            # Priority 2: Use REDIS_URL if provided (traditional Redis URL)
            elif REDIS_URL:
                print(f"[redis_cache] Connecting to Redis via URL")
                self.client = redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    ssl_cert_reqs=None  # Required for SSL connections
                )
                self.is_upstash_rest = False
                # Test connection
                self.client.ping()
                self.available = True
                print(f"[redis_cache] ✅ Redis connected successfully")
                
            # Priority 3: Use individual parameters (local Redis)
            else:
                print(f"[redis_cache] Connecting to local Redis at {REDIS_HOST}:{REDIS_PORT}")
                self.client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    password=REDIS_PASSWORD,
                    db=REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                self.is_upstash_rest = False
                # Test connection
                self.client.ping()
                self.available = True
                print(f"[redis_cache] ✅ Local Redis connected successfully")
                
        except Exception as e:
            print(f"[redis_cache] ❌ Redis not available: {e}")
            print(f"[redis_cache] Caching will be disabled")
            self.available = False
    
    def get_cached_odds(self, cache_key: str = 'live_odds') -> Optional[dict]:
        """
        Get cached odds if available. Redis TTL handles expiration automatically.
        Works with both Upstash REST API and traditional Redis.
        
        Returns:
            dict with 'data' and 'cached_at' keys, or None if not available
        """
        if not self.available:
            return None
        
        try:
            cached_data = self.client.get(cache_key)
            if cached_data:
                # Upstash REST returns string directly, traditional Redis may too
                if isinstance(cached_data, str):
                    parsed_data = json.loads(cached_data)
                else:
                    parsed_data = cached_data
                # Redis TTL handles expiration, so if we got data it's valid
                return parsed_data
            return None
        except Exception as e:
            print(f"[redis_cache] Error retrieving cache: {e}")
            return None
    
    def set_cached_odds(self, data: Any, cache_key: str = 'live_odds') -> bool:
        """
        Cache the odds data with timestamp.
        Works with both Upstash REST API and traditional Redis.
        
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
            
            # Set with expiry (TTL)
            # Both Upstash REST and traditional Redis support setex
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
