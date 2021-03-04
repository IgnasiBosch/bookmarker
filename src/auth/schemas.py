import secrets
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, SecretStr, validator

from src.common.schemas import CamelModel


class Credentials(BaseModel):
    username: EmailStr
    password: SecretStr


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    hashed_password: SecretStr
    last_login_at: Optional[datetime]
    is_active: bool = True
    failed_attempts: int = 0


class JWTPayload(CamelModel):
    sub: str
    exp: Optional[int]


class PublicAccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SessionFilter(BaseModel):
    user_id: Optional[UUID]
    created_before: Optional[datetime]
    is_active: Optional[bool]


class Session(BaseModel):
    id: UUID
    user: User
    token: str
    created_at: datetime
    is_active: bool


class SessionCreate(Session):
    id: UUID = Field(default_factory=uuid4)
    user: User
    token: Optional[str]
    created_at: Optional[datetime]
    is_active: bool = True

    @validator("token", always=True)
    def token_generator(cls, v, **kwargs):
        return secrets.token_urlsafe(32)

    @validator("created_at", always=True)
    def created_now(cls, v, **kwargs):
        return datetime.now(timezone.utc)
