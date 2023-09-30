from __future__ import annotations

import aiosu
from adapters.database import Database

database: Database
osu_storage: aiosu.v2.ClientStorage
