import redis.asyncio as redis
from app.core.config import settings

class RedisCache:
    client: redis.Redis = None

cache = RedisCache()

async def connect_to_redis():
    cache.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await cache.client.ping()
    except Exception:
        await cache.client.close()
        cache.client = None

async def close_redis_connection():
    if cache.client is not None:
        await cache.client.aclose()

def get_redis() -> redis.Redis:
    return cache.client
