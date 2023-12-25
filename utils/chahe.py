import typing as t
import pickle
from functools import wraps

from redis import StrictRedis

from src.conf.config import config


class RadisCache:
    redis = StrictRedis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0
    )

    async def cache_key(self, func_name, unique_arg):
        return f"{func_name}:{str(unique_arg)}"

    def cache(self, ttl=-1):

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                unique_arg, *_ = args
                key = await self.cache_key(func.__name__, unique_arg)
                result = self.redis.get(key)
                self.redis.expire(key, ttl)
                if result is None:
                    value = await func(*args, **kwargs)
                    value_pickle = pickle.dumps(value)
                    self.redis.set(key, value_pickle, ex=ttl)
                else:
                    value = pickle.loads(result)

                return value

            return wrapper

        return decorator

    async def update_cache(self, func: t.Callable, unique_arg, value: t.Any):
        key = await self.cache_key(func.__name__, unique_arg)
        value = pickle.dumps(value)
        ttl = self.redis.ttl(key)
        self.redis.set(key, value, ex=ttl)


rc = RadisCache()
