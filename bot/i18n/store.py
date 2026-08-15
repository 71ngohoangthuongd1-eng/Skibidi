import json
import os
from pathlib import Path

from bot.i18n.main import normalize_locale


def _data_dir() -> Path:
    override = os.getenv("USER_LOCALES_DIR")
    if override:
        return Path(override)
    # On read-only serverless filesystems use the writable tmp dir.
    data_dir = Path("data")
    try:
        data_dir.mkdir(exist_ok=True)
        probe = data_dir / ".write_probe"
        probe.touch()
        probe.unlink()
        return data_dir
    except OSError:
        tmp = Path("/tmp") / "telegram_shop"
        tmp.mkdir(parents=True, exist_ok=True)
        return tmp


def _store_path() -> Path:
    return _data_dir() / "user_locales.json"


_CACHE: dict[str, str] | None = None
_CACHE_PATH: Path | None = None


def _load() -> dict[str, str]:
    global _CACHE, _CACHE_PATH
    if _CACHE is not None and _CACHE_PATH == _store_path():
        return _CACHE

    _CACHE_PATH = _store_path()
    if not _CACHE_PATH.exists():
        _CACHE = {}
        return _CACHE

    try:
        _CACHE = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        _CACHE = {}
    return _CACHE


def _save(data: dict[str, str]) -> None:
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        # Read-only filesystem: state is kept in memory for this instance only.
        pass


def get_user_locale(user_id: int) -> str | None:
    return _load().get(str(user_id))


def set_user_locale(user_id: int, locale: str) -> str:
    data = _load()
    normalized = normalize_locale(locale)
    data[str(user_id)] = normalized
    _save(data)
    return normalized