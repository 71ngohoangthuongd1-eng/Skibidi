"""Tests for the centralized ChatActionMiddleware.

Coverage:
- a ``typing`` chat action is signalled for a normal user message,
- a ``typing`` chat action is signalled for a normal (non-photo) callback,
- an ``upload_photo`` chat action is signalled for photo-producing callbacks
  (SePay VietQR direct-purchase flow),
- a failing chat action never breaks the handler (best-effort UX),
- the handler result is always returned unchanged.
"""

import asyncio
import datetime
from unittest.mock import AsyncMock

import pytest

from aiogram.types import (
    User, Chat, Message, CallbackQuery,
)

from bot.middleware.chat_action import ChatActionMiddleware
from bot.misc.services.telegram_ux import send_chat_action


def _user(user_id: int = 555) -> User:
    return User(id=user_id, is_bot=False, first_name="Tester")


def _chat(chat_id: int = 444) -> Chat:
    return Chat(id=chat_id, type="private")


def _message(chat=None, user=None, text: str = "hello") -> Message:
    return Message(
        message_id=1,
        date=datetime.datetime.now(datetime.timezone.utc),
        chat=chat or _chat(),
        from_user=user or _user(),
        text=text,
    )


def _callback(data: str, chat=None, user=None) -> CallbackQuery:
    return CallbackQuery(
        id="cb_" + data,
        from_user=user or _user(),
        chat_instance="instance1",
        data=data,
        message=_message(chat=chat),
    )


async def _run(mw, event, bot=None):
    """Invoke the middleware with a trivial handler returning a sentinel."""
    sentinel = object()
    bot = bot or AsyncMock(spec=["send_chat_action"])
    bot.send_chat_action = AsyncMock(return_value=None)

    async def handler(ev, data):
        return sentinel

    result = await mw(handler, event, {"bot": bot})
    return result, bot


class TestSignalsTyping:

    async def test_message_signals_typing(self):
        mw = ChatActionMiddleware()
        result, bot = await _run(mw, _message(chat=_chat(123), text="/start"))
        assert result is not None
        bot.send_chat_action.assert_awaited_once_with(chat_id=123, action="typing")

    async def test_callback_signals_typing(self):
        mw = ChatActionMiddleware()
        result, bot = await _run(mw, _callback("open_item:chatgpt", chat=_chat(123)))
        assert result is not None
        bot.send_chat_action.assert_awaited_once_with(chat_id=123, action="typing")


class TestSignalsPhoto:

    async def test_qr_callback_signals_upload_photo(self):
        mw = ChatActionMiddleware()
        result, bot = await _run(mw, _callback("buy_direct_account", chat=_chat(123)))
        assert result is not None
        bot.send_chat_action.assert_awaited_once_with(chat_id=123, action="upload_photo")

    async def test_upload_photo_uses_current_api_action(self):
        mw = ChatActionMiddleware()
        result, bot = await _run(mw, _callback("buy_direct_account", chat=_chat(999)))
        # Ensure the enum value matches what send_chat_action forwards verbatim.
        assert result is not None
        bot.send_chat_action.assert_awaited_once_with(chat_id=999, action="upload_photo")


class TestRobustness:

    async def test_chat_action_failure_does_not_break_handler(self):
        mw = ChatActionMiddleware()
        bot = AsyncMock(spec=["send_chat_action"])
        bot.send_chat_action = AsyncMock(side_effect=RuntimeError("telegram down"))

        sentinel = object()

        async def handler(ev, data):
            return sentinel

        result = await mw(handler, _message(chat=_chat(123)), {"bot": bot})
        assert result is sentinel
        bot.send_chat_action.assert_awaited_once()

    async def test_handler_raises_propagates(self):
        mw = ChatActionMiddleware()
        bot = AsyncMock(spec=["send_chat_action"])
        bot.send_chat_action = AsyncMock(return_value=None)

        async def handler(ev, data):
            raise ValueError("handler failed")

        with pytest.raises(ValueError):
            await mw(handler, _message(chat=_chat(123)), {"bot": bot})

    async def test_no_bot_in_data_still_runs_handler(self):
        mw = ChatActionMiddleware()
        sentinel = object()

        async def handler(ev, data):
            return sentinel

        result = await mw(handler, _message(chat=_chat(123)), {})
        assert result is sentinel

    async def test_concurrent_signal_awaited(self):
        # Both the handler and the chat action are awaited within the call, so
        # no orphaned background task can outlive a Vercel request.
        mw = ChatActionMiddleware()
        bot = AsyncMock(spec=["send_chat_action"])
        bot.send_chat_action = AsyncMock(return_value=None)

        async def handler(ev, data):
            return "ok"

        await mw(handler, _message(chat=_chat(1)), {"bot": bot})
        assert bot.send_chat_action.await_count == 1
