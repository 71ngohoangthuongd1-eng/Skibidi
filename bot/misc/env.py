import logging
import os
from abc import ABC
from typing import Final
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


def is_serverless() -> bool:
    """True when running inside Vercel serverless runtime (or forced webhook mode)."""
    return os.getenv("VERCEL") == "1" or os.getenv("BOT_MODE") == "webhook"


class EnvKeys(ABC):
    """Secure environment configuration with validation"""

    @staticmethod
    def _get_required(key: str) -> str:
        val = os.getenv(key)
        if not val:
            raise ValueError(f"Missing required environment variable: {key}")
        return val

    @staticmethod
    def _get_optional(key: str, default: str = "") -> str:
        return os.getenv(key, default)

    # Telegram
    TOKEN: Final = _get_required('TOKEN')
    OWNER_ID: Final = int(_get_required('OWNER_ID'))

    # Runtime mode
    VERCEL: Final = _get_optional("VERCEL", "0")
    BOT_MODE: Final = _get_optional("BOT_MODE", "")
    CRON_SECRET: Final = _get_optional("CRON_SECRET", "")

    # Database
    DATABASE_URL_OVERRIDE: Final = _get_optional("DATABASE_URL")
    POSTGRES_DB: Final = _get_required("POSTGRES_DB") if not DATABASE_URL_OVERRIDE else _get_optional("POSTGRES_DB")
    POSTGRES_USER: Final = _get_required("POSTGRES_USER") if not DATABASE_URL_OVERRIDE else _get_optional("POSTGRES_USER")
    POSTGRES_PASSWORD: Final = _get_required("POSTGRES_PASSWORD") if not DATABASE_URL_OVERRIDE else _get_optional("POSTGRES_PASSWORD")
    DB_PORT: Final = int(_get_optional("DB_PORT", "5432"))
    DB_DRIVER: Final = _get_optional("DB_DRIVER", "postgresql+asyncpg")
    POSTGRES_HOST: Final = _get_optional("POSTGRES_HOST", "localhost")
    # Connection pool tuning (serverless instances share the same Postgres, so cap small pools)
    DB_POOL_SIZE: Final = int(_get_optional("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: Final = int(_get_optional("DB_MAX_OVERFLOW", "10"))
    DB_POOL_RECYCLE: Final = int(_get_optional("DB_POOL_RECYCLE", "1800"))

    # Redis
    REDIS_ENABLED: Final = _get_optional("REDIS_ENABLED", "1")
    REDIS_URL: Final = _get_optional("REDIS_URL", "")
    REDIS_HOST: Final = _get_optional("REDIS_HOST", "localhost")
    REDIS_PORT: Final = int(_get_optional("REDIS_PORT", "6379"))
    REDIS_DB: Final = int(_get_optional("REDIS_DB", "0"))
    REDIS_PASSWORD: Final = _get_optional("REDIS_PASSWORD", "")

    # Payments
    TELEGRAM_PROVIDER_TOKEN: Final = _get_optional("TELEGRAM_PROVIDER_TOKEN", "")
    CRYPTO_PAY_TOKEN: Final = _get_optional("CRYPTO_PAY_TOKEN", "")
    STARS_PER_VALUE: Final = float(_get_optional("STARS_PER_VALUE", "0.91"))
    REFERRAL_PERCENT: Final = int(_get_optional("REFERRAL_PERCENT", "0"))
    PAY_CURRENCY: Final = _get_optional("PAY_CURRENCY", "RUB")
    PAYMENT_TIME: Final = int(_get_optional("PAYMENT_TIME", "1800"))
    MIN_AMOUNT: Final = int(_get_optional("MIN_AMOUNT", "20"))
    MAX_AMOUNT: Final = int(_get_optional("MAX_AMOUNT", "10000"))
    SEPAY_RATE: Final = _get_optional("SEPAY_RATE", "26000")
    SEPAY_BANK_NAME: Final = _get_optional("SEPAY_BANK_NAME", "")
    SEPAY_ACCOUNT_NO: Final = _get_optional("SEPAY_ACCOUNT_NO", "")
    SEPAY_ACCOUNT_NAME: Final = _get_optional("SEPAY_ACCOUNT_NAME", "")
    SEPAY_WEBHOOK_SECRET: Final = _get_optional("SEPAY_WEBHOOK_SECRET", "")
    SEPAY_IPN_PATH: Final = _get_optional("SEPAY_IPN_PATH", "/sepay/ipn")
    SEPAY_PAYMENT_PREFIX: Final = _get_optional("SEPAY_PAYMENT_PREFIX", "SP")

    # Links / UI
    CHANNEL_URL: Final = _get_optional("CHANNEL_URL", "")
    CHANNEL_ID: Final = _get_optional("CHANNEL_ID", "")
    HELPER_ID: Final = _get_optional("HELPER_ID", "")
    RULES: Final = _get_optional("RULES", "")

    # Locale & logs
    BOT_LOCALE: Final = _get_optional("BOT_LOCALE", "en")
    BOT_LOGFILE: Final = _get_optional("BOT_LOGFILE", "logs/bot.log")
    BOT_AUDITFILE: Final = _get_optional("BOT_AUDITFILE", "logs/audit.log")
    LOG_TO_STDOUT: Final = _get_optional("LOG_TO_STDOUT", "1")
    LOG_TO_FILE: Final = _get_optional("LOG_TO_FILE", "1")
    DEBUG: Final = _get_optional("DEBUG", "0")
    REVIEWS_ENABLED: Final = _get_optional("REVIEWS_ENABLED", "1")

    # Auto product ad (promo rotation)
    AUTO_PRODUCT_AD_ENABLED: Final = _get_optional("AUTO_PRODUCT_AD_ENABLED", "0")
    AUTO_PRODUCT_AD_INTERVAL: Final = int(_get_optional("AUTO_PRODUCT_AD_INTERVAL", "3600"))

    # Web admin panel
    ADMIN_HOST: Final = _get_optional("ADMIN_HOST", _get_optional("MONITORING_HOST", "localhost"))
    ADMIN_PORT: Final = int(_get_optional("ADMIN_PORT", _get_optional("MONITORING_PORT", "9090")))
    ADMIN_USERNAME: Final = _get_optional("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: Final = _get_optional("ADMIN_PASSWORD", "admin")
    SECRET_KEY: Final = _get_optional("SECRET_KEY", "change-me-in-production")

    # Webhook
    WEBHOOK_ENABLED: Final = _get_optional("WEBHOOK_ENABLED", "0")
    WEBHOOK_URL: Final = _get_optional("WEBHOOK_URL", "")
    WEBHOOK_PATH: Final = _get_optional("WEBHOOK_PATH", "/webhook")
    WEBHOOK_SECRET: Final = _get_optional("WEBHOOK_SECRET", "")

    # Cleanup
    AUDIT_RETENTION_DAYS: Final = int(_get_optional("AUDIT_RETENTION_DAYS", "90"))
    PAYMENTS_RETENTION_DAYS: Final = int(_get_optional("PAYMENTS_RETENTION_DAYS", "90"))

    DATABASE_URL: Final = DATABASE_URL_OVERRIDE or (
        f"postgresql+asyncpg://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{DB_PORT}/{POSTGRES_DB}"
    )


def validate_production() -> None:
    """Fail fast with a clear message when a serverless-safe configuration is missing.

    Called only when running on Vercel (VERCEL=1) or when BOT_MODE=webhook is forced.
    Never breaks local development (polling + SQLite + in-memory are still allowed).
    """
    if not is_serverless():
        return

    errors = []

    # 1. PostgreSQL is mandatory on serverless (no local file database).
    url = EnvKeys.DATABASE_URL
    backend = (url or "").split(":", 1)[0]
    if backend.startswith("sqlite"):
        errors.append(
            "SQLite is not allowed in production. Set DATABASE_URL to a PostgreSQL "
            "async URL (e.g. postgresql+asyncpg://...) or configure POSTGRES_* vars."
        )

    # 2. Redis is mandatory for FSM state and distributed caching.
    if EnvKeys.REDIS_ENABLED != "1":
        errors.append(
            "REDIS_ENABLED must be '1' on serverless. In-memory (MemoryStorage) cannot "
            "persist FSM/dialog state across Vercel instances."
        )

    # 3. Webhook secret protects the Telegram webhook endpoint.
    if not EnvKeys.WEBHOOK_SECRET:
        errors.append("WEBHOOK_SECRET is recommended on serverless to verify webhook requests.")

    # 4. Bot must run via webhook (not polling) on Vercel.
    if EnvKeys.VERCEL == "1" and EnvKeys.WEBHOOK_ENABLED != "1":
        errors.append("WEBHOOK_ENABLED must be '1' on Vercel (the bot cannot poll).")

    # 5. Non-default admin credentials.
    if EnvKeys.ADMIN_USERNAME in ("", "admin") or EnvKeys.ADMIN_PASSWORD in ("", "admin") or EnvKeys.SECRET_KEY in ("", "change-me-in-production", "change-me"):
        errors.append("Set strong ADMIN_USERNAME / ADMIN_PASSWORD / SECRET_KEY in production.")

    if errors:
        raise RuntimeError(
            "Invalid production (Vercel) configuration:\n  - " + "\n  - ".join(errors)
        )

    # 6. Login rate limiting is security-critical: on serverless it requires Redis.
    if EnvKeys.REDIS_ENABLED != "1":
        logger.warning(
            "REDIS_ENABLED=0 on serverless: the admin login rate limiter falls back "
            "to per-instance memory and can be bypassed across Vercel instances. "
            "Set REDIS_URL + REDIS_ENABLED=1 for distributed login lockout."
        )
