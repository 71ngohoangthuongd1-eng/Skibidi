import json
from pathlib import Path

from bot.i18n.main import normalize_locale


_DATA_DIR = Path("data")
_STORE_PATH = _DATA_DIR / "user_locales.json"
_CACHE: dict[str, str] | None = None


def _load() -> dict[str, str]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    if not _STORE_PATH.exists():
        _CACHE = {}
        return _CACHE

    try:
        _CACHE = json.loads(_STORE_PATH.read_text(encoding="utf-8"))
    except Exception:
        _CACHE = {}
    return _CACHE


def _save(data: dict[str, str]) -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    _STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_user_locale(user_id: int) -> str | None:
    return _load().get(str(user_id))


def set_user_locale(user_id: int, locale: str) -> str:
    data = _load()
    normalized = normalize_locale(locale)
    data[str(user_id)] = normalized
    _save(data)
    return normalized
