"""Test harness: in-memory async SQLite + fake cache + factories.

Adapted from the historic suite (commit b577524) to the current async
SQLAlchemy layer and the serverless-safe modules under audit.
"""

import asyncio
import datetime
import fnmatch
from typing import Dict, Any

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool


class FakeCacheManager:
    """Dict-based cache that mirrors CacheManager's interface."""

    def __init__(self):
        self.store: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0

    async def get(self, key: str, deserialize: bool = True):
        if key in self.store:
            self.hits += 1
            return self.store[key]
        self.misses += 1
        return None

    async def set(self, key: str, value, ttl: int = None, serialize: bool = True):
        self.store[key] = value
        return True

    async def delete(self, key: str):
        self.store.pop(key, None)
        return True

    async def invalidate_pattern(self, pattern: str):
        to_delete = [k for k in self.store if fnmatch.fnmatch(k, pattern)]
        for k in to_delete:
            del self.store[k]
        return len(to_delete)

    def clear(self):
        self.store.clear()
        self.hits = 0
        self.misses = 0


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Replace the Database singleton with an async SQLite in-memory engine."""
    import bot.database.main as db_main
    from bot.database.main import Database

    Database._instance = None
    original_init = Database.__init__

    def test_init(self):
        self.__dict__['_Database__engine'] = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.__dict__['_Database__SessionLocal'] = async_sessionmaker(
            bind=self.__dict__['_Database__engine'],
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    Database.__init__ = test_init
    db = Database()

    async def _setup():
        async with db.engine.begin() as conn:
            from bot.database.models.main import (
                User, Role, Categories, Goods, ItemValues, BoughtGoods,
                Operations, Payments, ReferralEarnings, AuditLog,
                PromoCodes, PromoCodeUsages, CartItems, Reviews,
            )
            await conn.run_sync(Database.BASE.metadata.create_all)
        await Role.insert_roles()

    asyncio.run(_setup())

    yield

    Database.__init__ = original_init
    Database._instance = None
    # reset module-level cache pointers so later test sessions start clean
    db_main.Database = Database


@pytest.fixture(autouse=True)
async def db_cleanup(setup_test_database):
    """Clean all data between tests (roles keep the session-scoped built-ins)."""
    yield

    from bot.database.main import Database
    from bot.database.models.main import (
        ReferralEarnings, BoughtGoods, Operations, Payments,
        ItemValues, Goods, Categories, User, Role,
        PromoCodeUsages, PromoCodes, CartItems, Reviews, AuditLog,
    )

    db = Database()
    async with db.session() as s:
        await s.execute(delete(ReferralEarnings))
        await s.execute(delete(BoughtGoods))
        await s.execute(delete(Operations))
        await s.execute(delete(Payments))
        await s.execute(delete(ItemValues))
        await s.execute(delete(Goods))
        await s.execute(delete(Categories))
        await s.execute(delete(PromoCodeUsages))
        await s.execute(delete(PromoCodes))
        await s.execute(delete(CartItems))
        await s.execute(delete(Reviews))
        await s.execute(delete(AuditLog))
        await s.execute(delete(User))
        await s.execute(delete(Role).where(Role.name.notin_(['USER', 'ADMIN', 'OWNER'])))


@pytest.fixture(autouse=True)
def fake_cache():
    """Provide a FakeCacheManager and patch get_cache_manager everywhere."""
    cache = FakeCacheManager()

    with _patch_cache(cache):
        yield cache


def _patch_cache(cache):
    from unittest.mock import patch
    return patch('bot.misc.caching.cache._cache_manager', cache)


@pytest.fixture(autouse=True)
def patch_safe_create_task():
    """Make safe_create_task execute coroutines immediately."""
    from unittest.mock import patch

    def run_immediately(coro):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(coro)
        except RuntimeError:
            asyncio.run(coro)

    with patch('bot.database.methods.cache_utils.safe_create_task', side_effect=run_immediately), \
            patch('bot.database.methods.create.safe_create_task', side_effect=run_immediately), \
            patch('bot.database.methods.update.safe_create_task', side_effect=run_immediately), \
            patch('bot.database.methods.delete.safe_create_task', side_effect=run_immediately), \
            patch('bot.database.methods.transactions.safe_create_task', side_effect=run_immediately):
        yield


@pytest.fixture(autouse=True)
def patch_env_keys():
    """Provide safe default EnvKeys for tests."""
    from unittest.mock import patch
    patches = {
        'PAY_CURRENCY': 'RUB',
        'REFERRAL_PERCENT': 10,
        'OWNER_ID': 999999,
        'MIN_AMOUNT': 10,
        'MAX_AMOUNT': 10000,
        'PAYMENT_TIME': 1800,
        'SEPAY_PAYMENT_PREFIX': 'SP',
        'CHANNEL_URL': '',
        'HELPER_ID': '',
        'RULES': 'Test rules',
    }
    with patch.multiple('bot.misc.env.EnvKeys', **patches):
        yield


@pytest.fixture
async def user_factory(patch_env_keys):
    """Factory to create test users."""
    from bot.database.methods.create import create_user
    from bot.database.methods.update import update_balance
    from bot.database.methods.read import check_user

    async def _create(
            telegram_id: int = 100001,
            balance: int = 0,
            role_id: int = 1,
            referral_id: int = None,
    ):
        await create_user(
            telegram_id=telegram_id,
            registration_date=datetime.datetime.now(datetime.timezone.utc),
            referral_id=referral_id,
            role=role_id,
        )
        if balance > 0:
            await update_balance(telegram_id, balance)
        return await check_user(telegram_id)

    return _create


@pytest.fixture
async def category_factory():
    """Factory to create categories."""
    from bot.database.methods.create import create_category

    async def _create(name: str = "TestCategory"):
        await create_category(name)

    return _create


@pytest.fixture
async def item_factory(category_factory):
    """Factory to create items with optional stock values."""
    from bot.database.methods.create import create_item, add_values_to_item

    async def _create(
            name: str = "TestItem",
            price: int = 100,
            category: str = "TestCategory",
            description: str = "Test description",
            values: list = None,
    ):
        await category_factory(category)
        await create_item(name, description, price, category)
        if values:
            for val, is_inf in values:
                await add_values_to_item(name, val, is_inf)

    return _create