from __future__ import annotations

from datetime import datetime
from uuid import UUID

from aiosu.utils import auth
from common import clients
from common import logger
from common import settings
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
    token_expires_on: datetime | None = None,
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
            token_expires_on=token_expires_on,
            session_id=session_id,
        )
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to create user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    return user


async def verify(
    kohaku_code: str,
    osu_code: str,
    session_id: UUID,
) -> User | ServiceError:
    try:
        user = await users.fetch_by_verification_code(kohaku_code)

        if user is None:
            return ServiceError.USER_NOT_FOUND

        if user["verified"]:
            return ServiceError.USER_ALREADY_VERIFIED

        token = await auth.process_code(
            client_id=settings.OSU_CLIENT_ID,
            client_secret=settings.OSU_CLIENT_SECRET,
            redirect_uri=settings.OSU_REDIRECT_URI,
            code=osu_code,
        )

        client = await clients.osu_storage.get_client(id=user["user_id"], token=token)
        osu_user = await client.get_me()

        await clients.bot.give_role(
            int(user["discord_id"]),
            settings.DISCORD_VERIFIED_ROLE_ID,
        )

        user = await users.partial_update(
            user_id=user["user_id"],
            osu_id=str(osu_user.id),
            osu_username=osu_user.username,
            verified=True,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_expires_on=token.expires_on,
            session_id=session_id,
        )
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to verify user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user


async def remove_verification(
    discord_id: str,
    remove_role: bool,
) -> User | ServiceError:
    user = await users.fetch_by_discord_id(discord_id)

    if user is None:
        return ServiceError.USER_NOT_FOUND

    if not user["verified"]:
        return ServiceError.USER_NOT_VERIFIED

    client = await clients.osu_storage.get_client(id=user["user_id"])
    await clients.osu_storage.revoke_client(client_uid=user["user_id"])
    await client.revoke_token()

    if remove_role:
        await clients.bot.remove_role(
            int(user["discord_id"]),
            settings.DISCORD_VERIFIED_ROLE_ID,
        )

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


async def fetch_by_session_id(session_id: UUID) -> User | ServiceError:
    try:
        user = await users.fetch_by_session_id(session_id)
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
    verification_code: str | None | _UnsetSentinel = UNSET,
    access_token: str | None | _UnsetSentinel = UNSET,
    refresh_token: str | None | _UnsetSentinel = UNSET,
    token_expires_on: datetime | None | _UnsetSentinel = UNSET,
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
            token_expires_on=token_expires_on,
            session_id=session_id,
        )
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to update user", exc_info=exc)
        return ServiceError.INTERNAL_SERVER_ERROR

    if user is None:
        return ServiceError.USER_NOT_FOUND

    return user
