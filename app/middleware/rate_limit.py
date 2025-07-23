from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import redis.asyncio as redis
from typing import Dict, Optional
from app.config import get_settings

settings = get_settings()

class RateLimitMiddleware:
    def __init__(self, redis_client: redis.Redis, default_calls: int = 100, default_period: int = 60):
        self.redis_client = redis_client
        self.default_calls = default_calls
        self.default_period = default_period
        
        # Different rate limits for different endpoints
        self.rate_limits = {
            "/api/v1/auth/login": {"calls": 5, "period": 60},  # 5 per minute
            "/api/v1/auth/register": {"calls": 3, "period": 60},  # 3 per minute
            "/api/v1/auth/forgot-password": {"calls": 2, "period": 300},  # 2 per 5 minutes
        }
    
    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        
        # Get rate limit for this endpoint
        rate_limit = self.rate_limits.get(path, {
            "calls": self.default_calls,
            "period": self.default_period
        })
        
        # Create Redis key
        key = f"rate_limit:{client_ip}:{path}"
        
        try:
            # Get current count
            current_count = await self.redis_client.get(key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= rate_limit["calls"]:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded"}
                )
            
            # Increment counter
            await self.redis_client.incr(key)
            await self.redis_client.expire(key, rate_limit["period"])
            
        except Exception:
            # If Redis is down, allow the request
            pass
        
        response = await call_next(request)
        return response