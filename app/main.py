from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
import redis.asyncio as redis

from .config import get_settings
from .database import engine, Base
from .api.v1 import (
    auth, users, community, education, marketplace, 
    reviews, signals, calendar, websocket, search, 
    analytics, notifications
)
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.logging import LoggingMiddleware

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.redis = redis.from_url(settings.REDIS_URL)
    yield
    # Shutdown
    await app.state.redis.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="A comprehensive Forex & Crypto Trading Hub API",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(LoggingMiddleware)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    rate_limiter = RateLimitMiddleware(app.state.redis)
    return await rate_limiter(request, call_next)

# Exception handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(community.router, prefix=f"{settings.API_V1_STR}/community", tags=["community"])
app.include_router(education.router, prefix=f"{settings.API_V1_STR}/education", tags=["education"])
app.include_router(marketplace.router, prefix=f"{settings.API_V1_STR}/marketplace", tags=["marketplace"])
app.include_router(reviews.router, prefix=f"{settings.API_V1_STR}/reviews", tags=["reviews"])
app.include_router(signals.router, prefix=f"{settings.API_V1_STR}/signals", tags=["signals"])
app.include_router(calendar.router, prefix=f"{settings.API_V1_STR}/calendar", tags=["calendar"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])
app.include_router(websocket.router, prefix=f"{settings.API_V1_STR}", tags=["websocket"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to FxUtopia API",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "Authentication & Authorization",
            "Community Forums",
            "Educational Content",
            "Marketplace",
            "Reviews & Ratings", 
            "Trading Signals",
            "Economic Calendar",
            "Real-time WebSocket",
            "Search & Analytics"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )