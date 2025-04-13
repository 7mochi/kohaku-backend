from __future__ import annotations

from typing import Any

import discord
from bot.auth_view import AuthenticationView
from common import logger
from common.errors import ServiceError
from services import users


class Bot(discord.Client):
    def __init__(
        self: Any,
        verify_channel_id: int,
        guild_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.guild_id = guild_id
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

    async def give_role(self, user_id: int, role_id: int) -> None:
        guild = self.get_guild(self.guild_id)

        assert guild is not None

        discord_member = await guild.fetch_member(user_id)
        role = guild.get_role(role_id)

        assert discord_member is not None
        assert role is not None

        await discord_member.remove_roles(role)
        await discord_member.add_roles(role)

    async def remove_role(self, user_id: int, role_id: int) -> None:
        guild = self.get_guild(self.guild_id)

        assert guild is not None

        discord_member = await guild.fetch_member(user_id)
        role = guild.get_role(role_id)

        assert discord_member is not None
        assert role is not None

        await discord_member.remove_roles(role)

    async def on_ready(self) -> None:
        # Register persistent view
        await self.setup_verify_channel()

        assert self.user is not None
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        ignore = not message.guild
        ignore |= message.author.bot
        ignore |= not self.is_ready()
        if ignore:
            return

    async def on_member_remove(self, member: discord.Member) -> None:
        user = await users.fetch_by_discord_id(str(member.id))

        if isinstance(user, ServiceError):
            logger.info(
                f"The non-verified user {member.name} ({member.id}) left the server. Ignoring...",
            )
            return

        if user["verified"]:
            await users.remove_verification(str(member.id), False)

            logger.info(
                f"The verified user {member.name} ({member.id}) left the server. Verification removed.",
            )
        else:
            logger.info(
                f"The non-verified user {member.name} ({member.id}) left the server. Ignoring...",
            )
