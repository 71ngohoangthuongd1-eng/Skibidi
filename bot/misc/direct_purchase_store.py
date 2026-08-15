"""Direct-purchase intent store, distributed-friendly.

The intent links a SePay ``sepay_item`` payment to the item it should deliver.
It MUST survive across Vercel instances: a "create payment" request lands on one
instance, while the SePay IPN callback can land on another (or a different warm slot).
So we store it in Redis (JSON, TTL), never in a local JSON file. When Redis is not
configured (local development with ``REDIS_ENABLED=0``) we fall back to an in-memory
registry so the feature still works on a single-process install.
"""

import json
from typing import Optional

from bot.misc.caching.storage import get_shared_redis

_KEY_PREFIX = "dpi:"
_TTL_SECONDS = 7 * 24 * 3600  # 7 days, long enough to cover SePay IPN retries

# Local-development fallback (single process only).
_MEMORY: dict[str, dict] = {}


def _key(payment_id: int) -> str:
    return f"{_KEY_PREFIX}{payment_id}"


async def get_direct_purchase_intent(payment_id: int) -> Optional[dict]:
    redis = get_shared_redis()
    if redis is not None:
        try:
            raw = await redis.get(_key(payment_id))
            if raw is not None:
                try:
                    parsed = json.loads(raw if isinstance(raw, str) else raw.decode("utf-8"))
                except Exception:
                    parsed = None
                if parsed is not None:
                    return parsed
        except Exception:
            pass  # Redis hiccup: fall through to the memory registry
    return _MEMORY.get(str(payment_id))


async def set_direct_purchase_intent(payment_id: int, *, item_name: str, promo_code: str | None = None) -> None:
    data = {"item_name": item_name, "promo_code": promo_code}
    redis = get_shared_redis()
    if redis is not None:
        try:
            await redis.setex(_key(payment_id), _TTL_SECONDS, json.dumps(data, ensure_ascii=False))
            return
        except Exception:
            pass  # fall back to memory so a Redis hiccup doesn't break the flow
    _MEMORY[str(payment_id)] = data


async def delete_direct_purchase_intent(payment_id: int) -> None:
    redis = get_shared_redis()
    if redis is not None:
        try:
            await redis.delete(_key(payment_id))
        except Exception:
            pass
    _MEMORY.pop(str(payment_id), None)