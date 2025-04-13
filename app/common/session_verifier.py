from __future__ import annotations

from uuid import UUID

from api.osu.models import User as UserModel
from common.session_backend import DatabaseBackend
from fastapi import HTTPException
from fastapi_sessions.session_verifier import SessionVerifier


class BasicVerifier(SessionVerifier[UUID, UserModel]):  # type: ignore
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: DatabaseBackend,
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def backend(self) -> DatabaseBackend:
        return self._backend

    @property
    def auto_error(self) -> bool:
        return self._auto_error

    @property
    def auth_http_exception(self) -> HTTPException:
        return self._auth_http_exception

    def verify_session(self, model: UserModel) -> bool:
        """If the session exists, it is valid"""
        return True
