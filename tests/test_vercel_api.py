"""Tests for the Vercel serverless entrypoint (api/index.py)."""

from unittest.mock import patch, AsyncMock

import pytest

from bot.misc import EnvKeys


@pytest.fixture(autouse=True)
def patch_cron_secret():
    with patch.object(EnvKeys, "CRON_SECRET", "test-cron-secret"):
        yield


class FakeLockRedis:
    def __init__(self):
        self.locked = set()

    async def set(self, key, value, nx=False, ex=None):
        if nx and key in self.locked:
            return False
        self.locked.add(key)
        return True


@pytest.fixture
def fake_redis():
    return FakeLockRedis()


class TestCronSecretVerification:
    async def test_unauthorized_without_bearer(self):
        from api.index import _verify_cron_secret
        from starlette.requests import Request
        scope = {"type": "http", "method": "GET", "headers": [], "path": "/api/cron/recovery"}
        request = Request(scope)
        assert _verify_cron_secret(request) is False

    async def test_authorized_with_bearer(self):
        from api.index import _verify_cron_secret
        from starlette.requests import Request
        scope = {"type": "http", "method": "GET", "headers": [
            (b"authorization", b"Bearer test-cron-secret"),
        ], "path": "/api/cron/recovery"}
        request = Request(scope)
        assert _verify_cron_secret(request) is True

    async def test_unauthorized_wrong_bearer(self):
        from api.index import _verify_cron_secret
        from starlette.requests import Request
        scope = {"type": "http", "method": "GET", "headers": [
            (b"authorization", b"Bearer wrong-secret"),
        ], "path": "/api/cron/recovery"}
        request = Request(scope)
        assert _verify_cron_secret(request) is False

    async def test_no_secret_trusts_vercel_cron_header(self):
        from starlette.requests import Request
        with patch.object(EnvKeys, "CRON_SECRET", ""):
            from api.index import _verify_cron_secret
            scope = {"type": "http", "method": "GET", "headers": [
                (b"x-vercel-cron", b"1"),
            ], "path": "/api/cron/recovery"}
            request = Request(scope)
            assert _verify_cron_secret(request) is True


class TestCronLock:
    async def test_acquire_and_second_call_denied(self, fake_redis):
        with patch("api.index.get_shared_redis", return_value=fake_redis):
            from api.index import _cron_lock
            assert await _cron_lock("recovery") is True
            assert await _cron_lock("recovery") is False

    async def test_no_redis_allows_proceed(self):
        with patch("api.index.get_shared_redis", return_value=None):
            from api.index import _cron_lock
            assert await _cron_lock("cleanup") is True

    async def test_redis_error_does_not_block(self):
        class BrokenRedis(FakeLockRedis):
            async def set(self, *a, **k):
                raise RuntimeError("down")

        with patch("api.index.get_shared_redis", return_value=BrokenRedis()):
            from api.index import _cron_lock
            assert await _cron_lock("recovery") is True


class TestWebhookSecret:
    async def test_webhook_rejects_wrong_secret(self):
        from api.index import webhook_handler
        from starlette.requests import Request
        from starlette.responses import Response
        scope = {"type": "http", "method": "POST", "headers": [
            (b"x-telegram-bot-api-secret-token", b"wrong"),
        ], "path": "/webhook", "query_string": b"", "server": ("t", 80), "client": ("c", 123), "scheme": "http", "root_path": ""}

        with patch.object(EnvKeys, "WEBHOOK_SECRET", "correct-secret"):
            async def receive():
                return {"type": "http.request", "body": b"{}", "more_body": False}

            request = Request(scope, receive=receive)
            response = await webhook_handler(request)
            assert response.status_code == 403

    async def test_webhook_accepts_correct_secret(self):
        from api.index import webhook_handler
        from starlette.requests import Request
        body = b'{"update_id": 1}'
        scope = {"type": "http", "method": "POST", "headers": [
            (b"x-telegram-bot-api-secret-token", b"correct-secret"),
            (b"content-type", b"application/json"),
        ], "path": "/webhook", "query_string": b"", "server": ("t", 80), "client": ("c", 123), "scheme": "http", "root_path": ""}

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        request = Request(scope, receive=receive)
        fake_dp = AsyncMock()
        with patch.object(EnvKeys, "WEBHOOK_SECRET", "correct-secret"), \
                patch("api.index._ensure_runtime", new=AsyncMock(return_value={"bot": object(), "dp": fake_dp})):
            response = await webhook_handler(request)
            assert response.status_code == 200
            fake_dp.feed_update.assert_awaited_once()


class TestCronEndpoints:
    async def test_cron_recovery_requires_auth(self):
        from api.index import cron_recovery
        from starlette.requests import Request
        scope = {"type": "http", "method": "GET", "headers": [], "path": "/api/cron/recovery",
                 "query_string": b"", "server": ("t", 80), "client": ("c", 123), "scheme": "http", "root_path": ""}
        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}
        request = Request(scope, receive=receive)
        response = await cron_recovery(request)
        assert response.status_code == 401

    async def test_cron_recovery_conflict_when_locked(self, fake_redis):
        from api.index import cron_recovery
        from starlette.requests import Request
        scope = {"type": "http", "method": "GET", "headers": [
            (b"authorization", b"Bearer test-cron-secret"),
        ], "path": "/api/cron/recovery", "query_string": b"", "server": ("t", 80), "client": ("c", 123),
            "scheme": "http", "root_path": ""}
        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}
        request = Request(scope, receive=receive)
        with patch("api.index.get_shared_redis", return_value=fake_redis), \
                patch("api.index._cron_lock", new=AsyncMock(return_value=False)):
            response = await cron_recovery(request)
            assert response.status_code == 409

    async def test_cron_cleanup_requires_auth(self):
        from api.index import cron_cleanup
        from starlette.requests import Request
        scope = {"type": "http", "method": "GET", "headers": [], "path": "/api/cron/cleanup",
                 "query_string": b"", "server": ("t", 80), "client": ("c", 123), "scheme": "http", "root_path": ""}
        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}
        request = Request(scope, receive=receive)
        response = await cron_cleanup(request)
        assert response.status_code == 401


class TestAppRoutes:
    def test_app_exposes_expected_routes(self):
        import api.index
        paths = sorted(r.path for r in api.index.app.routes)
        assert "/webhook" in paths
        assert "/api/set-webhook" in paths
        assert "/api/cron/recovery" in paths
        assert "/api/cron/cleanup" in paths
        # Mount("/", ...) normalizes to an empty path
        assert "" in paths