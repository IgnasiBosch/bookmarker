from typing import Optional, Iterable
from uuid import UUID

from pymysql import IntegrityError
from sqlalchemy import select, or_

from src.auth.exceptions import DuplicatedToken
from src.auth.schemas import Session, SessionFilter, User, SessionCreate
from src.auth.tables import sessions, users
from src.db import database


async def add(session: SessionCreate) -> Session:
    try:
        query = sessions.insert().values(
            user_id=session.user.id, **session.dict(exclude={"user"})
        )
        _ = await database.execute(query)
    except IntegrityError:
        raise DuplicatedToken
    else:
        return session


async def get(
    id: Optional[UUID] = None, token: Optional[str] = None
) -> Optional[Session]:
    if id is None and token is None:
        raise ValueError("Id or token are needed to get a session entry")

    join = sessions.join(users, sessions.c.user_id == users.c.id)
    query = select(
        [
            sessions,
            users.c.email,
            users.c.last_login_at,
            users.c.is_active.label("user_is_active"),
            users.c.failed_attempts,
            users.c.hashed_password,
        ]
    ).select_from(join)

    if id:
        query = query.where(sessions.c.id == id)
    if token:
        query = query.where(sessions.c.token == token)

    result = await database.fetch_one(query)
    if result:
        return result_mapper(result)
    else:
        return None


async def filter(filter_params: SessionFilter) -> Iterable[Session]:
    filters = []
    if filter_params.user_id:
        filters.append(sessions.c.user_id == filter_params.user_id)
    if filter_params.created_before:
        filters.append(sessions.c.created_at <= filter_params.created_before)
    if filter_params.is_active is not None:
        filters.append(sessions.c.is_active == filter_params.is_active)

    where_clause = or_(*filters)

    join = sessions.join(users, sessions.c.user_id == users.c.id)
    query = (
        select(
            [
                sessions,
                users.c.email,
                users.c.last_login_at,
                users.c.is_active.label("user_is_active"),
                users.c.failed_attempts,
                users.c.hashed_password,
            ]
        )
        .select_from(join)
        .where(where_clause)
        .order_by(sessions.c.created_at.desc(), sessions.c.id)
    )

    result = await database.fetch_all(query)
    return (result_mapper(r) for r in result)


async def delete(sessions_: Iterable[Session]):
    query = sessions.delete().where(sessions.c.id.in_([s.id for s in sessions_]))
    _ = await database.execute(query)


def result_mapper(result) -> Session:
    user = User(
        id=result.user_id,
        email=result.email,
        last_login_at=result.last_login_at,
        is_active=result.user_is_active,
        failed_attempts=result.failed_attempts,
        hashed_password=result.hashed_password,
    )
    return Session(**dict(result), user=user)
