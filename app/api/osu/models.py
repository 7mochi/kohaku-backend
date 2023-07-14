from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


# input models


# output models


class User(BaseModel):
    user_id: int
    discord_id: str
    discord_username: str
    osu_id: str
    osu_username: str
    verified: bool
    verification_code: str
    access_token: str
    refresh_token: str
    created_at: datetime
    updated_at: datetime
