"""VietQR bank-payment QR generation for the SePay direct-purchase flow.

The QR image URL embeds the bank, account number, exact amount and each
payment's transfer memo (SP... code) so it can be prefilled when scanned.
"""

import asyncio
import urllib.parse
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.misc.services.sepay_qr import build_vietqr_url, fetch_qr_image
from bot.misc.services.telegram_ux import send_chat_action


def _params(url: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    return {k: v for k, v in urllib.parse.parse_qsl(parsed.query)}


class TestBuildVietQRUrl:
    def test_base_url(self):
        url = build_vietqr_url(bank="MSB", account_no="7614122003", amount_vnd=2000, content="SP329B613F2F")
        assert url.startswith("https://vietqr.app/img?")

    def test_correct_bank(self):
        url = build_vietqr_url(bank="MSB", account_no="7614122003", amount_vnd=2000, content="SPX")
        assert _params(url)["bank"] == "MSB"

    def test_correct_account(self):
        url = build_vietqr_url(bank="MSB", account_no="7614122003", amount_vnd=2000, content="SPX")
        assert _params(url)["acc"] == "7614122003"

    def test_correct_amount(self):
        url = build_vietqr_url(bank="MSB", account_no="7614122003", amount_vnd=2000, content="SPX")
        assert _params(url)["amount"] == "2000"

    def test_correct_content(self):
        url = build_vietqr_url(bank="MSB", account_no="7614122003", amount_vnd=2000, content="SP329B613F2F")
        assert _params(url)["des"] == "SP329B613F2F"

    def test_holder_optional_when_missing(self):
        url = build_vietqr_url(bank="MSB", account_no="1", amount_vnd=1, content="SP1")
        assert "holder" not in _params(url)

    def test_holder_included_when_provided(self):
        url = build_vietqr_url(bank="MSB", account_no="1", amount_vnd=1, content="SP1",
                               holder="BUI KIM ANH TUAN")
        assert _params(url)["holder"] == "BUI KIM ANH TUAN"

    def test_each_payment_has_its_own_code(self):
        # Two payments must never share a transfer memo / QR content.
        url_a = build_vietqr_url(bank="MSB", account_no="7614122003", amount_vnd=2000, content=build("AAA111"))
        url_b = build_vietqr_url(bank="MSB", account_no="7614122003", amount_vnd=2000, content=build("BBB222"))
        assert _params(url_a)["des"] != _params(url_b)["des"]
        assert url_a != url_b

    def test_amount_is_integer_vnd(self):
        url = build_vietqr_url(bank="MSB", account_no="1", amount_vnd=25000, content="SPX")
        assert _params(url)["amount"] == "25000"


def build(code: str) -> str:
    """Mimic build_sepay_transfer_content for a payment external_id."""
    return f"SP{code}"


class TestFetchQRImage:
    def _client(self, status: int, read_result=None):
        resp = MagicMock()
        resp.status = status
        resp.__aenter__ = AsyncMock(return_value=resp)
        resp.__aexit__ = AsyncMock(return_value=False)
        resp.read = AsyncMock(return_value=read_result)

        session = MagicMock()
        session.closed = False
        session.get = MagicMock(return_value=resp)
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        session.close = AsyncMock()
        client = MagicMock(return_value=session)
        return client

    def test_success_returns_bytes(self):
        client = self._client(200, read_result=b"\x89PNG fake bytes")
        with patch("bot.misc.services.sepay_qr.aiohttp.ClientSession", client):
            data = asyncio.run(fetch_qr_image("https://example.invalid/qr"))
        assert data == b"\x89PNG fake bytes"

    def test_non_200_returns_none(self):
        client = self._client(500, read_result=b"\x89PNG fake bytes")
        with patch("bot.misc.services.sepay_qr.aiohttp.ClientSession", client):
            data = asyncio.run(fetch_qr_image("https://example.invalid/qr"))
        assert data is None

    def test_network_error_returns_none(self):
        session = MagicMock()
        session.closed = False
        session.get = MagicMock(side_effect=RuntimeError("boom"))
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        session.close = AsyncMock()

        client = MagicMock(return_value=session)
        with patch("bot.misc.services.sepay_qr.aiohttp.ClientSession", client):
            data = asyncio.run(fetch_qr_image("https://example.invalid/qr"))
        assert data is None


class TestSendChatAction:
    def test_success_no_error(self):
        bot = MagicMock()
        bot.send_chat_action = AsyncMock()
        asyncio.run(send_chat_action(bot, 12345))
        bot.send_chat_action.assert_awaited_once()

    def test_failure_swallowed(self):
        bot = MagicMock()
        bot.send_chat_action = AsyncMock(side_effect=RuntimeError("boom"))
        # Must not raise.
        asyncio.run(send_chat_action(bot, 12345))
