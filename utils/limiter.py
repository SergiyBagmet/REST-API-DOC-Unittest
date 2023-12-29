import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.conf.config import config


def register_startup_event_limiter(app: FastAPI):
    """
    The register_startup_event_limiter function is a function that registers the startup event limiter.
    The startup event limiter is an asynchronous function that initializes the FastAPILimiter class with Redis as its backend.


    :param app: FastAPI: Pass the fastapi object to the function
    :return: A fastapilimiter instance
    :doc-author: Trelent
    """
    @app.on_event("startup")
    async def startup():
        """
        The startup function is called when the application starts up.
        It's a good place to initialize things that are needed by your app,
        such as database connections or external services.

        :return: A coroutine that is executed when the application starts
        :doc-author: Trelent
        """
        r = await redis.Redis(
            host=config.REDIS_DOMAIN,
            port=config.REDIS_PORT,
            db=0
        )
        await FastAPILimiter.init(r)
