from importlib import import_module as _import_module

from bot.database.methods.create import *
from bot.database.methods.read import *
from bot.database.methods.update import *
from bot.database.methods.delete import *
from bot.database.methods.lazy_queries import *
from bot.database.methods.transactions import *
from bot.database.methods.cache_utils import *
from bot.database.methods.audit import log_audit

# Expose submodules explicitly so dotted patch targets like
# `bot.database.methods.update.safe_create_task` resolve to the module.
update = _import_module("bot.database.methods.update")
delete = _import_module("bot.database.methods.delete")
transactions = _import_module("bot.database.methods.transactions")
cache_utils = _import_module("bot.database.methods.cache_utils")
