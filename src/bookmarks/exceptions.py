from http import HTTPStatus
from typing import Optional

from src.common.exceptions import BaseError


class BookmarkNotFound(BaseError):
    def __init__(self, msg: Optional[str] = "Bookmark doesn't exist"):
        super().__init__(msg, 3001, HTTPStatus.UNPROCESSABLE_ENTITY)
