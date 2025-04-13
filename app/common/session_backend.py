"""DatabaseBackend Custom implementation."""

from __future__ import annotations

from typing import Generic
from typing import cast
from uuid import UUID

from api.osu.models import User as UserModel
from common.errors import ServiceError
from fastapi_sessions.backends.session_backend import BackendError
from fastapi_sessions.backends.session_backend import SessionBackend
from fastapi_sessions.backends.session_backend import SessionModel
from fastapi_sessions.frontends.session_frontend import ID
from repositories.users import User
from services import users


class DatabaseBackend(SessionBackend[UUID, UserModel]):  # type: ignore
    """Stores session data in a dictionary."""

    async def create(self, session_id: UUID, data: UserModel) -> None:
        """Create a new session entry."""
        _data = cast(User, dict(data))
        user = await users.fetch_by_user_id(_data["user_id"])

        # we update it beceause we already created the user
        if not isinstance(user, ServiceError):
            await users.partial_update(
                user_id=_data["user_id"],
                session_id=session_id,
            )

    async def read(self, session_id: UUID) -> None | UserModel:
        """Read an existing session data."""
        user = await users.fetch_by_session_id(session_id)

        if isinstance(user, ServiceError):
            if user is ServiceError.USER_NOT_FOUND:
                return None

        return UserModel.model_validate(user)

    async def update(self, session_id: UUID, data: UserModel) -> None:
        """Update an existing session."""
        _data = cast(User, dict(data))
        user = await users.fetch_by_session_id(session_id)

        if not isinstance(user, ServiceError):
            await users.partial_update(
                user_id=_data["user_id"],
                session_id=session_id,
            )

    async def delete(self, session_id: UUID) -> None:
        """D"""
        user = await users.fetch_by_session_id(session_id)

        if not isinstance(user, ServiceError):
            await users.partial_update(
                user_id=user["user_id"],
                session_id=None,
            )
