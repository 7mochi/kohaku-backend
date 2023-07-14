from __future__ import annotations

from common import logger
from common.errors import ServiceError
from common.typing import UNSET
from common.typing import Unset
from repositories import users
from repositories.users import User


async def create(
    discord_id: int,
    discord_username: str,
    verified: bool,
    verification_code: str,
    osu_id: int | None = None,
    osu_username: str | None = None,
    access_token: str | None = None,
    refresh_token: str | None = None,
) -> User | ServiceError:
    try:
        user = await users.create(
            discord_id=discord_id,
            discord_username=discord_username,
            osu_id=osu_id,
            osu_username=osu_username,
            verified=verified,
            verification_code=verification_code,
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to create user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    return user


async def fetch_many(
    page: int = 1,
    page_size: int = 50,
) -> list[User] | ServiceError:
    try:
        _users = await users.fetch_many(page=page, page_size=page_size)
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to fetch users", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    return _users


async def fetch_by_user_id(user_id: int) -> User | ServiceError:
    try:
        user = await users.fetch_by_user_id(user_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to fetch user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user


async def fetch_by_discord_id(discord_id: int) -> User | ServiceError:
    try:
        user = await users.fetch_by_discord_id(discord_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to fetch discord user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user


async def fetch_by_discord_username(discord_username: str) -> User | ServiceError:
    try:
        user = await users.fetch_by_discord_username(discord_username)
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to fetch user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user


async def fetch_by_verification_code(verification_code: str) -> User | ServiceError:
    try:
        user = await users.fetch_by_verification_code(verification_code)
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to fetch user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user


async def partial_update(
    user_id: int,
    discord_id: str | Unset = UNSET,
    discord_username: str | Unset = UNSET,
    osu_id: str | Unset = UNSET,
    osu_username: str | Unset = UNSET,
    verified: bool | Unset = UNSET,
    verification_code: str | Unset = UNSET,
    access_token: str | Unset = UNSET,
    refresh_token: str | Unset = UNSET,
) -> User | ServiceError:
    try:
        user = await users.partial_update(
            user_id=user_id,
            discord_id=discord_id,
            discord_username=discord_username,
            osu_id=osu_id,
            osu_username=osu_username,
            verified=verified,
            verification_code=verification_code,
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to update user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user
