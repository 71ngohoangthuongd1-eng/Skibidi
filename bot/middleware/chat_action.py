"""Centralized Telegram chat-action signaling for every user-facing update.

Attached as inner middleware on the dispatcher update types a Telegram user can
interact with (``message``, ``callback_query``, ``pre_checkout_query``,
``successful_payment``). Before (and while) the actual handler runs it signals a
chat action — ``typing`` by default, or ``upload_photo`` for photo-producing
flows such as SePay QR — so the user always sees the bot is working instead of
appearing frozen during a slow DB/API/render step.

Safety guarantees (serverless-friendly):
  * Non-interactive endpoints never reach the dispatcher — ``/sepay/ipn``,
    Vercel cron, cleanup, recovery, health and the admin HTTP panel bypass
    ``dp.feed_update`` entirely, so no chat action is ever sent for them.
  * The chat action runs *concurrently* with the handler via ``asyncio.gather``
    and both are awaited before the request returns — no orphaned background
    task is left behind on Vercel, and no artificial ``sleep()`` is used.
  * Any chat-action failure is swallowed: it is a best-effort UX nicety and must
    never crash a payment / purchase handler.
  * It does NOT auto-answer callback queries. Telegram accepts only one
    ``answerCallbackQuery`` per callback id — pre-answering here would both drop
    the alert/toast texts handlers send and make the handler's own
    ``call.answer()`` raise. Early callback ack remains the handlers'
    responsibility (they already call ``call.answer()``).
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.enums import ChatAction
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, TelegramObject

# Callback-data prefixes that produce a photo (e.g. SePay VietQR) → upload_photo.
_PHOTO_CALLBACK_PREFIXES: tuple[str, ...] = (
    "buy_direct_account",
    "sepay_qr",
    "vietqr",
)


def _resolve_chat_id(event: TelegramObject) -> Optional[int]:
    """Best-effort chat id for the interactive event (None when unknown)."""
    if isinstance(event, (Message, CallbackQuery)):
        chat = getattr(event, "chat", None)
        if chat is not None:
            chat_id = getattr(chat, "id", None)
            if chat_id is not None:
                return chat_id
        # CallbackQuery may be detached (no .message); fall back to the user.
        message = getattr(event, "message", None)
        if message is not None:
            chat_id = getattr(message.chat, "id", None)
            if chat_id is not None:
                return chat_id
    user = getattr(event, "from_user", None)
    return getattr(user, "id", None) if user is not None else None


class ChatActionMiddleware(BaseMiddleware):
    """Signal a Telegram chat action for every interactive user update.

    ``photo_prefixes`` lets callers override which callback data should show
    ``upload_photo`` instead of ``typing`` (defaults to SePay QR flows).
    """

    def __init__(self, photo_prefixes: tuple[str, ...] = _PHOTO_CALLBACK_PREFIXES):
        self._photo_prefixes = photo_prefixes
        self.default_action = ChatAction.TYPING

    async def _action_for(self, event: TelegramObject) -> Optional[ChatAction]:
        if isinstance(event, CallbackQuery):
            data = event.data or ""
            if any(data.startswith(prefix) for prefix in self._photo_prefixes):
                return ChatAction.UPLOAD_PHOTO
            return self.default_action
        if isinstance(event, (Message, PreCheckoutQuery)):
            return self.default_action
        return None

    async def _safe_signal(self, bot, chat_id: Optional[int], action: ChatAction) -> None:
        if bot is None or chat_id is None or action is None:
            return
        try:
            await bot.send_chat_action(chat_id=chat_id, action=action)
        except Exception:
            # Best-effort UX only — never let a chat-action failure break the handler.
            pass

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        bot = data.get("bot")
        chat_id = _resolve_chat_id(event)
        action = await self._action_for(event)

        if bot is None or chat_id is None or action is None:
            return await handler(event, data)

        # Run the chat action concurrently with the real handler work and await
        # both. This keeps latency minimal (overlaps the slow DB/API step) while
        # guaranteeing no task outlives the Vercel request.
        handler_result, _ = await asyncio.gather(
            handler(event, data),
            self._safe_signal(bot, chat_id, action),
        )
        return handler_result
