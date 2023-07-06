from __future__ import annotations

from aiosu.utils import auth
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from orjson import JSONDecodeError

from app.common import settings
from app.services import users

auth_router = APIRouter(default_response_class=Response)


@auth_router.post("/auth")
async def auth_handler(request: Request):
    body = await request.json()
    # TODO: Maybe also validate if both codes aren't empty
    if "kohaku_code" not in body or "osu_code" not in body:
        raise HTTPException(status_code=400, detail="Missing codes in request body")

    user = await users.fetch_by_verification_code(body["kohaku_code"])

    if isinstance(user, users.ServiceError):
        if user is users.ServiceError.USER_NOT_FOUND:
            raise HTTPException(status_code=404, detail="User not found")

    # TODO: Check if user is already authenticated

    try:
        token = await auth.process_code(
            client_id=settings.OSU_CLIENT_ID,
            client_secret=settings.OSU_CLIENT_SECRET,
            redirect_uri=settings.OSU_REDIRECT_URI,
            code=body["osu_code"],
        )
    except:
        raise HTTPException(status_code=403, detail="Invalid osu! code")

    # TODO: Remove this after testing :tf:
    print("******************")
    print(token)
    print("******************")

    # TODO: Save access token, refresh token and user info to the database

    # TODO: Log user authentication
    return Response(status_code=204)
