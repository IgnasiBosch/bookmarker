from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.responses import JSONResponse

from src.auth.exceptions import TokenError, ExpiredToken, NotExpiredToken
from src.auth.schemas import PublicAccessToken, Credentials, Session
from src.auth.use_cases.session import (
    login,
    get_session_from_public_token,
    get_expired_session_from_public_token,
    refresh_session,
    logout,
)

router = APIRouter()


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/login")


async def get_current_session(
    token: str = Depends(reusable_oauth2),
) -> Session:

    try:
        return await get_session_from_public_token(
            PublicAccessToken(access_token=token)
        )
    except TokenError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Incorrect Token"
        )
    except ExpiredToken:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Expired Token")


async def get_current_expired_session(
    token: str = Depends(reusable_oauth2),
) -> Session:
    try:
        return await get_expired_session_from_public_token(
            PublicAccessToken(access_token=token)
        )
    except NotExpiredToken:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Token is not expired",
        )
    except TokenError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Incorrect Token"
        )


@router.post(
    "/api/login",
    name="Get Token",
    response_model=PublicAccessToken,
    response_description="Returns user access token",
    summary="Authenticate API user",
    description="Authenticate an API user and return a token for subsequent requests",
    include_in_schema=False,
)
async def login_handler(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    try:
        return await login(
            Credentials(username=form_data.username, password=form_data.password)
        )

    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Incorrect credentials",
        )


@router.post(
    "/api/token",
    name="Get Token",
    response_model=PublicAccessToken,
    response_description="Returns user access token",
    summary="Authenticate API user",
    description="Authenticate an API user and return a token for subsequent requests",
    include_in_schema=False,
)
async def api_token_handler(credentials: Credentials):
    try:
        return await login(credentials)

    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Incorrect credentials",
        )


@router.post("/api/logout")
async def bookmarks_handle(
    session: Session = Depends(get_current_session),
):
    await logout(session)
    return JSONResponse({"status": "ok"})


@router.post(
    "/refresh-session",
    name="Refresh Token",
    response_model=PublicAccessToken,
    response_description="Same response as Token endpoint",
    summary="Refreshes user access token",
    description="When a Token has expired you can obtain another one refreshing it "
    "from this endpoint. Notice that the token has to be expired",
)
async def refresh_token_handler(
    session: Session = Depends(get_current_expired_session),
):
    try:
        return await refresh_session(session)

    except TokenError:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Incorrect token",
        )
