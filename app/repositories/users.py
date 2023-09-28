from __future__ import annotations

from datetime import datetime
from typing import cast
from typing import TypedDict
from uuid import UUID

from common import clients
from common.typing import _UnsetSentinel
from common.typing import UNSET

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
    session_id,
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
    session_id: UUID | None
    created_at: datetime
    updated_at: datetime


class UserUpdateFields(TypedDict, total=False):
    discord_id: str
    discord_username: str
    osu_id: str | None
    osu_username: str | None
    verified: bool
    verification_code: str
    access_token: str | None
    refresh_token: str | None
    session_id: UUID | None


async def create(
    discord_id: str,
    discord_username: str,
    osu_id: str | None,
    osu_username: str | None,
    verified: bool,
    verification_code: str,
    access_token: str | None = None,
    refresh_token: str | None = None,
    session_id: UUID | None = None,
) -> User:
    user = await clients.database.fetch_one(
        query=f"""\
            INSERT INTO users (discord_id, discord_username, osu_id, osu_username,
                               verified, verification_code, access_token, refresh_token,
                               session_id, created_at, updated_at)
            VALUES (:discord_id, :discord_username, :osu_id, :osu_username,
                    :verified, :verification_code,:access_token, :refresh_token,
                    :session_id, NOW(), NOW())
            RETURNING {READ_PARAMS}
        """,
        values={
            "discord_id": discord_id,
            "discord_username": discord_username,
            "osu_id": osu_id,
            "osu_username": osu_username,
            "verified": verified,
            "verification_code": verification_code,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session_id": session_id,
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
            "user_id": user_id,
        },
    )

    return cast(User, user) if user is not None else None


async def fetch_by_discord_id(discord_id: str) -> User | None:
    user = await clients.database.fetch_one(
        query=f"""\
            SELECT {READ_PARAMS}
            FROM users
            WHERE discord_id = :discord_id
        """,
        values={
            "discord_id": discord_id,
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
    discord_id: str | _UnsetSentinel = UNSET,
    discord_username: str | _UnsetSentinel = UNSET,
    osu_id: str | None | _UnsetSentinel = UNSET,
    osu_username: str | None | _UnsetSentinel = UNSET,
    verified: bool | _UnsetSentinel = UNSET,
    verification_code: str | _UnsetSentinel = UNSET,
    access_token: str | None | _UnsetSentinel = UNSET,
    refresh_token: str | None | _UnsetSentinel = UNSET,
    session_id: UUID | None | _UnsetSentinel = UNSET,
) -> User | None:
    update_fields: UserUpdateFields = {}
    if not isinstance(discord_id, _UnsetSentinel):
        update_fields["discord_id"] = discord_id
    if not isinstance(discord_username, _UnsetSentinel):
        update_fields["discord_username"] = discord_username
    if not isinstance(osu_id, _UnsetSentinel):
        update_fields["osu_id"] = osu_id
    if not isinstance(osu_username, _UnsetSentinel):
        update_fields["osu_username"] = osu_username
    if not isinstance(verified, _UnsetSentinel):
        update_fields["verified"] = verified
    if not isinstance(verification_code, _UnsetSentinel):
        update_fields["verification_code"] = verification_code
    if not isinstance(access_token, _UnsetSentinel):
        update_fields["access_token"] = access_token
    if not isinstance(refresh_token, _UnsetSentinel):
        update_fields["refresh_token"] = refresh_token
    if not isinstance(session_id, _UnsetSentinel):
        update_fields["session_id"] = session_id

    query = f"""\
        UPDATE users
        SET {",".join(f"{k} = :{k}" for k in update_fields)}
        WHERE user_id = :user_id
        RETURNING {READ_PARAMS}
    """
    values = {"user_id": user_id} | update_fields

    user = await clients.database.fetch_one(query, values)
    return cast(User, user) if user is not None else None
