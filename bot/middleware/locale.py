from aiogram import BaseMiddleware

from bot.i18n.main import reset_active_locale, set_active_locale
from bot.i18n.store import get_user_locale
from bot.misc import EnvKeys


class LocaleMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        locale = get_user_locale(user.id) if user else EnvKeys.BOT_LOCALE
        set_active_locale(locale)
        try:
            return await handler(event, data)
        finally:
            reset_active_locale()
