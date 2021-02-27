from src.auth.exceptions import InvalidCredentials
from src.auth.repos import users, sessions
from src.auth.schemas import Credentials, User, PublicAccessToken, SessionCreate
from src.auth.utils import is_valid_password, to_public_token


async def obtain_access_token(credentials: Credentials) -> PublicAccessToken:
    user = await validate_credentials(credentials)
    session = await sessions.add(SessionCreate(user=user))

    return to_public_token(session)


async def validate_credentials(credentials: Credentials) -> User:
    user = await users.get(email=credentials.email)

    if user is None or not is_valid_password(
        plain_password=credentials.password, hashed_password=user.hashed_password
    ):
        raise InvalidCredentials

    return user
