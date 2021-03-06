import hashlib
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import AnyHttpUrl, BaseModel, Field, validator
from superslug import slugify

from src.common.schemas import PaginationResult
from src.config import settings


class Source(str, Enum):
    GITHUB = "github"
    MEDIUM = "medium"
    YOUTUBE = "youtube"
    GOOGLE_BOOKS = "google books"
    IMAGE = "image"
    OTHER = "other"
    UNDEFINED = "undefined"


class Label(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    slug: str

    @validator("slug")
    def slug_name(cls, v, values, **kwargs):
        if "name" in values:
            return slugify(values["name"])
        return v


class BookmarkStats(BaseModel):
    pending: int
    total: int
    inactive: int
    available: int


class OrderedBy(str, Enum):
    random = "random"
    last_fetch_asc = "date"
    last_fetch_desc = "-date"


class OrderParams(BaseModel):
    order_by: Optional[OrderedBy]


class PaginationParams(BaseModel):
    items_per_page: int
    current_page: int


class Url(BaseModel):
    url: AnyHttpUrl


class BookmarkFilter(BaseModel):
    id: Optional[UUID]
    url: Optional[AnyHttpUrl]
    source: Optional[Source]
    author: Optional[str]
    is_active: Optional[bool]
    is_read: Optional[bool]
    last_fetched_before: Optional[datetime]
    pending_to_fetch: Optional[bool]
    only_fetched: Optional[bool]


class Bookmark(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: Optional[str]
    url: AnyHttpUrl
    url_hash: Optional[str]
    source: Optional[Source]
    author: Optional[str]
    description: Optional[str]
    image_url: Optional[AnyHttpUrl]
    last_fetch_at: Optional[datetime]
    labels: Optional[List[Label]]
    is_active: bool = True
    failed_attempts: int = 0
    is_read: bool = False

    @validator("url_hash", pre=True, always=True)
    def url_hasher(cls, v, values, **kwargs):
        if "url" in values:
            hasher = hashlib.sha1()
            hasher.update(values["url"].encode())
            return hasher.hexdigest()
        return v

    @validator("image_url", pre=True, always=True)
    def default_image(cls, v, values, **kwargs):
        if not v:
            return f"{settings.base_url}/static/placeholder.jpg"
        return v


class BookmarkResponse(BaseModel):
    items: List[Bookmark]
    pagination: Optional[PaginationResult]
