"""VietQR bank-payment QR generation for the SePay direct-purchase flow.

Uses the SePay/VietQR public image generator (``vietqr.app/img``). The returned
image embeds a NAPAS/VietQR payload so Vietnamese banking apps pre-fill the
beneficiary account, amount and transfer memo when scanned.

Nothing is hard-coded here: bank, account number, amount and memo are all passed
by the caller from environment-driven data so each payment gets its own exact QR.
"""

import urllib.parse
from typing import Optional

import aiohttp

# SePay-documented VietQR image generator endpoint.
VIETQR_IMG_BASE = "https://vietqr.app/img"


def build_vietqr_url(
    *,
    bank: str,
    account_no: str,
    amount_vnd: int,
    content: str,
    holder: Optional[str] = None,
    store: Optional[str] = None,
    template: str = "compact",
) -> str:
    """Build a VietQR image URL for a real bank-transfer QR.

    Args:
        bank: Bank short name/alias/code/bin from vietqr.app/banks.json
              (e.g. "MSB", "Vietcombank"). Never hard-coded here.
        account_no: Beneficiary account number.
        amount_vnd: Exact transfer amount in VND (integer).
        content: Transfer memo; must be the exact payment/order code (e.g. "SP329B613F2F")
                 so SePay matches the transfer to the right payment.
        holder: Optional account-holder name shown on the QR image (no diacritics).
        store: Optional store/business name shown on the QR image.
        template: VietQR image layout ("compact", "qronly", "standee" or "").
    """
    params: dict[str, object] = {
        "acc": str(account_no),
        "bank": str(bank),
        "amount": str(int(amount_vnd)),
        "des": content,
    }
    if holder:
        params["holder"] = holder
    if store:
        params["store"] = store
    if template:
        params["template"] = template
    query = urllib.parse.urlencode(params)
    return f"{VIETQR_IMG_BASE}?{query}"


async def fetch_qr_image(url: str, timeout: float = 8.0) -> Optional[bytes]:
    """Download QR image bytes, returning None on any failure.

    A short timeout keeps the serverless handler from hanging; every network,
    HTTP or decode error is swallowed so callers can safely fall back to a
    plain-text payment message without losing the payment.
    """
    session = None
    try:
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout))
        async with session.get(url, headers={"User-Agent": "skibidi-shop-bot/1.0"}) as resp:
            if resp.status != 200:
                return None
            data = await resp.read()
            return data if data else None
    except Exception:
        return None
    finally:
        if session is not None and not session.closed:
            await session.close()
