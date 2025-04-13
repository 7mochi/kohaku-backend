from __future__ import annotations

from aiosu.models import OAuthToken
from aiosu.v2.repository import BaseTokenRepository
from common.errors import ServiceError
from services import users


class TokenRepository(BaseTokenRepository):
    """Repository for osu! tokens."""

    async def exists(self, session_id: int) -> bool:
        """Check if token exists in database.

        Args:
            session_id (int): User ID.
        Returns:
            bool: True if token exists, False otherwise.
        """
        user = await users.fetch_by_user_id(session_id)

        if isinstance(user, ServiceError):
            if user is ServiceError.USER_NOT_FOUND:
                return False

        return user["access_token"] is not None  # type: ignore

    async def get(self, session_id: int) -> OAuthToken:
        """Get osu! token from database.

        Args:
            session_id (int): User ID.
        Raises:
            ValueError: Token not found.
        Returns:
            OAuthToken: osu! token.
        """
        user = await users.fetch_by_user_id(session_id)

        if isinstance(user, ServiceError):
            raise ValueError("Token not found")

        if user["access_token"] is None:
            raise ValueError("Token not found")

        return OAuthToken.model_validate(
            {
                "access_token": user["access_token"],
                "refresh_token": user["refresh_token"],
                "expires_on": user["token_expires_on"],
            },
        )

    async def add(self, session_id: int, token: OAuthToken) -> OAuthToken:
        """Add new token to database.

        Args:
            session_id (int): User ID.
            token (OAuthToken): osu! token.
        """

        # Update because we already created a user
        await users.partial_update(
            user_id=session_id,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_expires_on=token.expires_on,
            osu_id=str(token.owner_id),
        )
        return token

    async def update(self, session_id: int, token: OAuthToken) -> OAuthToken:
        """Update token in database.

        Args:
            session_id (int): Session ID.
            token (OAuthToken): osu! token.
        """
        await users.partial_update(
            user_id=session_id,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_expires_on=token.expires_on,
            osu_id=str(token.owner_id),
        )
        return token

    async def delete(self, session_id: int) -> None:
        """Delete token data.

        Args:
            session_id (int): User ID.
        """
        await users.partial_update(
            user_id=session_id,
            verified=False,
            verification_code=None,
            access_token=None,
            refresh_token=None,
            token_expires_on=None,
            osu_id=None,
            osu_username=None,
            session_id=None,
        )
