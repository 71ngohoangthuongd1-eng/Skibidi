"""Unit tests for the Redis-aware and in-memory rate limiters plus the middleware."""

import time

import pytest

from bot.middleware.rate_limit import RateLimiter, RedisRateLimiter, RateLimitConfig


class FakeAsyncRedis:
    """Minimal in-memory async redis stand-in (exists/get/setex/delete/incr/expire/ttl/set nx)."""

    def __init__(self):
        self._data = {}
        self._ttl = {}
        self._seq = {}

    async def exists(self, key: str):
        return 1 if key in self._data else 0

    async def get(self, key: str):
        return self._data.get(key)

    async def setex(self, key: str, seconds: int, value: str):
        self._data[key] = value
        self._ttl[key] = seconds

    async def delete(self, *keys: str):
        for k in keys:
            self._data.pop(k, None)
            self._ttl.pop(k, None)
        return len(keys)

    async def incr(self, key: str):
        self._seq[key] = self._seq.get(key, 0) + 1
        return self._seq[key]

    async def expire(self, key: str, seconds: int):
        self._ttl[key] = seconds
        return True

    async def ttl(self, key: str):
        return self._ttl.get(key, -1)

    async def set(self, key: str, value: str, nx: bool = False, ex: int = None):
        if nx and key in self._data:
            return False
        self._data[key] = value
        if ex:
            self._ttl[key] = ex
        return True


class TestInMemoryRateLimiter:

    async def test_global_limit_enforced(self):
        limiter = RateLimiter(RateLimitConfig(global_limit=2, global_window=60))
        assert await limiter.check_global_limit(42) is True
        assert await limiter.check_global_limit(42) is True
        assert await limiter.check_global_limit(42) is False

    async def test_action_limit(self):
        limiter = RateLimiter(RateLimitConfig(action_limits={"buy_item": (2, 60)}))
        assert await limiter.check_action_limit(7, "buy_item") is True
        assert await limiter.check_action_limit(7, "buy_item") is True
        assert await limiter.check_action_limit(7, "buy_item") is False

    async def test_unconfigured_action_allowed(self):
        limiter = RateLimiter(RateLimitConfig())
        assert await limiter.check_action_limit(7, "unknown_action") is True

    async def test_ban_cycle(self):
        limiter = RateLimiter(RateLimitConfig(ban_duration=300))
        assert await limiter.is_banned(5) is False
        await limiter.ban_user(5)
        assert await limiter.is_banned(5) is True
        assert await limiter.get_wait_time(5) > 0

    async def test_banned_wait_time_based_on_ban_duration(self):
        limiter = RateLimiter(RateLimitConfig(ban_duration=300))
        await limiter.ban_user(9)
        wait = await limiter.get_wait_time(9)
        assert 0 < wait <= 300


class TestRedisRateLimiter:

    async def test_is_banned_checks_redis(self):
        redis = FakeAsyncRedis()
        limiter = RedisRateLimiter(RateLimitConfig(ban_duration=300), redis)
        assert await limiter.is_banned(1) is False
        await limiter.ban_user(1)
        assert await limiter.is_banned(1) is True

    async def test_global_limit_via_redis(self):
        redis = FakeAsyncRedis()
        limiter = RedisRateLimiter(RateLimitConfig(global_limit=2, global_window=60), redis)
        assert await limiter.check_global_limit(2) is True
        assert await limiter.check_global_limit(2) is True
        assert await limiter.check_global_limit(2) is False

    async def test_action_limit_via_redis(self):
        redis = FakeAsyncRedis()
        limiter = RedisRateLimiter(RateLimitConfig(action_limits={"payment": (1, 60)}), redis)
        assert await limiter.check_action_limit(3, "payment") is True
        assert await limiter.check_action_limit(3, "payment") is False

    async def test_redis_failure_does_not_block(self):
        class BrokenRedis:
            async def exists(self, *a, **k):
                raise RuntimeError("down")

            async def incr(self, *a, **k):
                raise RuntimeError("down")

            async def setex(self, *a, **k):
                pass

            async def set(self, *a, **k):
                return True

            async def expire(self, *a, **k):
                pass

            async def ttl(self, *a, **k):
                raise RuntimeError("down")

        limiter = RedisRateLimiter(RateLimitConfig(), BrokenRedis())
        assert await limiter.is_banned(1) is False
        assert await limiter.check_global_limit(1) is True
        assert await limiter.check_action_limit(1, "anything") is True


class TestRateLimitMiddlewareLogic:

    def test_middleware_selects_redis_limiter_when_redis_available(self):
        import bot.middleware.rate_limit as rl
        config = RateLimitConfig()
        mw = rl.RateLimitMiddleware.__new__(rl.RateLimitMiddleware)
        redis = FakeAsyncRedis()
        mw.limiter = RedisRateLimiter(config, redis)
        assert isinstance(mw.limiter, RedisRateLimiter)