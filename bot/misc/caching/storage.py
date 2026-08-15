import logging
from typing import Optional, Literal
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage, StorageKey
from bot.misc import EnvKeys

_SHARED_REDIS: Optional[Redis] = None


def build_redis_client() -> Redis:
    """Build a Redis client honoring REDIS_URL (e.g. Upstash) or host/port settings."""
    if EnvKeys.REDIS_URL.strip():
        return Redis.from_url(
            EnvKeys.REDIS_URL.strip(),
            decode_responses=False,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    return Redis(
        host=EnvKeys.REDIS_HOST,
        port=EnvKeys.REDIS_PORT,
        db=EnvKeys.REDIS_DB,
        password=EnvKeys.REDIS_PASSWORD,
        decode_responses=False,
        socket_connect_timeout=5,
        socket_timeout=5,
    )


def get_shared_redis() -> Optional[Redis]:
    """Return a lazily-created process-wide Redis client for non-FSM use.

    Serverless warm slots reuse it across requests; returns None when Redis is disabled.
    """
    global _SHARED_REDIS
    if EnvKeys.REDIS_ENABLED != "1":
        return None
    if _SHARED_REDIS is None:
        try:
            _SHARED_REDIS = build_redis_client()
        except Exception as e:
            logging.error(f"Failed to create shared Redis client: {e}")
            return None
    return _SHARED_REDIS


class CustomRedisStorage(RedisStorage):
    """
    Custom Redis storage with TTL support for FSM states.
    States will expire after the specified TTL to prevent memory leaks.
    """

    def __init__(
            self,
            redis: Redis,
            state_ttl: Optional[int] = 3600,  # 1 hour by default
            data_ttl: Optional[int] = 3600,
    ):
        super().__init__(redis=redis)
        self.state_ttl = state_ttl
        self.data_ttl = data_ttl

    async def set_state(self, key: StorageKey, state: str = None) -> None:
        """Set state with TTL"""
        await super().set_state(key, state)
        if state and self.state_ttl:
            redis_key = self._build_key(key, "state")
            await self.redis.expire(redis_key, self.state_ttl)

    async def set_data(self, key: StorageKey, data: dict) -> None:
        """Set data with TTL"""
        await super().set_data(key, data)
        if data and self.data_ttl:
            redis_key = self._build_key(key, "data")
            await self.redis.expire(redis_key, self.data_ttl)

    def _build_key(self, key: StorageKey, part: Literal["data", "state", "lock"]) -> str:
        """Build Redis key"""
        assert self.key_builder is not None, "KeyBuilder should be initialized"
        return self.key_builder.build(key, part)


def get_redis_storage() -> Optional[RedisStorage]:
    """
    Create Redis storage with proper configuration.
    Returns None if Redis is disabled or not available.
    """
    if EnvKeys.REDIS_ENABLED != "1":
        logging.info("Redis is disabled via REDIS_ENABLED=0")
        return None

    try:
        redis = build_redis_client()

        # Use custom storage with TTL
        storage = CustomRedisStorage(
            redis=redis,
            state_ttl=3600,  # 1 hour
            data_ttl=3600,  # 1 hour
        )

        logging.info(f"Redis storage configured: {EnvKeys.REDIS_URL or f'{EnvKeys.REDIS_HOST}:{EnvKeys.REDIS_PORT}'}")
        return storage

    except Exception as e:
        logging.error(f"Failed to create Redis storage: {e}")
        return None
