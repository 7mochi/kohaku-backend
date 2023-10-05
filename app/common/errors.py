from __future__ import annotations

from asyncio.events import AbstractEventLoop
from enum import Enum
from signal import Signals

from common import logger


class ServiceError(str, Enum):
    INTERNAL_SERVER_ERROR = "global.internal_server_error"

    USER_NOT_FOUND = "user.not_found"
    USER_ALREADY_VERIFIED = "user.already_verified"
    USER_NOT_VERIFIED = "user.not_verified"


class SignalHaltError(SystemExit):
    def __init__(self, signal_enum: Signals):
        self.signal_enum = signal_enum
        logger.info(f"Shutting down discord bot due to {repr(self)}")
        # Set exit code as 0, so no error will appear in the terminal since
        # is being executed from a bash script with 'set -euo pipefail'
        super().__init__(0)

    @property
    def exit_code(self) -> int:
        return self.signal_enum.value

    def __repr__(self) -> str:
        return self.signal_enum.name


def immediate_exit(signal_enum: Signals, loop: AbstractEventLoop) -> None:
    loop.stop()
    raise SignalHaltError(signal_enum=signal_enum)
