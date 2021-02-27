from datetime import datetime, timezone, timedelta

from src.auth.exceptions import (
    InvalidCredentials,
    MaxFailedAttemptsRaised,
    TokenError,
    ExpiredToken,
    NotExpiredToken,
)
from src.auth.repos import users, sessions
from src.auth.schemas import (
    Credentials,
    User,
    PublicAccessToken,
    SessionCreate,
    SessionFilter,
    Session,
)
from src.auth.utils import is_valid_password, to_public_token, decode_token
from src.db import database
from src.config import settings


async def login(credentials: Credentials) -> PublicAccessToken:
    user = await validate_credentials(credentials)

    if user.failed_attempts >= settings.max_failed_login_attempts:
        raise MaxFailedAttemptsRaised

    async with database.transaction():
        session = await sessions.add(SessionCreate(user=user))

        user.last_login_at = datetime.now(timezone.utc)
        user.failed_attempts = 0
        await users.update(user)

    return to_public_token(session)


async def logout(session: Session):
    await sessions.delete([session])


async def validate_credentials(credentials: Credentials) -> User:
    user = await users.get(email=credentials.username)

    if user is None or not user.is_active:
        raise InvalidCredentials

    if not is_valid_password(
        plain_password=credentials.password, hashed_password=user.hashed_password
    ):
        user.failed_attempts += 1
        await users.update(user)
        raise InvalidCredentials

    return user


async def refresh_session(session: Session) -> PublicAccessToken:

    if session.created_at.replace(tzinfo=timezone.utc) + timedelta(
        days=settings.access_token_max_refreshable_days
    ) <= datetime.now(timezone.utc):
        raise TokenError

    new_session = await sessions.add(SessionCreate(user=session.user))
    return to_public_token(new_session)


async def get_session_from_public_token(public_token: PublicAccessToken) -> Session:
    jwt_payload = decode_token(public_token.access_token)
    session = await sessions.get(token=jwt_payload.sub)

    if session is None:
        raise TokenError

    if session.created_at.replace(tzinfo=timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    ) <= datetime.now(timezone.utc):
        raise ExpiredToken

    return session


async def get_expired_session_from_public_token(
    public_token: PublicAccessToken,
) -> Session:
    jwt_payload = decode_token(public_token.access_token, verify_exp=False)
    session = await sessions.get(token=jwt_payload.sub)

    if session is None:
        raise TokenError

    if not session.created_at.replace(tzinfo=timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    ) <= datetime.now(timezone.utc):
        raise NotExpiredToken

    return session


async def prune_old_sessions():
    threshold_time = datetime.now(timezone.utc) - timedelta(
        days=settings.remove_sessions_older_than_days
    )
    session_filter = SessionFilter(created_before=threshold_time, is_active=False)

    async with database.transaction():
        sessions_to_delete = await sessions.filter(session_filter)
        await sessions.delete(sessions_to_delete)
