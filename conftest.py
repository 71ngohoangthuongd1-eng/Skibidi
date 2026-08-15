"""Root conftest: set safe default env vars before any bot module import.

The bot reads env vars at import time (see ``bot.misc.env``), so these must
exist before ``bot`` / ``api`` modules are imported by the test suite.
"""
import os


def _default(key: str, value: str) -> None:
    if not os.getenv(key):
        os.environ[key] = value


_default("TOKEN", "123456789:test_token")
_default("OWNER_ID", "123456789")
_default("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
_default("POSTGRES_DB", "test")
_default("POSTGRES_USER", "test")
_default("POSTGRES_PASSWORD", "test")
_default("REDIS_ENABLED", "0")
_default("REDIS_URL", "")
_default("PAY_CURRENCY", "RUB")
_default("REFERRAL_PERCENT", "10")
_default("ADMIN_USERNAME", "testadmin")
_default("ADMIN_PASSWORD", "testadminpw")
_default("SECRET_KEY", "test-secret-not-default")
_default("WEBHOOK_ENABLED", "0")
_default("WEBHOOK_SECRET", "test-webhook-secret")
_default("CRON_SECRET", "test-cron-secret")
_default("SEPAY_PAYMENT_PREFIX", "SP")
_default("LOG_TO_FILE", "0")
_default("LOG_TO_STDOUT", "0")