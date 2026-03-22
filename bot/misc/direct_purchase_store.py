import json
from pathlib import Path


_DATA_DIR = Path("data")
_STORE_PATH = _DATA_DIR / "direct_purchase_intents.json"
_CACHE: dict[str, dict] | None = None


def _load() -> dict[str, dict]:
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


def _save(data: dict[str, dict]) -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    _STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_direct_purchase_intent(payment_id: int) -> dict | None:
    return _load().get(str(payment_id))


def set_direct_purchase_intent(payment_id: int, *, item_name: str, promo_code: str | None = None) -> None:
    data = _load()
    data[str(payment_id)] = {
        "item_name": item_name,
        "promo_code": promo_code,
    }
    _save(data)


def delete_direct_purchase_intent(payment_id: int) -> None:
    data = _load()
    if str(payment_id) in data:
        data.pop(str(payment_id), None)
        _save(data)
