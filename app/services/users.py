from __future__ import annotations

from app.common import logger
from app.common.errors import ServiceError
from app.common.typing import UNSET
from app.common.typing import Unset
from app.repositories import users
from app.repositories.users import User


async def create(
    discord_id: int,
    username: str,
    verified: bool,
    verification_code: str,
) -> User | ServiceError:
    try:
        user = await users.create(
            discord_id=discord_id,
            username=username,
            verified=verified,
            verification_code=verification_code,
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


async def fetch_by_username(username: str) -> User | ServiceError:
    try:
        user = await users.fetch_by_username(username)
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
    username: str | Unset = UNSET,
    verified: bool | Unset = UNSET,
    verification_code: str | Unset = UNSET,
) -> User | ServiceError:
    try:
        user = await users.partial_update(
            user_id=user_id,
            discord_id=discord_id,
            username=username,
            verified=verified,
            verification_code=verification_code,
        )
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to update user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user
