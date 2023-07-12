from __future__ import annotations

import base64
import ssl

from adapters import database
from common import clients
from common import logger
from common import settings


async def _start_database():
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


async def _shutdown_database():
    logger.info("Closing database connection...")
    await clients.database.disconnect()
    del clients.database
    logger.info("Closed database connection")


async def start():
    await _start_database()


async def shutdown():
    await _shutdown_database()
