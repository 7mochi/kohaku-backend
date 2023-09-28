from __future__ import annotations

from uuid import UUID
from uuid import uuid4

import aiosu
from aiosu.utils import auth
from api.osu.models import User
from common import logger
from common import settings
from common.errors import ServiceError
from common.session_verifier import BasicVerifier
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import CookieParameters
from fastapi_sessions.frontends.implementations import SessionCookie
from services import users

auth_router = APIRouter(default_response_class=Response)

cookie_params = CookieParameters()

cookie = SessionCookie(
    cookie_name=settings.SESSION_COOKIE_NAME,
    identifier=settings.SESSION_COOKIE_IDENTIFIER,
    auto_error=True,
    secret_key=settings.SESSION_COOKIE_KEY,
    cookie_params=cookie_params,
)
cookie_backend = InMemoryBackend[UUID, User]()

cookie_verifier = BasicVerifier(
    identifier=settings.SESSION_COOKIE_IDENTIFIER,
    auto_error=True,
    backend=cookie_backend,
    auth_http_exception=HTTPException(status_code=403, detail="Invalid session"),
)


@auth_router.post("/auth")
async def auth_handler(request: Request) -> Response:
    body = await request.json()
    # TODO: Maybe also validate if both codes aren't empty
    if "kohaku_code" not in body or "osu_code" not in body:
        raise HTTPException(status_code=400, detail="Missing codes in request body")

    user = await users.fetch_by_verification_code(body["kohaku_code"])

    if isinstance(user, ServiceError):
        if user is ServiceError.USER_NOT_FOUND:
            raise HTTPException(status_code=404, detail="User not found")

    if user["verified"]:  # type: ignore
        raise HTTPException(status_code=403, detail="User already verified")

    try:
        token = await auth.process_code(
            client_id=settings.OSU_CLIENT_ID,
            client_secret=settings.OSU_CLIENT_SECRET,
            redirect_uri=settings.OSU_REDIRECT_URI,
            code=body["osu_code"],
        )
    except:
        raise HTTPException(status_code=403, detail="Invalid osu! code")

    client_storage = aiosu.v2.Client(token=token)
    osu_user = await client_storage.get_me()
    await client_storage.close()

    session = uuid4()
    _user = await users.partial_update(
        user_id=user["user_id"],  # type: ignore
        osu_id=osu_user.id,
        osu_username=osu_user.username,
        verified=True,
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        session_id=session,
    )

    user_mdl = User.parse_obj(_user)
    await cookie_backend.create(session_id=session, data=user_mdl)

    response = Response(user_mdl.json(), status_code=200, media_type="application/json")
    cookie.attach_to_response(response, session)

    logger.info(
        f"User {_user['discord_username']} ({_user['discord_id']}) with osu! account {_user['osu_username']} ({_user['osu_id']}) verified successfully",  # type: ignore
    )

    return response


@auth_router.post("/deauth", dependencies=[Depends(cookie)])
async def deauth_handler(
    request: Request,
    user: User = Depends(cookie_verifier),
) -> Response:
    _user = await users.fetch_by_discord_id(user.discord_id)

    if isinstance(_user, ServiceError):
        if _user is ServiceError.USER_NOT_FOUND:
            raise HTTPException(status_code=404, detail="User not found")

    if not _user["verified"]:  # type: ignore
        raise HTTPException(status_code=403, detail="User not verified")

    await cookie_backend.delete(session_id=_user["session_id"])  # type: ignore

    logger.info(
        f"User {_user['discord_username']} ({_user['discord_id']}) with osu! account {_user['osu_username']} ({_user['osu_id']}) deauthenticated successfully",  # type: ignore
    )

    assert _user is not None
    await users.partial_update(
        user_id=_user["user_id"],  # type: ignore
        osu_id=None,
        osu_username=None,
        verified=False,
        access_token=None,
        refresh_token=None,
        session_id=None,
    )

    return Response(status_code=200)


@auth_router.get("/user", dependencies=[Depends(cookie)])
async def user_handler(user: User = Depends(cookie_verifier)) -> Response:
    return Response(user.json(), media_type="application/json")
