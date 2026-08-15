"""Vercel serverless entrypoint for the Telegram shop bot.

The bot runs in webhook mode here. One ASGI app serves:
  - Telegram webhook  (POST {WEBHOOK_PATH}, default ``/webhook``)
  - SQLAdmin panel + /health /metrics /export + SePay IPN (mounted below)
  - cron endpoints for payment recovery and data cleanup

Works with ``vercel.json`` rewrites that forward every path to this function.

Serverless safety rules enforced here:
  - no long-lived process / no polling
  - Redis (not MemoryStorage) when running on Vercel
  - cron endpoints are locked (distributed) and authenticated via CRON_SECRET
  - the admin panel's SePay IPN can trigger a lazy bot/runtime init on a cold slot
"""

import asyncio
import logging

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.misc import EnvKeys
from bot.misc.env import is_serverless, validate_production
from bot.misc.caching import get_redis_storage
from bot.misc.caching.storage import get_shared_redis
from bot.web.admin import create_admin_app

logger = logging.getLogger("vercel")

# Fail fast on obviously broken serverless configuration before the app exists.
validate_production()

# SQLAdmin / health / metrics / export / SePay IPN app (built once per warm instance).
admin_app = create_admin_app(bot=None)

_runtime: dict | None = None
_runtime_lock = asyncio.Lock()

_CRON_PREFIX = "bot:cron:lock:"
_CRON_LOCK_TTL = 240  # seconds; keep under the Vercel function max runtime


def _verify_cron_secret(request: Request) -> bool:
    """Accept Vercel cron invocations only.

    Vercel sends ``Authorization: Bearer $CRON_SECRET`` when CRON_SECRET is set, and
    additionally sets the ``x-vercel-cron`` header on real cron invocations. We also
    allow a manual call if it carries the correct Bearer secret (useful for testing).
    """
    cron_secret = EnvKeys.CRON_SECRET
    if cron_secret:
        auth = request.headers.get("Authorization", "")
        if auth == f"Bearer {cron_secret}":
            return True
        return False
    # No secret configured: trust Vercel's own cron marker; otherwise reject so random
    # internet hits cannot trigger expensive DB scans.
    return request.headers.get("x-vercel-cron") == "1" or request.headers.get("x-vercel-cron-schedule") is not None


async def _cron_lock(token: str) -> bool:
    """Acquire a distributed cron lock (Redis). False when another invocation is running."""
    redis = get_shared_redis()
    if redis is None:
        return True  # no Redis: single invoker (local / non-shared) — proceed
    try:
        acquired = await redis.set(f"{_CRON_PREFIX}{token}", "1", nx=True, ex=_CRON_LOCK_TTL)
        return bool(acquired)
    except Exception as e:
        logger.error(f"Cron lock error ({token}): {e}")
        return True  # never block the maintenance path on a Redis hiccup


async def _ensure_runtime() -> dict:
    """Lazily build the aiogram Bot + Dispatcher once per warm serverless instance."""
    global _runtime
    if _runtime is not None:
        return _runtime

    async with _runtime_lock:
        if _runtime is not None:
            return _runtime

        from bot.logger_mesh import configure_logging
        configure_logging(
            console=EnvKeys.LOG_TO_STDOUT == "1",
            debug=EnvKeys.DEBUG == "1",
        )

        from bot.main import initialize_bot_runtime

        storage = get_redis_storage()
        if storage is None:
            if is_serverless():
                raise RuntimeError(
                    "Redis is required on Vercel but get_redis_storage() returned None. "
                    "Check REDIS_ENABLED=1 and REDIS_URL/REDIS_* configuration."
                )
            storage = MemoryStorage()
            logger.warning(
                "Using MemoryStorage on serverless - FSM state may reset between invocations. "
                "Configure Redis (e.g. Upstash) for reliable multi-step dialogs."
            )

        dp = Dispatcher(storage=storage)
        bot = Bot(
            token=EnvKeys.TOKEN,
            default=DefaultBotProperties(
                parse_mode="HTML",
                link_preview_is_disabled=False,
                protect_content=False,
            ),
        )

        await initialize_bot_runtime(dp, bot)

        admin_app.state.bot = bot
        _runtime = {"bot": bot, "dp": dp}
        return _runtime


