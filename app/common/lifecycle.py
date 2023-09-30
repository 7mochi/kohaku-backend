from __future__ import annotations

import base64
import ssl

import aiosu
from adapters import database
from common import clients
from common import logger
from common import settings
from repositories import token


async def _start_database() -> None:
    logger.info("Connecting to database...")
    clients.database = database.Database(
        read_dsn=database.dsn(
            scheme=settings.READ_DB_SCHEME,
            user=settings.READ_DB_USER,
            password=settings.READ_DB_PASS,
            host=settings.READ_DB_HOST,
            port=settings.READ_DB_PORT,
            database=settings.READ_DB_NAME,
        ),
        read_db_ssl=(
            ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cadata=base64.b64decode(settings.READ_DB_CA_CERT_BASE64).decode(),
            )
            if settings.READ_DB_USE_SSL
            else False
        ),
        write_dsn=database.dsn(
            scheme=settings.WRITE_DB_SCHEME,
            user=settings.WRITE_DB_USER,
            password=settings.WRITE_DB_PASS,
            host=settings.WRITE_DB_HOST,
            port=settings.WRITE_DB_PORT,
            database=settings.WRITE_DB_NAME,
        ),
        write_db_ssl=(
            ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cadata=base64.b64decode(settings.WRITE_DB_CA_CERT_BASE64).decode(),
            )
            if settings.WRITE_DB_USE_SSL
            else False
        ),
        min_pool_size=settings.READ_DB_MIN_POOL_SIZE,
        max_pool_size=settings.READ_DB_MAX_POOL_SIZE,
    )
    await clients.database.connect()
    logger.info("Connected to database(s)")


async def _shutdown_database() -> None:
    logger.info("Closing database connection...")
    await clients.database.disconnect()
    del clients.database
    logger.info("Closed database connection")


async def _start_osu_storage() -> None:
    logger.info("Starting osu! token storage...")
    clients.osu_storage = aiosu.v2.ClientStorage(
        token_repository=token.TokenRepository(),
        client_id=settings.OSU_CLIENT_ID,
        client_secret=settings.OSU_CLIENT_SECRET,
    )
    logger.info("Started osu! token storage")


async def _shutdown_osu_storage() -> None:
    logger.info("Closing osu! token storage...")
    await clients.osu_storage.close()
    del clients.osu_storage
    logger.info("Closed osu! token storage")


async def start() -> None:
    await _start_database()
    await _start_osu_storage()


async def shutdown() -> None:
    await _shutdown_database()
    await _shutdown_osu_storage()
