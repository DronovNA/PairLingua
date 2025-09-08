import redis.asyncio as redis
from app.core.config import settings

# Redis connection
redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    retry_on_timeout=True,
    socket_keepalive=True,
    socket_keepalive_options={}
)


async def get_redis():
    return redis_client


class RedisService:
    def __init__(self):
        self.redis = redis_client
    
    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ex: int = None) -> bool:
        return await self.redis.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> int:
        return await self.redis.delete(key)
    
    async def exists(self, key: str) -> int:
        return await self.redis.exists(key)
    
    async def expire(self, key: str, time: int) -> bool:
        return await self.redis.expire(key, time)
    
    async def sadd(self, key: str, *values) -> int:
        return await self.redis.sadd(key, *values)
    
    async def sismember(self, key: str, value: str) -> bool:
        return await self.redis.sismember(key, value)


redis_service = RedisService()
