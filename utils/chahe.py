import typing as t
import pickle
from functools import wraps

from redis import StrictRedis
from blinker import signal

from src.conf.config import config


def hash_func(func_name, arg):
    return f"{func_name}:{str(arg)}"


class RadisCache:
    redis = StrictRedis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0
    )

    updated = signal("updated")

    def redis_cache(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = pickle.dumps(hash_func(func.__name__, list(args)[0]))  # TODO костиль
            result = self.redis.get(key)

            if result is None:
                value = await func(*args, **kwargs)
                value_pickle = pickle.dumps(value)
                self.redis.set(key, value_pickle)
            else:
                value = pickle.loads(result)

            return value

        return wrapper

    @updated.connect
    def update_cache(self, sender, func_name: str, arg, value: t.Any):
        key = hash_func(func_name, arg)
        value = pickle.dumps(value)
        cache.redis.set(key, value)
        print(f"cache updated")


cache = RadisCache()
