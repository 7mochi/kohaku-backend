from __future__ import annotations

from enum import Enum


class ServiceError(str, Enum):
    INTERNAL_SERVER_ERROR = "global.internal_server_error"

    USER_NOT_FOUND = "user.not_found"
    USER_ALREADY_VERIFIED = "user.already_verified"
