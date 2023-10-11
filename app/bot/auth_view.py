from __future__ import annotations

import base64
import os

import discord
from common import logger
from common import settings
from common.errors import ServiceError
from services import users


class AuthenticationView(discord.ui.View):
    # Make the button persistent
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verificarse",
        style=discord.ButtonStyle.grey,
        emoji="✅",
        custom_id="persistent:kohaku_auth",
    )
    async def button_callback(
        self,
        interaction: discord.Interaction,  # type: ignore
        button: discord.ui.Button,  # type: ignore
    ) -> None:
        user = await users.fetch_by_discord_id(str(interaction.user.id))

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
                    discord_id=str(interaction.user.id),
                    discord_username=interaction.user.name,
                    verified=False,
                    verification_code=code,
                )

                return await interaction.response.send_message(
                    f"To verify, go to: {settings.FRONTEND_URL}?kohaku_code={code}",
                    ephemeral=True,
                )

        if user["verified"]:  # type: ignore
            logger.info(
                f"User {interaction.user.name} ({interaction.user.id}) tried to verify again",
            )
            return await interaction.response.send_message(
                "You're already verified!",
                ephemeral=True,
            )
        else:
            code = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("ascii")

            user = await users.partial_update(
                user_id=user["user_id"],  # type: ignore
                verification_code=code,
            )

            return await interaction.response.send_message(
                f"To verify, go to: {settings.FRONTEND_URL}?kohaku_code={code}",
                ephemeral=True,
            )
