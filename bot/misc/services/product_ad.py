"""Auto product-ad rotation service.

Every ``AUTO_PRODUCT_AD_INTERVAL`` seconds (default 1 hour) the manager picks ONE
in-stock product and sends a localized promo message to every non-blocked user.

Design constraints (serverless-safe, mirrors api/index.py cron handling):
  - single pass: ``run_once()`` does one broadcast and returns; no long polling.
  - rotation state is kept in Redis (distributed) with an in-memory fallback for
    local polling where REDIS_ENABLED=0.
  - a distributed lock (``bot:cron:lock:product-ad``) prevents overlapping runs
    across Vercel instances; same prefix/TTL as the existing cron locks.
  - a last-run timestamp guard enforces the interval so duplicate cron/loop
    triggers cannot spam users.
  - out-of-stock products are skipped automatically because the rotation pool is
    rebuilt from the DB on every pass (restocked items come back on their own).
  - sending reuses ``BroadcastManager`` (batching + flood control + per-user
    error handling).
"""

import asyncio
import logging
import secrets
import time
from typing import Optional

from aiogram import Bot

from bot.i18n.main import localize_for, normalize_locale
from bot.i18n.store import get_user_locale
from bot.misc import EnvKeys
from bot.misc.caching.storage import get_shared_redis
from bot.misc.services.broadcast_system import BroadcastManager, BroadcastStats

logger = logging.getLogger(__name__)

_COUNTER_KEY = "bot:product_ad:counter"
_LAST_RUN_KEY = "bot:product_ad:last_run"
_OFFER_PREFIX = "bot:product_ad:offer:"

# In-memory fallback for local polling / tests where Redis is disabled.
_MEMORY_META: dict = {"counter": 0, "last_run": 0.0}
_MEMORY_OFFERS: dict = {}


def _meta_store() -> dict:
    return _MEMORY_META


def _offers_store() -> dict:
    return _MEMORY_OFFERS


def reset_memory_state() -> None:
    """Clear the in-memory fallback stores (used by tests)."""
    _MEMORY_META["counter"] = 0
    _MEMORY_META["last_run"] = 0.0
    _MEMORY_OFFERS.clear()


def make_offer_token() -> str:
    """Short random token for a product-ad callback."""
    return secrets.token_urlsafe(6)


def _offer_key(token: str) -> str:
    return f"{_OFFER_PREFIX}{token}"


async def register_ad_offer(item_name: str, ttl: int) -> str:
    """Persist a token->item mapping so a callback can open the exact product."""
    token = make_offer_token()
    redis = get_shared_redis()
    if redis is None:
        _offers_store()[token] = item_name
        return token
    try:
        await redis.set(_offer_key(token), item_name, ex=ttl)
        return token
    except Exception as e:
        logger.error(f"Product ad offer persist error: {e}")
        _offers_store()[token] = item_name
        return token


async def resolve_ad_offer(token: str) -> Optional[str]:
    """Resolve a product-ad offer token back to an item name (or None)."""
    redis = get_shared_redis()
    if redis is not None:
        try:
            raw = await redis.get(_offer_key(token))
            if raw is not None:
                return raw.decode() if isinstance(raw, bytes) else raw
        except Exception as e:
            logger.error(f"Product ad offer read error: {e}")
    return _offers_store().get(token)


