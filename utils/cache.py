import redis

from src.conf.config import config


def get_cache():
    return redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0
    )
