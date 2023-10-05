from __future__ import annotations

import asyncio
import atexit
import os
from functools import partial
from signal import SIGINT
from signal import SIGTERM

import discord
from bot.kohaku_bot import Bot
from common import logger
from common import settings
from common.errors import immediate_exit


logger.configure_logging(
    app_env=settings.APP_ENV,
    log_level=settings.APP_LOG_LEVEL,
)
logger.overwrite_exception_hook()
atexit.register(logger.restore_exception_hook)


async def main() -> int:
    # set cwd to main directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    logger.info("Starting discord bot...")

    intents = discord.Intents.default()
    intents.message_content = True

    bot = Bot(
        intents=intents,
        verify_channel_id=settings.DISCORD_VERIFY_CHANNEL_ID,
    )

    loop = asyncio.get_running_loop()

    for signal_enum in [SIGINT, SIGTERM]:
        exit_func = partial(immediate_exit, signal_enum=signal_enum, loop=loop)
        loop.add_signal_handler(signal_enum, exit_func)

    loop.run_until_complete(await bot.start(settings.DISCORD_BOT_TOKEN))  # type: ignore

    logger.info("Started discord bot")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
