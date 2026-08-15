"""Unit tests for serverless detection and production validation."""

from bot.misc.env import is_serverless, validate_production


class TestIsServerless:
    def test_not_serverless_by_default(self, monkeypatch):
        monkeypatch.delenv("VERCEL", raising=False)
        monkeypatch.delenv("BOT_MODE", raising=False)
        assert is_serverless() is False

    def test_vercel_flag(self, monkeypatch):
        monkeypatch.setenv("VERCEL", "1")
        monkeypatch.delenv("BOT_MODE", raising=False)
        assert is_serverless() is True

    def test_bot_mode_webhook(self, monkeypatch):
        monkeypatch.delenv("VERCEL", raising=False)
        monkeypatch.setenv("BOT_MODE", "webhook")
        assert is_serverless() is True

    def test_bot_mode_polling_not_serverless(self, monkeypatch):
        monkeypatch.delenv("VERCEL", raising=False)
        monkeypatch.setenv("BOT_MODE", "polling")
        assert is_serverless() is False


class TestValidateProduction:
    def test_skipped_when_not_serverless(self, monkeypatch):
        monkeypatch.delenv("VERCEL", raising=False)
        monkeypatch.delenv("BOT_MODE", raising=False)
        validate_production()  # must not raise

    def test_fails_with_sqlite(self, monkeypatch):
        monkeypatch.setenv("VERCEL", "1")
        from unittest.mock import patch
        with patch("bot.misc.env.is_serverless", return_value=True), \
                patch.object(__import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys, "DATABASE_URL",
                             "sqlite+aiosqlite:///./data/x.db"), \
                patch.object(__import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys, "REDIS_ENABLED", "1"), \
                patch.object(__import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys, "WEBHOOK_SECRET", "sec"), \
                patch.object(__import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys, "WEBHOOK_ENABLED", "1"), \
                patch.object(__import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys, "ADMIN_USERNAME", "boss"), \
                patch.object(__import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys, "ADMIN_PASSWORD", "boss9"), \
                patch.object(__import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys, "SECRET_KEY", "secret9x"):
            import pytest
            with pytest.raises(RuntimeError):
                validate_production()

    def test_fails_when_redis_disabled(self, monkeypatch):
        monkeypatch.setenv("VERCEL", "1")
        from unittest.mock import patch
        EnvKeys = __import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys
        with patch("bot.misc.env.is_serverless", return_value=True), \
                patch.object(EnvKeys, "DATABASE_URL", "postgresql+asyncpg://u:p@h/db"), \
                patch.object(EnvKeys, "REDIS_ENABLED", "0"), \
                patch.object(EnvKeys, "WEBHOOK_SECRET", "sec"), \
                patch.object(EnvKeys, "WEBHOOK_ENABLED", "1"), \
                patch.object(EnvKeys, "ADMIN_USERNAME", "boss"), \
                patch.object(EnvKeys, "ADMIN_PASSWORD", "boss9"), \
                patch.object(EnvKeys, "SECRET_KEY", "secret9x"):
            import pytest
            with pytest.raises(RuntimeError, match="REDIS_ENABLED"):
                validate_production()

    def test_fails_with_weak_admin_creds(self, monkeypatch):
        monkeypatch.setenv("VERCEL", "1")
        from unittest.mock import patch
        EnvKeys = __import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys
        with patch("bot.misc.env.is_serverless", return_value=True), \
                patch.object(EnvKeys, "DATABASE_URL", "postgresql+asyncpg://u:p@h/db"), \
                patch.object(EnvKeys, "REDIS_ENABLED", "1"), \
                patch.object(EnvKeys, "WEBHOOK_SECRET", "sec"), \
                patch.object(EnvKeys, "WEBHOOK_ENABLED", "1"), \
                patch.object(EnvKeys, "ADMIN_USERNAME", "admin"), \
                patch.object(EnvKeys, "ADMIN_PASSWORD", "admin"), \
                patch.object(EnvKeys, "SECRET_KEY", "change-me-in-production"):
            import pytest
            with pytest.raises(RuntimeError, match="ADMIN_USERNAME"):
                validate_production()

    def test_passes_with_valid_production_config(self, monkeypatch):
        monkeypatch.setenv("VERCEL", "1")
        from unittest.mock import patch
        EnvKeys = __import__("bot.misc.env", fromlist=["EnvKeys"]).EnvKeys
        with patch("bot.misc.env.is_serverless", return_value=True), \
                patch.object(EnvKeys, "DATABASE_URL", "postgresql+asyncpg://u:p@h/db"), \
                patch.object(EnvKeys, "REDIS_ENABLED", "1"), \
                patch.object(EnvKeys, "WEBHOOK_SECRET", "sec"), \
                patch.object(EnvKeys, "WEBHOOK_ENABLED", "1"), \
                patch.object(EnvKeys, "ADMIN_USERNAME", "boss"), \
                patch.object(EnvKeys, "ADMIN_PASSWORD", "boss9"), \
                patch.object(EnvKeys, "SECRET_KEY", "secret9x"):
            validate_production()