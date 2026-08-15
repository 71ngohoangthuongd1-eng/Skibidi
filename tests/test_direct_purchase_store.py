"""Tests for the distributed direct-purchase intent store (Redis + memory fallback)."""

from unittest.mock import patch

import pytest

from bot.misc.direct_purchase_store import (
    get_direct_purchase_intent,
    set_direct_purchase_intent,
    delete_direct_purchase_intent,
    _MEMORY,
)


class FakeRedis:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        raw = self.data.get(key)
        return raw

    async def setex(self, key, seconds, value):
        self.data[key] = value

    async def delete(self, key):
        self.data.pop(key, None)


@pytest.fixture(autouse=True)
def clear_memory():
    _MEMORY.clear()
    yield
    _MEMORY.clear()


class TestRedisBackedStore:
    async def test_set_and_get_roundtrip(self):
        redis = FakeRedis()
        with patch("bot.misc.direct_purchase_store.get_shared_redis", return_value=redis):
            await set_direct_purchase_intent(101, item_name="Premium Account", promo_code="SAVE10")
            intent = await get_direct_purchase_intent(101)
        assert intent == {"item_name": "Premium Account", "promo_code": "SAVE10"}

    async def test_get_missing_returns_none(self):
        redis = FakeRedis()
        with patch("bot.misc.direct_purchase_store.get_shared_redis", return_value=redis):
            assert await get_direct_purchase_intent(404) is None

    async def test_delete_removes(self):
        redis = FakeRedis()
        with patch("bot.misc.direct_purchase_store.get_shared_redis", return_value=redis):
            await set_direct_purchase_intent(202, item_name="VIP")
            await delete_direct_purchase_intent(202)
            assert await get_direct_purchase_intent(202) is None

    async def test_no_promo_code_defaults_to_none(self):
        redis = FakeRedis()
        with patch("bot.misc.direct_purchase_store.get_shared_redis", return_value=redis):
            await set_direct_purchase_intent(303, item_name="Basic")
            assert await get_direct_purchase_intent(303) == {"item_name": "Basic", "promo_code": None}

    async def test_redis_error_falls_back_to_memory(self):
        class BrokenRedis(FakeRedis):
            async def setex(self, key, seconds, value):
                raise RuntimeError("down")

            async def get(self, key):
                raise RuntimeError("down")

            async def delete(self, key):
                raise RuntimeError("down")

        redis = BrokenRedis()
        with patch("bot.misc.direct_purchase_store.get_shared_redis", return_value=redis):
            await set_direct_purchase_intent(404, item_name="Tolerant")
            # get through redis path fails => falls through to memory
            intent = await get_direct_purchase_intent(404)
        assert intent == {"item_name": "Tolerant", "promo_code": None}


class TestMemoryFallbackStore:
    async def test_memory_roundtrip_when_redis_disabled(self):
        with patch("bot.misc.direct_purchase_store.get_shared_redis", return_value=None):
            await set_direct_purchase_intent(1, item_name="Local")
            assert await get_direct_purchase_intent(1) == {"item_name": "Local", "promo_code": None}
            await delete_direct_purchase_intent(1)
            assert await get_direct_purchase_intent(1) is None

    async def test_memory_missing_returns_none(self):
        with patch("bot.misc.direct_purchase_store.get_shared_redis", return_value=None):
            assert await get_direct_purchase_intent(999) is None