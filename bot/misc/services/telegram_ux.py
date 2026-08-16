"""Tiny Telegram UX helpers: safely signal activity so handlers can mask a
slow DB/API/render step without ever failing or leaving background work."""

from typing import Optional

from aiogram import Bot
from aiogram.enums import ChatAction


async def send_chat_action(
    bot: Bot,
    chat_id: int,
    action: ChatAction = ChatAction.TYPING,
) -> None:
    """Send a Telegram chat action (typing / upload_photo / ...).

    Errors are swallowed: chat actions are best-effort UX niceties and must
    never crash a payment handler. The action ends automatically when the bot
    sends the next message, so no background task is left behind.
    """
    try:
        await bot.send_chat_action(chat_id=chat_id, action=action)
    except Exception:
        pass
