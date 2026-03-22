import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import make_url

from bot.database.dsn import dsn
from bot.misc import SingletonMeta


class Database(metaclass=SingletonMeta):
    BASE = declarative_base()

    def __init__(self):
        database_url = dsn()
        url = make_url(database_url)
        engine_kwargs = {
            "echo": False,
            "pool_pre_ping": True,
        }

        if url.get_backend_name() == "sqlite":
            engine_kwargs["connect_args"] = {"check_same_thread": False}
        else:
            engine_kwargs.update(
                pool_size=20,
                max_overflow=40,
                pool_timeout=30,
                pool_recycle=3600,
                connect_args={
                    "timeout": 10,
                    "command_timeout": 30,
                    "server_settings": {
                        "lc_messages": "C",
                    },
                },
            )

        self.__engine: AsyncEngine = create_async_engine(
            database_url,
            **engine_kwargs,
        )

        if url.get_backend_name() == "sqlite":
            logging.info("SQLite database initialized")
        else:
            logging.info(f"Database pool initialized: size={20}, max_overflow={40}")

        self.__SessionLocal = async_sessionmaker(
            bind=self.__engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self):
        """Async contextual session: guaranteed to close/rollback on error."""
        async with self.__SessionLocal() as db:
            try:
                yield db
                await db.commit()
            except Exception:
                await db.rollback()
                raise

    @property
    def engine(self) -> AsyncEngine:
        return self.__engine

    async def dispose(self):
        """Dispose of the connection pool."""
        await self.__engine.dispose()
