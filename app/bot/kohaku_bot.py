from __future__ import annotations

import atexit
from typing import Any

import discord
from bot.auth_view import AuthenticationView
from common import lifecycle
from common import logger
from common import settings


class Bot(discord.Client):
    def __init__(self: Any, verify_channel_id: int, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.verify_channel_id = verify_channel_id

    async def start(self, *args: Any, **kwargs: Any) -> None:
        await super().start(*args, **kwargs)

    async def close(self, *args: Any, **kwargs: Any) -> None:
        await super().close(*args, **kwargs)

    async def setup_verify_channel(self) -> None:
        self.add_view(AuthenticationView())
        logger.info("Persistent button registered")

        channel = self.get_channel(self.verify_channel_id)

        if isinstance(channel, discord.TextChannel):
            latest_messages = [message async for message in channel.history(limit=100)]

            for message in latest_messages:
                assert self.user is not None

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

        assert self.user is not None
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        ignore = not message.guild
        ignore |= message.author.bot
        ignore |= not self.is_ready()
        if ignore:
            return
