from __future__ import annotations
from contextvars import ContextVar
from typing import Any

from bot.misc import EnvKeys
from .strings import TRANSLATIONS, DEFAULT_LOCALE
from bot.logger_mesh import logger

LOCALE_ALIASES = {
    "ru-ru": "ru",
    "en-us": "en",
    "en-gb": "en",
    "english": "en",
    "vi-vn": "vi",
    "vn": "vi",
}

_active_locale: ContextVar[str | None] = ContextVar("active_locale", default=None)


def normalize_locale(locale: str | None) -> str:
    loc = (locale or "").lower().strip()
    loc = LOCALE_ALIASES.get(loc, loc)
    return loc if loc in TRANSLATIONS else DEFAULT_LOCALE


def set_active_locale(locale: str | None) -> None:
    _active_locale.set(normalize_locale(locale))


def reset_active_locale() -> None:
    _active_locale.set(None)


def get_locale() -> str:
    active = _active_locale.get()
    if active:
        return active
    return normalize_locale(EnvKeys.BOT_LOCALE)


# Kept for test compatibility after removing locale caching.
get_locale.cache_clear = lambda: None


def localize_for(locale: str | None, key: str, /, **kwargs: Any) -> str:
    loc = normalize_locale(locale)

    text = TRANSLATIONS.get(loc, {}).get(key)
    if text is None:
        text = TRANSLATIONS.get(DEFAULT_LOCALE, {}).get(key)
    if text is None:
        text = key

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to format translation key '{key}' with kwargs {kwargs}: {e}")

    return str(text)


def localize(key: str, /, **kwargs: Any) -> str:
    """
    Get translation by key.
    Fallback: current locale -> DEFAULT_LOCALE -> the key itself.
    """
    return localize_for(get_locale(), key, **kwargs)
