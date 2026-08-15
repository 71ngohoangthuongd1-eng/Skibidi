"""Tests for the auto product-ad rotation service.

Coverage:
- ``query_in_stock_items`` only returns products that have stock.
- Rotation advances through in-stock products and wraps around.
- Sold-out products are skipped; restocked products re-enter the rotation.
- ``run_once`` broadcasts to non-blocked users and skips blocked ones.
- Interval guard / disabled flag short-circuit the pass.
- Offer registry round-trips a token to the advertised item.
- VN/EN i18n keys exist for the promo message and button.
"""

from unittest.mock import patch

import pytest

from bot.misc import EnvKeys
from bot.misc.services import ProductAdManager, reset_memory_state
from bot.misc.services.product_ad import register_ad_offer, resolve_ad_offer


@pytest.fixture(autouse=True)
def clean_memory_state():
    reset_memory_state()
    yield
    reset_memory_state()


@pytest.fixture
def enable_ad():
    with patch.object(EnvKeys, "AUTO_PRODUCT_AD_ENABLED", "1"), \
            patch.object(EnvKeys, "AUTO_PRODUCT_AD_INTERVAL", 60):
        yield


class FakeBot:
    def __init__(self):
        self.messages = []
        self.unknown = set()

    async def send_message(self, chat_id, text, reply_markup=None, parse_mode="HTML", disable_notification=True):
        self.messages.append({
            "chat_id": chat_id, "text": text,
            "reply_markup": reply_markup, "parse_mode": parse_mode,
        })
        return True


@pytest.fixture
def fake_bot():
    return FakeBot()


class TestInStockQuery:
    async def test_returns_only_items_with_stock(self, item_factory):
        await item_factory(name="HasFinite", values=[("v1", False)])
        await item_factory(name="HasInfinity", values=[("unlimited", True)])
        await item_factory(name="EmptyItem", values=[])

        from bot.database.methods import query_in_stock_items
        result = await query_in_stock_items(limit=100)
        assert "HasFinite" in result
        assert "HasInfinity" in result
        assert "EmptyItem" not in result

    async def test_count_only(self, item_factory):
        await item_factory(name="A", values=[("v1", False)])
        await item_factory(name="B", values=[("v2", False)])

        from bot.database.methods import query_in_stock_items
        assert await query_in_stock_items(count_only=True) == 2


class TestRotation:
    async def test_picks_next_product_and_wraps(self, item_factory, enable_ad, fake_bot):
        await item_factory(name="Alpha", values=[("v", False)])
        await item_factory(name="Beta", values=[("v", False)])
        await item_factory(name="Gamma", values=[("v", False)])

        mgr = ProductAdManager(bot=fake_bot)
        assert await mgr._pick_next_in_stock() == "Alpha"
        assert await mgr._pick_next_in_stock() == "Beta"
        assert await mgr._pick_next_in_stock() == "Gamma"
        assert await mgr._pick_next_in_stock() == "Alpha"

    async def test_infinite_item_is_advertisable(self, item_factory, enable_ad, fake_bot):
        await item_factory(name="Unlimited", values=[("shared", True)])
        await item_factory(name="Empty", values=[])

        mgr = ProductAdManager(bot=fake_bot)
        assert await mgr._pick_next_in_stock() == "Unlimited"

    async def test_sold_out_skipped_restock_returns(self, item_factory, enable_ad, fake_bot):
        from bot.database.methods.create import add_values_to_item
        from bot.database.methods.delete import delete_only_items

        await item_factory(name="First", values=[("v1", False)])
        await item_factory(name="Second", values=[("v2", False)])

        mgr = ProductAdManager(bot=fake_bot)
        assert await mgr._pick_next_in_stock() == "First"

        # Sell out First -> rotation should skip it
        await delete_only_items("First")
        assert await mgr._pick_next_in_stock() == "Second"

        # Restock First -> it comes back into rotation
        await add_values_to_item("First", "v1-again", False)
        assert await mgr._pick_next_in_stock() == "First"


