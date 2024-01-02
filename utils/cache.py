import typing as t
import pickle
from functools import wraps

from redis import StrictRedis

from src.conf.config import config


class RedisCache:
    """
    A class that caches the results of function calls using Redis.

    This class provides functions for:

    * Generating unique keys for function calls
    * Caching function results with a configurable TTL
    * Updating cached values

    Attributes:

    * redis (StrictRedis): The Redis client used to interact with the Redis database.
    """
    redis = StrictRedis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0
    )

    async def cache_key(self, func_name, unique_arg):

        """
        The cache_key function is used to generate a unique key for each function call.
        The cache_key function takes in two arguments: the name of the function being called, and a unique argument from that
        call. The cache_key then returns a string with the format &quot;func_name:unique_arg&quot;. This allows us to store multiple
        calls of different functions in one Redis database.

        :param self: Access the class attributes
        :param func_name: Identify the function that is being called
        :param unique_arg: Create a unique key for each function call
        :return: A string with the function name and the unique argument
        :doc-author: Trelent
        """
        return f"{func_name}:{str(unique_arg)}"

    def cache(self, ttl=5000):
        """
        The cache function is a decorator that caches the result of a function call.
        The cache key is generated from the function name and its arguments.
        If there's already an entry in Redis for this key, it will be returned instead of calling the decorated function again.
        Otherwise, we'll call the decorated function and store its return value in Redis with an expiration time (ttl).


        :param self: Access the class attributes and methods
        :param ttl: Set the time to live for a key
        :return: A decorator
        :doc-author: Trelent
        """
        def decorator(func):
            """
            The decorator function is a wrapper that takes in the function to be decorated,
            and returns a new function. The new function will check if the result of calling
            the original funciton with args and kwargs exists in redis. If it does not exist,
            it will call the original funciton and store its return value in redis for future use.
            If it does exist, then we simply return that value from redis.

            :param func: Pass in the function that is being decorated
            :return: A wrapper function
            :doc-author: Trelent
            """
            @wraps(func)
            async def wrapper(*args, **kwargs):
                """
                The wrapper function is a decorator that takes in the function to be cached,
                and returns a wrapper function. The wrapper function will check if the result of
                the original funciton has been cached, and if so return it. If not, it will call
                the original funciton and cache its result before returning.

                :param *args: Pass in the arguments to the function
                :param **kwargs: Pass in keyword arguments to the function
                :return: The value of the function it wraps
                :doc-author: Trelent
                """
                unique_arg, *_ = args
                key = await self.cache_key(func.__name__, unique_arg)
                result = self.redis.get(key)
                if result is None:
                    value = await func(*args, **kwargs)
                    value_pickle = pickle.dumps(value)
                    self.redis.set(key, value_pickle, ex=ttl)
                else:
                    self.redis.expire(key, ttl)
                    value = pickle.loads(result)

                return value

            return wrapper

        return decorator

    async def update_cache(self, func: t.Callable, unique_arg, value: t.Any):

        """
        The update_cache function is used to update the cache with a new value.

        :param self: Access the redis object
        :param func: t.Callable: Pass the function that is being cached
        :param unique_arg: Create a unique key for the function
        :param value: t.Any: Pass in the value that will be cached
        :return: The value of the key in redis
        :doc-author: Trelent
        """
        key = await self.cache_key(func.__name__, unique_arg)
        value = pickle.dumps(value)
        ttl = self.redis.ttl(key)
        if ttl <= 0:
            ttl = 5000
        self.redis.set(key, value, ex=ttl)


rc = RedisCache()
