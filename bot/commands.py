from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

_COMMAND_NAMES = ("start", "shop", "profile", "orders", "balance", "rules", "help")


def get_private_commands(locale: str = "en") -> list[BotCommand]:
    from bot.i18n.main import localize_for

    return [
        BotCommand(command=name, description=localize_for(locale, f"commands.{name}"))
        for name in _COMMAND_NAMES
    ]


async def setup_bot_commands(bot: Bot) -> None:
    # Default scope (any language): English descriptions.
    await bot.set_my_commands(
        commands=get_private_commands("en"),
        scope=BotCommandScopeAllPrivateChats(),
    )
    # Language-specific overrides: Telegram picks these based on the client language.
    await bot.set_my_commands(
        commands=get_private_commands("en"),
        scope=BotCommandScopeAllPrivateChats(),
        language_code="en",
    )
    await bot.set_my_commands(
        commands=get_private_commands("vi"),
        scope=BotCommandScopeAllPrivateChats(),
        language_code="vi",
    )