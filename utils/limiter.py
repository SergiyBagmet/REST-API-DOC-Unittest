import redis.asyncio as redis
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter

from src.conf.config import config


@asynccontextmanager
async def lifespan_limiter(app: FastAPI) -> None:
    """
    The on_startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    such as database connections or external services.

    :param app: The FastAPI application.
    :type app: FastAPI
    :yield: None
    :doc-Author: Trelent
    """

    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0
    )
    await FastAPILimiter.init(r)
    yield

