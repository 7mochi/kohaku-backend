from __future__ import annotations

import asyncio
import atexit
import base64
import os
from asyncio.events import AbstractEventLoop
from functools import partial
from signal import SIGINT
from signal import Signals
from signal import SIGTERM
from typing import Any

import discord
from common import lifecycle
from common import logger
from common import settings
from common.errors import ServiceError
from services import users

logger.configure_logging(
    app_env=settings.APP_ENV,
    log_level=settings.APP_LOG_LEVEL,
)
logger.overwrite_exception_hook()
atexit.register(logger.restore_exception_hook)


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


class Bot(discord.Client):
    def __init__(self, verify_channel_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.verify_channel_id = verify_channel_id

    async def start(self, *args, **kwargs) -> None:
        await super().start(*args, **kwargs)

    async def close(self, *args: Any, **kwargs: Any) -> None:
        await super().close(*args, **kwargs)

    async def setup_verify_channel(self) -> None:
        self.add_view(AuthenticationView())
        logger.info("Persistent button registered")

        channel = self.get_channel(self.verify_channel_id)
        latest_messages = [message async for message in channel.history(limit=100)]

        for message in latest_messages:
            if message.author.id == self.user.id and len(message.components) > 0:
                logger.info(
                    "Found an already existing button for verification. The bot will not create a new one",
                )
                return

        await channel.send("", view=AuthenticationView())
        logger.info("Verification button created")

    async def on_ready(self) -> None:
        # Register persistent view
        await self.setup_verify_channel()
        await lifecycle.start()

        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        ignore = not message.guild
        ignore |= message.author.bot
        ignore |= not self.is_ready()
        if ignore:
            return

        await self.process_commands(message)


class AuthenticationView(discord.ui.View):
    # Make the button persistent
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verificarse",
        style=discord.ButtonStyle.grey,
        emoji="✅",
        custom_id="persistent:kohaku_auth",
    )
    async def button_callback(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        user = await users.fetch_by_discord_id(interaction.user.id)

        if isinstance(user, ServiceError):
            if user is ServiceError.USER_NOT_FOUND:
                logger.info(
                    f"User {interaction.user.name} ({interaction.user.id}) not found. Creating...",
                )

                code = (
                    base64.urlsafe_b64encode(os.urandom(32))
                    .rstrip(b"=")
                    .decode("ascii")
                )

                user = await users.create(
                    discord_id=interaction.user.id,
                    discord_username=interaction.user.name,
                    verified=False,
                    verification_code=code,
                )

                await interaction.response.send_message(
                    f"To verify, go to: {settings.FRONTEND_URL}?kohaku_code={code}",
                    ephemeral=True,
                )

        if user["verified"]:
            logger.info(
                f"User {interaction.user.name} ({interaction.user.id}) tried to verify again",
            )
            await interaction.response.send_message(
                "You're already verified!",
                ephemeral=True,
            )
        else:
            code = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("ascii")

            user = await users.partial_update(
                user_id=user["user_id"],
                verification_code=code,
            )

            await interaction.response.send_message(
                f"To verify, go to: {settings.FRONTEND_URL}?kohaku_code={code}",
                ephemeral=True,
            )


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

    loop.run_until_complete(await bot.start(settings.DISCORD_BOT_TOKEN))

    logger.info("Started discord bot")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
