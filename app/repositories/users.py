from __future__ import annotations

from datetime import datetime
from typing import cast
from typing import TypedDict

from common import clients
from common.typing import UNSET
from common.typing import Unset

READ_PARAMS = """
    user_id,
    discord_id,
    discord_username,
    osu_id,
    osu_username,
    verified,
    verification_code,
    access_token,
    refresh_token,
    created_at,
    updated_at
"""


class User(TypedDict):
    user_id: int
    discord_id: str
    discord_username: str
    osu_id: str | None
    osu_username: str | None
    verified: bool
    verification_code: str
    access_token: str | None
    refresh_token: str | None
    created_at: datetime
    updated_at: datetime


class UserUpdateFields(TypedDict, total=False):
    discord_id: str
    discord_username: str
    osu_id: str
    osu_username: str
    verified: bool
    verification_code: str
    access_token: str | None
    refresh_token: str | None


async def create(
    discord_id: int,
    discord_username: str,
    osu_id: int | None,
    osu_username: str | None,
    verified: bool,
    verification_code: str,
    access_token: str | None = None,
    refresh_token: str | None = None,
) -> User:
    user = await clients.database.fetch_one(
        query=f"""\
            INSERT INTO users (discord_id, discord_username, osu_id, osu_username,
                               verified, verification_code, access_token, refresh_token,
                               created_at, updated_at)
            VALUES (:discord_id, :discord_username, :osu_id, :osu_username,
                    :verified, :verification_code,:access_token, :refresh_token,
                    NOW(), NOW())
            RETURNING {READ_PARAMS}
        """,
        values={
            "discord_id": str(discord_id),
            "discord_username": discord_username,
            "osu_id": str(osu_id),
            "osu_username": osu_username,
            "verified": verified,
            "verification_code": verification_code,
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    )

    assert user is not None
    return cast(User, user)


async def fetch_many(
    page: int | None = None,
    page_size: int | None = None,
) -> list[User]:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM users
    """
    values = {}
    if page is not None and page_size is not None:
        query += """
            LIMIT :limit
            OFFSET :offset
        """
        values["limit"] = page
        values["offset"] = (page - 1) * page_size

    users = await clients.database.fetch_all(query, values)
    return cast(list[User], users)


async def fetch_by_user_id(user_id: int) -> User | None:
    user = await clients.database.fetch_one(
        query=f"""\
            SELECT {READ_PARAMS}
            FROM users
            WHERE user_id = :user_id
        """,
        values={
            "user_id": str(user_id),
        },
    )

    return cast(User, user) if user is not None else None


async def fetch_by_discord_id(discord_id: int) -> User | None:
    user = await clients.database.fetch_one(
        query=f"""\
            SELECT {READ_PARAMS}
            FROM users
            WHERE discord_id = :discord_id
        """,
        values={
            "discord_id": str(discord_id),
        },
    )

    return cast(User, user) if user is not None else None


async def fetch_by_discord_username(discord_username: int) -> User | None:
    user = await clients.database.fetch_one(
        query=f"""\
            SELECT {READ_PARAMS}
            FROM users
            WHERE discord_username = :discord_username
        """,
        values={
            "discord_username": discord_username,
        },
    )

    return cast(User, user) if user is not None else None


async def fetch_by_verification_code(verification_code: str) -> User | None:
    user = await clients.database.fetch_one(
        query=f"""\
            SELECT {READ_PARAMS}
            FROM users
            WHERE verification_code = :verification_code
        """,
        values={
            "verification_code": verification_code,
        },
    )

    return cast(User, user) if user is not None else None


async def partial_update(
    user_id: int,
    discord_id: int | Unset = UNSET,
    discord_username: str | Unset = UNSET,
    osu_id: str | Unset = UNSET,
    osu_username: str | Unset = UNSET,
    verified: bool | Unset = UNSET,
    verification_code: str | Unset = UNSET,
    access_token: str | Unset = UNSET,
    refresh_token: str | Unset = UNSET,
) -> User | None:
    update_fields = UserUpdateFields = {}
    if not isinstance(discord_id, Unset):
        update_fields["discord_id"] = str(discord_id)
    if not isinstance(discord_username, Unset):
        update_fields["discord_username"] = discord_username
    if not isinstance(osu_id, Unset):
        update_fields["osu_id"] = str(osu_id)
    if not isinstance(osu_username, Unset):
        update_fields["osu_username"] = osu_username
    if not isinstance(verified, Unset):
        update_fields["verified"] = verified
    if not isinstance(verification_code, Unset):
        update_fields["verification_code"] = verification_code
    if not isinstance(access_token, Unset):
        update_fields["access_token"] = access_token
    if not isinstance(refresh_token, Unset):
        update_fields["refresh_token"] = refresh_token

    query = f"""\
        UPDATE users
        SET {",".join(f"{k} = :{k}" for k in update_fields)}
        WHERE user_id = :user_id
        RETURNING {READ_PARAMS}
    """
    values = {"user_id": user_id} | update_fields

    user = await clients.database.fetch_one(query, values)
    return cast(User, user) if user is not None else None
