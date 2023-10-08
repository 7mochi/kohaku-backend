from __future__ import annotations

import aiosu
from adapters.database import Database
from bot.kohaku_bot import Bot

database: Database
osu_storage: aiosu.v2.ClientStorage
bot: Bot
