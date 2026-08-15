"""Vercel serverless entrypoint for the Telegram shop bot.

The bot runs in webhook mode here. One ASGI app serves:
  - Telegram webhook  (POST {WEBHOOK_PATH}, default ``/webhook``)
  - SQLAdmin panel + /health /metrics /export + SePay IPN (mounted below)
  - cron endpoints for payment recovery and data cleanup

Works with ``vercel.json`` rewrites that forward every path to this function.
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
from bot.misc.caching import get_redis_storage
from bot.web.admin import create_admin_app

logger = logging.getLogger("vercel")

# SQLAdmin / health / metrics / export / SePay IPN app (built once per warm instance).
admin_app = create_admin_app(bot=None)

_runtime: dict | None = None
_runtime_lock = asyncio.Lock()


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

        storage = get_redis_storage() or MemoryStorage()
        if isinstance(storage, MemoryStorage):
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
    update = Update.model_validate_raw(body)
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
    """Run one payment-recovery pass (invoked by Vercel Cron)."""
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
    """Run one cleanup pass (invoked by Vercel Cron)."""
    try:
        from bot.misc.services.cleanup import CleanupManager

        cm = CleanupManager()
        cm.running = False  # single pass, no loop
        await cm.cleanup_once()
        return JSONResponse({"ok": True})
    except Exception as e:
        logger.error(f"Cron cleanup failed: {e}", exc_info=True)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


webhook_path = EnvKeys.WEBHOOK_PATH or "/webhook"

app = Starlette(
    routes=[
        Route(webhook_path, webhook_handler, methods=["POST"]),
        Route("/api/set-webhook", set_webhook_handler, methods=["GET", "POST"]),
        Route("/api/cron/recovery", cron_recovery, methods=["GET", "POST"]),
        Route("/api/cron/cleanup", cron_cleanup, methods=["GET", "POST"]),
        Mount("/", app=admin_app),
    ]
)