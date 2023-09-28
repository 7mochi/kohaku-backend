from __future__ import annotations

from uuid import UUID

from common import logger
from common.errors import ServiceError
from common.typing import _UnsetSentinel
from common.typing import UNSET
from repositories import users
from repositories.users import User


async def create(
    discord_id: str,
    discord_username: str,
    verified: bool,
    verification_code: str,
    osu_id: str | None = None,
    osu_username: str | None = None,
    access_token: str | None = None,
    refresh_token: str | None = None,
    session_id: UUID | None = None,
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
            session_id=session_id,
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


async def fetch_by_discord_id(discord_id: str) -> User | ServiceError:
    try:
        user = await users.fetch_by_discord_id(discord_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to fetch discord user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user


async def fetch_by_discord_username(discord_username: int) -> User | ServiceError:
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
    discord_id: str | _UnsetSentinel = UNSET,
    discord_username: str | _UnsetSentinel = UNSET,
    osu_id: str | None | _UnsetSentinel = UNSET,
    osu_username: str | None | _UnsetSentinel = UNSET,
    verified: bool | _UnsetSentinel = UNSET,
    verification_code: str | _UnsetSentinel = UNSET,
    access_token: str | None | _UnsetSentinel = UNSET,
    refresh_token: str | None | _UnsetSentinel = UNSET,
    session_id: UUID | None | _UnsetSentinel = UNSET,
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
            session_id=session_id,
        )
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to update user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user
