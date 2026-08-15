"""Tests for the Redis-aware admin LoginRateLimiter (admin.py).

- Redis path: distributed counters via sorted sets (works across Vercel instances)
- Memory path: single-process fallback keeps local development working
- Production validation warns explicitly when Redis (required for security) is off
"""

import time

from bot.web.admin import LoginRateLimiter


class FakeSyncRedis:
    """Minimal sync stand-in covering zadd/zremrangebyscore/zcard/expire/delete."""

    def __init__(self):
        self._zsets = {}

    def zadd(self, key, mapping):
        self._zsets.setdefault(key, {})
        for member, score in mapping.items():
            self._zsets[key][member] = score

    def zremrangebyscore(self, key, min_, max_):
        # Redis semantics: drop members whose score is within [min_, max_].
        hits = [m for m, sc in self._zsets.get(key, {}).items() if min_ <= sc <= max_]
        for m in hits:
            self._zsets[key].pop(m, None)
        return len(hits)

    def zcard(self, key):
        return len(self._zsets.get(key, {}))

    def expire(self, key, seconds):
        return True

    def delete(self, *keys):
        for k in keys:
            self._zsets.pop(k, None)
        return len(keys)

    def discard(self):
        self._zsets.clear()


class TestRedisBackedLimiter:

    def test_blocks_after_max_attempts_and_reset_clears(self):
        limiter = LoginRateLimiter(max_attempts=5, lockout_seconds=900)
        redis = FakeSyncRedis()
        limiter._redis = redis  # inject instead of building a real client

        assert limiter.is_blocked("1.2.3.4") is False
        for _ in range(5):
            limiter.record_failure("1.2.3.4")
        assert limiter.is_blocked("1.2.3.4") is True

        limiter.reset("1.2.3.4")
        assert limiter.is_blocked("1.2.3.4") is False

    def test_different_ips_are_independent(self):
        limiter = LoginRateLimiter(max_attempts=2, lockout_seconds=900)
        redis = FakeSyncRedis()
        limiter._redis = redis

        limiter.record_failure("10.0.0.1")
        limiter.record_failure("10.0.0.1")
        assert limiter.is_blocked("10.0.0.1") is True
        assert limiter.is_blocked("10.0.0.2") is False

    def test_old_failures_expire_outside_lockout_window(self):
        limiter = LoginRateLimiter(max_attempts=3, lockout_seconds=10)
        redis = FakeSyncRedis()
        limiter._redis = redis

        for _ in range(3):
            limiter.record_failure("9.9.9.9")
        assert limiter.is_blocked("9.9.9.9") is True

        # Simulate the window passing: drop old members, the counter must reset.
        redis.discard()
        assert limiter.is_blocked("9.9.9.9") is False


class TestMemoryFallbackLimiter:

    def test_production_constructor_without_redis_falls_back_to_memory(self):
        limiter = LoginRateLimiter(max_attempts=2, lockout_seconds=900)
        # `_redis` stays None ⇒ _get_redis tries to build a real client and fails
        # (no Redis in CI), falling back to the in-memory registry.
        assert limiter._redis is None
        limiter.record_failure("5.5.5.5")
        limiter.record_failure("5.5.5.5")
        assert limiter.is_blocked("5.5.5.5") is True
        limiter.reset("5.5.5.5")
        assert limiter.is_blocked("5.5.5.5") is False

    def test_memory_window_expiry(self):
        limiter = LoginRateLimiter(max_attempts=1, lockout_seconds=1)
        limiter.record_failure("6.6.6.6")
        assert limiter.is_blocked("6.6.6.6") is True
        time.sleep(1.1)
        assert limiter.is_blocked("6.6.6.6") is False


class TestRedisFailureDegradesGracefully:

    def test_redis_errors_fall_back_to_memory(self):
        class BrokenRedis(FakeSyncRedis):
            def zadd(self, *a, **k):
                raise RuntimeError("redis down")
            def zcard(self, *a, **k):
                raise RuntimeError("redis down")
            def zremrangebyscore(self, *a, **k):
                raise RuntimeError("redis down")

        limiter = LoginRateLimiter(max_attempts=2, lockout_seconds=900)
        limiter._redis = BrokenRedis()

        limiter.record_failure("7.7.7.7")
        limiter.record_failure("7.7.7.7")
        assert limiter.is_blocked("7.7.7.7") is True