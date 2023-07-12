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
    username,
    verified,
    verification_code,
    created_at,
    updated_at
"""


class User(TypedDict):
    user_id: int
    discord_id: str
    username: str
    verified: bool
    verification_code: str
    created_at: datetime
    updated_at: datetime


class UserUpdateFields(TypedDict, total=False):
    discord_id: str
    username: str
    verified: bool
    verification_code: str


async def create(
    discord_id: int,
    username: str,
    verified: bool,
    verification_code: str,
) -> User:
    user = await clients.database.fetch_one(
        query=f"""\
            INSERT INTO users (discord_id, username, verified, verification_code,
                               created_at, updated_at)
            VALUES (:discord_id, :username, :verified, :verification_code,
                    NOW(), NOW())
            RETURNING {READ_PARAMS}
        """,
        values={
            "discord_id": str(discord_id),
            "username": username,
            "verified": verified,
            "verification_code": verification_code,
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


async def fetch_by_username(username: int) -> User | None:
    user = await clients.database.fetch_one(
        query=f"""\
            SELECT {READ_PARAMS}
            FROM users
            WHERE username = :username
        """,
        values={
            "username": username,
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
    discord_id: str | Unset = UNSET,
    username: str | Unset = UNSET,
    verified: bool | Unset = UNSET,
    verification_code: str | Unset = UNSET,
) -> User | None:
    update_fields = UserUpdateFields = {}
    if not isinstance(discord_id, Unset):
        update_fields["discord_id"] = discord_id
    if not isinstance(username, Unset):
        update_fields["username"] = username
    if not isinstance(verified, Unset):
        update_fields["verified"] = verified
    if not isinstance(verification_code, Unset):
        update_fields["verification_code"] = verification_code

    query = f"""\
        UPDATE users
        SET {",".join(f"{k} = :{k}" for k in update_fields)}
        WHERE user_id = :user_id
        RETURNING {READ_PARAMS}
    """
    values = {"user_id": user_id} | update_fields

    user = await clients.database.fetch_one(query, values)
    return cast(User, user) if user is not None else None
