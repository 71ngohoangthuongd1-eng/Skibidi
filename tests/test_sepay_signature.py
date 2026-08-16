"""SePay IPN webhook authentication (HMAC-SHA256 + legacy API-Key header)."""

import hashlib
import hmac
import time

from unittest.mock import patch

from starlette.requests import Request

from bot.misc import EnvKeys
from bot.web.admin import _verify_sepay_ipn_signature

SECRET = "whsec_test_abc123"


def _signed(body: bytes, secret: str = SECRET, at: int | None = None) -> tuple[list, bytes]:
    ts = str(int(time.time() if at is None else at))
    sig = "sha256=" + hmac.new(secret.encode(), (ts + ".").encode() + body, hashlib.sha256).hexdigest()
    headers = [
        (b"x-sepay-signature", sig.encode()),
        (b"x-sepay-timestamp", ts.encode()),
    ]
    return headers, body


def _request(headers: list) -> Request:
    scope = {"type": "http", "method": "POST", "headers": headers, "path": "/sepay/ipn"}
    return Request(scope)


class TestHmacSha256:
    BODY = b'{"id":42,"transferType":"in","transferAmount":150000,"content":"SPTEST001","gateway":"TPBANK"}'

    def test_valid_signature_accepted(self):
        headers, body = _signed(self.BODY)
        with patch.object(EnvKeys, "SEPAY_WEBHOOK_SECRET", SECRET):
            assert _verify_sepay_ipn_signature(_request(headers), body) is True

    def test_tampered_body_rejected(self):
        headers, _ = _signed(self.BODY)
        with patch.object(EnvKeys, "SEPAY_WEBHOOK_SECRET", SECRET):
            assert _verify_sepay_ipn_signature(_request(headers), self.BODY + b"x") is False

    def test_wrong_secret_rejected(self):
        headers, body = _signed(self.BODY, secret="other-secret")
        with patch.object(EnvKeys, "SEPAY_WEBHOOK_SECRET", SECRET):
            assert _verify_sepay_ipn_signature(_request(headers), body) is False

    def test_stale_timestamp_rejected(self):
        headers, body = _signed(self.BODY, at=int(time.time()) - 400)
        with patch.object(EnvKeys, "SEPAY_WEBHOOK_SECRET", SECRET):
            assert _verify_sepay_ipn_signature(_request(headers), body) is False

    def test_malformed_signature_prefix_rejected(self):
        body = self.BODY
        ts = str(int(time.time()))
        bad_sig = b"hmac=" + hmac.new(SECRET.encode(), (ts + ".").encode() + body, hashlib.sha256).hexdigest().encode()
        headers = [(b"x-sepay-signature", bad_sig), (b"x-sepay-timestamp", ts.encode())]
        with patch.object(EnvKeys, "SEPAY_WEBHOOK_SECRET", SECRET):
            assert _verify_sepay_ipn_signature(_request(headers), body) is False

    def test_missing_signature_rejected(self):
        body = self.BODY
        with patch.object(EnvKeys, "SEPAY_WEBHOOK_SECRET", SECRET):
            assert _verify_sepay_ipn_signature(_request([]), body) is False


class TestLegacyApiKeyHeader:
    BODY = b'{"id":1}'

    def test_matching_header_accepted(self):
        with patch.object(EnvKeys, "SEPAY_WEBHOOK_SECRET", SECRET):
            assert _verify_sepay_ipn_signature(
                _request([(b"x-secret-key", SECRET.encode())]), self.BODY
            ) is True

    def test_mismatch_rejected(self):
        with patch.object(EnvKeys, "SEPAY_WEBHOOK_SECRET", SECRET):
            assert _verify_sepay_ipn_signature(
                _request([(b"x-secret-key", b"bad")]), self.BODY
            ) is False


class TestNoSecretConfigured:
    BODY = b'{"id":1}'

    def test_trusts_request_without_secret(self):
        with patch.object(EnvKeys, "SEPAY_WEBHOOK_SECRET", ""):
            assert _verify_sepay_ipn_signature(_request([]), self.BODY) is True