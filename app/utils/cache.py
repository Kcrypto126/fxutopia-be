import redis.asyncio as redis
import json
from typing import Any, Optional
from ..config import get_settings

settings = get_settings()

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """Set value in cache"""
        try:
            if expire is None:
                expire = settings.CACHE_EXPIRE_IN_SECONDS
            
            await self.redis.setex(
                key, 
                expire, 
                json.dumps(value, default=str)
            )
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception:
            return False

cache = CacheService()