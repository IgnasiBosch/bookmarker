from src.auth.repos import users
from src.auth.schemas import User, UserCreate
from src.auth.utils import hash_password


async def create_new_user(user: UserCreate) -> User:
    return await users.add(
        User(
            email=user.email,
            hashed_password=hash_password(user.password),
        )
    )
