from __future__ import annotations

import atexit
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from api.osu.auth import auth_router
from common import lifecycle
from common import logger
from common import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger.configure_logging(
    app_env=settings.APP_ENV,
    log_level=settings.APP_LOG_LEVEL,
)
logger.overwrite_exception_hook()
atexit.register(logger.restore_exception_hook)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# auth hosts
app.host(settings.DOMAIN if settings.DOMAIN else settings.APP_HOST, auth_router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    await lifecycle.start()
    yield
    await lifecycle.shutdown()
