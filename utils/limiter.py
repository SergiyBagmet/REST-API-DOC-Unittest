import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.conf.config import config


def register_startup_event_limiter(app: FastAPI):
    @app.on_event("startup")
    async def startup():
        r = await redis.Redis(
            host=config.REDIS_DOMAIN,
            port=config.REDIS_PORT,
            db=0
        )
        await FastAPILimiter.init(r)
