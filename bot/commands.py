from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


def get_private_commands(locale: str = "en") -> list[BotCommand]:
    from bot.i18n.main import localize_for

    return [
        BotCommand(command="start", description=localize_for(locale, "commands.start")),
        BotCommand(command="menu", description=localize_for(locale, "commands.menu")),
        BotCommand(command="profile", description=localize_for(locale, "commands.profile")),
        BotCommand(command="rules", description=localize_for(locale, "commands.rules")),
        BotCommand(command="help", description=localize_for(locale, "commands.help")),
    ]


async def setup_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        commands=get_private_commands("en"),
        scope=BotCommandScopeAllPrivateChats(),
    )
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
