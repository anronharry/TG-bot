"""
Redis client configuration and utilities
"""
import json
from typing import Any, Optional, Union
import redis.asyncio as redis
from app.core.config import settings


class RedisClient:
    """Async Redis client wrapper"""
    
    def __init__(self):
        self.pool: Optional[redis.ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self._connect_attempted: bool = False
    
    async def connect(self):
        """Initialize Redis connection pool and client"""
        try:
            self.pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=True
            )
            self.client = redis.Redis(connection_pool=self.pool)
        finally:
            self._connect_attempted = True

    async def _ensure_connected(self) -> bool:
        """Try to connect once; return whether connected."""
        if self.client is not None:
            return True
        if not self._connect_attempted:
            try:
                await self.connect()
            except Exception:
                pass
        return self.client is not None
    
    async def disconnect(self):
        """Close Redis connections"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if not await self._ensure_connected():
            return None
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set key-value pair with optional expiration"""
        if not await self._ensure_connected():
            return False
        return await self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> int:
        """Delete key"""
        if not await self._ensure_connected():
            return 0
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not await self._ensure_connected():
            return False
        return bool(await self.client.exists(key))
    
    async def incr(self, key: str, ex: Optional[int] = None) -> int:
        """Increment counter with optional expiration"""
        if not await self._ensure_connected():
            return 0
        result = await self.client.incr(key)
        if ex and result == 1:  # Set expiration only on first increment
            await self.client.expire(key, ex)
        return result
    
    async def lpush(self, key: str, *values: str) -> int:
        """Push values to left of list"""
        if not await self._ensure_connected():
            return 0
        return await self.client.lpush(key, *values)
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim list to specified range"""
        if not await self._ensure_connected():
            return True
        return await self.client.ltrim(key, start, end)
    
    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get list range"""
        if not await self._ensure_connected():
            return []
        return await self.client.lrange(key, start, end)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set key expiration"""
        if not await self._ensure_connected():
            return False
        return await self.client.expire(key, seconds)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get and parse JSON value"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set JSON value"""
        json_str = json.dumps(value, ensure_ascii=False)
        return await self.set(key, json_str, ex=ex)


# Global Redis client instance
redis_client = RedisClient()
