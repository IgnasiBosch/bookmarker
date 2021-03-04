import sqlalchemy as sa
from fastapi_utils.guid_type import GUID

from src.db import metadata

bookmarks = sa.Table(
    "bookmarks",
    metadata,
    sa.Column("id", GUID, primary_key=True),
    sa.Column("url", sa.String(1000)),
    sa.Column("url_hash", sa.String(40), unique=True),
    sa.Column("title", sa.String(255), nullable=True),
    sa.Column("source", sa.String(50)),
    sa.Column("author", sa.String(50), nullable=True),
    sa.Column("description", sa.String(500), nullable=True),
    sa.Column("image_url", sa.String(500), nullable=True),
    sa.Column("last_fetch_at", sa.DateTime, nullable=True),
    sa.Column("is_active", sa.Boolean, default=True),
    sa.Column("failed_attempts", sa.Integer, default=0),
    sa.Column("is_read", sa.Boolean, default=False),
)
