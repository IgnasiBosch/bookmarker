from datetime import timedelta, datetime, timezone

from fastapi.encoders import jsonable_encoder
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.hash import argon2
from pydantic import SecretStr

from src.auth.exceptions import ExpiredToken, TokenError
from src.auth.schemas import JWTPayload, Session, PublicAccessToken
from src.config import Settings, settings


def is_valid_password(plain_password: SecretStr, hashed_password: SecretStr):
    return argon2.verify(
        plain_password.get_secret_value(), hashed_password.get_secret_value()
    )


def hash_password(password: SecretStr):
    return argon2.hash(password.get_secret_value())


def token(settings: Settings):
    def encode(payload: dict) -> str:
        return jwt.encode(
            payload,
            settings.access_token_secret_key,
            algorithm=settings.access_token_algorithm,
        )

    def decode(token_str: str, verify_exp=True) -> JWTPayload:
        try:
            payload = jwt.decode(
                token_str,
                settings.access_token_secret_key,
                algorithms=[settings.access_token_algorithm],
                options={"verify_exp": verify_exp},
            )
            return JWTPayload(**payload)
        except ExpiredSignatureError:
            raise ExpiredToken
        except JWTError:
            raise TokenError

    return encode, decode


encode_token, decode_token = token(settings)


def to_public_token(session: Session) -> PublicAccessToken:
    jwt_token = JWTPayload(sub=session.token)

    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    # https://docs.python.org/3.8/library/datetime.html#datetime.datetime.utcnow
    expire = datetime.now(timezone.utc) + expires_delta

    jwt_token.exp = int(datetime.timestamp(expire))
    encoded_token = encode_token(
        jsonable_encoder(jwt_token.dict(exclude_none=True, by_alias=True))
    )

    return PublicAccessToken(access_token=encoded_token)
