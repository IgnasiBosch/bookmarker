import sqlalchemy as sa
from fastapi_utils.guid_type import GUID
from sqlalchemy import ForeignKey

from src.db import metadata


users = sa.Table(
    "users",
    metadata,
    sa.Column("id", GUID, primary_key=True),
    sa.Column("email", sa.String(255), unique=True),
    sa.Column("hashed_password", sa.String(255)),
    sa.Column("last_login_at", sa.DateTime, nullable=True),
    sa.Column("is_active", sa.Boolean, default=True),
    sa.Column("failed_attempts", sa.Integer, default=0),
)


sessions = sa.Table(
    "sessions",
    metadata,
    sa.Column("id", GUID, primary_key=True),
    sa.Column("user_id", GUID, ForeignKey("users.id")),
    sa.Column("token", sa.String(255), unique=True, nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=True),
    sa.Column("is_active", sa.Boolean, default=True),
)