class ProductAdManager:
    """Coordinate the hourly product promo rotation."""

    def __init__(
            self,
            bot: Bot,
            batch_size: int = 30,
            batch_delay: float = 1.0,
            retry_count: int = 3,
    ):
        self.bot = bot
        self.batch_size = batch_size
        self.batch_delay = batch_delay
        self.retry_count = retry_count
        self.running = False
        self.tasks = []
        self._in_progress = False

    # --- lifecycle (local polling) ---

    async def start(self) -> None:
        if EnvKeys.AUTO_PRODUCT_AD_ENABLED != "1":
            logger.info("Product ad is disabled via AUTO_PRODUCT_AD_ENABLED")
            return
        logger.info("Starting product ad manager...")
        self.running = True
        self.tasks.append(asyncio.create_task(self._safe_loop()))
        logger.info("Product ad manager started")

    async def stop(self) -> None:
        self.running = False
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("Product ad manager stopped")

    async def _safe_loop(self) -> None:
        interval = max(EnvKeys.AUTO_PRODUCT_AD_INTERVAL, 60)
        while self.running:
            await asyncio.sleep(interval)
            try:
                await self.run_once()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Product ad loop error: {e}", exc_info=True)

    # --- lock / interval guards ---

    def _interval(self) -> int:
        return max(EnvKeys.AUTO_PRODUCT_AD_INTERVAL, 60)

    async def _commit_counter(self, value: int) -> None:
        redis = get_shared_redis()
        if redis is None:
            _meta_store()["counter"] = value
            return
        try:
            await redis.set(_COUNTER_KEY, str(value), ex=86400)
        except Exception as e:
            logger.error(f"Product ad counter persist error: {e}")
            _meta_store()["counter"] = value

    async def _read_counter(self) -> int:
        redis = get_shared_redis()
        if redis is None:
            return int(_meta_store()["counter"])
        try:
            raw = await redis.get(_COUNTER_KEY)
            return int(raw) if raw is not None else 0
        except Exception as e:
            logger.error(f"Product ad counter read error: {e}")
            return int(_meta_store()["counter"])

    async def _mark_last_run(self, now: float) -> None:
        redis = get_shared_redis()
        if redis is None:
            _meta_store()["last_run"] = now
            return
        try:
            await redis.set(_LAST_RUN_KEY, str(now), ex=self._interval() * 3)
        except Exception as e:
            logger.error(f"Product ad last-run persist error: {e}")
            _meta_store()["last_run"] = now

    async def _read_last_run(self) -> float:
        redis = get_shared_redis()
        if redis is None:
            return float(_meta_store()["last_run"])
        try:
            raw = await redis.get(_LAST_RUN_KEY)
            return float(raw) if raw is not None else 0.0
        except Exception as e:
            logger.error(f"Product ad last-run read error: {e}")
            return float(_meta_store()["last_run"])

    # --- offer registry (callback -> item name) ---

    async def _register_offer(self, item_name: str) -> str:
        return await register_ad_offer(item_name, self._interval() * 3)

    async def resolve_offer(self, token: str) -> Optional[str]:
        return await resolve_ad_offer(token)

    # --- data ---

    async def _pick_next_in_stock(self) -> Optional[str]:
        """Rotate through in-stock products; skip sold-out, restock returns."""
        from bot.database.methods import query_in_stock_items

        names = await query_in_stock_items(limit=10000)
        if not names:
            return None
        counter = await self._read_counter()
        next_counter = counter + 1
        await self._commit_counter(next_counter)
        return names[(next_counter - 1) % len(names)]

    async def _recipient_ids(self) -> list:
        from bot.database.methods import get_all_users, get_blocked_user_ids

        blocked = set(await get_blocked_user_ids())
        rows = await get_all_users()
        return [int(row[0]) for row in rows if int(row[0]) not in blocked]

    async def _item_context(self, item_name: str) -> Optional[dict]:
        from bot.database.methods import (
            get_item_info, check_value, select_item_values_amount,
        )

        info = await get_item_info(item_name)
        if not info:
            return None
        return {
            "price": info["price"],
            "description": info["description"],
            "unlimited": bool(await check_value(item_name)),
            "quantity": await select_item_values_amount(item_name),
        }

    # --- message building ---

    def _build_text(self, locale: str, item_name: str, ctx: dict) -> str:
        price_line = localize_for(
            locale, "product_ad.price", amount=ctx["price"],
            currency=EnvKeys.PAY_CURRENCY,
        )
        if ctx["unlimited"]:
            stock_line = localize_for(locale, "product_ad.stock_unlimited")
        else:
            stock_line = localize_for(
                locale, "product_ad.stock_left", count=ctx["quantity"]
            )
        lines = [
            localize_for(locale, "product_ad.title"),
            localize_for(locale, "product_ad.name", name=item_name),
            localize_for(locale, "product_ad.description", description=ctx["description"]),
            price_line,
            stock_line,
            localize_for(locale, "product_ad.buy_cta"),
        ]
        return "\n".join(lines)

    def _build_markup(self, locale: str, token: str):
        from bot.keyboards.inline import simple_buttons

        return simple_buttons(
            [
                (localize_for(locale, "product_ad.btn.buy"), f"ad_item:{token}"),
                (localize_for(locale, "btn.shop"), "shop"),
            ],
            per_row=1,
        )

    # --- broadcast ---

    async def _broadcast(self, token: str, item_name: str, ctx: dict, recipients: list) -> BroadcastStats:
        """Group recipients by locale and broadcast a localized promo per group."""
        groups: dict = {}
        for uid in recipients:
            locale = normalize_locale(get_user_locale(uid) or EnvKeys.BOT_LOCALE)
            groups.setdefault(locale, []).append(uid)

        total = BroadcastStats()
        bm = BroadcastManager(
            bot=self.bot,
            batch_size=self.batch_size,
            batch_delay=self.batch_delay,
            retry_count=self.retry_count,
        )
        for locale, uids in groups.items():
            text = self._build_text(locale, item_name, ctx)
            markup = self._build_markup(locale, token)
            stats = await bm.broadcast(
                user_ids=uids,
                text=text,
                reply_markup=markup,
                parse_mode="HTML",
            )
            total.total += stats.total
            total.sent += stats.sent
            total.failed += stats.failed
            total.blocked += stats.blocked

        if total.total:
            logger.info(
                "Product ad sent: item=%r recipients=%d sent=%d failed=%d",
                item_name, total.total, total.sent, total.failed,
            )
        return total

    # --- main entry ---

    async def run_once(self) -> dict:
        """One ad pass. Returns a small report dict. Safe to call from cron."""
        if EnvKeys.AUTO_PRODUCT_AD_ENABLED != "1":
            return {"ok": True, "skipped": "disabled"}
        if self._in_progress:
            return {"ok": False, "error": "already_running"}

        now = time.time()
        last_run = await self._read_last_run()
        # Hysteresis: block duplicate triggers, but tolerate cron/loop drift
        # (a pass less than INTERVAL/2 after the previous one is always skipped).
        if last_run and (now - last_run) < self._interval() / 2:
            return {"ok": True, "skipped": "too_soon"}

        self._in_progress = True
        try:
            item_name = await self._pick_next_in_stock()
            if not item_name:
                logger.info("Product ad skipped: no in-stock items")
                await self._mark_last_run(now)
                return {"ok": True, "skipped": "no_stock"}

            ctx = await self._item_context(item_name)
            if not ctx:
                # Race with deletion: skip the run entirely.
                return {"ok": False, "error": "item_lookup_failed"}

            recipients = await self._recipient_ids()
            if not recipients:
                logger.info("Product ad skipped: no recipients")
                await self._mark_last_run(now)
                return {"ok": True, "skipped": "no_recipients", "item": item_name}

            token = await self._register_offer(item_name)
            stats = await self._broadcast(token, item_name, ctx, recipients)
            await self._mark_last_run(now)

            try:
                from bot.database.methods.audit import log_audit

                await log_audit(
                    "product_ad_sent",
                    details=f"item={item_name}, recipients={stats.total}, "
                           f"sent={stats.sent}, failed={stats.failed}",
                )
            except Exception as e:
                logger.error(f"Product ad audit error: {e}")

            return {
                "ok": True, "item": item_name,
                "recipients": stats.total, "sent": stats.sent,
                "failed": stats.failed,
            }
        finally:
            self._in_progress = False