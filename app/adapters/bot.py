from __future__ import annotations

import base64
import os
from typing import Any

import discord

from app.common import logger
from app.common import settings
from app.common.errors import ServiceError
from app.services import users


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
                    username=interaction.user.name,
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
