from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from pymysql import IntegrityError

from src.auth.exceptions import EmailAlreadyUsed
from src.auth.schemas import User
from src.auth.tables import users
from src.db import database


async def add(user: User) -> User:
    try:
        query = users.insert().values(
            hashed_password=user.hashed_password.get_secret_value(),
            **user.dict(exclude={"hashed_password"})
        )
        _ = await database.execute(query)

    except IntegrityError:
        raise EmailAlreadyUsed
    else:
        return user


async def update(user: User) -> User:
    try:
        query = (
            users.update()
            .where(users.c.id == user.id)
            .values(**user.dict(exclude={"hashed_password"}))
        )
        _ = await database.execute(query)

    except IntegrityError:
        raise EmailAlreadyUsed
    else:
        return user


async def get(
    id: Optional[UUID] = None, email: Optional[EmailStr] = None
) -> Optional[User]:
    if id is None and email is None:
        raise ValueError("Id or Email are needed to get a user entry")

    query = users.select()

    if id:
        query = query.where(users.c.id == id)
    if email:
        query = query.where(users.c.email == email)

    result = await database.fetch_one(query)
    if result:
        return User(**dict(result))
    else:
        return None
