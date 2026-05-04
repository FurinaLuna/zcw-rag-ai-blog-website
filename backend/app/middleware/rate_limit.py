from fastapi import Request, HTTPException, status
from loguru import logger
from redis.asyncio import Redis

from app.core.config import settings
from app.core.redis import get_redis


async def rate_limit_middleware(request: Request, call_next):
    redis: Redis | None = None
    try:
        redis = await get_redis()
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"
        current = await redis.get(key)

        if current is None:
            await redis.setex(key, 60, 1)
        elif int(current) >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"success": False, "message": "Too many requests, please try again later", "data": None},
            )
        else:
            await redis.incr(key)
    except HTTPException:
        raise
    except Exception:
        logger.warning("Rate limit check failed, allowing request")
        pass

    return await call_next(request)