class TestBroadcast:
    async def test_broadcasts_to_non_blocked_users(self, item_factory, user_factory, enable_ad, fake_bot):
        await item_factory(name="PromoItem", price=500, values=[("v", False)])
        await user_factory(telegram_id=1001)
        await user_factory(telegram_id=1002)

        mgr = ProductAdManager(bot=fake_bot)
        report = await mgr.run_once()

        assert report["ok"] is True
        assert report["item"] == "PromoItem"
        assert report["recipients"] == 2
        assert report["sent"] == 2
        assert len(fake_bot.messages) == 2
        sent_ids = {m["chat_id"] for m in fake_bot.messages}
        assert sent_ids == {1001, 1002}

    async def test_skips_blocked_users(self, item_factory, user_factory, enable_ad, fake_bot):
        from bot.database.methods import set_user_blocked

        await item_factory(name="PromoItem", price=500, values=[("v", False)])
        await user_factory(telegram_id=1001)
        await user_factory(telegram_id=1002)
        await set_user_blocked(1002, True)

        mgr = ProductAdManager(bot=fake_bot)
        report = await mgr.run_once()

        assert report["recipients"] == 1
        assert report["sent"] == 1
        assert {m["chat_id"] for m in fake_bot.messages} == {1001}

    async def test_no_recipients_skips(self, item_factory, enable_ad, fake_bot):
        await item_factory(name="PromoItem", values=[("v", False)])
        mgr = ProductAdManager(bot=fake_bot)
        report = await mgr.run_once()
        assert report["ok"] is True
        assert report["skipped"] == "no_recipients"

    async def test_no_stock_skips(self, item_factory, enable_ad, fake_bot):
        await item_factory(name="Empty", values=[])
        mgr = ProductAdManager(bot=fake_bot)
        report = await mgr.run_once()
        assert report["ok"] is True
        assert report["skipped"] == "no_stock"


class TestGuards:
    async def test_disabled_flag_skips(self, item_factory, user_factory, fake_bot):
        with patch.object(EnvKeys, "AUTO_PRODUCT_AD_ENABLED", "0"):
            await item_factory(name="PromoItem", values=[("v", False)])
            await user_factory(telegram_id=1001)
            mgr = ProductAdManager(bot=fake_bot)
            report = await mgr.run_once()
        assert report["ok"] is True
        assert report["skipped"] == "disabled"
        assert fake_bot.messages == []

    async def test_too_soon_guard(self, item_factory, user_factory, enable_ad, fake_bot):
        await item_factory(name="PromoItem", values=[("v", False)])
        await user_factory(telegram_id=1001)

        mgr = ProductAdManager(bot=fake_bot)
        first = await mgr.run_once()
        assert first["sent"] == 1

        # Immediately re-running must be skipped by the interval guard.
        second = await mgr.run_once()
        assert second["ok"] is True
        assert second["skipped"] == "too_soon"
        assert len(fake_bot.messages) == 1

    async def test_in_progress_guard(self, item_factory, user_factory, enable_ad, fake_bot):
        await item_factory(name="PromoItem", values=[("v", False)])
        await user_factory(telegram_id=1001)

        mgr = ProductAdManager(bot=fake_bot)
        mgr._in_progress = True
        report = await mgr.run_once()
        assert report["ok"] is False
        assert report["error"] == "already_running"


class TestOfferRegistry:
    async def test_roundtrip(self):
        token = await register_ad_offer("PromoItem", ttl=3600)
        assert await resolve_ad_offer(token) == "PromoItem"

    async def test_unknown_token_returns_none(self):
        assert await resolve_ad_offer("nope") is None


class TestI18n:
    def test_promo_keys_exist_in_en_and_vi(self):
        from bot.i18n.strings import TRANSLATIONS

        required = [
            "product_ad.title",
            "product_ad.name",
            "product_ad.description",
            "product_ad.price",
            "product_ad.stock_left",
            "product_ad.stock_unlimited",
            "product_ad.buy_cta",
            "product_ad.btn.buy",
        ]
        for loc in ("en", "vi"):
            for key in required:
                assert key in TRANSLATIONS[loc], f"missing {key} in {loc}"

    def test_vi_uses_vietnamese_copies(self):
        from bot.i18n.main import localize_for

        assert "Sản phẩm nổi bật" in localize_for("vi", "product_ad.title")
        assert "Mua Ngay" in localize_for("vi", "product_ad.btn.buy")
        assert "Buy Now" in localize_for("en", "product_ad.btn.buy")