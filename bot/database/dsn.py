import os
from bot.misc import EnvKeys


def dsn() -> str:
    return os.getenv("DATABASE_URL") or EnvKeys.DATABASE_URL