async def webhook_handler(request: Request) -> Response:
    """Feed a Telegram update into the dispatcher."""
    # Optional webhook secret verification
    if EnvKeys.WEBHOOK_SECRET:
        token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if token != EnvKeys.WEBHOOK_SECRET:
            return Response(status_code=403)

    body = await request.body()
    from aiogram.types import Update

    rt = await _ensure_runtime()
    update = Update.model_validate_json(body)
    await rt["dp"].feed_update(bot=rt["bot"], update=update)
    return Response(status_code=200)


async def set_webhook_handler(request: Request) -> JSONResponse:
    """Convenience endpoint to (re)register the Telegram webhook to this deployment.

    Call once after each deploy: GET https://<project>.vercel.app/api/set-webhook
    """
    rt = await _ensure_runtime()
    base = str(request.base_url).rstrip("/")
    webhook_path = EnvKeys.WEBHOOK_PATH or "/webhook"
    url = f"{base}{webhook_path}"
    try:
        await rt["bot"].set_webhook(
            url=url,
            secret_token=EnvKeys.WEBHOOK_SECRET or None,
            allowed_updates=["message", "callback_query", "pre_checkout_query", "successful_payment"],
        )
        return JSONResponse({"ok": True, "url": url})
    except Exception as e:
        logger.error(f"setWebhook failed: {e}")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


async def cron_recovery(request: Request) -> JSONResponse:
    """Run one payment-recovery pass (invoked by Vercel Cron). Idempotent + locked."""
    if not _verify_cron_secret(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    if not await _cron_lock("recovery"):
        return JSONResponse({"ok": False, "error": "already running"}, status_code=409)
    try:
        from bot.misc.services.recovery import RecoveryManager

        rt = await _ensure_runtime()
        rm = RecoveryManager(bot=rt["bot"])
        rm.running = False  # single pass, no loop
        await rm.recover_pending_payments_once()
        return JSONResponse({"ok": True})
    except Exception as e:
        logger.error(f"Cron recovery failed: {e}", exc_info=True)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


async def cron_cleanup(request: Request) -> JSONResponse:
    """Run one cleanup pass (invoked by Vercel Cron). Idempotent + locked."""
    if not _verify_cron_secret(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    if not await _cron_lock("cleanup"):
        return JSONResponse({"ok": False, "error": "already running"}, status_code=409)
    try:
        from bot.misc.services.cleanup import CleanupManager

        cm = CleanupManager()
        cm.running = False  # single pass, no loop
        await cm.cleanup_once()
        return JSONResponse({"ok": True})
    except Exception as e:
        logger.error(f"Cron cleanup failed: {e}", exc_info=True)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


async def cron_product_ad(request: Request) -> JSONResponse:
    """Send one auto product-ad pass (invoked by Vercel Cron). Idempotent + locked.

    The manager re-checks AUTO_PRODUCT_AD_ENABLED and the interval guard itself,
    so duplicate triggers (extra cron instance / manual call) are harmless.
    """
    if not _verify_cron_secret(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    if not await _cron_lock("product-ad"):
        return JSONResponse({"ok": False, "error": "already running"}, status_code=409)
    try:
        from bot.misc.services.product_ad import ProductAdManager

        rt = await _ensure_runtime()
        pam = ProductAdManager(bot=rt["bot"])
        pam.running = False  # single pass, no loop
        report = await pam.run_once()
        return JSONResponse(report)
    except Exception as e:
        logger.error(f"Cron product-ad failed: {e}", exc_info=True)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


webhook_path = EnvKeys.WEBHOOK_PATH or "/webhook"

admin_app.state.ensure_runtime = _ensure_runtime

app = Starlette(
    routes=[
        Route(webhook_path, webhook_handler, methods=["POST"]),
        Route("/api/set-webhook", set_webhook_handler, methods=["GET", "POST"]),
        Route("/api/cron/recovery", cron_recovery, methods=["GET", "POST"]),
        Route("/api/cron/cleanup", cron_cleanup, methods=["GET", "POST"]),
        Route("/api/cron/product-ad", cron_product_ad, methods=["GET", "POST"]),
        Mount("/", app=admin_app),
    ]
)