from __future__ import annotations

from uuid import UUID
from uuid import uuid4

import aiosu
from aiosu.utils import auth
from api.osu.models import User
from common import clients
from common import logger
from common import settings
from common.errors import ServiceError
from common.session_verifier import BasicVerifier
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi import status
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


def determine_status_code(error: ServiceError) -> int:
    match error:
        case ServiceError.USER_NOT_FOUND:
            return status.HTTP_404_NOT_FOUND
        case ServiceError.USER_ALREADY_VERIFIED:
            return status.HTTP_409_CONFLICT
        case ServiceError.USER_NOT_VERIFIED:
            return status.HTTP_403_FORBIDDEN
        case ServiceError.INTERNAL_SERVER_ERROR:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        case _:
            logger.warning(
                "Unhandled error code in accounts rest api controller",
                service_error=error,
            )
            return status.HTTP_500_INTERNAL_SERVER_ERROR


@auth_router.post("/auth")
async def auth_handler(request: Request) -> Response:
    body = await request.json()
    # TODO: Maybe also validate if both codes aren't empty
    if "kohaku_code" not in body or "osu_code" not in body:
        raise HTTPException(status_code=400, detail="Missing codes in request body")

    session_id = uuid4()
    user = await users.verify(
        kohaku_code=body["kohaku_code"],
        osu_code=body["osu_code"],
        session_id=session_id,
    )

    if isinstance(user, ServiceError):
        status_code = determine_status_code(user)
        raise HTTPException(status_code=status_code, detail="Failed to verify user")

    user_mdl = User.parse_obj(user)
    await cookie_backend.create(session_id=session_id, data=user_mdl)

    response = Response(user_mdl.json(), status_code=200, media_type="application/json")
    cookie.attach_to_response(response, session_id)

    logger.info(
        f"User {user['discord_username']} ({user['discord_id']}) with osu! account {user['osu_username']} ({user['osu_id']}) verified successfully",
    )

    return response


@auth_router.post("/deauth", dependencies=[Depends(cookie)])
async def deauth_handler(
    user: User = Depends(cookie_verifier),
) -> Response:
    _user = await users.remove_verification(user.discord_id)

    if isinstance(user, ServiceError):
        status_code = determine_status_code(user)
        raise HTTPException(status_code=status_code, detail="Failed to verify user")

    await cookie_backend.delete(session_id=_user["session_id"])  # type: ignore

    logger.info(
        f"User {_user['discord_username']} ({_user['discord_id']}) with osu! account {_user['osu_username']} ({_user['osu_id']}) deauthenticated successfully",  # type: ignore
    )

    return Response(status_code=200)


@auth_router.get("/user", dependencies=[Depends(cookie)])
async def user_handler(user: User = Depends(cookie_verifier)) -> Response:
    return Response(user.json(), media_type="application/json")
